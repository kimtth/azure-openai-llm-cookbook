import os
from routellm.controller import Controller

os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

# Initialize RouteLLM client
client = Controller(
    routers=["mf"],
    strong_model="gpt-4o-mini",
    weak_model="gpt-4o",
)


# Example function to use the router
def get_llm_response(prompt):
    response = client.chat.completions.create(
        model="router-mf-0.11593", messages=[{"role": "user", "content": prompt}]
    )
    message_content = response["choices"][0]["message"]["content"]
    model_name = response["model"]
    return message_content, model_name


# Example usage
if __name__ == "__main__":
    prompt = "What is your message?"
    message, model = get_llm_response(prompt)
    print(f"User: {prompt}")
    print(f"AI ({model}): {message}")
