# Azure OpenAI Samples

![Static Badge](https://img.shields.io/badge/llm-azure_openai-blue?style=flat-square) ![GitHub Created At](https://img.shields.io/github/created-at/kimtth/azure-openai-samples?style=flat-square)

## 📌 Quick Reference: Code Cookbook / Sample Code Collection

- If you find this repository useful, please consider giving it a star ⭐!

> [!NOTE] 
> 
> This repository is categorized by topic to reduce the time spent searching and reviewing sample code. It provides a collection of minimal implementations and a sample code library, including demo code that has been 🧲copied, ✨created, or 🎡modified from various sources. (`priortizing jupyter notebook and official examples`). 

> [!IMPORTANT]  
> 🔹For more details and the latest code updates, please refer to the original link provided in the `README.md` file within each directory.  
> 🔹Disclaimer: Some examples are created for OpenAI-based APIs. 

💡[How to switch between OpenAI and Azure OpenAI endpoints with Python](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/switching-endpoint)

## 📜Legend

- Python:🐍 | Jupyter Notebook:📔 | JavaScript/TypeScript:🟦 | See the details at the URL:🔗 | Extra:🔴 
- Created:✨ | Modified:🎡 | Copied:🧲 (= when created or modified emojis are not following) 
- Microsoft libraries or products:🪟

## 📖 Repository structure

## 📁 agent
- agent_debates_with_tools📔
- agent_multi-agent_pattern📔🪟
- agent_planning_pattern📔🪟
- agent_react_pattern📔
- agent_reflection_pattern📔
- agent_tool_use_pattern📔🪟
- arxiv_agent🐍✨🎡
- chess_agent🐍
- role_playing📔
- web_scrap_agent🐍✨🎡
- x-ref: [📁industry](#-industry) 

## 📁 azure
- azure_ai_foundry_sft_finetuning📔🪟: Supervised Fine-tuning
- azure_ai_foundry_workshop📔🪟
- azure_ai_search📔🪟: Chuncking, Document Processing, Evaluation
- azure_bot📔🪟: Bot service API
- azure_cosmos_db📔🪟: Vector Database
- azure_devops_(project_stauts_report)🐍✨🪟
- azure_document_intelligence🐍🪟
- azure_evaluation_sdk🐍🪟
- azure_machine_learning📔🪟
- azure_postgres_db📔🪟: pgvector for Vector Database
- azure_sql_db📔🪟: Vector Database
- copilot_studio🔗🪟: A low-code platform for bots and agents (formerly known as Power Virtual Agents)
- m365_agents_sdk🟦🪟: Rebranding Azure Bot Framework
- sentinel_openai🔗🪟: Sentinel: security information and event management (SIEM)
- sharepoint_azure_function📔🪟: Sharepoint Integration with Azure Functions
- teams_ai_sdk🔗🪟

## 📁 data
- azure_oai_usage_stats_(power_bi)🔴🪟
- azure_ocr_scan_doc_to_table🐍✨🪟: Azure Document Intelligence demo to extract tables from document images and convert them to Excel.
- chain-of-thought🐍🔴
- fabric_cosmosdb_chat_analytics📔🔴🪟: [Fabric](https://learn.microsoft.com/en-us/fabric/): data processing, ingestion, transformation, and reporting on a single platform.
- firecrawl_(crawling)🐍
- ms_graph_api📔🪟
- presidio_(redaction)📔🪟
- prompt_buddy_(power_app)🔴🪟: Prompt sharing application built on Power App
- prompt_leaked🔴
- sammo_(prompt_opt)📔🪟: A Structure-Aware Approach to Efficient Compile-Time Prompt Optimization
- semantic_chunking_(rag)📔

## 📁 dev
- code_editor_(vscode)🐍✨🔗🪟: Visual Code Extension Development
- diagram_to_infra_template_(bicep)🐍✨🪟: Bicep: an Infrastructure as Code (IaC) language. 
- e2e_testing_agent📔🪟: Playwright Testing Automation Framework
- gui_automation🔗🪟: Omni parser: Screen parsing tool / Windows Agent Arena (WAA)
- llm_router🐍✨🎡
- mcp_(model_context_protocol)🐍✨🔗
- memory_for_llm🐍🔗
- memory_graphiti🐍
- mini-copilot🐍✨🔗: DSL approach to calling the M365 API
- mixture_of_agents🐍✨🎡
- open_telemetry🐍✨: Open Telemetry: Tracing LLM requests and logging

## 📁 eval
- evaluation_llm_as_judge📔
- guardrails📔
- pyrit_(safety_eval)📔🪟: Python Risk Identification Tool for generative AI 

## 📁 framework
- agno_(framework)🐍
- autogen_(framework)🐍🪟
- crewai_(framework)🐍
- dspy_(framework)🐍📔
- guidance_(framework)📔🪟
- haystack_(framework)🐍📔
- langchain_(framework)📔
- llamaindex_(framework)📔
- magentic-one_(agent)🐍🪟
- mem0_(framework)🐍📔
- omniparser_(gui)📔🪟
- prompt_flow_(framework)📔🪟
- prompty_(framework)🔗🔴🪟
- pydantic_ai_(framework)🐍
- semantic_kernel_(framework)🐍🪟
- smolagent_(framework)🐍
- tiny_troupe_(framework)📔🪟
- x-ref: [📁microsoft-frameworks-and-libraries](#-microsoft-frameworks-and-libraries): 

## 📁 industry
- auto_insurance_claims📔
- career_assistant_agent📔
- contract_review📔
- customer_support_agent📔
- damage_insurance_claims📔
- invoice_+_sku_matching📔
- invoice_payments📔
- invoice_unit_standardization📔
- music_compositor_agent📔
- news_summarization_agent📔
- nyc_taxi_pickup_(ui)🐍
- patient_case_summary📔
- project_management📔
- stock_analysis🐍✨🔗: AutoGen demo for analyzing stock investments
- travel_planning_agent
- youtube_summarize🐍✨

## 📁 llm
- finetuning_grpo📔:  Group Relative Policy Optimization (GRPO)
- knowledge_distillation📔
- llama_finetuning_with_lora📔: LoRA: Low-Rank Adaptation of Large Language Models
- nanoGPT🐍
- nanoMoE🐍

## 📁 llmops
- mlflow📔: OSS platform managing ML workflows
- azure_prompt_flow🔗🪟: Prompt flow: E2E development tools for creating LLM flows and evaluation

## 📁 multimodal
- image_gen📔
- openai-agents-sdk-voice-pipeline📔
- openai-chat-vision📔
- phi-series-cookbook_(slm)🔗🪟
- video_understanding📔
- vision_rag📔
- visualize_embedding📔
- voice_audio🟦: RTClient sample to use Realtime API

## 📁 nlp
- multilingual_translation_(co-op-translator)🐍🪟
- search_the_internet_and_summarize📔
- sentiment_analysis_for_customer_feedback📔
- translate_manga_into_english🐍✨
- txt2sql🐍

## 📁 rag
- adaptive-rag📔
- agentic_rag📔
- contextual_retrieval_(rag)📔
- corrective_rag📔
- fusion_retrieval_reranking_(rag)📔
- graphrag📔🪟
- hyde_(rag)📔: Hypothetical Document Embeddings
- query_rewriting_(rag)📔
- raptor_(rag)📔: Recursive Abstractive Processing for Tree-Organized Retrieval
- self_rag📔

## 📁 research
- analysis_of_twitter_the-algorithm_source_code📔
- deep_research🐍📔
- openai_code_interpreter🐍📔
- r&d-agent🐍(🪟RD-agent)

## 📚 References  

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