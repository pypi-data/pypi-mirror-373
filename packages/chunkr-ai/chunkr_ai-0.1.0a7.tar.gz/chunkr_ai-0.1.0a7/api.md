# Tasks

Types:

```python
from chunkr_ai.types import (
    BoundingBox,
    Cell,
    CellStyle,
    Chunk,
    ChunkProcessing,
    ExtractConfiguration,
    ExtractOutputResponse,
    FileInfo,
    GenerationConfig,
    LlmProcessing,
    OcrResult,
    Page,
    ParseConfiguration,
    ParseOutputResponse,
    Segment,
    SegmentProcessing,
    TaskResponse,
    VersionInfo,
)
```

Methods:

- <code title="get /tasks">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">list</a>(\*\*<a href="src/chunkr_ai/types/task_list_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task_response.py">SyncTasksPage[TaskResponse]</a></code>
- <code title="delete /tasks/{task_id}">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">delete</a>(task_id) -> None</code>
- <code title="get /tasks/{task_id}/cancel">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">cancel</a>(task_id) -> None</code>
- <code title="get /tasks/{task_id}">client.tasks.<a href="./src/chunkr_ai/resources/tasks/tasks.py">get</a>(task_id, \*\*<a href="src/chunkr_ai/types/task_get_params.py">params</a>) -> <a href="./src/chunkr_ai/types/task_response.py">TaskResponse</a></code>

## Extract

Types:

```python
from chunkr_ai.types.tasks import ExtractCreateResponse, ExtractGetResponse
```

Methods:

- <code title="post /tasks/extract">client.tasks.extract.<a href="./src/chunkr_ai/resources/tasks/extract.py">create</a>(\*\*<a href="src/chunkr_ai/types/tasks/extract_create_params.py">params</a>) -> <a href="./src/chunkr_ai/types/tasks/extract_create_response.py">ExtractCreateResponse</a></code>
- <code title="get /tasks/{task_id}/extract">client.tasks.extract.<a href="./src/chunkr_ai/resources/tasks/extract.py">get</a>(task_id, \*\*<a href="src/chunkr_ai/types/tasks/extract_get_params.py">params</a>) -> <a href="./src/chunkr_ai/types/tasks/extract_get_response.py">ExtractGetResponse</a></code>

## Parse

Types:

```python
from chunkr_ai.types.tasks import ParseCreateResponse, ParseGetResponse
```

Methods:

- <code title="post /tasks/parse">client.tasks.parse.<a href="./src/chunkr_ai/resources/tasks/parse.py">create</a>(\*\*<a href="src/chunkr_ai/types/tasks/parse_create_params.py">params</a>) -> <a href="./src/chunkr_ai/types/tasks/parse_create_response.py">ParseCreateResponse</a></code>
- <code title="get /tasks/{task_id}/parse">client.tasks.parse.<a href="./src/chunkr_ai/resources/tasks/parse.py">get</a>(task_id, \*\*<a href="src/chunkr_ai/types/tasks/parse_get_params.py">params</a>) -> <a href="./src/chunkr_ai/types/tasks/parse_get_response.py">ParseGetResponse</a></code>

# Files

Types:

```python
from chunkr_ai.types import Delete, File, FilesListResponse, FileURL
```

Methods:

- <code title="post /files">client.files.<a href="./src/chunkr_ai/resources/files.py">create</a>(\*\*<a href="src/chunkr_ai/types/file_create_params.py">params</a>) -> <a href="./src/chunkr_ai/types/file.py">File</a></code>
- <code title="get /files">client.files.<a href="./src/chunkr_ai/resources/files.py">list</a>(\*\*<a href="src/chunkr_ai/types/file_list_params.py">params</a>) -> <a href="./src/chunkr_ai/types/file.py">SyncFilesPage[File]</a></code>
- <code title="delete /files/{file_id}">client.files.<a href="./src/chunkr_ai/resources/files.py">delete</a>(file_id) -> <a href="./src/chunkr_ai/types/delete.py">Delete</a></code>
- <code title="get /files/{file_id}/content">client.files.<a href="./src/chunkr_ai/resources/files.py">content</a>(file_id) -> None</code>
- <code title="get /files/{file_id}">client.files.<a href="./src/chunkr_ai/resources/files.py">get</a>(file_id) -> <a href="./src/chunkr_ai/types/file.py">File</a></code>
- <code title="get /files/{file_id}/url">client.files.<a href="./src/chunkr_ai/resources/files.py">url</a>(file_id, \*\*<a href="src/chunkr_ai/types/file_url_params.py">params</a>) -> <a href="./src/chunkr_ai/types/file_url.py">FileURL</a></code>

# Health

Types:

```python
from chunkr_ai.types import HealthCheckResponse
```

Methods:

- <code title="get /health">client.health.<a href="./src/chunkr_ai/resources/health.py">check</a>() -> str</code>

# Webhooks

Types:

```python
from chunkr_ai.types import (
    WebhookURLResponse,
    TaskExtractUpdatedWebhookEvent,
    TaskParseUpdatedWebhookEvent,
    UnwrapWebhookEvent,
)
```

Methods:

- <code title="get /webhook/url">client.webhooks.<a href="./src/chunkr_ai/resources/webhooks.py">url</a>() -> <a href="./src/chunkr_ai/types/webhook_url_response.py">WebhookURLResponse</a></code>
