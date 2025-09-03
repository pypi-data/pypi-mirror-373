import os
import requests
import json
import urllib.parse

class AKGPT:
    def __init__(self):
        self.base_url = "https://text.pollinations.ai"

    def query(self, prompt, model=None, seed=None, temperature=None, top_p=None, presence_penalty=None, frequency_penalty=None, json_response=False, system=None, stream=False, private=False, referrer=None):
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"{self.base_url}/{encoded_prompt}"

        params = {}
        if model: params["model"] = model
        if seed: params["seed"] = seed
        if temperature: params["temperature"] = temperature
        if top_p: params["top_p"] = top_p
        if presence_penalty: params["presence_penalty"] = presence_penalty
        if frequency_penalty: params["frequency_penalty"] = frequency_penalty
        if json_response: params["json"] = "true"
        if system: params["system"] = system
        if stream: params["stream"] = "true"
        if private: params["private"] = "true"
        if referrer: params["referrer"] = referrer

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            if json_response:
                return response.json()
            else:
                return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None

# Пример использования
if __name__ == "__main__":
    client = AKGPT()

    print("\n--- Тестовый запрос: Что такое искусственный интеллект? ---")
    result = client.query("Что такое искусственный интеллект?")
    if result:
        print("Ответ API:", result)

    print("\n--- Тестовый запрос с параметрами: Короткое стихотворение о роботах ---")
    result_poem = client.query("Напиши короткое стихотворение о роботах", model="mistral", seed=123, system="Ты поэт")
    if result_poem:
        print("Ответ API:", result_poem)

    print("\n--- Тестовый запрос с JSON ответом: Что такое AI? ---")
    result_json = client.query("Что такое AI?", json_response=True)
    if result_json:
        print("Ответ API (JSON):", json.dumps(result_json, indent=2, ensure_ascii=False))


