# SPARK.md — Project Rules

This file defines conventions and rules for this project.
The AI agent (Spark) reads this on startup and follows these guidelines.

## Code Style

- Use TypeScript for new files
- 2-space indentation
- Prefer `const` over `let` and `function` over `const fn = () =>`
- File names: kebab-case for utils, PascalCase for components
- CSS: Tailwind utility classes preferred over custom CSS

## Architecture

- Frontend: Vue 3 + Pinia + Vue Router
- Backend: Fastify + Prisma + PostgreSQL
- Monorepo with pnpm workspaces

## Conventions

- Commit messages: conventional commits (feat:, fix:, chore:, docs:)
- Branch names: feat/description, fix/description
- Tests required for all new features
- PR description must include screenshots for UI changes
