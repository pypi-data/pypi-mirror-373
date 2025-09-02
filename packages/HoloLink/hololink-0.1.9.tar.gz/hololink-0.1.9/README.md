
---

# HoloLink

## Overview

**HoloLink** is a next-generation framework for managing and executing skills/actions with large language models (**LLMs**) using **natural language**—not vendor-bound JSON or TYPED schemas definitions.
Unlike traditional function-calling, HoloLink lets your LLM output actions in freeform(Natural Language) text. The HoloLink framework interprets, maps, and executes those actions using your own Python code—no matter what you call your skills/actions or where you store them.

**Highlights:**

* **Zero vendor lock-in:** Not tied to any model provider’s format or schema.
* **No naming restrictions:** Name your skills, folders, or groups anything you like—HoloLink doesn’t care.
* **No JSON schemas:** No decorators, no rigid typing, no endless schema maintenance.
* **Natural language as the interface:** The LLM outputs actions in text, not function\_call JSON or TYPED.
* **Add/organize skills freely:** Just point HoloLink at your code—group, reload, or restrict however you want.
* **Centralized execution:** All skill mapping, argument parsing, and execution happens in one place.

**Backward compatible:**

* **Want to stick with traditional function calling?** No problem. HoloLink can still work with JSON and TYPED schemas definitions if you prefer that style.
* **Want to use HoloLink with existing function calls?** You can still use it alongside traditional function calling, so you can migrate gradually or keep both styles.

> **NOTE:**
> If you want to use JSON schemas or TYPED definitions (like OpenAI, Gemini, Anthropic, etc.),
> **HoloLink automatically generates and manages all required schemas for you based on your code and docstrings—**
> **You NEVER have to write, maintain, or register schemas manually.**

---

## Why HoloLink?

Traditional LLM “function calling” means:

* Rigid function and argument definitions.
* Tedious JSON and TYPED schema management.
* Forced adherence to provider conventions.
* Locked into one vendor’s API.

**HoloLink:**

* Uses only natural language—models describe actions however they want.
* Lets you migrate skills and switch model providers instantly.
* Removes all JSON and TYPED schema headaches.
* Lets you organize, group, and name skills however you want.

---

## Key Features

* **Flexible Skill Loading:**
  Add, reload, or restrict any set of skills, with any folder or group name.

* **Natural Language Action Parsing:**
  Models output plain English (or any language), and HoloLink interprets it to execute your code.

* **Centralized Execution:**
  No scattered registries—skill mapping, argument parsing, and execution are all in one place.

---

## Organizing and Naming Your Skills

There are **no reserved names, no required folder layout, and no fixed naming conventions** in HoloLink.
You control all naming, grouping, and structure—use whatever makes sense for your team, project, or workflow.

**Examples:**

**Just point HoloLink at any directory or skill group you want—no restrictions, ever.**

---

### Example Layouts (ALL are valid)

```
project_root/
├── Skills/ # This is just an example, you can name it whatever you want, you can even nest the directories it does not have to be at the root
│   ├── Foo/ # Can do nested folders, any names
│   │   ├── summarize.py
│   │   └── summarize_pdf.py
│   ├── Bar/
│   │   ├── sendEmail.py
│   │   └── joke_skill.py
│   ├── EmailTool.py # Or directly in the directory
│   └── ping_tool.py
├── Tools/ # This is just an example, you can name it whatever you want, you can even nest the directories it does not have to be at the root
│   ├── Foo/ # Can do nested folders, any names
│   │   ├── summarize.py
│   │   └── summarize_pdf.py
│   ├── Bar/
│   │   ├── sendEmail.py
│   │   └── joke_skill.py
│   ├── EmailTool.py # Or directly in the directory
│   └── ping_tool.py
├── SkillLoader.py # Whatever you want to call it
├── .env
└── ...

```

Or any structure you prefer.

---

## How It Works

1. **Model outputs natural language:**
   "Summarize the latest report and update our dashboard."
2. **HoloLink parses the text** and finds the right skills (whatever you’ve named them).
3. **Skills are executed** and results returned—no schemas, no JSON or TYPED schemas, just Python code.

---

## Example: Comparing Approaches

### 1. With HoloLink (No Naming Restrictions)

**Behind the scenes:**

* HoloLink parses and executes your skills, regardless of how you’ve named or grouped them.
* No decorators, no JSON no TYPED schemas.

---

### 2. Traditional Function/Tool Calling (Provider Schema Required)

* Must define every function and argument as a JSON or TYPED schema.
* Register all with the provider.
* Model outputs strict `function_call` blobs.
* You parse, validate, and execute under the provider’s constraints.

> **HoloLink does this part for you automatically if you ever need it—no manual schemas, no boilerplate.**

---

## Adding and Organizing Skills

* Drop Python modules into any folder, with any name or grouping.
* Point HoloLink at those folders in your class (`loadComponents`).
* No JSON or TYPED, no schemas, no required naming—total freedom.

---

## Why Use HoloLink?

* **Never locked into a provider.**
* **No JSON or TYPED schema maintenance.**
* **Flexible skill organization:** Name and group skills however you want.
* **Production ready:** Clean, scalable, and easy to extend.

---

## FAQ

**Q: Do I need to follow a specific naming or folder structure?**
A: No. You can use any names and any folder hierarchy.

**Q: Can I use this with any LLM PROVIDER?**
A: Yes.

**Q: How does HoloLink know what to execute?**
A: It parses the model’s plain language output and matches actions to your Python skills, regardless of naming.

**Q: Do I have to write JSON or TYPED schemas or tool definitions?**
A: **Never. HoloLink auto-generates and manages them for you when required.**

---

## Code Examples

You can find code examples on my [GitHub repository](https://github.com/TristanMcBrideSr/TechBook).

---

## License

This project is licensed under the [Apache License, Version 2.0](LICENSE).
Copyright 2025 Tristan McBride Sr.

---

## Authors
- Tristan McBride Sr.
- Sybil
