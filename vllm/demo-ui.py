import streamlit as st
import openai
import base64

# Set the title for the Streamlit app
st.title("vLLM Demo App")

# Create a text area for user input
prompt = st.text_area("Enter your prompt:", height=150)
image = st.file_uploader("Upload a .jpg", type=["jpg","jpeg"])


client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="null"  # API key is not used by vLLM but is required by the client
)

# Print the response
# Create a button to trigger the API call
if st.button("Generate Response"):
    if prompt:
        imageData = base64.b64encode(image.getvalue()).decode('utf-8')
       
        with st.spinner("Generating..."):
            response = client.chat.completions.create(
              model="/huggingface/ibm-granite/granite-vision-3.2-2b",
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
                            "image_url": {"url":f"data:image/jpeg;base64,{imageData}"},
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ]
                }
              ]
            )

            response = response.choices[0].message.content

        # Display the model's response
        print(response)
        st.write("### Model Response")
        st.write(response)
