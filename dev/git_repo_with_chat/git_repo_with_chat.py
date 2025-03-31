import os
import tempfile
import numpy as np
from typing import List, Dict, Any
from gitingest import ingest  # Keeping this for GitHub repo ingestion
from openai import AzureOpenAI


# Azure OpenAI configuration
AZURE_OPENAI_API_KEY = "your-api-key"  # Replace with your OpenAI API key
AZURE_OPENAI_EMBED_MODEL_NAME = "your-model-name"  # Embed model for text embeddings
AZURE_OPENAI_CHAT_MODEL_NAME = "your-model-name"  # Chat model for conversation
AZURE_OPENAI_API_VERSION = "your-api-version"  # API version for OpenAI
AZURE_OPENAI_ENDPOINT = "your-endpoint"  # Azure endpoint for OpenAI


class Document:
    """Simple document class to store text chunks and their embeddings"""

    def __init__(self, text: str, metadata: Dict[str, Any] = None):
        self.text = text
        self.metadata = metadata or {}
        self.embedding = None


class GitHubRepoProcessor:
    """Process GitHub repositories and enable chat interaction using Azure OpenAI"""

    def __init__(self):
        self.client = AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
        )
        self.repositories = {}
        self.messages = []

    def process_repository(self, github_url: str) -> bool:
        """Process a GitHub repository and prepare it for querying"""
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                print(f"Processing repository: {github_url}")
                repo_name = github_url.split("/")[-1]

                # Use the existing gitingest function to get repository content
                summary, tree, content = ingest(github_url)

                # Write content to a file for reference (optional)
                content_path = os.path.join(temp_dir, f"{repo_name}_content.md")
                with open(content_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Process the content into chunks
                documents = self._chunk_content(content, github_url)

                # Generate embeddings for all documents
                self._generate_embeddings(documents)

                # Store the documents for this repository
                self.repositories[github_url] = documents

                return True
        except Exception as e:
            print(f"Error processing repository: {str(e)}")
            return False

    def _chunk_content(
        self, content: str, source: str, chunk_size: int = 1000
    ) -> List[Document]:
        """Split content into manageable chunks"""
        documents = []

        # Simple paragraph-based chunking
        paragraphs = content.split("\n\n")

        current_chunk = ""
        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                # Create document from current chunk
                doc = Document(text=current_chunk, metadata={"source": source})
                documents.append(doc)
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        # Add the last chunk if not empty
        if current_chunk:
            doc = Document(text=current_chunk, metadata={"source": source})
            documents.append(doc)

        return documents

    def _generate_embeddings(self, documents: List[Document]):
        """Generate embeddings for a list of documents using Azure OpenAI"""
        for i in range(0, len(documents), 20):  # Process in batches of 20
            batch = documents[i : i + 20]
            texts = [doc.text for doc in batch]

            response = self.client.embeddings.create(
                input=texts, model=AZURE_OPENAI_EMBED_MODEL_NAME
            )

            for j, doc in enumerate(batch):
                doc.embedding = response.data[j].embedding

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        a_array = np.array(a)
        b_array = np.array(b)
        return np.dot(a_array, b_array) / (
            np.linalg.norm(a_array) * np.linalg.norm(b_array)
        )

    def _search_documents(
        self, query: str, github_url: str, top_k: int = 5
    ) -> List[Document]:
        """Search for relevant documents based on embedding similarity"""
        if github_url not in self.repositories:
            return []

        # Get query embedding
        query_response = self.client.embeddings.create(
            input=[query], model=AZURE_OPENAI_EMBED_MODEL_NAME
        )
        query_embedding = query_response.data[0].embedding

        # Calculate similarity scores
        documents = self.repositories[github_url]
        similarities = []

        for doc in documents:
            similarity = self._cosine_similarity(query_embedding, doc.embedding)
            similarities.append((doc, similarity))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top k documents
        return [doc for doc, _ in similarities[:top_k]]

    def clear_chat(self):
        """Reset the chat history"""
        self.messages = []

    def chat(self, query: str, github_url: str) -> str:
        """Chat with the repository using RAG approach"""
        if github_url not in self.repositories:
            return "Please load a repository first."

        # Add user message to history
        self.messages.append({"role": "user", "content": query})

        # Retrieve relevant documents
        relevant_docs = self._search_documents(query, github_url)

        if not relevant_docs:
            response = "No relevant information found in the repository."
            self.messages.append({"role": "assistant", "content": response})
            return response

        # Prepare context from retrieved documents
        context_str = "\n\n".join([doc.text for doc in relevant_docs])

        # Create prompt
        system_message = (
            "You are an AI assistant that helps users understand GitHub repositories. "
            "Answer questions based on the provided context information. "
            "If you don't know the answer, say 'I don't know!'"
        )

        user_prompt = (
            "Context information is below.\n"
            "---------------------\n"
            f"{context_str}\n"
            "---------------------\n"
            "Given the context information above I want you to think step by step to answer the query in a "
            "highly precise and crisp manner focused on the final answer, in case you don't know the answer say 'I don't know!'.\n"
            f"Query: {query}\n"
            "Answer: "
        )

        # Call Azure OpenAI
        completion = self.client.chat.completions.create(
            model=AZURE_OPENAI_CHAT_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=800,
        )

        response = completion.choices[0].message.content

        # Add assistant response to history
        self.messages.append({"role": "assistant", "content": response})

        return response


# Example usage (command-line interface)
def main():
    processor = GitHubRepoProcessor()

    print("GitHub Repository Chat")
    github_url = input("Enter GitHub repository URL: ")

    print("Processing repository...")
    success = processor.process_repository(github_url)

    if not success:
        print("Failed to process repository.")
        return

    print(
        "Repository processed. Start chatting! (type 'exit' to quit, 'clear' to clear chat history)"
    )

    while True:
        query = input("\nYou: ")

        if query.lower() == "exit":
            break
        elif query.lower() == "clear":
            processor.clear_chat()
            print("Chat history cleared.")
            continue

        response = processor.chat(query, github_url)
        print(f"\nAssistant: {response}")


if __name__ == "__main__":
    main()

