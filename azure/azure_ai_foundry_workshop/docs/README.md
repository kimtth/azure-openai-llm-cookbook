# Azure AI Foundry Workshop

<div align="center">

[📦Prerequisites](#-prerequisites) | [🚀Quick Start](#-quick-start) | [🤖Overview](#-overview) | [📔Workshop Content](#-workshop-content) | [🧩Project Structure](#-project-structure) | [❓Support](#-support) | [🤝Contributing](#-contributing)

</div>


## 🤖 Overview

A hands-on workshop that guides you through building intelligent apps and AI agents on top of Azure AI Foundry, with fun examples related to health and dietary advice. You will:
- Learn Azure AI Foundry fundamentals
- Set up authentication and project configuration
- Deploy and test AI models
- Build AI agents (health advisor examples)
- Implement health calculations and dietary planning
- Evaluate agent performance and monitor quality attributes
- Deploy an end-to-end AI native sample app that incorporates all these capabilities and design patterns

> **Duration**: 4-5 hours  
> **Focus**: Hands-on exercises, interactive notebooks, practical examples, end-to-end project

## 📸 Visuals

### Sections Overview
![Sections](sections.png)
*Figure 1: Overview of different sections in this workshop.*

### End-to-End Sample UI
![e2esample](./3-ai-native-e2e-sample/assets/ui.png)
*Figure 2: User interface of the end-to-end AI native sample project.*

---

## 📦 Prerequisites    

Before starting the workshop, ensure you have:

- [Python 3.10](https://www.python.org/downloads/) or higher installed
- An active Azure subscription with access to [Azure AI Foundry](https://ai.azure.com)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- [Git](https://git-scm.com/downloads) installed
- [VS Code](https://code.visualstudio.com/), [GitHub Codespaces](https://github.com/features/codespaces), or [Jupyter Notebook](https://jupyter.org/install) environment
- Basic Python programming knowledge
- Model deployment and [AI Search](https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search) connection configured in Azure AI Foundry

---

## 🚀 Quick Start

1. **Clone the repo**:
   ```bash
   git clone https://github.com/Azure/ai-foundry-workshop.git
   cd ai-foundry-workshop
   ```

2. **Install uv**:
   ```bash
   # Unix/Linux/macOS
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   (Invoke-WebRequest -Uri https://astral.sh/uv/install.ps1 -UseBasicParsing).Content | pwsh
   ```

3. **Create & activate a virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

4. **Set up Azure AI Foundry**:

   a. **Create Project and Deploy Resources**:
      1. Go to [Azure AI Foundry](https://ai.azure.com)
      2. Create a new AI Hub and Project using the AI Foundry Wizard
      3. Deploy required models:
         - GPT models(gpt-4o, gpt-4o-mini) for chat/completion (**set TPM to max** to avoid issues with Agents notebooks)
         - Embedding model for vector search
         - Ensure the model is deployed in `Global-Standard` or `DataZone-Standard`
      4. Set up connections:
         - Configure [Grounding with Bing](https://learn.microsoft.com/en-us/azure/ai-services/agents/how-to/tools/bing-grounding?view=azure-python-preview&tabs=python&pivots=overview) connection
         - Configure Azure AI Search connection
      5. Add your user account to the `Azure AI Developer` role from Azure AI Foundry Management Portal

   b. **Configure Environment Variables**:
      ```bash
      cp .env.example .env
      ```
      Update `.env` with your Azure AI Foundry values:
      - `PROJECT_CONNECTION_STRING`: Your project connection string from Azure ML workspace
      - `MODEL_DEPLOYMENT_NAME`: Your model deployment name
      - `EMBEDDING_MODEL_DEPLOYMENT_NAME`: Your embedding model deployment name
      - `TENANT_ID`: Your tenant ID from Azure portal
      - `BING_CONNECTION_NAME`: Your Bing search connection name
      - `SERVERLESS_MODEL_NAME`: Your serverless model name

      > **Note**: The model specified in `MODEL_DEPLOYMENT_NAME` must be supported by Azure AI Agents Service or Assistants API. See [supported models](https://learn.microsoft.com/en-us/azure/ai-services/agents/concepts/model-region-support?tabs=python#azure-openai-models) for details. For Grounding with Bing Search, you need to use `gpt-4o-mini` model.

5. **Install dependencies**:
   ```bash
   # Install core Azure AI SDKs and Jupyter requirements
   uv pip install azure-identity azure-ai-projects azure-ai-inference[opentelemetry] azure-search-documents azure-ai-evaluation azure-monitor-opentelemetry

   # Install Jupyter requirements
   uv pip install ipykernel jupyterlab notebook

   # Register the kernel with Jupyter
   python -m ipykernel install --user --name=.venv --display-name="Python (.venv)"

   # Install additional requirements (optional - for deploying repo or running mkdocs)
   uv pip install -r requirements.txt
   ```

   > **Note**: If you encounter kernel errors in VS Code, try:
   > 1. Select kernel: Click "Select Kernel" > "Python Environments" > "Python (.venv)"
   > 2. If kernel is not listed, run `python -m ipykernel install --user --name=.venv` again, or use the "Create New Kernel" wizard in VS Code to create a new Python environment
   > 3. Reload VS Code if needed

6. **Choose your notebook environment**:

   **Option A: VS Code**
   - Install [VS Code Python extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
   - Install either:
     - [Jupyter extension](https://marketplace.visualstudio.com/items?itemName=ms-toolsai.jupyter) for .ipynb files
     - [Polyglot Notebooks extension](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.dotnet-interactive-vscode) for .dib files
   - Open any notebook and select your Python kernel (.venv)

   **Option B: GitHub Codespaces**
   - Click "Code" > "Create codespace" on the repository
   - Wait for environment setup
   - Notebooks will be ready to run

   **Option C: Jupyter Lab/Notebook**
   ```bash
   # Install Jupyter if you haven't already
   uv pip install jupyterlab notebook

   # Start Jupyter Lab (recommended)
   jupyter lab

   # Or start Jupyter Notebook
   jupyter notebook
   ```

7. **Follow the Learning Path**:
    1. **Introduction** (`1-introduction/`)
       - `1-authentication.ipynb`: Set up your Azure credentials
       - `2-environment_setup.ipynb`: Configure your environment
       - `3-quick_start.ipynb`: Learn basic operations

    2. **Main Workshop** (`2-notebooks/`)
       - Chat Completion & RAG (`1-chat_completion/`)
       - Agent Development (`2-agent_service/`)
       - Quality Attributes (`3-quality_attributes/`)

---

## 📔 Workshop Learning Path

Follow these notebooks in sequence to complete the workshop:

### 1. Introduction (`1-introduction/`)
| Notebook | Description |
|----------|-------------|
| [1. Authentication](1-introduction/1-authentication.ipynb) | Set up Azure credentials and access |
| [2. Environment Setup](1-introduction/2-environment_setup.ipynb) | Configure your development environment |
| [3. Quick Start](1-introduction/3-quick_start.ipynb) | Learn basic Azure AI Foundry operations |

### 2. Main Workshop (`2-notebooks/`)
| Topic | Notebooks |
|-------|-----------|
| **Chat Completion & RAG** | • [Chat Completion & RaG](2-notebooks/1-chat_completion/) |
| **Agent Development** | • [Agent Development](2-notebooks/2-agent_service/) |
| **Quality Attributes** | • [Observability & Evaluations](2-notebooks/3-quality_attributes/) |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on how to:
- Submit bug reports and feature requests
- Submit pull requests
- Follow our coding standards
- Participate in code reviews

---

## ❓ Support

If you need help or have questions:

---




