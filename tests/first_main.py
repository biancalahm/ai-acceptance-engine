from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3.1")

prompt = """ Porque a terra é redonda? """

response = model.invoke(prompt)

print(response)