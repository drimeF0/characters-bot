from deep_translator import GoogleTranslator
from transformers import AutoTokenizer
from petals import AutoDistributedModelForCausalLM
from transformers import TextGenerationPipeline
import torch

translate_to_ru = GoogleTranslator(source='en', target='ru')
translate_to_en = GoogleTranslator(source='ru', target='en')
models = "petals-team/StableBeluga2"
model = AutoDistributedModelForCausalLM.from_pretrained(models,dtype=torch.half)
tokenizer = AutoTokenizer.from_pretrained(models)

pipe = TextGenerationPipeline(model=model,tokenizer=tokenizer)

class Petals_sampler:
    
    def __init__(self):
        self.models = models

    
    
    def sample(self,prompt_,memory):
        prompt = translate_to_en.translate(f"{memory}\n{prompt_}")
        generated = pipe(prompt,top_p=0.9,repetition_penalty=1.20,temperature=0.6,max_new_tokens=200,min_length=20,do_sample=True,return_full_text=False)[0]["generated_text"]
        return translate_to_ru.translate(generated)