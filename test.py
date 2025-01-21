from openai import OpenAI
import os


API_KEY = os.environ.get('OPENAI_API_KEY', None)
MODEL = "gpt-3.5-turbo"

client = OpenAI(api_key=API_KEY)
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant. Create a detailed plan to achieve the given goal, breaking it down into actionable steps with a timeline. Make sure the plan is practical and achievable, including daily or weekly tasks, milestones, and any additional tips or resources that might be helpful. \
            Give me the output in JSON format with goal as a key and the plan/steps as sub-keys."},
        {"role": "user", "content": "meet Dhimant"}
    ]
)

print("Assistant: " + response.choices[0].message.content)