# Prava Python SDK

Minimal, OpenAI-like client for the Prava API.

## Install

```
pip install prava
```

## Usage

```python
from prava import Prava
import os

client = Prava(api_key=os.getenv("PRAVA_API_KEY"))

completion = client.chat.completions.create({
    "model": "prava-large",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a haiku about coffee."},
    ],
})

print(completion["choices"][0]["message"]["content"])
```

## Configuration

- `api_key`: Explicit API key, or set `PRAVA_API_KEY` env var.
- `base_url`: Override base URL or set `PRAVA_BASE_URL` env var.
- `timeout`: Request timeout seconds (default 60).

## License

MIT

