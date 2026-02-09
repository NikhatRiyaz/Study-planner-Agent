# Google ADK Study Planner Agent (with Opik Observability)

A multi‑agent CLI application that generates **realistic, sustainable study plans** with **spaced revision**, **load smoothing**, and a **final consolidation buffer**—fully traced with **Opik** for end‑to‑end observability. The pipeline uses **Google ADK** for agent orchestration and **Gemini** via the **Google GenAI Python client**. [1](blob:https://www.microsoft365.com/75deb6e8-2fe6-4c2d-b991-9bd59e6158cb)

---

## ✨ Features

- **Multi‑agent pipeline**  
  `StudyPlanner` → `PlanAuditor` → `StudyCoach`, orchestrated by `StudyMasterAgent` (via a `SequentialAgent`). [1](blob:https://www.microsoft365.com/75deb6e8-2fe6-4c2d-b991-9bd59e6158cb)
- **Built‑in tools for auditing plans**  
  `compute_study_metrics` (overload days, variance, revision ratio, final buffer) and `syllabus_coverage` (minutes per subject). [1](blob:https://www.microsoft365.com/75deb6e8-2fe6-4c2d-b991-9bd59e6158cb)
- **Observability with Opik**  
  OpikTracer hooks wrap all agent/model/tool calls; traces are flushed on exit and show up in your Opik project. [1](blob:https://www.microsoft365.com/75deb6e8-2fe6-4c2d-b991-9bd59e6158cb)
- **Gemini 2.5 Flash‑Lite** as default model  
  Fast, cost‑efficient, 1M‑token context; suitable for planner agents. (Model set in each Agent definition.) [1](blob:https://www.microsoft365.com/75deb6e8-2fe6-4c2d-b991-9bd59e6158cb)
- **Simple CLI UX**  
  Runs locally with Rich panels that show each agent’s output as the pipeline executes. [1](blob:https://www.microsoft365.com/75deb6e8-2fe6-4c2d-b991-9bd59e6158cb)

---

## 🧱 Project Structure
