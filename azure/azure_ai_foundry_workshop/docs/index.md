# Building a Health & Fitness AI Advisor with Azure AI Foundry 🏃‍♂️

Welcome to this hands-on, 2-hour workshop where you'll build a practical health and fitness AI advisor using Azure AI Foundry! You'll learn how to deploy an AI model, create an intelligent agent, and evaluate its performance - all through an engaging health-focused use case. 💪

> [!NOTE]
> This documentation is a work in progress. Some sections may be incomplete or subject to change as we continue to improve and expand the workshop content.


```mermaid
flowchart TB
    %% Top: Environment Setup
    ES[Environment Setup:\n• Clone Repo & Set up Python Env\n• Deploy Models & Configure Connections @ ai.azure.com]

    %% Next: Introduction
    I[Introduction:\n1. Authentication\n2. Environment Setup\n3. Quick Start]

    %% Row with Chat Completion & Agent Service side by side
    subgraph WorkshopRow[ ]
      direction LR
      CR[Chat Completion & RAG:\n1. Basic Chat Completion\n2. Embeddings\n3. Basic RAG\n4. PHI-4\n5. DeepSeek R1]
      AS[Agent Service:\n1. Agent Basics\n2. Code Interpreter\n3. File Search\n4. Bing Grounding\n5. Agents + Azure Search\n6. Agents + Azure Functions]
    end

    %% Below: Quality Attributes
    QA[Quality Attributes:\n1. Observability\n2. Evaluation\n3. End-to-End GenAI Ops]

    %% Next: Frameworks
    FW[Frameworks:\n1. RAG + SK + Agents + AI Search]

    %% Finally: E2E Sample
    E2E[E2E AI Native Sample]

    %% Connections
    ES --> I
    I --> CR
    I --> AS
    CR --> QA
    AS --> QA
    QA --> FW
    FW --> E2E
```


## The Use Case: Smart Health Advisory

You'll build an AI agent that can:
- Provide personalized fitness guidance
- Handle nutrition and exercise inquiries
- Access health and wellness resources
- Learn from user interactions
- Provide safe, accurate health advice with disclaimers

## Workshop Timeline (2 hours)

1. **Setup and Model Deployment (30 min)**
   - Quick platform overview
   - Deploy Azure OpenAI model
   - Basic configuration and testing

2. **Agent Development (45 min)**
   - Create health advisor agent
   - Implement health guidance system
   - Add health knowledge base

3. **Evaluation and Monitoring (45 min)**
   - Set up key metrics
   - Monitor performance
   - Analyze and improve responses

## Prerequisites

- Azure subscription with AI services access
- Python 3.8 or later
- Basic Python knowledge
- Text editor or IDE

## What You'll Learn

Through this practical example, you'll understand:
- How to use the AI Foundry SDK
- Model deployment and configuration
- Agent creation and management
- Performance evaluation and monitoring
- Best practices for AI applications

Let's start by [setting up your environment](introduction/overview.md)!
