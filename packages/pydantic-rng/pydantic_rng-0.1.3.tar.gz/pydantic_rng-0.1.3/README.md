# pydantic-rng

A simple library for generating random, valid Pydantic models.

This tool helps you quickly create mock data for testing, prototyping, and demonstration purposes by generating random values that conform to your Pydantic model schemas. It supports a wide range of types and validation constraints.

## ✨ Features

* **Type-aware Generation**: Generates appropriate data for common Python types (`str`, `int`, `float`, `bool`, `list`, `dict`, `set`, etc.).
* **pydantic Integration**: Works seamlessly with Pydantic's `BaseModel` for recursive data generation.
* **Constraint Support**: Respects a wide variety of Pydantic validation constraints from the `annotated_types` library, including `MinLen`, `MaxLen`, `Ge`, `Gt`, `Le`, `Lt`, and `MultipleOf`.
* **Configurable**: Customize the behavior of the random generator with global settings for things like numeric and string ranges, and the probability of generating `None` for optional fields.

## 🚀 Installation

Install the package (usually as a dev dependency):

```bash
uv add --dev pydantic-random-data
```

## Generate Basic Class RNG

```python
from pydantic import BaseModel
from pydantic_random_data import generate

class User(BaseModel):
    user_id: int
    name: str
    is_active: bool
    email: str | None

random_user = generate(User)
print(random_user.model_dump_json(indent=2))
```
