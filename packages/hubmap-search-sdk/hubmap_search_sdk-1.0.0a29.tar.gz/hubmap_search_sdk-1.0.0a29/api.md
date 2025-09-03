# Indices

Types:

```python
from hubmap_search_sdk.types import IndexListResponse
```

Methods:

- <code title="get /indices">client.indices.<a href="./src/hubmap_search_sdk/resources/indices.py">list</a>() -> <a href="./src/hubmap_search_sdk/types/index_list_response.py">IndexListResponse</a></code>

# Search

Types:

```python
from hubmap_search_sdk.types import Dataset
```

Methods:

- <code title="post /{index_name}/search">client.search.<a href="./src/hubmap_search_sdk/resources/search.py">execute_index_query</a>(index_name, \*\*<a href="src/hubmap_search_sdk/types/search_execute_index_query_params.py">params</a>) -> object</code>
- <code title="post /search">client.search.<a href="./src/hubmap_search_sdk/resources/search.py">execute_query</a>(\*\*<a href="src/hubmap_search_sdk/types/search_execute_query_params.py">params</a>) -> object</code>

# ParamSearch

Methods:

- <code title="get /param-search/{entity_type}">client.param_search.<a href="./src/hubmap_search_sdk/resources/param_search.py">execute</a>(entity_type, \*\*<a href="src/hubmap_search_sdk/types/param_search_execute_params.py">params</a>) -> object</code>

# Reindex

Methods:

- <code title="put /reindex/{identifier}">client.reindex.<a href="./src/hubmap_search_sdk/resources/reindex.py">update</a>(identifier) -> None</code>

# Mget

Methods:

- <code title="post /mget">client.mget.<a href="./src/hubmap_search_sdk/resources/mget.py">retrieve_multiple</a>(\*\*<a href="src/hubmap_search_sdk/types/mget_retrieve_multiple_params.py">params</a>) -> object</code>
- <code title="post /{index_name}/mget">client.mget.<a href="./src/hubmap_search_sdk/resources/mget.py">retrieve_multiple_by_index</a>(index_name, \*\*<a href="src/hubmap_search_sdk/types/mget_retrieve_multiple_by_index_params.py">params</a>) -> object</code>

# Mapping

Methods:

- <code title="get /mapping">client.mapping.<a href="./src/hubmap_search_sdk/resources/mapping.py">retrieve_default</a>() -> object</code>
- <code title="get /{index_name}/mapping">client.mapping.<a href="./src/hubmap_search_sdk/resources/mapping.py">retrieve_index</a>(index_name) -> object</code>

# Update

Methods:

- <code title="put /update/{uuid}">client.update.<a href="./src/hubmap_search_sdk/resources/update.py">update_document</a>(uuid, \*\*<a href="src/hubmap_search_sdk/types/update_update_document_params.py">params</a>) -> None</code>
- <code title="put /update/{uuid}/{index}">client.update.<a href="./src/hubmap_search_sdk/resources/update.py">update_document_at_index</a>(index, \*, uuid, \*\*<a href="src/hubmap_search_sdk/types/update_update_document_at_index_params.py">params</a>) -> None</code>
- <code title="put /update/{uuid}/{index}/{scope}">client.update.<a href="./src/hubmap_search_sdk/resources/update.py">update_document_with_scope</a>(scope, \*, uuid, index, \*\*<a href="src/hubmap_search_sdk/types/update_update_document_with_scope_params.py">params</a>) -> None</code>

# Add

Methods:

- <code title="post /add/{uuid}">client.add.<a href="./src/hubmap_search_sdk/resources/add.py">create_document</a>(uuid, \*\*<a href="src/hubmap_search_sdk/types/add_create_document_params.py">params</a>) -> None</code>
- <code title="post /add/{uuid}/{index}">client.add.<a href="./src/hubmap_search_sdk/resources/add.py">create_document_with_index</a>(index, \*, uuid, \*\*<a href="src/hubmap_search_sdk/types/add_create_document_with_index_params.py">params</a>) -> None</code>
- <code title="post /add/{uuid}/{index}/{scope}">client.add.<a href="./src/hubmap_search_sdk/resources/add.py">update_document_with_scope</a>(scope, \*, uuid, index, \*\*<a href="src/hubmap_search_sdk/types/add_update_document_with_scope_params.py">params</a>) -> None</code>

# ClearDocs

Methods:

- <code title="post /clear-docs/{index}">client.clear_docs.<a href="./src/hubmap_search_sdk/resources/clear_docs.py">clear_all</a>(index) -> None</code>
- <code title="post /clear-docs/{index}/{uuid}">client.clear_docs.<a href="./src/hubmap_search_sdk/resources/clear_docs.py">clear_by_uuid</a>(uuid, \*, index) -> None</code>
- <code title="post /clear-docs/{index}/{uuid}/{scope}">client.clear_docs.<a href="./src/hubmap_search_sdk/resources/clear_docs.py">clear_by_uuid_and_scope</a>(scope, \*, index, uuid) -> None</code>

# ScrollSearch

Methods:

- <code title="post /{index}/scroll-search">client.scroll_search.<a href="./src/hubmap_search_sdk/resources/scroll_search.py">create</a>(index, \*\*<a href="src/hubmap_search_sdk/types/scroll_search_create_params.py">params</a>) -> None</code>
