import os
import urllib
from pymongo import MongoClient
from openai import AzureOpenAI


# Configuration
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_EMBED_MODEL_NAME = os.environ.get("AZURE_OPENAI_EMBED_MODEL_NAME")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")

COSMOS_DB_ENDPOINT = os.environ.get("COSMOS_DB_ENDPOINT")
COSMOS_DB_DATABASE = os.environ.get("COSMOS_DB_DATABASE")
COSMOS_DB_COLLECTION_NAME = os.environ.get("COSMOS_DB_COLLECTION_NAME")
COSMOS_DB_USERNAME = os.environ.get("COSMOS_DB_USERNAME")
COSMOS_DB_PASSWORD = os.environ.get("COSMOS_DB_PASSWORD")


def init_openai_client():
    """Initialize and return an Azure OpenAI client"""
    client = AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
    )
    return client


def generate_embedding(client, text):
    """Generate embedding for the given text"""
    response = client.embeddings.create(input=text, model=AZURE_OPENAI_EMBED_MODEL_NAME)
    embedding = response.data[0].embedding
    return embedding


def init_cosmos_client():
    """Initialize and return a Cosmos DB for MongoDB client"""
    mongo_conn = (
        "mongodb+srv://"
        + urllib.parse.quote(str(COSMOS_DB_USERNAME))
        + ":"
        + urllib.parse.quote(str(COSMOS_DB_PASSWORD))
        + "@"
        + str(COSMOS_DB_ENDPOINT)
        + "/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
    )

    mongo_client = MongoClient(mongo_conn)
    return mongo_client


def ensure_database_and_container(client):
    """Ensure the database and collection exist, create them if they don't"""
    db = client[COSMOS_DB_DATABASE]

    if COSMOS_DB_COLLECTION_NAME not in db.list_collection_names():
        # Creates a unsharded collection that uses the DBs shared throughput
        # database.drop_collection(COSMOS_DB_COLLECTION_NAME)
        db.create_collection(COSMOS_DB_COLLECTION_NAME)
        print("Created collection '{}'.\n".format(COSMOS_DB_COLLECTION_NAME))
    else:
        print("Using collection: '{}'.\n".format(COSMOS_DB_COLLECTION_NAME))

    # Check if vector search index exists, create if it doesn't
    collection = db[COSMOS_DB_COLLECTION_NAME]
    indexes = collection.list_indexes()
    vector_index_exists = any("embedding" in idx.get("key", {}) for idx in indexes)

    if not vector_index_exists:
        ## Create the vector index
        # **IMPORTANT**: You can create only one index per vector property.
        # The HNSW index is available only for M50 and higher cluster tiers.
        # The IVF index does not support a 3072 embedding size, which is required by text-embedding-3-large model.
        collection.drop_indexes()
        db.command(
            {
                "createIndexes": COSMOS_DB_COLLECTION_NAME,
                "indexes": [
                    {
                        "name": "VectorSearchIndex",
                        "key": {"embedding": "cosmosSearch"},
                        "cosmosSearchOptions": {
                            "kind": "vector-ivf",
                            "numLists": 1,
                            "similarity": "COS",  # Ensure similarity metric is valid
                            "dimensions": 1536,
                        },
                    }
                ],
            }
        )

    return collection


def search_embeddings_enn(collection, query_embedding, top_k=2):
    """
    Search for similar embeddings using Exact Nearest Neighbor (ENN) search.
    https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/vcore/vector-search
    """
    pipeline = [
        {
            "$search": {
                "cosmosSearch": {
                    "vector": query_embedding,
                    "exact": True,  # Enable Exact Nearest neighbor search
                    "path": "embedding",
                    "k": top_k,  # , #, "efsearch": 40 # optional for HNSW only
                    # "filter": {"title": {"$ne": "Azure Cosmos DB"}}
                },
                "returnStoredSource": True,
            }
        }
    ]
    results = list(collection.aggregate(pipeline))
    return results


def store_embedding(collection, doc_id, text, embedding):
    """Store a document with its embedding in the database"""
    document = {"id": doc_id, "text": text, "embedding": embedding}
    collection.insert_one(document)


def main(first_run=False):
    try:
        # Initialize clients
        openai_client = init_openai_client()
        cosmos_client = init_cosmos_client()
        # Ensure database and container exist
        collection = ensure_database_and_container(cosmos_client)

        if first_run:
            # Example usage: Store embeddings
            text1 = "The quick brown fox jumps over the lazy dog."
            text2 = "A fast auburn canine leaps above the idle hound."
            text3 = "Scientists discover new galaxy in deep space."

            embedding1 = generate_embedding(openai_client, text1)
            embedding2 = generate_embedding(openai_client, text2)
            embedding3 = generate_embedding(openai_client, text3)

            store_embedding(collection, "doc1", text1, embedding1)
            store_embedding(collection, "doc2", text2, embedding2)
            store_embedding(collection, "doc3", text3, embedding3)

            print("Embeddings stored successfully.")

        # Example usage: Search for similar embeddings
        query_text = "The space shuttle launches into orbit."
        query_embedding = generate_embedding(openai_client, query_text)

        # Use ENN search for exact matches
        print(f"\nENN search results for: '{query_text}'")
        vector_results = search_embeddings_enn(collection, query_embedding)
        for result in vector_results:
            search_result = dict(result)
            print(f"{search_result['id']}: {search_result['text']}")
            # print(f"Embedding: {search_result['embedding']}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
