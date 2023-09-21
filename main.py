import openai
import json

# Open the file for reading
with open('keys.json', 'r') as f:
    keys = json.load(f)
    openai.api_key = keys["openai_key"]

with open('a.csv', 'r') as f:
    lines = f.readlines()

lines = [line.strip() for line in lines]
lines = [line.replace(",", "") for line in lines]
lines = [line for line in lines if line.strip()]
lines = [line for line in lines if line.find("park") < 0]


batch_size = 20
res = []

for i in range(0, len(lines), batch_size):
    batch = lines[i:i + batch_size]
    print(f"working on records {i} to {i+batch_size}")
    text = "\n".join(batch)
    the_message = [{"role": "user", "content": text}, ]
    the_message.insert(0, {"role": "system",
                           "content": "for each line in the following text, i need exactly one line output with the following comma-separated format: short summary in english of the issue, classification label. the label should be one of the following: mechanical, electrical, clean up, dangerous, operational. the operational label should capture anything related to a device not working as expected or temperature change"},
                       )

    chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=the_message, temperature=0)
    res.append(chat_completion['choices'][0]['message']['content'])



with open("res3.txt", "w") as f:
    f.write("\n".join(res))
