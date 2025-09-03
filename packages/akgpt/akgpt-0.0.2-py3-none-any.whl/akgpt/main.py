import os
import requests
import json

class AKGPT:
    def __init__(self, api_key=None):
        # API ключ не требуется для fullai.vercel.app, но оставлен для общей гибкости
        self.api_key = api_key or os.getenv('AKGPT_API_KEY')
        self.base_url = "https://fullai.vercel.app"

    def query(self, model, prompt, **kwargs):
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]

        payload = {
            "model": model,
            "messages": messages,
            **kwargs
        }

        try:
            response = requests.post(f"{self.base_url}/chat", headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None

    def get_models(self):
        try:
            response = requests.get(f"{self.base_url}/models")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting models: {e}")
            return None

# Пример использования (для демонстрации, не будет частью финальной библиотеки)
if __name__ == "__main__":
    # Для тестирования, установите переменную окружения AKGPT_API_KEY (если требуется для другого API)
    # export AKGPT_API_KEY="your_secret_api_key"

    client = AKGPT()

    print("\n--- Доступные модели ---")
    models = client.get_models()
    if models:
        for model_info in models:
            print(f"- {model_info['name']} ({model_info['description']})")

    print("\n--- Тестовый запрос к модели deepseek ---")
    try:
        # Пример текстового запроса
        result = client.query("deepseek", "Привет! Как дела?")
        if result:
            print("API Response:", json.dumps(result, indent=2, ensure_ascii=False))

        print("\n--- Тестовый запрос к модели gpt-5-nano с параметрами ---")
        # Пример запроса с дополнительными параметрами (temperature, max_tokens)
        result_gpt = client.query("gpt-5-nano", "Напиши короткий рассказ о роботе, который учится рисовать.", temperature=0.7, max_tokens=150)
        if result_gpt:
            print("API Response:", json.dumps(result_gpt, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")


