"""commented one is creating index for 768 dimension for google gemini, You can use mistral embeddings which are 1024 dimensions, so created a new index for mistral embeddings"""

"""this is purely for creating index in azure search, you can run this file directly to create the index, it will read the local.settings.json file and create the index in azure search or you can directly go this in azure portal and create the index manually, but make sure to use the same fields as defined in this file"""
# import os

# from azure.core.credentials import AzureKeyCredential
# from azure.search.documents.indexes import SearchIndexClient
# from azure.search.documents.indexes.models import (
#     SearchIndex,
#     SearchField,
#     SearchFieldDataType,
#     SimpleField,
#     SearchableField,
#     VectorSearch,
#     HnswAlgorithmConfiguration,
#     VectorSearchProfile,
# )

# import json
# import os

# # Load local.settings.json manually if running outside of 'func start'
# if os.path.exists("local.settings.json"):
#     with open("local.settings.json", "r") as f:
#         config = json.load(f)
#         # Azure Functions stores environment variables inside the "Values" object
#         values = config.get("Values", {})
#         for key, value in values.items():
#             os.environ[key] = value


# def create_index():
#     endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
#     key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
#     index_name = os.environ.get(
#         "AZURE_SEARCH_INDEX", "eka-knowledge-index"
#     )
#     dimensions = int(
#         os.environ.get("EMBEDDING_DIMENSIONS", "768")
#     )

#     client = SearchIndexClient(
#         endpoint=endpoint,
#         credential=AzureKeyCredential(key),
#     )

#     index = SearchIndex(
#         name=index_name,
#         fields=[
#             SimpleField(
#                 name="id",
#                 type=SearchFieldDataType.String,
#                 key=True,
#                 filterable=True,
#             ),
#             SearchableField(
#                 name="document_name",
#                 type=SearchFieldDataType.String,
#                 filterable=True,
#             ),
#             SimpleField(
#                 name="chunk_number",
#                 type=SearchFieldDataType.Int32,
#                 filterable=True,
#             ),
#             SearchableField(
#                 name="content",
#                 type=SearchFieldDataType.String,
#             ),
#             SearchField(
#                 name="content_vector",
#                 type=SearchFieldDataType.Collection(
#                     SearchFieldDataType.Single
#                 ),
#                 searchable=True,
#                 vector_search_dimensions=dimensions,
#                 vector_search_profile_name="vector-profile",
#             ),
#         ],
#         vector_search=VectorSearch(
#             algorithms=[
#                 HnswAlgorithmConfiguration(name="hnsw-config")
#             ],
#             profiles=[
#                 VectorSearchProfile(
#                     name="vector-profile",
#                     algorithm_configuration_name="hnsw-config",
#                 )
#             ],
#         ),
#     )

#     result = client.create_or_update_index(index)
#     print(f"Index ready: {result.name}")


# if __name__ == "__main__":
#     create_index()


import json
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
)


def load_local_settings():
    """Load local.settings.json when running outside func start."""
    settings_path = Path(__file__).parent / "local.settings.json"

    if settings_path.exists():
        with settings_path.open("r", encoding="utf-8") as file:
            config = json.load(file)

        for key, value in config.get("Values", {}).items():
            # Existing environment variables take precedence.
            os.environ.setdefault(key, str(value))


def create_index():
    load_local_settings()

    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]

    # Use a separate index for Mistral embeddings.
    index_name = os.environ.get(
        "AZURE_SEARCH_INDEX",
        "eka-knowledge-index-mistral",
    )
    dimensions = int(
        os.environ.get("EMBEDDING_DIMENSIONS", "1024")
    )

    if dimensions != 1024:
        raise ValueError(
            f"Expected 1024 dimensions for this configuration, "
            f"got {dimensions}. Verify your Mistral embedding model."
        )

    client = SearchIndexClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
    )

    index = SearchIndex(
        name=index_name,
        fields=[
            SimpleField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SearchableField(
                name="document_name",
                type=SearchFieldDataType.String,
                searchable=True,
                filterable=True,
            ),
            SimpleField(
                name="chunk_number",
                type=SearchFieldDataType.Int32,
                filterable=True,
                sortable=True,
            ),
            SearchableField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="content_vector",
                type=SearchFieldDataType.Collection(
                    SearchFieldDataType.Single
                ),
                searchable=True,
                vector_search_dimensions=dimensions,
                vector_search_profile_name="vector-profile",
            ),
        ],
        vector_search=VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="hnsw-config")
            ],
            profiles=[
                VectorSearchProfile(
                    name="vector-profile",
                    algorithm_configuration_name="hnsw-config",
                )
            ],
        ),
    )

    try:
        result = client.create_or_update_index(index)
        print(f"Index ready: {result.name}")
        print(f"Vector dimensions: {dimensions}")
    finally:
        client.close()


if __name__ == "__main__":
    create_index()

