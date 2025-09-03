import os
import requests

class AKGPT:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('AKGPT_API_KEY')
        if not self.api_key:
            raise ValueError("API key not provided. Please pass it as an argument or set the AKGPT_API_KEY environment variable.")
        self.base_url = "https://api.your-service.com/v1/"

    def query(self, model, prompt, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "prompt": prompt,
            **kwargs
        }
        try:
            response = requests.post(f"{self.base_url}completions", headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}")
            return None

# Пример использования (для демонстрации, не будет частью финальной библиотеки)
if __name__ == "__main__":
    # Для тестирования, установите переменную окружения AKGPT_API_KEY
    # export AKGPT_API_KEY="your_secret_api_key"
    # или передайте ключ напрямую:
    # client = AKGPT(api_key="your_secret_api_key")

    try:
        client = AKGPT()
        result = client.query("text-davinci-003", "Hello, how are you?", temperature=0.7)
        if result:
            print("API Response:", result)
    except ValueError as e:
        print(e)


