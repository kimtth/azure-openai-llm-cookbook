# RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval

- https://github.com/langchain-ai/langchain/tree/master/cookbook
- https://github.com/run-llama/llama_index > llama-index-packs/llama-index-packs-raptor/examples

## RAPTOR vs. GraphRAG

### RAPTOR  
[RAPTOR](https://arxiv.org/abs/2401.18059v1) constructs a tree structure by recursively embedding, clustering, and summarizing text. It enhances retrieval-augmented models (RAG) for complex reasoning tasks by integrating information across different abstraction levels.

### GraphRAG  
[GraphRAG](https://arxiv.org/abs/2404.16130v1) builds a graph-based index with entity knowledge graphs and community summaries. It excels at query-specific summarization, efficiently handling large datasets by leveraging entity relationships.

### Key Differences:
- Structure:  
  - RAPTOR uses a tree structure with recursive summarization.  
  - GraphRAG uses a graph structure with community summaries based on entity relationships.

- Focus:  
  - RAPTOR enhances retrieval for complex reasoning tasks.  
  - GraphRAG focuses on query-specific summarization for large datasets.