# Azure AI Search Index Design for Retriever

- https://github.com/microsoft/RAG-Knowledge
- https://github.com/farzad528/azure-ai-search-python-playground
- https://github.com/Azure-Samples/azure-ai-document-processing-samples

---

## Scenario

1. **Product Technical Documentation**

   - **Overview**: A RAG application that answers based on the detailed specifications of products and services, derived from technical documentation.
   - **Objective**: Build a basic RAG application using structured documents.
   - **Utilized Data**: [Azure AI Search Technical Documentation](https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search)
   - **File Structure**: 
     - `01_Preprocessing.ipynb`: Perform OCR on the documents to extract text and images.
     - `01_IndexingPushType.ipynb`: Use the text and images extracted by `01_Preprocessing.ipynb` as input, build a search index on Azure AI Search, and import the data in a PUSH type using the SDK. Additionally, define an RGA pipeline for manual evaluation.
     - `01_IndexingPullType.ipynb`: Use the text and images extracted by `01_Preprocessing.ipynb` as input, build a search index on Azure AI Search, and import the data in a PULL type using an indexer. Additionally, define an RGA pipeline for manual evaluation.

2. **Business Documents**

   - **Overview**: A RAG application that answers based on the content of business documents (pptx, pdf, word, etc.).
   - **Objective**: Build a RAG application using diverse business documents (in terms of content and format).
   - **Utilized Data**: Various materials from the Cabinet Office’s [AI Strategy Conference](https://www8.cao.go.jp/cstp/ai/index.html).
   - **File Structure**:
     - `03_Preprocessing.ipynb`: Perform OCR on the documents to extract text and images.
     - `03_IndexingPushType.ipynb`: Use the text and images extracted by `03_Preprocessing.ipynb` as input, build a search index on Azure AI Search, and import the data in a PUSH type using the SDK.
     - `03_Query.ipynb`: Define an RAG pipeline on the search index built by `03_IndexingPushType.ipynb` and evaluate it using Azure AI’s Evaluation feature.

--- 
