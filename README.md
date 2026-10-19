# Enterprise Knowledge Assistant

A prototype enterprise knowledge assistant that answers employee questions using internal documents and creates a support ticket when the available evidence is insufficient.

The solution combines Microsoft Power Platform with an Azure-hosted retrieval-augmented generation (RAG) API.

## Architecture

```text
Employee
   |
   v
Power Apps Canvas
   |
   v
Power Automate
   |
   v
Azure Functions API ------> Google Gemini API
   |
   v
Azure AI Search

Original documents -------> Azure Blob Storage

Unanswered question + ticket option -------> Microsoft Dataverse
```

## Components

- **Power Apps Canvas:** Employee-facing question interface with an option to create a ticket when an answer cannot be found.
- **Power Automate:** Connects the app to the backend and handles the response and conditional ticket workflow.
- **Azure Functions (Python):** API for document ingestion and question answering.
- **Azure Blob Storage:** Stores uploaded source documents.
- **Azure AI Search:** Stores searchable document chunks and vectors for retrieval.
- **Google Gemini:** Generates embeddings and answers grounded in retrieved context.
- **Microsoft Dataverse:** Stores tickets and supporting metadata, including document information, categories, and routing rules.
# Sample UI
[power canvas UI](power_canvas_app_basic_ui.png)

# Power Automate Workflow
[Workflow](power_automater_flow.png)

## How it works

### 1. Document ingestion

1. A supported document is uploaded to the ingestion endpoint.
2. The original file is stored in the private Azure Blob Storage container.
3. Text is extracted and split into chunks.
4. The chunks are embedded using the configured Gemini embedding model.
5. The chunks and vectors are indexed in Azure AI Search.

The current implementation has been set up for `.txt`, `.pdf`, and `.docx` files. Confirm supported formats in `function_app.py`.

### 2. Question answering

1. An employee submits a question through Power Apps.
2. Power Automate sends it to the Azure Functions API.
3. The API embeds the question and searches Azure AI Search for relevant chunks.
4. Gemini generates an answer using the retrieved context.
5. The API returns the answer, source references, and an insufficient-evidence flag.
6. Power Automate returns the result to Power Apps.

The intended behavior is to ground answers in retrieved documents rather than rely only on the model's general knowledge.

### 3. Conditional ticket creation

The app includes a ticket-creation toggle. When enabled, a question that cannot be answered from the available knowledge base can be routed into a Dataverse ticket. When disabled, the app should return the answer status without creating a ticket.

Insufficient-evidence detection needs testing against unanswered, partially answered, and misleading questions before it can be relied on.

## Repository scope

This repository contains the Python Azure Functions backend. The Power Apps Canvas app and Power Automate flow are separate parts of the overall solution.

The backend includes routes for health checks, local development, cloud document ingestion, and cloud question answering. Check `function_app.py` for the exact route names and request/response schemas.

## Configuration

Use environment variables or `local.settings.json` for local development. Never commit API keys, connection strings, function keys, or other credentials.

Example settings template:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "<storage-connection-string-or-local-emulator-setting>",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "GEMINI_API_KEY": "<your-gemini-api-key>",
    "GEMINI_EMBEDDING_MODEL": "<configured-embedding-model>",
    "GEMINI_GENERATION_MODEL": "<configured-generation-model>",
    "EMBEDDING_DIMENSIONS": "<dimensions-matching-the-embedding-model>",
    "AZURE_STORAGE_CONNECTION_STRING": "<blob-storage-connection-string>",
    "AZURE_STORAGE_CONTAINER": "knowledge-base",
    "AZURE_SEARCH_ENDPOINT": "<azure-ai-search-endpoint>",
    "AZURE_SEARCH_KEY": "<azure-ai-search-key>",
    "AZURE_SEARCH_INDEX": "<index-name>"
  }
}
```

This is an illustrative template, not a guaranteed complete list. Keep setting names aligned with the current code and Azure resources. Do not share real secrets.

## Local development

Prerequisites:

- Python version supported by the Function App
- Azure Functions Core Tools v4
- Access to the configured Azure Blob Storage and Azure AI Search resources
- A Gemini API key with access to the configured models

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
func start
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

If the Functions host reports that `AzureWebJobsStorage` is unhealthy, check whether it points to a local storage emulator or a real Azure Storage account. A local emulator setting requires the emulator to be running. A cloud connection string requires valid credentials and network access.

## Gemini connectivity from Azure Functions

Gemini API requests from a cloud-hosted Function App can fail because of outbound connectivity, DNS, proxy, or provider-availability restrictions in the deployment environment.

If direct requests fail:

1. Inspect the exact error and confirm that the Gemini API is available from the Function App's region and network.
2. If your organization's network policy permits it, configure an approved outbound HTTPS proxy using Function App application settings such as `HTTPS_PROXY` and `HTTP_PROXY`.
3. Keep proxy credentials in secure application settings or a secret store, not in source code, and redact them from logs.

**Do not use arbitrary public proxies in production environments.**A proxy can expose API traffic and credentials, and it does not guarantee that a provider-side regional restriction will be resolved. Prefer an approved, trusted proxy or a supported deployment region/network configuration.

## Security notes

- Keep `local.settings.json` out of Git.
- Ignore local settings, virtual environments, caches, and secrets in `.gitignore`.
- Do not embed Azure Function keys in the Canvas app.
- For function-level authorization, prefer sending the key in the `x-functions-key` header.
- Use synthetic or non-sensitive documents while authentication and access controls are still being finalized.
- Before using real company data, review authentication, authorization, data access, logging, and secret management.

## Current limitations

- This is an MVP/prototype, not a production-ready enterprise service.
- Answer quality depends on document extraction, chunking, retrieval, prompts, and the configured Gemini models.
- Source references should be checked against retrieved chunks and displayed clearly in the app.
- Insufficient-evidence detection needs systematic testing before relying on it for ticket routing.
- This README describes the backend; the Canvas app and Power Automate flow are maintained separately.

## Suggested test cases

1. Ask a question clearly answered by an indexed document.
2. Ask a question not covered by any document.
3. Ask a question only partially answered by the documents.
4. Ask a misleading question that contains a false assumption.
5. Test ticket creation with the toggle enabled and disabled.
6. Upload a supported document and verify that it is stored and indexed.
7. Check that source references match the retrieved content.
8. Test API failures and Gemini connectivity without exposing credentials in logs.

## License

Add a license before distributing or reusing this repository publicly.
