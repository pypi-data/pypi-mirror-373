
---

# HoloAI – A modular, provider-agnostic AI framework for multi-model orchestration, agent workflows, and vision."


# NOTICE: PLEASE DO NOT INSTALL VERSION 0.1.0 - 0.1.7, 0.2.4 - 0.2.6, and 0.2.9 - 0.3.1 THEY ARE NOT STABLE AND WILL BREAK YOUR PROJECT.

---

## Overview

HoloAI is a production-grade, multi-provider orchestrator for LLM and vision models.  
Supports OpenAI, Google Gemini, Groq, Grok, and Anthropic, with automatic provider inference.
Built for:

* Agents & bots
* Workflow automation
* Voice assistants
* Any application needing multi-model, multi-provider intelligence

HoloAI unifies OpenAI, Google Gemini, Groq, Grok, and Anthropic: handling agents, conversation, vision, all from a single interface.

---

## Fixes

* Fixed response issue when using Anthropics reasoning.

---

## New Features

* **Flexible Skills & Actions**  
  You can now provide both skills and actions to the model in two ways:
    - **Bundled:** `capabilities=[skills, actions]`
    - **Separate:** `skills=skills, actions=actions`
  > If only actions is provided (without skills), this will result in an error.  
  Skills and actions will be executed if the model chooses to call them.
* Tool/Function calling
* Agent support
* Manual Provider setup (Overrides automatic provider inference using the .env file and model name)
* Can now pass in files as well as images to the model limited only by the models max context window. (pdf, docx, txt) NOTE: images in pdf and docx files are not supported yet. and will be ignored.
* Image generation support (xAI, OpenAI, Google)

---

## Up Coming Features

* Support for more file and image types

---

## Key Features

* **Universal Provider Support:**
  Instantly switch between OpenAI, Google Gemini, Groq, Grok, and Anthropic—no vendor lock-in.
* **Multimodal Ready:**
  Handles text, vision, generation, out of the box.
* **Automatic Provider Inference:**
  Just specify your model; HoloAI selects the right backend.
* **Minimal, Clean API:**
  One interface for all major models—rapid integration.

---

## Why HoloAI?

Most LLM wrappers lock you into a single vendor or force you to juggle multiple APIs and formats.
**HoloAI** delivers:

* **One Framework, any provider.**
* **No boilerplate, no rewrites.**
* **Plug-and-play for agents, scripts, automations, or apps.**

---

## Environment

Set API keys as environment variables:

* `OPENAI_API_KEY`
* `ANTHROPIC_API_KEY`
* `GEMINI_API_KEY`
* `GROQ_API_KEY`

Only providers with keys set will be loaded.

---

## Provider Setup (`setProvider` Usage)

You can configure your providers directly in code—no `.env` required (unless you want it).  
`setProvider` is flexible and supports all of the following patterns:

### 1. **Single Provider (String)**

```python
client = HoloAI()
client.setProvider('OPENAI_API_KEY=sk-xxxx')
````

*Registers only OpenAI as a provider.*

---

### 2. **Multiple Providers (Tuple of Strings)**

```python
client = HoloAI()
client.setProvider((
    'OPENAI_API_KEY=sk-xxxx',
    'ANTHROPIC_API_KEY=claude-xxxx'
))
```

*Registers OpenAI and Anthropic as providers.*

---

### 3. **Multiple Providers (List of Strings)**

```python
client = HoloAI()
client.setProvider([
    'OPENAI_API_KEY=sk-xxxx',
    'ANTHROPIC_API_KEY=claude-xxxx',
    'GEMINI_API_KEY=g-xxxx',
    'GROQ_API_KEY=gsk-xxxx'
])
```

*Registers all four providers (OpenAI, Anthropic, Google, Groq).*

---

4. No Arguments: Use Environment Variables or .env
If you want to load API keys automatically from environment variables or a .env file,
you do not need to call setProvider() at all—just instantiate HoloAI:

```python
client = HoloAI()
```

Any providers with API keys available in your environment will be registered automatically.

---

> **Tip:**
> You can mix and match—use direct code for development, `.env`/env for production, or both.
> Only providers with keys will be registered and available.

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
