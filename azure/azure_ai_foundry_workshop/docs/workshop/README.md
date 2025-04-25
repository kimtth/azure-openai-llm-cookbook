# Azure AI Foundry Workshop (4-5 hours)

This hands-on workshop guides you through building AI-native applications using Azure AI Foundry, with examples related to health and dietary advice.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/Azure/ai-foundry-workshop)

You can run this workshop in several ways:
1. **GitHub Codespaces**: Click the button above to start coding in your browser
2. **Visual Studio Code**: Visit [aka.ms/wksp](https://aka.ms/wksp) to set up your local environment
3. **Your IDE**: Fork and clone this repository to work locally

👉 **Get Started**:
1. ⭐ Star this repository to show your support
2. 🔄 Fork it to your account to start building
3. 📝 Follow the learning path below

## Learning Path

### 1. Introduction (30 minutes)
- [Authentication](../1-introduction/1-authentication.ipynb): Set up Azure credentials
- [Environment Setup](../1-introduction/2-environment_setup.ipynb): Configure development environment
- [Quick Start](../1-introduction/3-quick_start.ipynb): Basic Azure AI operations

### 2. Chat Completion & RAG (1 hour)
- [Basic Chat Completion](../2-notebooks/1-chat_completion/1-basic-chat-completion.ipynb)
- [Embeddings](../2-notebooks/1-chat_completion/2-embeddings.ipynb)
- [Basic RAG](../2-notebooks/1-chat_completion/3-basic-rag.ipynb)
- [Phi-4 Model](../2-notebooks/1-chat_completion/4-phi-4.ipynb)

### 3. Building AI Agents (2 hours)
- [Agent Basics](../2-notebooks/2-agent_service/1-basics.ipynb)
- [Code Interpreter](../2-notebooks/2-agent_service/2-code_interpreter.ipynb)
- [File Search](../2-notebooks/2-agent_service/3-file-search.ipynb)
- [Bing Grounding](../2-notebooks/2-agent_service/4-bing_grounding.ipynb)
- [AI Search Integration](../2-notebooks/2-agent_service/5-agents-aisearch.ipynb)
- [Azure Functions Deployment](../2-notebooks/2-agent_service/6-agents-az-functions.ipynb)

### 4. Quality & Monitoring (30 minutes)
- [Observability](../2-notebooks/3-quality_attributes/1-Observability.ipynb)
- [Evaluation](../2-notebooks/3-quality_attributes/2-evaluation.ipynb)

### 5. E2E Sample Application (1 hour)
Build a complete AI-native health advisor application:
- [Sample Architecture](architecture.md)
- [Backend Implementation](../3-ai-native-e2e-sample/backend/README.md)
- [Frontend Implementation](../3-ai-native-e2e-sample/frontend/README.md)

## Prerequisites
See the [Prerequisites](../README.md) section for detailed setup instructions.

## Azure Documentation
For detailed service documentation, refer to:
- [Azure AI Foundry](https://learn.microsoft.com/azure/ai-foundry) 【†L1】
- [Azure AI Services](https://learn.microsoft.com/azure/ai-services) 【†L2】
- [Azure AI Search](https://learn.microsoft.com/azure/search/search-what-is-azure-search) 【†L3】

## Copy Context for LLMs
To get AI-friendly context about Azure AI SDKs and implementation patterns, click the "Copy Context for LLMs" button at the top of this page. This will copy relevant information about:
- Azure AI Projects SDK
- Azure AI Inference SDK
- Azure AI Agent patterns and tools
