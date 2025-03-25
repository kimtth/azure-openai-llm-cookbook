import asyncio
from datetime import datetime

from openai import AsyncAzureOpenAI
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.edges import EntityEdge
from graphiti_core.llm_client import OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient

# Azure OpenAI configuration
API_KEY = "<your-azure-openai-key>"
API_VERSION_EMBED = "<your-azure-openai-embedding-api-version>"  # Use the API version for embedding
API_VERSION_CHAT = "<your-azure-openai-api-version>"  # Use the API version for chat
AZURE_ENDPOINT = "https://<your_endpoint>.openai.azure.com"
AZURE_EMBED_MODEL_NAME = "<your-azure-embedding-model-name>"  # e.g., "text-embedding-3-small"
AZURE_CHAT_MODEL_NAME = "<your-azure-chat-model-name>"  # e.g., "gpt4o-mini"

# Create Azure OpenAI clients
azure_openai_client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    azure_deployment=AZURE_CHAT_MODEL_NAME,
    api_version=API_VERSION_CHAT,
    api_key=API_KEY,
)
azure_openai_embed_client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    azure_deployment=AZURE_EMBED_MODEL_NAME,
    api_version=API_VERSION_EMBED,
    api_key=API_KEY,
)


# Initialize Graphiti with Azure OpenAI clients
graphiti = Graphiti(
    "bolt://localhost:7687",
    "neo4j",
    "password",
    llm_client=OpenAIClient(client=azure_openai_client),
    embedder=OpenAIEmbedder(
        config=OpenAIEmbedderConfig(embedding_model=AZURE_EMBED_MODEL_NAME),
        client=azure_openai_embed_client,
    ),
    cross_encoder=OpenAIRerankerClient(client=azure_openai_client),
)


async def perform_graphiti_operations():
    if graphiti is None:
        print("Graphiti initialization failed.")
        return

    # Build indices and constraints once
    await graphiti.build_indices_and_constraints()

    episodes = [
        "Donald Trump was the 45th president of the United States.",
        "Before his presidency, he was a businessman and television personality.",
        "He served as president from January 20, 2017, to January 20, 2021.",
        "After a successful campaign in 2024, he was inaugurated as the 47th president on January 20, 2025",
        "Becoming the second individual in U.S. history to serve non-consecutive terms, following Grover Cleveland.",
    ]

    for i, episode in enumerate(episodes):
        try:
            await graphiti.add_episode(
                name=f"Radio {i}",
                episode_body=episode,
                source=EpisodeType.text,
                source_description="podcast",
                reference_time=datetime.now(),
            )
        except Exception as error:
            print(f"Error adding episode {i}: {error}")
        else:
            print(f"Episode {i} added successfully.")
        await asyncio.sleep(1)


async def graphiti_search(query: str):
    try:
        results: EntityEdge = await graphiti.search(query)
        if results:
            print("Query Results:")
            print(results[-1].fact)
        else:
            print("No results found.")
    except Exception as error:
        print(f"Error during search: {error}")


async def close_graphiti():
    await graphiti.close()


def main():
    asyncio.run(perform_graphiti_operations())
    query = "Who is the 45th president of the United States?"
    asyncio.run(graphiti_search(query))
    asyncio.run(close_graphiti())


if __name__ == "__main__":
    main()

'''
# Tip

The official documentation for Graphiti recommends using Neo4j Desktop for local development.

Instead, the following uses Neo4J Docker for local development. https://github.com/getzep/graphiti/issues/289

1. The command for initializing the password is:
The password is set to "password" in this example.

> docker exec -it neo4j-container bash
> neo4j-admin dbms set-initial-password password

2. The command for starting the Neo4j Docker container is:
The "neo4j/password" means that "neo4j" is the username and "password" is the password.

> docker run -d --name neo4j-container  -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password  -v neo4j_data:/data neo4j

# Console output

'''