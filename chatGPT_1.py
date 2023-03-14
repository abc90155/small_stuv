import openai
openai.api_key = "your_key"

response = openai.Completion.create(
    engine = "text-davinci-003",
    prompt = "tell me a joke",
    max_tokens = 32,
    temperature = 1,
    top_p = 0.75,
    n = 1,
)

answer = response["choices"][0]["text"]

print(answer)