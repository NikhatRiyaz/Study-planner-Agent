# Online Evaluation Rules — Google ADK Study Planner Agent
This guide walks you through **creating Online Evaluation Rules in Opik** for the Study Planner Agent.  
Online evaluations automatically score **every production trace** using LLM‑as‑judge prompts you define.

Online Rules allow Opik to:
- Score traces in real time
- Use LLM-as-judge prompts (e.g., feasibility, clarity, safety) [1](https://www.datastudios.org/post/all-gemini-models-available-in-2025-complete-list-for-web-app-api-and-vertex-ai)
- Apply rules to **Trace** or **Span** entities
- Filter by tags, agent names, or attributes
- Store results as feedback scores for dashboards and quality monitoring  
Opik’s automation engine evaluates traces asynchronously and supports multiple evaluator types. [2](https://docs.oracle.com/en-us/iaas/Content/generative-ai/google-gemini-2-5-flash-lite.htm)

---

## 📌 PRE‑REQUISITES
Before creating rules, confirm:

1. Your **Study Planner app is already logging traces to Opik** using:
   ```python
   OpikTracer(tags=["study", "multi-agent"])