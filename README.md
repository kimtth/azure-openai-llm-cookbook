# Azure OpenAI LLM Cookbook

![Static Badge](https://img.shields.io/badge/llm-azure_openai-blue?style=flat-square) ![GitHub Created At](https://img.shields.io/github/created-at/kimtth/azure-openai-samples?style=flat-square)

## 📌 Quick Reference: Curated Sample Collection

`A one-stop hub, like a sample library.` This repository is organized by topic to help reduce the time spent searching for and reviewing sample code. It offers a curated collection of minimal implementations and sample code from various sources.

> [!IMPORTANT]
> 🔹For more details and the latest code updates, please refer to the original link provided in the `README.app.md` file within each directory.  
> 🔹Disclaimer: Some examples are created for OpenAI-based APIs. 

💡[How to switch between OpenAI and Azure OpenAI endpoints with Python](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoint)

- Programming Languages
    - Python:🐍 
    - Jupyter Notebook:📔
    - JavaScript/TypeScript:🟦
    - Extra:🔴 
- Status & Action
    - Created:✨ (A unique example found only in this repository)
    - Modified:🎡 (An example that has been modified from a referenced source)
    - Copied:🧲 (When created or modified emojis are not following) 
    - See the details at the URL:🔗
- Microsoft libraries or products:🪟

⭐ If you find this repository useful, please consider giving it a star!

## 📖 Repository structure

## 📁 agent
- a2a_semantic_kernel🐍✨🔗🪟: Agent2Agent (A2A) Protocol Implementation with Semantic Kernel
- a2a_server_client🐍: Agent2Agent (A2A) Protocol - official implementation of Server/Client
- agent_multi-agent_pattern📔🪟: Agent multi-agent pattern
- agent_planning_pattern📔🪟: Agent planning pattern
- agent_react_pattern📔: Agent react pattern
- agent_reflection_pattern📔: Agent reflection pattern with LangGraph
- agent_reflection_pattern📔: Agent reflection pattern
- agent_tool_use_pattern📔🪟: Agent tool use pattern
- arxiv_agent🐍✨🎡: ArXiv agent
- chess_agent🐍: Chess agent
- multi_agentic_system_simulator🐍✨🔗: A Multi-Agentic System Simulator. Visualize Agent interactions.
- role_playing📔: Role-playing
- web_scrap_agent🐍✨🎡: Web scraping agent
- x-ref: [📁industry](#-industry) 

## 📁 azure
- azure_ai_foundry_sft_finetuning📔🪟: Supervised Fine-tuning
- azure_ai_foundry_workshop📔🪟: Azure AI Foundry Workshop
- azure_ai_search📔🪟: Chunking, Document Processing, Evaluation
- azure_bot📔🪟: Bot Service API
- azure_cosmos_db📔🪟: Cosmos DB as a Vector Database
- azure_cosmos_db_enn🐍✨🪟: Cosmos DB Exact Nearest Neighbor (ENN) Vector Search for Precise Retrieval
- azure_devops_(project_status_report)🐍✨🪟: Azure DevOps – Project Status Report
- azure_document_intelligence🐍🪟: Azure Document Intelligence
- azure_evaluation_sdk🐍🪟: Azure Evaluation SDK
- azure_machine_learning📔🪟: Azure Machine Learning
- azure_postgres_db📔🪟: pgvector for Vector Database
- azure_sql_db📔🪟: Azure SQL as a Vector Database
- copilot_studio🔗🪟: A low-code platform for bots and agents (formerly Power Virtual Agents)
- m365_agents_sdk🟦🪟: Rebranding of Azure Bot Framework
- sentinel_openai🔗🪟: Sentinel – Security Information and Event Management (SIEM)
- sharepoint_azure_function📔🪟: SharePoint Integration with Azure Functions
- teams_ai_sdk🔗🪟: Teams AI SDK

## 📁 cookbook

- anthropic: [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)
- gemini: [Gemini API Cookbook](https://github.com/google-gemini/cookbook)
- openai: [OpenAI Cookbook](https://github.com/openai/openai-cookbook)

## 📁 data
- azure_oai_usage_stats_(power_bi)🔴🪟: Azure OpenAI usage stats using Power BI
- azure_ocr_scan_doc_to_table🐍✨🪟: Azure Document Intelligence – Extract tables from document images and convert them to Excel
- chain-of-thought🐍🔴: Chain-of-thought reasoning prompt
- fabric_cosmosdb_chat_analytics📔🔴✨(visual)🪟: [Fabric](https://learn.microsoft.com/en-us/fabric/): Data processing, ingestion, transformation, and reporting on a single platform
- firecrawl_(crawling)🐍: Firecrawl – Web crawling and scraping
- ms_graph_api📔🪟: Microsoft Graph API
- presidio_(redaction)📔🪟: Presidio – Data redaction and anonymization
- prompt_buddy_(power_app)🔴🪟: Prompt sharing application built on Power App
- prompt_leaked🔴: Prompt leakage detection and analysis
- sammo_(prompt_opt)📔🪟: A Structure-Aware Approach to Efficient Compile-Time Prompt Optimization
- semantic_chunking_(rag)📔: Semantic chunking for Retrieval-Augmented Generation (RAG)

## 📁 dev
- code_editor_(vscode)🐍✨🔗🪟: Visual Studio Code extension development
- diagram_to_infra_template_(bicep)🐍✨🪟: Bicep – Infrastructure as Code (IaC) language
- e2e_testing_agent📔🪟: End-to-end testing with Playwright automation framework
- git_repo_with_chat🐍✨: Chat with Github repository
- gui_automation🔗🪟: Omni Parser – Screen parsing tool / Windows Agent Arena (WAA)
- llm_router🐍✨🎡: LLM request routing and orchestration
- mcp_(model_context_protocol)🐍✨🔗: Model Context Protocol
- mcp_(sse)🐍✨🔗: Remote MCP (Model Context Protocol) calls  
- mcp_to_openai_func_call🐍✨: MCP Tool Spec to OpenAI Function Call Converter
- memory_for_llm🐍🔗: Memory management techniques for LLMs – [K-LaMP](https://arxiv.org/pdf/2311.06318.pdf)🪟
- memory_graphiti🐍✨: Graph and neo4j based Memory 
- mini-copilot🐍✨🔗: DSL approach to calling the M365 API
- mixture_of_agents🐍✨🎡: Multi-agent system for collecting responses from multiple LLMs
- open_telemetry🐍✨: OpenTelemetry – Tracing LLM requests and logging

## 📁 eval
- evaluation_llm_as_judge📔: Using LLMs for automated evaluation and scoring
- guardrails📔: Guardrails for AI safety and compliance
- pyrit_(safety_eval)📔🪟: Python Risk Identification Tool

## 📁 framework
- agno_(framework)🐍: Agno – A simple, intuitive agent framework
- autogen_(framework)🐍🪟: AutoGen – A Framework for LLM Agent
- crewai_(framework)🐍: CrewAI – Agent collaboration framework
- dspy_(framework)🐍📔: DSPy – Declarative Language Model Calls into Self-Improving Pipelines
- guidance_(framework)📔🪟: Guidance – Prompt programming framework
- haystack_(framework)🐍📔: Haystack – NLP framework for RAG and search
- langchain_(framework)📔: LangChain – Framework for LLM applications
- llamaindex_(framework)📔: LlamaIndex – Data framework for LLM retrieval/agent
- magentic-one_(agent)🐍🪟: Magentic-One – Multi-agent system for solving open-ended web and file-based tasks
- mem0_(framework)🐍📔: Mem0 – LLM Memory
- omniparser_(gui)📔🪟: OmniParser – GUI automation and parsing tool
- prompt_flow_(framework)📔🪟: Prompt Flow – LLM Workflow
- prompty_(framework)🔗🔴🪟: Prompty – Prompt management
- pydantic_ai_(framework)🐍: Pydantic AI – Pydantic agent framework
- semantic_kernel_(framework)🐍🪟: Semantic Kernel – Microsoft LLM orchestration framework
- smolagent_(framework)🐍: SmolAgent – Hugging Face Lightweight AI agent framework
- tiny_troupe_(framework)📔🪟: Tiny Troupe – Multi agent persona simulation
- x-ref: [📁microsoft-frameworks-and-libraries](#-microsoft-frameworks-and-libraries): 

## 📁 industry
- auto_insurance_claims📔: Automation for auto insurance claims processing
- career_assistant_agent📔: Career guidance and job recommendation agent
- contract_review📔: Legal contract analysis and review
- customer_support_agent📔: Customer support automation
- damage_insurance_claims📔: Automated claims processing for damage insurance
- invoice_sku_product_catalog_matching📔: Invoice and SKU reconciliation for accounting
- invoice_payments📔: Automation for invoice payments
- invoice_standardization📔: Standardizing invoice units for consistency
- music_compositor_agent📔: Music composition assistant
- news_summarization_agent📔: Automated summarization of news articles
- nyc_taxi_pickup_(ui)🐍: NYC taxi pickup analysis and UI visualization
- patient_case_summary📔: Summaries for patient medical cases
- project_management📔: a tools for project tracking and task management
- stock_analysis🐍✨🔗: AutoGen demo for analyzing stock investments
- travel_planning_agent📔: Travel itinerary planner
- youtube_summarize🐍✨: Summarizing YouTube videos using AI

## 📁 llm
- finetuning_grpo📔: Group Relative Policy Optimization (GRPO) for LLM fine-tuning
- knowledge_distillation📔: Compressing LLM knowledge into smaller models
- llama_finetuning_with_lora📔: LoRA – Low-Rank Adaptation of Large Language Models
- nanoGPT🐍: Lightweight GPT implementation
- nanoMoE🐍: Lightweight Mixture of Experts (MoE) implementation

## 📁 llmops
- azure_prompt_flow🔗🪟: Azure AI Foundry - Prompt flow: E2E development tools for creating LLM flows and evaluation
- mlflow📔: OSS platform managing ML workflows

## 📁 multimodal
- image_gen_dalle📔: Image creation with segmentaion
- openai-agents-sdk-voice-pipeline📔✨: OpenAI Agents SDK for voice processing
- openai-chat-vision📔: Multimodal chat with vision capabilities
- phi-series-cookbook_(slm)🔗🪟: Phi series models cookbook (small language models)
- video_understanding📔: Video content analysis and understanding
- vision_rag📔: Combining visual data with retrieval-augmented generation (RAG)
- visualize_embedding📔: Tools for embedding visualization and analysis
- voice_audio🟦: RTClient sample for using the Realtime API in voice applications

## 📁 nlp
- multilingual_translation_(co-op-translator)🐍🪟: a library for multilingual translation
- search_the_internet_and_summarize📔: Internet search and summarization
- sentiment_analysis_for_customer_feedback📔: Sentiment analysis for customer feedback
- translate_manga_into_english🐍✨: Manga translation into English
- txt2sql🐍: Converting natural language queries into SQL

## 📁 rag
- adaptive-rag📔: Adaptive retrieval-augmented generation (RAG)
- agentic_rag📔: Agent-based RAG system
- contextual_retrieval_(rag)📔: Context-aware retrieval for RAG
- corrective_rag📔: Improving retrieval results with corrective techniques
- fusion_retrieval_reranking_(rag)📔: Fusion-based retrieval and reranking for RAG
- graphrag📔🪟: Graph-based retrieval-augmented generation
- hyde_(rag)📔: Hypothetical Document Embeddings for better retrieval
- query_rewriting_(rag)📔: Enhancing RAG by rewriting queries for better retrieval
- raptor_(rag)📔: Recursive Abstractive Processing for Tree-Organized Retrieval
- self_rag📔: Self-improving retrieval-augmented generation

## 📁 research
- analysis_of_twitter_the-algorithm_source_code📔: Analyzing [Twitter’s open-source ranking algorithm ](https://github.com/twitter/the-algorithm)
- deep_research_langchain🐍📔: AI-driven deep research and analysis tools using LangChain
- deep_research_smolagents🐍📔: AI-driven deep research and analysis tools using smolagents
- openai_code_interpreter🐍📔: OpenAI’s code interpreter for data analysis
- r&d-agent🐍🪟: Research and development AI agent

## 🛠️ Comparing Local with Remote Repository

You can use the `git_cmp.py` script (and related files) to compare your local project directories with their corresponding remote GitHub repositories. 

### Typical Workflow

1. **Index all projects and their GitHub URLs:**
    ```bash
    python git_cmp.py --index --root <root_dir> --csv git_cmp_index.csv
    ```
    This creates a CSV file listing all projects and their remote URLs.

2. **Compare local and remote repositories:**
    ```bash
    python git_cmp.py --compare --root <root_dir> --csv git_cmp_index.csv --report git_cmp_report.txt --update_csv git_cmp_needs_update.csv
    ```
    This generates a report and a CSV of projects needing updates. It also copies changed files into `.cache/` for review.

3. **Update local files from cache (optional, use with care):**
    ```bash
    python git_cmp.py --manipulate --root <root_dir> --update_csv git_cmp_needs_update.csv
    ```
    This copies files from `.cache/` back into your project directories, optionally deleting files if flagged.

### Mode & Command

- **SUBDIR Mode**  
`target_remote_path` refers to a path in a remote repository that should be used as the starting point for comparison.  
When the mode is set to `SUBDIR`, a directory with the same name as `project_name` is expected to exist under that path. The comparison should target all files and directories within that `SUBDIR`.  
If there are files or directories that exist only in the remote (excluding `readme.app.md`, `.url`, and any folder—including its subdirectories—that contains a `DONOTCMP` file), they should all be copied into the `SUBDIR`.

- **FILE Mode**  
When the mode is set to `FILE`, `target_remote_path` is not provided. A file with the same name is expected to exist at the specified GitHub URL. The comparison should target only that specific file, excluding `readme.app.md`, `.url`, and any folder—including its subdirectories—that contains a `DONOTCMP` file.

- **ROOT Mode**  
When the mode is set to `ROOT`, `target_remote_path` is also not provided. All files and directories under `project_name` (excluding `readme.app.md`, `.url`, and any folder—including its subdirectories—that contains a `DONOTCMP` file) should be compared with those in the specified GitHub URL.  Files or directories that exist only in the remote should be copied into the `project_name`.

- **Compare Command**  
In compare mode, for files and directories that exist only in the remote, zero-size placeholder files will be created locally.  
Remote files and directories are treated as the source of truth. 

- **Manipulation Command**  
In manipulation mode, the remote repository for `project_name` should be updated. It is first cloned using the `git clone` command into the `.repo_cache` directory. After cloning, the actual file copying process to the local directories begins.  
All local files and directories should be deleted first—excluding `readme.app.md`, `.url`, and any folder—including its subdirectories—that contains a `DONOTCMP` file—and then replaced with the corresponding remote versions. However, this local wipe will only be triggered when `allow_delete == 'DELETE'` to ensure safety.

- `DONOTCMP` is a marker file used to explicitly indicate that a directory is local-only and should be excluded from comparison.

### Options

- `--delay_sec <seconds>`: Add a delay between GitHub API calls to avoid rate limits.
- `--index`: Index projects and write a CSV.
- `--compare`: Compare projects and write a report.
- `--manipulate`: Update local files from the cache based on the update CSV.

### Example

```bash
python git_cmp.py --index --root . --csv git_cmp_index.csv
python git_cmp.py --compare --root . --csv git_cmp_index.csv --report git_cmp_report.txt --update_csv git_cmp_needs_update.csv
python git_cmp.py --manipulate --root . --update_csv git_cmp_needs_update.csv
```

> **Note:**  
> - Create `.env` file. Set the `GITHUB_TOKEN`. `e.g.,GITHUB_TOKEN=<your_key>`
> - Review `.cache/` and the generated report before running `--manipulate`.
> - See comments and docstrings in `git_cmp.py` for more details.

## 📚 References & Sources

- [OpenAI Cookbook](https://github.com/openai/openai-cookbook)
- [LangChain Cookbook](https://github.com/langchain-ai/langchain/tree/master/cookbook)
- [LlamaCloud Demo](https://github.com/run-llama/llamacloud-demo)
- [Chainlit Cookbook](https://github.com/Chainlit/cookbook)
- [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners)
- [GenAI Agents by NirDiamant](https://github.com/NirDiamant/GenAI_Agents)
- [RAG Techniques by NirDiamant](https://github.com/NirDiamant/RAG_Techniques)
- [Gemini API Cookbook](https://github.com/google-gemini/cookbook)
- [Anthropic Cookbook](https://github.com/anthropics/anthropic-cookbook)
- [Awesome LLM Apps](https://github.com/Shubhamsaboo/awesome-llm-apps)
- [AI Engineering Hub](https://github.com/patchy631/ai-engineering-hub)

## 💻 Microsoft Frameworks and Libraries

1. [Semantic Kernel](https://devblogs.microsoft.com/semantic-kernel/) (Feb 2023): An open-source SDK for integrating AI services like OpenAI, Azure OpenAI, and Hugging Face with conventional programming languages such as C# and Python. It's an LLM orchestrator, similar to LangChain. / [git](https://github.com/microsoft/semantic-kernel) ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/semantic-kernel?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [Azure ML Prompt Flow](https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/overview-what-is-prompt-flow) (Jun 2023): A visual designer for prompt crafting using Jinja as a prompt template language. / [ref](https://techcommunity.microsoft.com/t5/ai-machine-learning-blog/harness-the-power-of-large-language-models-with-azure-machine/ba-p/3828459) / [git](https://github.com/microsoft/promptflow)
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/promptflow?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [SAMMO](https://github.com/microsoft/sammo) (Apr 2024): A general-purpose framework for prompt optimization. / [ref](https://www.microsoft.com/en-us/research/blog/sammo-a-general-purpose-framework-for-prompt-optimization/)
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/sammo?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [guidance](https://github.com/microsoft/guidance) (Nov 2022): A domain-specific language (DSL) for controlling large language models, focusing on model interaction and implementing the "Chain of Thought" technique.
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/guidance?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [Autogen](https://github.com/microsoft/autogen) (Mar 2023): A customizable and conversable agent framework. / [ref](https://www.microsoft.com/en-us/research/blog/autogen-enabling-next-generation-large-language-model-applications/) / [Autogen Studio](https://www.microsoft.com/en-us/research/blog/introducing-autogen-studio-a-low-code-interface-for-building-multi-agent-workflows/) (June 2024)
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/autogen?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [UFO](https://github.com/microsoft/UFO) (Mar 2024): A UI-focused agent for Windows OS interaction.
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/UFO?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [Prompty](https://github.com/microsoft/prompty) (Apr 2024): A template language for integrating prompts with LLMs and frameworks, enhancing prompt management and evaluation.
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/prompty?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [OmniParser](https://github.com/microsoft/OmniParser) (Sep 2024): A simple screen parsing tool towards pure vision based GUI agent.
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/OmniParser?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [TinyTroupe](https://github.com/microsoft/TinyTroupe): LLM-powered multiagent persona simulation for imagination enhancement and business insights. [Mar 2024] ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/TinyTroupe?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [RD-Agent](https://github.com/microsoft/RD-Agent): open source R&D automation tool [ref](https://rdagent.azurewebsites.net/) [Apr 2024]
 ![GitHub Repo stars](https://img.shields.io/github/stars/microsoft/RD-Agent?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [Magentic-One](https://aka.ms/magentic-one): Built on AutoGen. A Generalist Multi-Agent System for Solving Complex Tasks [Nov 2024]
1. [PyRIT](https://github.com/Azure/PyRIT) (Dec 2023): Python Risk Identification Tool for generative AI, focusing on LLM robustness against issues like hallucination, bias, and harassment.
 ![GitHub Repo stars](https://img.shields.io/github/stars/Azure/PyRIT?style=flat-square&label=%20&color=gray&cacheSeconds=36000)
1. [Presidio](https://github.com/microsoft/presidio): Presidio (Origin from Latin praesidium ‘protection, garrison’). Context aware, pluggable and customizable data protection and de-identification SDK for text and images. [Oct 2019]
1. [Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/): Fabric integrates technologies like Azure Data Factory, Azure Synapse Analytics, and Power BI into a single unified product [May 2023]

## ➡️ Convert ipynb to Python

- To convert a Jupyter notebook (.ipynb) into a runnable Python scrip

```bash
pip install nbformat nbconvert
```

```python
import nbformat
from nbconvert import PythonExporter

# Load the notebook
notebook_filename = 'your_notebook.ipynb'
with open(notebook_filename, 'r', encoding='utf-8') as notebook_file:
notebook_content = nbformat.read(notebook_file, as_version=4)

# Convert the notebook to a Python script
python_exporter = PythonExporter()
python_code, _ = python_exporter.from_notebook_node(notebook_content)

# Save the converted Python code to a .py file
python_filename = notebook_filename.replace('.ipynb', '.py')
with open(python_filename, 'w', encoding='utf-8') as python_file:
python_file.write(python_code)

print(f"Notebook converted to Python script: {python_filename}")
```

## **Contributor** 👀

<a href="https://github.com/kimtth/azure-openai-samples/graphs/contributors">
<img src="https://contrib.rocks/image?repo=kimtth/azure-openai-samples" />
</a>

ⓒ `https://github.com/kimtth` all rights reserved.