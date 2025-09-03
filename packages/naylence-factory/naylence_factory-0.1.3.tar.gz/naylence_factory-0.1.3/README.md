# Naylence factory

**Naylence factory** is the resource factory and extension management framework for the [Naylence](https://github.com/naylence) ecosystem.
It provides a structured way to define, register, and instantiate resources (connectors, stores, clients, etc.) using Pydantic-based configuration, priority-based defaults, and plugin-style extension loading.

---

## Features

* 🏭 **Resource Factories** — Define factories that build typed resources from configs.
* 🔌 **Extension Management** — Discover and register implementations via Python entry points.
* ⚡ **Priority-based Defaults** — Automatically select the “best” default implementation.
* 🧩 **Composable Configs** — Pydantic models with expression support (`${env:VAR:default}`).
* 🔒 **Policy-driven Evaluation** — Control how config expressions are handled: evaluate, literal, or error.
* 🔄 **Polymorphic Dispatch** — Automatically instantiate subclasses based on `type` fields.

---

## Installation

```bash
pip install naylence-factory
```

Requires **Python 3.12+**.

---
## License

Apache 2.0 © Naylence Dev
