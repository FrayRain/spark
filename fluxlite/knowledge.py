"""Knowledge base — local semantic search over project files.

Zero external dependencies (no torch, no faiss). Uses character n-gram TF-IDF
for fast, offline code-aware search. Optionally upgrades to sentence-transformers
if installed.

Usage:
    kb = KnowledgeBase(project_root)
    kb.build()              # index all project files
    results = kb.search("user auth flow")  # list of {file, line, content, score}
"""
import os
import json
import math
import re
import hashlib
import time
from pathlib import Path
from collections import Counter
from datetime import datetime
from .i18n import _

KNOWLEDGE_DIR = Path.home() / ".fluxlite" / "knowledge"

INDEX_EXTENSIONS = {
    ".py", ".md", ".rst", ".txt", ".toml", ".yaml", ".yml",
    ".json", ".cfg", ".ini", ".env.example",
    ".js", ".ts", ".jsx", ".tsx", ".rs", ".go", ".java",
    ".c", ".cpp", ".h", ".hpp", ".sql",
}

EXCLUDE_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".tox", ".egg-info", "dist", "build", ".idea", ".vscode",
    ".mypy_cache", ".pytest_cache", ".ruff_cache", ".claude",
}

CHUNK_MIN_CHARS = 80
CHUNK_MAX_CHARS = 1500
MAX_CHUNKS = 3000


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _py_chunks(text: str, filepath: str) -> list[dict]:
    """Split Python file into chunks at class/function boundaries."""
    lines = text.split("\n")
    chunks: list[dict] = []
    buf_start = 0
    buf_end = 0
    heading = ""

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()

        # Detect function/class definition or standalone block
        is_boundary = (
            stripped.startswith("def ")
            or stripped.startswith("async def ")
            or stripped.startswith("class ")
            or stripped.startswith("@")
            or (stripped.startswith("#") and lineno > buf_end + 1)
        )

        # Flush chunk at boundary if current buffer is large enough
        if is_boundary and (lineno - buf_start > 3 or _buf_char_count(lines, buf_start, lineno) >= CHUNK_MIN_CHARS):
            if buf_start < lineno - 1:
                content = "\n".join(lines[buf_start:lineno - 1])
                if content.strip():
                    chunks.append({
                        "file": filepath,
                        "start": buf_start + 1,
                        "end": lineno - 1,
                        "heading": heading,
                        "content": content,
                    })
            buf_start = lineno - 1
            buf_end = lineno - 1
            heading = stripped

        # Flush when buffer exceeds max size
        if _buf_char_count(lines, buf_start, lineno) >= CHUNK_MAX_CHARS:
            content = "\n".join(lines[buf_start:lineno])
            if content.strip():
                chunks.append({
                    "file": filepath,
                    "start": buf_start + 1,
                    "end": lineno,
                    "heading": heading,
                    "content": content,
                })
            buf_start = lineno
            heading = ""

    # Flush remainder
    if buf_start < len(lines):
        content = "\n".join(lines[buf_start:])
        if content.strip():
            chunks.append({
                "file": filepath,
                "start": buf_start + 1,
                "end": len(lines),
                "heading": heading,
                "content": content,
            })

    return chunks


def _md_chunks(text: str, filepath: str) -> list[dict]:
    """Split markdown at heading boundaries."""
    lines = text.split("\n")
    chunks: list[dict] = []
    buf_start = 0
    heading = ""

    for lineno, line in enumerate(lines, 1):
        if line.startswith("##") and lineno > 1:
            if lineno - buf_start > 2:
                content = "\n".join(lines[buf_start:lineno - 1])
                if content.strip():
                    chunks.append({
                        "file": filepath,
                        "start": buf_start + 1,
                        "end": lineno - 1,
                        "heading": heading,
                        "content": content,
                    })
                buf_start = lineno - 1
                heading = line.lstrip("#").strip()

    if buf_start < len(lines):
        content = "\n".join(lines[buf_start:])
        if content.strip():
            chunks.append({
                "file": filepath,
                "start": buf_start + 1,
                "end": len(lines),
                "heading": heading,
                "content": content,
            })

    return chunks


def _generic_chunks(text: str, filepath: str) -> list[dict]:
    """Split generic text at paragraph boundaries."""
    paragraphs = re.split(r"\n\n+", text)
    chunks: list[dict] = []
    line_offset = 0
    buf = []
    buf_start = 0
    char_count = 0

    for para in paragraphs:
        lines = para.split("\n")
        para_chars = len(para)

        if char_count + para_chars > CHUNK_MAX_CHARS and buf:
            chunks.append({
                "file": filepath,
                "start": buf_start + 1,
                "end": buf_start + len(buf),
                "heading": "",
                "content": "\n".join(buf),
            })
            buf = []
            char_count = 0

        if not buf:
            buf_start = line_offset
        buf.extend(lines)
        buf.append("")
        char_count += para_chars + 1
        line_offset += len(lines) + 1

    if buf:
        chunks.append({
            "file": filepath,
            "start": buf_start + 1,
            "end": buf_start + len(buf),
            "heading": "",
            "content": "\n".join(buf).rstrip(),
        })

    return chunks


