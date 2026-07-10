# Custom AI Agents

Author: Bhargavi Kurukunda

A series of small, hands-on agent-building learning projects, each one adding a new
core skill on top of the last — starting from a single stateless tool call,
ending with a full-CRUD, OAuth-authenticated agent with its own GUI.

---

## 1. Calculator Agent

The starting point — a minimal tool-calling loop using a local model via
Ollama (OpenAI-compatible API).

**What it does:** Takes a natural-language math question, lets the model
decide to call a `calculate_add` tool, executes it, and returns the result.

**Core concepts learned:**
- The basic tool-calling round trip: model requests a tool → code executes it
  → result sent back → model phrases the final answer
- Why small local models are unreliable at consistently using tool calls
- Type safety issues (arguments arriving as strings instead of integers)

**Stack:** Ollama, OpenAI Python SDK (against Ollama's compatibility endpoint)

---

## 2. Weather Agent

Introduces a real external API and Google's `google-genai` SDK, including
**automatic vs. manual function calling.**

**What it does:** Answers natural-language weather questions by geocoding a
city name, then fetching current conditions from OpenWeatherMap.

**Core concepts learned:**
- Automatic vs. manual function calling in the Gemini SDK, and when to
  disable automatic mode for full visibility/control
- Building conversation history correctly (`Content`/`Part` objects) so
  multi-turn context doesn't silently break
- Free-tier API gotchas (endpoint access levels, response shape differences)

**Stack:** `google-genai`, OpenWeatherMap API

>> Note: Python SDK for google-genai keeps changing frequently. So check the docs if something is deprecated.

---

## 3. Expense Tracker Agent

The first agent with real persistent state and multiple tools working
together, plus a from-scratch evaluation harness.

**What it does:** Tracks spending via natural language — "I spent $12 on
coffee today" — and answers questions about totals, categories, and time
ranges, backed by a local SQLite database.

**Core concepts learned:**
- Parameterized SQL queries (and the exact bugs that happen without them)
- Dictionary-based tool dispatch instead of long if/elif chains
- Injecting ground-truth values (today's date) into prompts, rather than trusting the model to compute relative dates itself
- The "loop until no more function calls" pattern, for requests needing multiple chained tool calls in one turn
- Writing a basic eval suite: known queries with expected tool + arguments,
  scored automatically

**Stack:** `google-genai`, SQLite

---

## 4. Calendar Agent

The most complete agent — real OAuth against Google Calendar, full CRUD,
computed statistics (not model-guessed math), and a Tkinter GUI.

**What it does:** Manages a real Google Calendar via natural language — create, list, update, and delete events — plus higher-value reasoning tools:
meeting-load statistics, period-over-period comparisons, and free-time
finding.

**Core concepts learned:**
- OAuth 2.0 against a real external service (Google's desktop-app flow), distinct from token-based auth used elsewhere
- Designing tools so the model only *phrases* answers, never computes them — all arithmetic (hours, averages, gap-finding) happens in code
- **Timezone-aware vs. timezone-naive** datetimes, and why comparing them directly fails
- A simple Tkinter GUI wrapping the same agent loop, with the slow API call run on a background thread so the window stays responsive

**Stack:** `google-genai`, Google Calendar API, `google-auth-oauthlib`, Tkinter

---

Feel free to clone this repo and use for your own learning journey. 