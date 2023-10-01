from deep_translator import GoogleTranslator
from auto_gptq import AutoGPTQForCausalLM
from transformers import AutoTokenizer
from transformers import TextGenerationPipeline


model = AutoGPTQForCausalLM.from_quantized("TheBloke/Pygmalion-2-13B-GPTQ",device="cuda:0",use_safetensors=True)
tokenizer = AutoTokenizer.from_pretrained("TheBloke/Pygmalion-2-13B-GPTQ")

pipe = TextGenerationPipeline(model=model,tokenizer=tokenizer)

translate_to_ru = GoogleTranslator(source='en', target='ru')
translate_to_en = GoogleTranslator(source='ru', target='en')



class Autogptq_sampler:
    def __init__(self):
        self.models = ["TheBloke/Pygmalion-2-13B-GPTQ"]
        pass

    def sample(self,prompt_,memory):
        prompt = translate_to_en.translate(f"{memory}\n{prompt_}")
        generated = pipe(prompt,top_p=0.95,repetition_penalty=1.20,temperature=0.8,max_new_tokens=200,min_length=50,do_sample=True,return_full_text=False)[0]["generated_text"]
        return translate_to_ru.translate(generated)