# TenxAgent 🤖

**A flexible, Pydantic-powered library for building and composing AI agents in Python.**

TenxAgent allows you to easily define your own tools and plug in any language model, all with robust type-checking and validation. String agents together or use them as tools for other agents to create powerful, hierarchical systems.

---

### ✨ Features

* **Pydantic Validation:** Define tool inputs with Pydantic for automatic validation and schema generation.
* **Composable Agents:** Any agent can be wrapped and used as a tool by another agent.
* **Pluggable Models:** Bring your own LLM. A simple abstract class makes it easy to integrate any API.
* **Flexible Prompting:** Use our helpful default system prompt or provide your own for complete control over agent behavior.

---

### 🚀 Quick Start

**1. Installation**

```bash
pip install TenxAgent