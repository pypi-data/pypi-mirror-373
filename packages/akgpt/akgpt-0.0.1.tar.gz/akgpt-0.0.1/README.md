# akgpt

A simple Python library for interacting with your custom GPT API.

## Installation

```bash
pip install akgpt
```

## Usage

```python
import os
from akgpt import AKGPT

# Set your API key as an environment variable (recommended)
# export AKGPT_API_KEY="your_secret_api_key"

# Or pass it directly (less secure)
# client = AKGPT(api_key="your_secret_api_key")

client = AKGPT()

response = client.query("text-davinci-003", "What is the capital of France?")
print(response)

response = client.query("gpt-4", "Write a short story about a robot.", temperature=0.8, max_tokens=100)
print(response)
```

## API Key

Your API key can be provided in two ways:

1.  **Environment Variable (Recommended):** Set the `AKGPT_API_KEY` environment variable.
    ```bash
    export AKGPT_API_KEY="your_secret_api_key"
    ```
2.  **Directly in Code:** Pass the `api_key` argument when initializing the `AKGPT` class.
    ```python
    client = AKGPT(api_key="your_secret_api_key")
    ```

## Models

Specify the model you want to use in the `query` method. Available models depend on your backend API.

## Parameters

Additional parameters can be passed as keyword arguments to the `query` method. These will be forwarded to your backend API. Common parameters include `temperature`, `max_tokens`, etc.

## Contributing

Feel free to contribute to this project by opening issues or pull requests on GitHub.