def _buf_char_count(lines: list[str], start: int, end: int) -> int:
    return sum(len(l) for l in lines[start:end])


def _chunk_file(path: Path, root: Path) -> list[dict]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return []

    rel = str(path.relative_to(root))
    ext = path.suffix.lower()

    if ext == ".py":
        return _py_chunks(text, rel)
    elif ext in (".md", ".rst"):
        return _md_chunks(text, rel)
    else:
        return _generic_chunks(text, rel)


# ---------------------------------------------------------------------------
# TF-IDF vectorization (zero external deps)
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Extract character n-grams (n=2,3,4) for code-aware tokenization."""
    text = text.lower()
    # Preserve code identifiers, split on whitespace/punctuation
    tokens = re.findall(r"[a-z0-9_#.]+", text)
    # Add character n-grams for fuzzy matching
    ngrams = []
    for t in tokens:
        ngrams.append(t)
        if len(t) > 3:
            for n in (2, 3):
                for i in range(len(t) - n + 1):
                    ngrams.append(t[i:i + n])
    return ngrams


def _compute_idf(chunks: list[dict]) -> dict[str, float]:
    """Compute IDF for all tokens across chunks."""
    doc_count = Counter()
    for ch in chunks:
        tokens = set(_tokenize(ch["content"]))
        for t in tokens:
            doc_count[t] += 1
    n = len(chunks)
    return {t: math.log((n + 1) / (c + 1)) + 1 for t, c in doc_count.items()}


def _vectorize(text: str, idf: dict[str, float]) -> dict[str, float]:
    """Convert text to TF-IDF weighted vector (sparse dict)."""
    tokens = _tokenize(text)
    tf = Counter(tokens)
    return {t: tf[t] * idf.get(t, 1.0) for t in tf}


def _cosine_sim(a: dict[str, float], b: dict[str, float]) -> float:
    """Cosine similarity between two sparse vectors."""
    common = set(a) & set(b)
    if not common:
        return 0.0
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


# ---------------------------------------------------------------------------
# Sentence-transformers integration (optional upgrade)
# ---------------------------------------------------------------------------

def _try_st_embed(texts: list[str]) -> list[list[float]] | None:
    """Try embedding with sentence-transformers. Returns None if not installed."""
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        return None
    try:
        model = SentenceTransformer("all-MiniLM-L6-v2")
        vectors = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Main KnowledgeBase
# ---------------------------------------------------------------------------

class KnowledgeBase:
    """Project-level knowledge base with file chunking and search.

    Usage:
        kb = KnowledgeBase(project_root)
        print(kb.build())       # index or reload
        results = kb.search("auth middleware")
    """

    def __init__(self, project_root: str | Path):
        self.root = Path(project_root).resolve()
        _hash = hashlib.md5(str(self.root).encode()).hexdigest()[:12]
        self.store_dir = KNOWLEDGE_DIR / _hash
        self.chunks: list[dict] = []
        self.idf: dict[str, float] = {}
        self.st_vectors: list[list[float]] | None = None
        self._built = False
        self._build_time = 0
        self._file_mtimes: dict[str, float] = {}

    # -- Public API ---------------------------------------------------------

    def build(self, force: bool = False) -> str:
        """Build or rebuild the index. Incremental if not forced."""
        t0 = time.time()

        # Discover files
        files = self._discover_files()

        if not force and self.store_dir.exists():
            loaded = self._load()
            if loaded:
                # Check if any files changed
                need_rebuild = self._check_changes(files)
                if not need_rebuild:
                    self._built = True
                    elapsed = time.time() - t0
                    return _("know_up_to_date", chunks=len(self.chunks), elapsed=elapsed)

        # Full rebuild
        self.chunks = []
        for fp in files:
            self.chunks.extend(_chunk_file(fp, self.root))

        if not self.chunks:
            return _("know_no_files")

        if len(self.chunks) > MAX_CHUNKS:
            self.chunks = self.chunks[:MAX_CHUNKS]

        # Build TF-IDF
        self.idf = _compute_idf(self.chunks)
        self._file_mtimes = {str(f.relative_to(self.root)): f.stat().st_mtime for f in files}

        # Try sentence-transformers upgrade
        texts = [c["content"][:1000] for c in self.chunks]
        self.st_vectors = _try_st_embed(texts)

        self._save()
        self._built = True
        elapsed = time.time() - t0
        mode = "st" if self.st_vectors else "tfidf"
        return _("know_indexed", chunks=len(self.chunks), files=len(files), mode=mode, elapsed=elapsed)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search index and return top-k chunks with scores."""
        if not self._built or not self.chunks:
            return []

        if self.st_vectors:
            return self._search_st(query, top_k)
        return self._search_tfidf(query, top_k)

    def is_built(self) -> bool:
        return self._built

    def stats(self) -> str:
        """Return a summary string."""
        if not self._built or not self.chunks:
            return _("know_not_init")
        mode = "sentence-transformers" if self.st_vectors else "TF-IDF (char n-gram)"
        return (
            f"[knowledge] {len(self.chunks)} chunks, {len(self.idf)} tokens, "
            f"mode={mode}"
        )

    # -- Internal -----------------------------------------------------------

    def _discover_files(self) -> list[Path]:
        files = []
        try:
            for dirpath, dirnames, filenames in os.walk(self.root):
                dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS and not d.startswith(".")]
                for fn in filenames:
                    if fn.startswith("."):
                        continue
                    fp = Path(dirpath) / fn
                    if fp.suffix.lower() in INDEX_EXTENSIONS:
                        files.append(fp)
        except OSError:
            pass
        return sorted(files)

    def _check_changes(self, files: list[Path]) -> bool:
        current = {}
        for fp in files:
            try:
                rel = str(fp.relative_to(self.root))
                current[rel] = fp.stat().st_mtime
            except (OSError, ValueError):
                continue
        if set(current.keys()) != set(self._file_mtimes.keys()):
            return True
        for rel, mtime in current.items():
            if abs(mtime - self._file_mtimes.get(rel, 0)) > 0.001:
                return True
        return False

    def _search_tfidf(self, query: str, top_k: int) -> list[dict]:
        qvec = _vectorize(query, self.idf)
        scored = []
        for ch in self.chunks:
            dvec = _vectorize(ch["content"], self.idf)
            score = _cosine_sim(qvec, dvec)
            if score > 0.01:
                scored.append((score, ch))
        scored.sort(key=lambda x: -x[0])
        results = []
        for score, ch in scored[:top_k]:
            results.append({
                "file": ch["file"],
                "start": ch["start"],
                "end": ch["end"],
                "heading": ch.get("heading", ""),
                "score": round(score, 4),
                "content": ch["content"],
            })
        return results

    def _search_st(self, query: str, top_k: int) -> list[dict]:
        qvec = _try_st_embed([query])
        if not qvec or not self.st_vectors:
            return self._search_tfidf(query, top_k)
        import numpy as np
        q = np.array(qvec[0])
        mat = np.array(self.st_vectors)
        scores = mat @ q  # normalized, so dot = cosine
        top_idx = np.argsort(scores)[-top_k:][::-1]
        results = []
        for idx in top_idx:
            if scores[idx] > 0.1:
                ch = self.chunks[idx]
                results.append({
                    "file": ch["file"],
                    "start": ch["start"],
                    "end": ch["end"],
                    "heading": ch.get("heading", ""),
                    "score": round(float(scores[idx]), 4),
                    "content": ch["content"],
                })
        return results

    # -- Persistence --------------------------------------------------------

    def _save(self):
        self.store_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "built_at": datetime.now().isoformat(),
            "file_mtimes": self._file_mtimes,
            "chunks": [
                {k: v for k, v in c.items() if k != "content"}
                for c in self.chunks
            ],
            "content": [c["content"] for c in self.chunks],
            "idf_tokens": list(self.idf.keys()),
            "idf_values": list(self.idf.values()),
        }
        # Save metadata + content separately to keep json manageable
        (self.store_dir / "meta.json").write_text(
            json.dumps(data, ensure_ascii=False), encoding="utf-8"
        )
        if self.st_vectors:
            try:
                import numpy as np
                np.save(self.store_dir / "vectors.npy", np.array(self.st_vectors))
            except Exception:
                pass

    def _load(self) -> bool:
        meta_path = self.store_dir / "meta.json"
        if not meta_path.exists():
            return False
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False

        self._file_mtimes = data.get("file_mtimes", {})
        chunks_meta = data.get("chunks", [])
        content_list = data.get("content", [])
        tokens = data.get("idf_tokens", [])
        values = data.get("idf_values", [])

        if len(chunks_meta) != len(content_list):
            return False

        self.chunks = []
        for i, meta in enumerate(chunks_meta):
            self.chunks.append({**meta, "content": content_list[i]})

        self.idf = dict(zip(tokens, values))

        # Load sentence-transformers vectors if available
        vec_path = self.store_dir / "vectors.npy"
        if vec_path.exists():
            try:
                import numpy as np
                self.st_vectors = np.load(vec_path).tolist()
            except Exception:
                self.st_vectors = None

        self._built = True
        return True
