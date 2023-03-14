import openai
openai.api_key = "your_key"

compoletion = openai.ChatCompletion.create(
    model ="gpt-3.5-turbo",
    messages = [{"role" : "user", "content" : "tell me a joke"}]
    )

print(compoletion)

answer = compoletion.choices[0].message.content
print(answer)
