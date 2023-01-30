import os
import openai
import config
from typing import Dict, Tuple

openai.api_key = config.OPEN_AI_API_KEY


def make_ai_prompt(data: Dict[str, str]) -> str:
    prompt = f"Write creative sell {data['offer-type']} offer:\r\n" \
             f"Product: {data['offer-name']}\r\n" \
             f"Description: {data['description']}\r\n"
    seed_words = data.get("seed-words", False)
    location = data.get("location", False)
    result = data.get("result", False)

    if seed_words:
        prompt += f"Seed-words: {seed_words}"
    if location:
        prompt += f"Location: {location}"

    if result:
        prompt += f"Expected effects for client: {result}"
    return prompt


def generate_ai_text(prompt: str):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=0,
        max_tokens=2000,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response['choices'][0]['text']


if __name__ == '__main__':
    data = {'offer-type': 'short', 'offer-name': 'Chocolate cakes', 'description': 'Homemade bakery',
            'seed-words': 'tasty, organic, sweet', 'location': 'Goa', 'result': 'good mood'}
    prompt = make_ai_prompt(data)
    print(generate_ai_text(prompt))
