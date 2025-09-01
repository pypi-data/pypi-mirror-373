# Chat

Types:

```python
from premai.types import ChatCompletionsResponse
```

Methods:

- <code title="post /api/v1/chat/completions">client.chat.<a href="./src/premai/resources/chat.py">completions</a>(\*\*<a href="src/premai/types/chat_completions_params.py">params</a>) -> <a href="./src/premai/types/chat_completions_response.py">ChatCompletionsResponse</a></code>

# Models

Types:

```python
from premai.types import ModelListResponse, ModelCheckStatusResponse
```

Methods:

- <code title="get /api/v1/models">client.models.<a href="./src/premai/resources/models.py">list</a>() -> <a href="./src/premai/types/model_list_response.py">ModelListResponse</a></code>
- <code title="get /api/v1/models/running">client.models.<a href="./src/premai/resources/models.py">check_status</a>(\*\*<a href="src/premai/types/model_check_status_params.py">params</a>) -> <a href="./src/premai/types/model_check_status_response.py">ModelCheckStatusResponse</a></code>
- <code title="post /api/v1/models/up">client.models.<a href="./src/premai/resources/models.py">load</a>(\*\*<a href="src/premai/types/model_load_params.py">params</a>) -> None</code>
- <code title="post /api/v1/models/down">client.models.<a href="./src/premai/resources/models.py">unload</a>(\*\*<a href="src/premai/types/model_unload_params.py">params</a>) -> None</code>
