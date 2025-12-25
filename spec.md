# HPC Assistant Server – Specification

## 1. Purpose and Overview

This document specifies the design and requirements for a **self-hosted assistant server** running on an HPC cluster (Slurm-managed), intended for **research, analysis, coding, and report-driven workflows**. The assistant is designed to:

* Run on a **single compute node** with GPU acceleration
* Provide **model inference, tool calling, and orchestration** through a single API server
* Support **asynchronous, long-running jobs** (e.g. report writing)
* Notify the user upon task completion
* Be **modular and extensible**, allowing new tools, workflows, and models to be added with minimal refactoring

The system is intended to behave like a **private, OpenAI-style assistant**, optimized for local use by a single researcher, with an emphasis on correctness, debuggability, and future extensibility.

---

## 2. Deployment Environment

### Hardware

* GPU: **Single NVIDIA L40 (~48 GB VRAM)**
* CPU RAM: **~60 GB**
* Storage: Shared or local filesystem for persistent job artifacts

### Software / Platform

* Scheduler: **Slurm**
* OS: Linux (HPC standard)
* Inference Engine: **vLLM**
* Model: **Qwen2.5-14B-Instruct** (bf16)
* API Framework: **FastAPI**
* Access Pattern: **Local-only**, via SSH tunneling

---

## 3. High-Level Architecture

The system runs as **a single server process** within one Slurm allocation. This server encapsulates:

* API endpoints
* Model inference
* Tool execution
* Orchestration logic
* Persistent storage

Conceptually, the architecture is divided into logical layers:

* **API Layer** – handles HTTP requests from the local client
* **Orchestration Layer** – manages tool-calling loops, phases, and workflows
* **Model Layer** – interfaces with the LLM (via vLLM)
* **Tool Layer** – executes external actions (search, notification, execution)
* **Storage Layer** – persists reports, job state, and logs

All components live within a single service for simplicity and reliability under Slurm.

---

## 4. Core Functional Requirements

### 4.1 Model Inference

* Serve a single primary LLM (Qwen2.5-14B-Instruct)
* Support:

  * Data analysis
  * Code generation
  * Long-form report writing
  * Structured outputs (JSON)
* Allow future model swaps or upgrades without changing API semantics

### 4.2 Tool Calling

* Use an **OpenAI-style function/tool calling interface**
* The model may request tools, but **never executes them directly**
* The server:

  * Validates tool calls
  * Executes tools safely
  * Feeds results back to the model

Initial tools include:

* Academic search (Semantic Scholar / arXiv / OpenAlex)
* Notification (email, webhook)
* Checklist or task execution

### 4.3 Asynchronous Jobs

* Support long-running tasks (e.g. multi-minute report generation)
* API requests should return immediately with a `job_id`
* Jobs execute in the background within the same server process
* Job state and outputs must be persisted to disk

### 4.4 Notification on Completion

* Notify the user when a job finishes
* Initial notification mechanism: **email** (HPC-safe default)
* Optional future mechanisms: webhook, Slack, local listener

---

## 5. Phase-Based Orchestration (Key Design Feature)

The assistant explicitly supports **phases**, which define *how* the model behaves during a request.

### Core Phases

1. **Report Phase**

   * Goal: Produce a detailed written report
   * Tools: Search tools allowed
   * Output: Long-form text (Markdown or plain text)

2. **Suggest Phase**

   * Goal: Convert a report into actionable recommendations
   * Tools: None (reasoning-only)
   * Output: Structured checklist or suggestions

3. **Execute Phase**

   * Goal: Act on suggestions or verify them
   * Tools: Execution tools, notification
   * Output: Execution log or status summary

Phases determine:

* System prompt
* Allowed tools
* Expected output format

Phases can be chained to form workflows.

---

## 6. Workflows

A **workflow** is an explicit composition of phases. Example:

1. Report → generate research report
2. Suggest → derive recommendations or next steps
3. Execute → carry out or validate the recommendations
4. Notify → alert user on completion

Workflows are implemented server-side and are reusable and testable.

---

## 7. Storage and Persistence

The system must persist all critical artifacts to survive disconnects or job termination:

* Job metadata (status, timestamps)
* Reports (text / Markdown)
* Tool outputs
* Execution logs

Storage is filesystem-based, organized by `job_id`.

---

## 8. API Requirements

* Provide endpoints for:

  * Submitting a task
  * Querying job status
  * Fetching reports or results
* API should be compatible with OpenAI-style clients where possible
* No public exposure; access via SSH tunnel only

---

## 9. Non-Functional Requirements

* **Reliability**: Jobs should not be lost due to SSH disconnects
* **Observability**: Logs and intermediate artifacts should be inspectable
* **Safety**: Tools are whitelisted and server-executed only
* **Simplicity**: One Slurm job, one node, one server
* **Extensibility**: New tools, phases, workflows, or models added without refactor

---

## 10. Planned Extensions / Quality-of-Life Ideas

The design explicitly supports future extensions, including:

* Additional phases (e.g. critique, summarize, validate)
* Local corpus search (FAISS / embeddings)
* Multiple workflows selectable at runtime
* Lightweight router models (optional)
* Improved execution tools (checklists, simulations)
* Model upgrades or multi-model support
* Richer notifications and dashboards

---

## 11. Design Philosophy

* Prefer **clear orchestration** over autonomous agents
* Prefer **explicit phases** over implicit prompting tricks
* Keep the model powerful but constrained
* Optimize for a single researcher’s productivity

This system is intended to grow with use, remaining understandable and controllable as complexity increases.

