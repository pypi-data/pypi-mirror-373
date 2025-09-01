# CheshireCat Python SDK

----

**CheshireCat Python SDK** is a library to help the implementation
of [Cheshire Cat](https://github.com/matteocacciola/cheshirecat-core) on a Python Project

* [Installation](#installation)
* [Usage](#usage)

## Installation

To install CheshireCat Python SDK, run:

```bash
pip install cheshirecat-python-sdk
```

## Usage
Initialization and usage:

```python
from cheshirecat_python_sdk import CheshireCatClient, Configuration

configuration = Configuration(host="localhost", port=1865, auth_key="test", secure_connection=False)

cheshire_cat_client = CheshireCatClient(configuration)
```
Send a message to the websocket:

```python
from cheshirecat_python_sdk import CheshireCatClient, Configuration, Message

configuration = Configuration(host="localhost", port=1865, auth_key="test", secure_connection=False)
cheshire_cat_client = CheshireCatClient(configuration)

notification_closure = lambda message: None # handle websocket notification, like chat token stream

# result is the result of the message
result = cheshire_cat_client.message.send_websocket_message(
    Message(text="Hello world!"),  # message body
    "agent", # agent ID
    "user", # user ID
    callback=notification_closure # websocket notification closure handle
)
```

Load data to the rabbit hole:
```python
import asyncio

from cheshirecat_python_sdk import CheshireCatClient, Configuration, Message

configuration = Configuration(host="localhost", port=1865, auth_key="test", secure_connection=False)
cheshire_cat_client = CheshireCatClient(configuration)

# file
file = "path/to/file"
result = asyncio.run(cheshire_cat_client.rabbit_hole.post_file(file, "agent"))

# url
url = "https://www.google.com"
result = asyncio.run(cheshire_cat_client.rabbit_hole.post_web(url, "agent"))
```

Memory management utilities:

```python
from cheshirecat_python_sdk import Collection, CheshireCatClient, Configuration, Message

configuration = Configuration(host="localhost", port=1865, auth_key="test", secure_connection=False)
cheshire_cat_client = CheshireCatClient(configuration)

cheshire_cat_client.memory.get_memory_collections("agent")  # get number of vectors in the working memory
cheshire_cat_client.memory.get_memory_recall("HELLO", "agent", "user")  # recall memories by text

url = "https://www.google.com"

# delete memory points by metadata, like this example delete by source
cheshire_cat_client.memory.delete_memory_points_by_metadata(Collection.DECLARATIVE, "agent", {"source": url})
```
