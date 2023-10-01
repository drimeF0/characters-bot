from deep_translator import GoogleTranslator
import requests
import time
from config import KOBOLDAI_DEFAULT_MODELS


translate_to_ru = GoogleTranslator(source='en', target='ru')
translate_to_en = GoogleTranslator(source='ru', target='en')


headers_post = {
    "Client-Agent":"KoboldAiLite:17",
    "Accept-Language":"ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    'Accept': '*/*',
    "Host":"horde.koboldai.net",
    "Origin":"https://lite.koboldai.net",
    "Referer":"https://lite.koboldai.net/",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    'Content-Type': 'application/json',
    'apikey': '0000000000',
    'Client-Agent': 'KoboldAiLite:2',
    'Connection': 'keep-alive',
}

headers_get = {
    "Client-Agent":"KoboldAiLite:17",
    "Accept-Language":"ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    'Accept': '*/*',
    "Host":"horde.koboldai.net",
    "Origin":"https://lite.koboldai.net",
    "Referer":"https://lite.koboldai.net/",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/114.0",
    'Content-Type': 'application/json',
    'apikey': '0000000000',
    'Client-Agent': 'KoboldAiLite:2',
    'Connection': 'keep-alive',
}


class kobold_sampler:
    
    def __init__(self,models=None):
        self.params = {
        'n': 1,
        'max_context_length':2048,
        'max_length': 80,
        'rep_pen': 1.10,
        'temperature': 0.7,
        'top_p': 0.95,
        'top_k': 0,
        'top_a': 0,
        'typical': 1,
        'tfs': 1,
        'rep_pen_range': 1024,
        'rep_pen_slope': 0.7,
        'sampler_order': [0,1,2,3,4,5,6,],
        }
        self.models = models if models else KOBOLDAI_DEFAULT_MODELS
    
    
    def sample(self,prompt_,memory):
        prompt = translate_to_en.translate(prompt_)
        memory = translate_to_en.translate(memory)
        generate_request = {
        'prompt': f"{memory}\n{prompt}",
        'params': self.params,
        'models': self.models,
        'workers': [],
        }
        response = requests.post('https://horde.koboldai.net/api/v2/generate/text/async', headers=headers_post, json=generate_request)
        response_id = response.json().get("id")
        
        for i in range(120):
            time.sleep(1)
            generated = self.get(response_id)
            if generated:
                return translate_to_ru.translate(generated)
            
            
    
    def get(self,response_id):
        if response_id == None:
            return "response id is None"
        response = requests.get(
        f'https://horde.koboldai.net/api/v2/generate/text/status/{response_id}',
        headers=headers_get,
        )
        
        try:
            response = response.json()
        except:
            return f"response status: {response}"
        
        if response["faulted"] == True:
            return "Faulted response"
        if response["done"] == True and len(response["generations"]):
            return response["generations"][0]["text"]