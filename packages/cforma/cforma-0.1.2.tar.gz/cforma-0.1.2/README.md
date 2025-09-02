# cforma

A utility to format Pydantic models into clean, LLM-ready JSON Schemas.

## Description

`cforma` introspects Pydantic models, resolves all nested references, and cleans the resulting schema to make it minimal and efficient for use with Large Language Models that support structured JSON output (Tested with OpenRouter).

## Installation

```
pip install cforma
```

## Usage

Here is how to convert your Pydantic models into a schema and use it in an API call.

### 1. Define your Pydantic Models

You can define complex, nested models. `cforma` will handle them automatically.

```python
from pydantic import BaseModel, Field
from typing import List

class Author(BaseModel):
    name: str = Field(description="The author's full name.")
    is_prolific: bool = Field(description="True if the author has written more than 10 books.")

class Book(BaseModel):
    title: str = Field(description="The title of the book.")
    published_year: int = Field(description="The year the book was published.")
    authors: List[Author] = Field(description="A list of the book's authors.")
```

### 2. Generate the Schema

Import `StructFormatter` and use the `ingest` method to generate the complete schema required by the LLM.

```python
from cforma import StructFormatter

llm_schema = StructFormatter.ingest(
    schemaName="BookSchema",
    schemaDescription="A schema to extract detailed information about a book and its authors.",
    schemaObject=Book
)
```

### 3. Use the Schema in an API Call

You can now pass the generated `llm_schema` directly into the `response_format` parameter of your LLM API call (e.g., using an OpenAI-compatible client with OpenRouter).

```python
# This is a hypothetical example using an OpenAI-compatible client
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_OPENROUTER_KEY",
)

response = client.chat.completions.create(
  model="google/gemini-flash-1.5",
  messages=[
    {"role": "user", "content": "Extract the book details for 'The Hobbit'."},
  ],
  extra_body={
    "response_format": llm_schema
  }
)

# The response will contain structured JSON matching your Book model
# print(response.choices[0].message.content)
```
