Welcome to ransack
==================

**ransack** is a modern, extensible language for manipulation with structured data.

Structured data --- like `JSON <https://json.org>`_, `YAML <https://yaml.org/>`_, `TOML <https://toml.io/>`_ and domain-specific formats such as `IDEA <https://idea.cesnet.cz>`_ --- form the backbone of many modern applications. These formats appear in configuration files, security logs, telemetry systems, and beyond.

**ransack** was designed to meet the increasing need for a robust and expressive language to query, filter, and inspect structured data. Whether used in Python code, as part of a log analysis tool, or as a compiler frontend for other systems, **ransack** provides a flexible foundation.

Why ransack?
------------

ransack is a new implementation and improvement over existing libraries like *Pynspect*, which was widely used in security monitoring systems like `NEMEA <https://nemea.liberouter.org/>`_ and `Mentat <https://mentat.cesnet.cz>`_. Compared to older tools, ransack:

- supports **user-defined variables**
- enables **multi-argument functions**
- is **extensible** and **modular**
- supports **multiple backends** (e.g., Python evaluation, SQL translation)
- offers a clean internal architecture for future enhancements

Key features
------------

- a simple and expressive syntax for filters and conditions
- support for context-aware variables and data scoping
- predefined functions
- support for IPv4/IPv6, datetimes, string and list manipulation
- safe and maintainable implementation using `Lark <https://lark-parser.readthedocs.io/en/stable/>`_ for parsing

