import asyncio
import os
from openai import AsyncOpenAI, OpenAI

# Define the models
reference_models = ["gpt-4-turbo", "gpt-4", "gpt-4o"]
aggregator_model = "gpt-4o"  # Aggregator model for response synthesis

# Define the aggregator system prompt
aggregator_system_prompt = """
You have been provided with a set of responses 
from various models to the latest user query. 
Your task is to synthesize these responses into a single, 
high-quality response. It is crucial to critically evaluate the information 
provided in these responses, recognizing that some of it may be biased or incorrect. 
Your response should not simply replicate the given answers but should offer a refined, accurate, 
and comprehensive reply to the instruction. Ensure your response is well-structured, coherent, 
and adheres to the highest standards of accuracy and reliability. Responses from models:
"""


async def run_llm(client, model, user_prompt):
    """Run a single LLM call with a reference model."""
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.7,
            max_tokens=512,
        )
        return model, response.choices.message.content
    except Exception as e:
        print(f"Error with model {model}: {e}")
        return model, None


async def process_question(user_prompt, api_key):
    """Process a user question through multiple models and aggregate the responses."""
    client = AsyncOpenAI(api_key=api_key)
    sync_client = OpenAI(api_key=api_key)

    print("Getting responses from individual models...")
    tasks = [run_llm(client, model, user_prompt) for model in reference_models]
    results = await asyncio.gather(*tasks)

    # Display individual model responses
    print("\n--- Individual Model Responses ---")
    for model, response in results:
        if response:
            print(f"\n### Response from {model} ###")
            print(response)
            print("\n" + "-" * 50)

    # Aggregate responses
    print("\n--- Aggregated Response ---")
    response_texts = [response for _, response in results if response]
    final_response = sync_client.chat.completions.create(
        model=aggregator_model,
        messages=[
            {"role": "system", "content": aggregator_system_prompt},
            {"role": "user", "content": "\n\n".join(response_texts)},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    print(final_response.choices.message.content)
    return {
        "individual_responses": {
            model: response for model, response in results if response
        },
        "aggregated_response": final_response.choices.message.content,
    }


def main():
    """Main function to run the mixture-of-agents application."""
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "API key not found. Please set the OPENAI_API_KEY environment variable."
        )

    # Get the user's question
    user_prompt = "What is the capital of France?"  # Example prompt

    # Process the question
    if user_prompt:
        result = asyncio.run(process_question(user_prompt, api_key))
        return result
    else:
        print("Please enter a question.")
        return None


if __name__ == "__main__":
    print("Mixture-of-Agents LLM Application")
    print("--------------------------------")
    print(
        "This app sends your question to multiple OpenAI models and aggregates their responses."
    )
    main()
