# Keystone AI

## Project Overview

Keystone is an Adaptive Multi-Agent AI Orchestration Platform.

The objective is NOT to build another chatbot.

Keystone coordinates multiple AI agents to solve complex engineering tasks through planning, execution, validation, retries and reporting.

Current status:
Prototype / MVP

---

# Team

Frontend
- Built using Next.js 15
- Tailwind CSS v4
- TypeScript
- shadcn/ui

Backend
- FastAPI
- SQLite (prototype)
- Python

---

# Vision

The user gives one objective.

Example:

"Build a FastAPI authentication service."

Keystone will:

Planner
↓

Research Agent
↓

Executor Agent
↓

Validator Agent
↓

Reporter Agent

Each agent has a dedicated responsibility.

The frontend visualizes the workflow.

The backend executes it.

---

# Product Philosophy

Keystone is NOT:

- ChatGPT
- Cursor
- GitHub Copilot
- Analytics Dashboard
- Admin Panel

Keystone IS:

An engineering workspace for orchestrating AI agents.

---

# UI Principles

Style inspiration:

- Cursor IDE
- Claude Desktop
- Linear
- Vercel

Design rules:

- Minimal
- Professional
- Large whitespace
- Rounded corners
- Subtle borders
- Dark and Light mode
- No gradients
- No glassmorphism
- No dashboard metrics
- No fake statistics

---

# Frontend Roadmap

Completed

✓ Landing Page

✓ Navigation Bar

✓ Theme Toggle (needs stabilization)

Next

1. Chat Workspace

2. Workflow Panel

3. Agent Timeline

4. Logs

5. Settings

6. Backend Integration

---

# Chat Workspace

This is the primary screen.

Layout

Sidebar

↓

Chat Area

↓

Workflow Monitor

↓

Input Box

The chat page is the heart of Keystone.

---

# Workflow

Planner

↓

Research

↓

Executor

↓

Validator

↓

Reporter

The UI should display each stage.

No fake percentages.

No analytics.

Only real execution status.

---

# Backend

Backend is developed independently.

Frontend must consume backend APIs.

Do NOT implement fake backend logic.

Do NOT simulate completed workflows.

---

# AI Agent Rules

When modifying this project:

1. Do NOT redesign unrelated pages.

2. Do NOT modify more than one feature at a time.

3. Reuse existing components whenever possible.

4. Never replace working code unless requested.

5. Explain major architectural changes before making them.

6. If more than five files require modification, stop and explain why.

7. Preserve existing project structure.

---

# Git Workflow

Every completed milestone:

git status

↓

git add .

↓

git commit

↓

git push

Never mix multiple features into one commit.

---

# Coding Standards

Use:

TypeScript

Functional Components

App Router

Reusable Components

Clean Folder Structure

Meaningful Names

Avoid:

Huge components

Duplicate code

Hardcoded mock analytics

Unused dependencies

---

# Long-term Goal

Keystone should feel like an operating system for AI agents rather than a chatbot.

Users should be able to:

Create workflows

Monitor execution

Inspect agent decisions

Retry failed stages

View audit history

Review final reports

All from one workspace.