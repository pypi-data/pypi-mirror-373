"""
The `.enpi_api_client.EnpiApiClient` class is the main entry point for interacting with the ENPICOM API. You use
it as a context manager, and by default it wil fetch the API key from the `ENPI_API_KEY` environment variable.

Different functionalities are separated by their contexts, a list of these can be found in the `.api`
module. These are all available as attributes of the `.enpi_api_client.EnpiApiClient` instance.

For example, to access the `collection` API to list all your collections with their metadata, you can do the following:

```python
with EnpiApiClient() as enpi_client:
    for collection in enpi_client.collection_api.get_collections_metadata():
        print(collection)
```
"""
