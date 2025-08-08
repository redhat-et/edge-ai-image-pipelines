import openai

# Point the client to your local vLLM server
client = openai.OpenAI(
    base_url="http://server:8000/v1",
    api_key="vllm"  # API key is not used by vLLM but is required by the client
)

# Call the chat completions endpoint
completion = client.chat.completions.create(
  model="/share/granite",
  messages=[
    {
        "role": "system", 
        "content": "You are a helpful assistant."
    },
    {
        "role": "user", 
        "content": [
            {
                "type": "image_url",
                "image_url": {"url":"https://cataas.com/cat"}
            },
            {
                "type": "text",
                "text": "Describe the provided image"
            },
        ]
    }
  ]
)

# Print the response
print(completion.choices[0].message.content)
