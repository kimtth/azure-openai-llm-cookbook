from scrapegraphai.graphs import SmartScraperGraph

def main():
    print("Web Scrapping AI Agent 🕵️‍♂️")
    print("This app allows you to scrape a website using OpenAI API")

    # Get OpenAI API key from user
    openai_access_token = input("Enter your OpenAI API Key: ")
    
    if openai_access_token:
        # Using only gpt-4 model
        graph_config = {
            "llm": {
                "api_key": openai_access_token,
                "model": "gpt-4",
            },
        }
        
        # Get the URL of the website to scrape
        url = input("Enter the URL of the website you want to scrape: ")
        
        # Get the user prompt
        user_prompt = input("What do you want the AI agent to scrape from the website? ")
        
        # Create a SmartScraperGraph object
        smart_scraper_graph = SmartScraperGraph(
            prompt=user_prompt,
            source=url,
            config=graph_config
        )
        
        # Scrape the website
        print("Scraping... Please wait.")
        result = smart_scraper_graph.run()
        print("\nResults:")
        print(result)

if __name__ == "__main__":
    main()