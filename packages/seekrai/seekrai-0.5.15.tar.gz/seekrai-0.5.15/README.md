The Seekr Python Library is the official Python client for SeekrFlow's API platform, providing a convenient way for interacting with the REST APIs and enables easy integrations with Python 3.9+ applications with easy to use synchronous and asynchronous clients.

# Installation

To install Seekr Python Library from PyPi, simply run:

```shell Shell
pip install --upgrade seekrai
```

## Setting up API Key

> 🚧 You will need to create an account with [Seekr.com](https://seekr.com/) to obtain a SeekrFlow API Key.

### Setting environment variable

```shell
export SEEKR_API_KEY=xxxxx
```

### Using the client

```python
from seekrai import SeekrFlow

client = SeekrFlow(api_key="xxxxx")
```

# Usage – Python Client

## Chat Completions

```python
import os
from seekrai import SeekrFlow

client = SeekrFlow(api_key=os.environ.get("SEEKR_API_KEY"))

response = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "tell me about new york"}],
)
print(response.choices[0].message.content)
```

### Streaming

```python
import os
from seekrai import SeekrFlow

client = SeekrFlow(api_key=os.environ.get("SEEKR_API_KEY"))
stream = client.chat.completions.create(
    model="meta-llama/Llama-3.1-8B-Instruct",
    messages=[{"role": "user", "content": "tell me about new york"}],
    stream=True,
)

for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="", flush=True)
```

### Async usage

```python
import os, asyncio
from seekrai import AsyncSeekrFlow

async_client = AsyncSeekrFlow(api_key=os.environ.get("SEEKR_API_KEY"))
messages = [
    "What are the top things to do in San Francisco?",
    "What country is Paris in?",
]


async def async_chat_completion(messages):
    async_client = AsyncSeekrFlow(api_key=os.environ.get("SEEKR_API_KEY"))
    tasks = [
        async_client.chat.completions.create(
            model="meta-llama/Llama-3.1-8B-Instruct",
            messages=[{"role": "user", "content": message}],
        )
        for message in messages
    ]
    responses = await asyncio.gather(*tasks)

    for response in responses:
        print(response.choices[0].message.content)


asyncio.run(async_chat_completion(messages))
```

## Files

The files API is used for fine-tuning and allows developers to upload data to fine-tune on. It also has several methods to list all files, retrieve files, and delete files

```python
import os
from seekrai import SeekrFlow

client = SeekrFlow(api_key=os.environ.get("SEEKR_API_KEY"))

client.files.upload(file="somedata.parquet")  # uploads a file
client.files.list()  # lists all uploaded files
client.files.delete(id="file-d0d318cb-b7d9-493a-bd70-1cfe089d3815")  # deletes a file
```

## Fine-tunes

The finetune API is used for fine-tuning and allows developers to create finetuning jobs. It also has several methods to list all jobs, retrieve statuses and get checkpoints.

```python
import os
from seekrai import SeekrFlow

client = SeekrFlow(api_key=os.environ.get("SEEKR_API_KEY"))

client.fine_tuning.create(
    training_file='file-d0d318cb-b7d9-493a-bd70-1cfe089d3815',
    model='meta-llama/Llama-3.1-8B-Instruct',
    n_epochs=3,
    n_checkpoints=1,
    batch_size=4,
    learning_rate=1e-5,
    suffix='my-demo-finetune',
)
client.fine_tuning.list()  # lists all fine-tuned jobs
client.fine_tuning.retrieve(id="ft-c66a5c18-1d6d-43c9-94bd-32d756425b4b")  # retrieves information on finetune event
```
