import os
import requests
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

# Retrieve and check required environment variables
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL")
BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY")

if not all([AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_MODEL]):
    raise ValueError("Missing one or more Azure OpenAI environment variables.")
if not BING_SUBSCRIPTION_KEY:
    raise ValueError("Missing Bing subscription key environment variable.")

# Configure OpenAI to use Azure OpenAI
openai.api_type = "azure"
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = AZURE_OPENAI_API_VERSION

# Bing Search API URL
BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/search"

def search_bing(query, count=5):
    """
    Search the web using Bing Search API.
    """
    headers = {"Ocp-Apim-Subscription-Key": BING_SUBSCRIPTION_KEY}
    params = {"q": query, "count": count, "responseFilter": "Webpages"}
    
    response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    
    # Extract and format search results
    formatted_results = []
    if "webPages" in search_results and "value" in search_results["webPages"]:
        for result in search_results["webPages"]["value"]:
            formatted_results.append({
                "title": result.get("name"),
                "url": result.get("url"),
                "snippet": result.get("snippet")
            })
    
    return formatted_results

def web_search_agent(user_query):
    """
    Agent that uses Azure OpenAI with grounding from Bing Search.
    """
    # Step 1: Determine if a web search is needed
    system_message = (
        "You are a helpful assistant that determines if a web search is needed to answer a question. "
        "Respond with 'Yes' if a search is needed, and 'No' if the question can be answered without searching the web."
    )
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": f"Do I need to search the web to answer this question: {user_query}?"}
    ]
    
    search_decision = openai.ChatCompletion.create(
        model=AZURE_OPENAI_MODEL,
        messages=messages,
        temperature=0
    )
    
    decision_text = search_decision.choices[0].message.content.lower()
    need_search = "yes" in decision_text
    
    # Step 2: Prepare messages based on whether a web search is needed
    if need_search:
        # Perform web search
        search_results = search_bing(user_query)
        
        # Build context with search results
        context = "Here are some search results that might help:\n\n"
        for i, result in enumerate(search_results, 1):
            context += f"{i}. {result['title']}\n"
            context += f"   URL: {result['url']}\n"
            context += f"   {result['snippet']}\n\n"
        
        system_prompt = (
            "You are a helpful assistant that answers questions based on web search results. "
            "Use the provided search results to ground your answer. If the search results don't contain "
            "relevant information, acknowledge the limitations of your knowledge. Always cite your sources."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Question: {user_query}\n\nSearch results: {context}"}
        ]
    else:
        # Answer without a web search
        system_prompt = (
            "You are a helpful assistant that answers questions based on your knowledge. "
            "If you don't know the answer, suggest that a web search might be helpful."
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
    
    # Generate final answer using Azure OpenAI
    response = openai.ChatCompletion.create(
        model=AZURE_OPENAI_MODEL,
        messages=messages,
        temperature=0.7
    )
    
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Web Search Agent (powered by Azure OpenAI and Bing)")
    print("Type 'exit' to quit\n")
    
    while True:
        user_input = input("\nWhat would you like to know? ")
        if user_input.lower() in ["exit", "quit"]:
            break
        
        try:
            answer = web_search_agent(user_input)
            print(f"\nAgent: {answer}")
        except Exception as e:
            print(f"\nError: {str(e)}")
