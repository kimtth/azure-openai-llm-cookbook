import requests
from mem0 import Memory
from openai import OpenAI

class ArxivResearchAgent:
    def __init__(self, openai_api_key):
        config = {
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                    "temperature": 0.2,
                    "max_tokens": 1500,
                },
            },
            "vector_store": {
                "provider": "chroma",
                "config": {
                    "collection_name": "demo",
                    "path": "db",
                },
            },
        }
        self.memory = Memory.from_config(config)
        self.openai_client = OpenAI(api_key=openai_api_key)

    def search_arxiv(self, query):
        url = f"https://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results=5"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error fetching data from arXiv: {e}"

    def process_with_gpt4(self, result, context=""):
        prompt = f"""
Based on the following arXiv search result and context, provide a structured markdown output:
Context: {context}
Search Result: {result}
Format: Table columns = Title, Authors, Abstract, Link
"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            if not response.choices or len(response.choices) == 0:
                return "No response from OpenAI API."
            return response.choices[0].message.content
        except Exception as e:
            return f"Error processing with GPT-4: {e}"

    def search_papers(self, search_query, user_id):
        try:
            relevant_memories = self.memory.search(search_query, user_id=user_id, limit=3)
        except Exception as e:
            relevant_memories = []
        context = " ".join(mem.get("text", "") for mem in relevant_memories)
        search_results = self.search_arxiv(search_query)
        return self.process_with_gpt4(search_results, context)

    def get_all_memories(self, user_id):
        try:
            memories = self.memory.get_all(user_id=user_id)
            return [mem.get("text", "") for mem in memories]
        except Exception as e:
            return [f"Error retrieving memory: {e}"]

if __name__ == "__main__":
    try:
        openai_api_key = input("Enter your OpenAI API Key: ")
        agent = ArxivResearchAgent(openai_api_key)
        user_id = input("Enter your Username: ")
        search_query = input("Research paper search query: ")
        print("\nSearch Results:")
        print(agent.search_papers(search_query, user_id))
        if input("\nView memory? (y/n): ").lower() == "y":
            for memory in agent.get_all_memories(user_id):
                print(f"- {memory}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
