
# How to Use ENN Vector Search

- Before using ENN Vector Search, ensure that a vector index (e.g., IVF, HNSW, DiskANN) is created for the relevant path. If a vector index already exists, there's no need to rebuild it when switching between search methods, since ENN operates independently of these indexes during query execution.​ [ref](https://devblogs.microsoft.com/cosmosdb/exact-nearest-neighbor-enn-vector-search/)

- To enable ENN, set `"exact": true` in your query. For example:

```json
{
  "$search": {
    "cosmosSearch": {
      "path": "myVectorField",
      "exact": true,               // Enables ENN
      "query": [0.2, 0.4, 0.9],    // Query vector
      "k": 10,                     // Number of results to return
      "filter": {
        "tenant_id": { "$eq": "tenant123" }
      }
    }
  }
}
```

### Configuration

```bash
pip install pymongo openai
```

