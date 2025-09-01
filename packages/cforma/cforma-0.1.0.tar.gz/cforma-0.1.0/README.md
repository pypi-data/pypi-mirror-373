# cforma

A utility to format Pydantic models into clean, LLM-ready JSON Schemas.

## Description

`cforma` introspects Pydantic models, resolves all nested references, and cleans the resulting schema to make it minimal and efficient for use with Large Language Models that support structured JSON output (Tested with OpenRouter).

## Installation

```bash
pip install cforma
```
