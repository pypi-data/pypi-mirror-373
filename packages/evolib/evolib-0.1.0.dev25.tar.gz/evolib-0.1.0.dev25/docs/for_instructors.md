# EvoLib for Instructors

EvoLib is a modern open-source framework for evolutionary algorithms and neuroevolution in Python.
It was designed with **teaching, clarity, and modularity** in mind.

---

## Why use EvoLib in teaching?

* **Clear API design**: `from evolib import Population, Vector, EvoNet`
* **Config-driven experiments**: YAML + Pydantic validation (no hidden parameters)
* **Quick results**: ready-to-use examples and visualizations
* **Low entry barrier**: students get working code in minutes
* **Extensible**: advanced students can implement custom operators or representations

---

## Typical Course Topics

| Topic                   | Example Assignment                               | EvoLib Support                       |
| ----------------------- | ------------------------------------------------ | ------------------------------------ |
| **Introduction to EAs** | Minimize Sphere or Rastrigin function            | `Population.run()` with YAML configs |
| **Mutation strategies** | Compare constant vs. adaptive vs. exponential    | `mutation.strategy: ...`             |
| **Selection methods**   | Roulette, tournament, ranking                    | `selection.strategy: ...`            |
| **Crossover operators** | BLX, SBX, intermediate                           | Config switch, built-in operators    |
| **Neuroevolution**      | Solve XOR with structural growth                 | `EvoNet` + `mutate_structure`        |
| **Projects**            | Image approximation, agent control, co-evolution | Showcase examples included           |

---

## Benefits for Instructors

* **Reduced entry barrier**: students can run experiments in the first session.
* **Structured configuration**: YAML + Pydantic catches mistakes early.
* **Visual support**: ready-made plots and GIFs illustrate evolutionary dynamics.
* **Extensibility**: instructors can extend EvoLib with minimal boilerplate.

---

## Example Showcases

* **XOR** with structural network growth
* **Sine approximation** (continuous optimization)
* **Image approximation** (evolving networks to reproduce an image)
* **Adaptive mutation strategies** (trackable with built-in logging)

---

## Installation & First Steps

```bash
pip install evolib
```

Minimal example:

```python
from evolib import Population

pop = Population("examples/01_basic_usage/population.yaml")
pop.run()
```

* **Source Code**: [github.com/EvoLib/evo-lib](https://github.com/EvoLib/evo-lib)
* **Documentation**: [evolib.readthedocs.io](https://evolib.readthedocs.io)

---

## License & Openness

* MIT License – free for teaching, research, and industry use.
* Actively developed, open for contributions, and well-suited for student projects.

---

## Summary

> *“EvoLib bridges the gap between overly simple GA libraries and overly complex research frameworks – with a focus on clarity, teaching, and extensibility.”*
