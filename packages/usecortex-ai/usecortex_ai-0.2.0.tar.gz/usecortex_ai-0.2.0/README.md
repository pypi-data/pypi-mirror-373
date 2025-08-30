```
# Introduction

> You can generate and manage API keys from your Cortex Dashboard. All endpoints require an API key sent as a Bearer token in the Authorization header.

Welcome to the Cortex SDK API Reference. This section documents every available endpoint and how to interact with them to power AI apps and agents with intelligent memory and retrieval.

> Base URL: `https://api.usecortex.ai`
>
> Contact us to get your API key at [founders@usecortex.ai](mailto:founders@usecortex.ai)

```mdx
Authorization: Bearer <your_api_key>
```

### **Data Ingestion**

Upload and import content into Cortex from various sources.

* `/upload/upload_document` — Upload single documents
* `/upload/upload_text` — Upload text/markdown content
* `/upload/upload_app_sources` — Import from workplace apps (Gmail, Slack, etc.)
* `/upload/scrape_webpage` — Scrape and index web content
* `/upload/verify_processing` — Check upload processing status
* `/upload/batch_upload` — Upload multiple files at once

### **Search & Query**

Retrieve answers and information from your knowledge base.

* `/search/qna` — Main search endpoint with AI-powered responses. Supports optional `metadata` parameter to filter sources by `source_title` or `source_type`.
* `/search/retrieve` — Hybrid search without AI generation. Returns structured search results for custom processing.
  – `/search/full-text-search` – Perform a full text search without AI generation. Allows you to use operators like logical `AND`, `OR`

### **Knowledge Management**

Browse, fetch, and manage your knowledge base.

* `/list/sources` — Browse all indexed sources
* `/list/sources_by_id` — Get specific sources by ID
* `/fetch/fetch_content` — Retrieve file content and download URLs
* `/delete_source` — Remove sources from knowledge base

### **Update & Upsert**

Update existing content and embeddings. If a `source_id` does not exist, these endpoints upsert (create or update).

* `/upload/update_text` — Upsert markdown/text content by `source_id`
* `/upload/update_document` — Upsert a file/document by `source_id`
* `/upload/update_webpage` — Re-scrape and upsert a webpage by `source_id` and `web_url`
* `/upload/update_embeddings` — Update existing embeddings by `chunk_id` within a batch/source

### **Embeddings**

Manage and query pre-computed embeddings.

* `/upload/upload_embeddings` — Upload embeddings and get generated `chunk_ids`
* `/embeddings/search` — Vector similarity search; returns nearest `chunk_ids` and scores
* `/embeddings/by-chunk-ids` — Retrieve embedding vectors for specific `chunk_ids`
* `/embeddings/delete` — Delete embeddings by `chunk_id`

### **Tenant Management**

Create and monitor tenants for multi-tenant setups.

* `/user/create_tenant` — Create a tenant (optionally provide `tenant_id`, or auto-generate)
* `/embeddings/create_embeddings_tenant` — Create an embeddings-only tenant (sets `sub_tenant_id = tenant_id`); use when directly uploading/searching embeddings
* `/tenant/stats` — Get tenant stats (object count, vector dimension, identifiers)

### **User Memory**

Personalize, retrieve, and manage user-specific AI memories for advanced agentic workflows.

* `/user_memory/list_user_memories` — Browse user memories
* `/user_memory/retrieve_user_memory` — Get specific user memories
* `/user_memory/add_user_memory` — Manually add user-specific memories
* `/user_memory/generate_user_memory` — AI-generated personalized memories
* `/user_memory/delete_user_memory` — Remove user memories

## 💡 Best Practices

* Use **sub-tenants** to support multi-user isolation in B2B use cases.
* Leverage **metadata** (e.g., `source_title`, `source_type` in the QnA API) for fine-grained filtering and agentic retrieval.
* Tune **search\_alpha** and **recency\_bias** to control relevance.
* Enable **highlight\_chunks** for chunk-level citations.

---

```

```
