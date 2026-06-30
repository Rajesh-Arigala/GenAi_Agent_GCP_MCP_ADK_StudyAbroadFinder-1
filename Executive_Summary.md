# Study Abroad Finder (Google ADK + MCP) — One Page Execution Summary

## Objective

Build a production-oriented AI application using **Google ADK**, **Gemini 2.5 Flash**, and **Model Context Protocol (MCP)** that helps students discover universities by orchestrating multiple MCP servers instead of relying solely on prompt engineering.

---

# Initial Architecture

```
Browser
   │
Flask
   │
Google ADK
   │
Gemini 2.5 Flash
   │
MCP Servers
```

Planned MCP Servers

- Tavily MCP (University Search)
- Google Maps MCP (Weather + Nearby Places)
- Scholarship MCP (Scholarships, Cost of Living, Visa)
- Filesystem MCP (Generate Markdown Reports)

---

# Phase 1 — Gemini Validation

Validated:

- Google API Key
- Gemini SDK
- Google ADK
- Latest Gemini model

Issues Fixed

- Invalid API Key
- Deprecated model (`gemini-2.0-flash`)
- Migrated to:

```
gemini-2.5-flash
```

Result

✅ Gemini working locally

---

# Phase 2 — Scholarship MCP

Objective

Validate Local Python MCP.

Result

- Scholarships
- Visa
- Cost of Living

were successfully returned.

Conclusion

✅ Python-based Local MCP works.

---

# Phase 3 — Filesystem MCP

Objective

Generate Markdown reports.

Local

✅ Worked

Render

❌ Failed

Symptoms

- Failed MCP Session
- Worker Timeout
- Hanging Requests

Initial assumption

Filesystem MCP was broken.

Later discovered

Filesystem MCP required

```
Node
npm
npx
```

---

# Phase 4 — Tavily MCP

Objective

Validate Remote MCP.

Result

- University Search
- Live Search

worked successfully.

Conclusion

✅ Remote HTTP MCP works.

---

# Phase 5 — Google Maps MCP

Validated

- Weather
- Nearby Places

Issues Fixed

- API Keys
- Authentication
- Google configuration

Conclusion

✅ Maps MCP works.

---

# Root Cause Analysis

At this point

Everything worked except

Filesystem MCP on Render.

Observation

Scholarship MCP

↓

Python

Filesystem MCP

↓

Node.js

The problem was NOT

- Google ADK
- Gemini
- MCP

The problem was

Runtime.

---

# Engineering Strategy

Instead of debugging everything together,

every MCP server was isolated.

Testing sequence

```
Gemini

↓

Scholarship MCP

↓

Filesystem MCP

↓

Tavily MCP

↓

Google Maps MCP

↓

Combined Agent
```

This identified the exact failing component.

---

# Docker Decision

Three options were considered.

Option A

Remove Filesystem MCP.

Option B

Rewrite Filesystem functionality in Python.

Option C

Standardize the runtime.

Chosen

✅ Docker

Reason

Docker could package

- Python
- Node.js
- npm
- npx

inside one container.

---

# Before Docker

```
Python Runtime

↓

Filesystem MCP

↓

Failure
```

---

# After Docker

```
Docker

↓

Python

↓

Node

↓

npm

↓

npx

↓

Filesystem MCP

↓

Success
```

Docker solved the environment mismatch.

---

# Final Architecture

```
User

↓

Browser

↓

Flask

↓

Google ADK

↓

Gemini 2.5 Flash

↓

Tavily MCP

↓

Google Maps MCP

↓

Scholarship MCP

↓

Filesystem MCP

↓

Markdown Report

↓

Final Response
```

---

# What Was Proven

✅ Google ADK orchestration

✅ Gemini reasoning

✅ Local MCP servers

✅ Remote MCP servers

✅ Multi-tool orchestration

✅ Docker deployment

✅ Render deployment

✅ Report generation

---

# Major Engineering Lessons

- AI systems are distributed systems.
- Gemini performs reasoning; MCP servers perform execution.
- Runtime dependencies matter as much as application code.
- Local success does not guarantee cloud success.
- Docker standardizes environments rather than fixing application logic.
- Incremental debugging is significantly more effective than debugging an entire system simultaneously.
- MCP enables modular, reusable, tool-augmented AI architectures.

---

# Final Outcome

The project successfully evolved from a simple AI chatbot into a modular AI application demonstrating:

- Google ADK
- Gemini 2.5 Flash
- Multiple MCP Servers
- Local + Remote Tool Integration
- Docker Containerization
- Cloud Deployment on Render

The resulting architecture serves as a reusable reference implementation for future AI systems built using Google ADK and the Model Context Protocol.