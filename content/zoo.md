+++
title = "Zoo"
template = "zoo.html"
description = "One real example per way, archived in [Software Heritage](https://www.softwareheritage.org/). Click an example to see the exact lines."
+++

**Granularity**, the smallest unit a way can vary:

| level | varies | e.g. |
|---|---|---|
| line | a statement or expression | `#ifdef`, `#[cfg]` |
| block | a function, class or code path | AspectJ, feature toggles |
| file | a whole source or resource file | Go build constraints, `values-fr/` |
| module | a package, plugin or library | Cargo dependencies, OSGi |
| component | how parts are wired | Spring beans, systemd units |
| process | one running program | env vars, `nginx.conf` |
| user | one account | `.bashrc`, GSettings |
| project | a repository or its tools | CI matrix, `AGENTS.md` |
| machine | a whole host or device | sysctl, Ansible |
| cluster | many hosts or services | Terraform, Helm |
| request | one user or call | flag targeting, `Accept-Language` |
| feature | an abstract feature, no code | FODA, UVL |
