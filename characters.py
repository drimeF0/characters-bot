#from sampler_kobold import koboldAI_sampler
#from sampler_autogptq import Autogptq_sampler
from sampler_petals import Petals_sampler
from utils import FixedSizeArray
import os
import json
import prompt_manager

class MessagesContext:

    def __init__(self,max_size):
        self.fixed_size_array = FixedSizeArray(max_size=max_size)
    
    def __str__(self):
        result = "\n".join(self.fixed_size_array.arr)
        return result
    
    def append(self,message,name):
        self.fixed_size_array.append(f"{name}: {message}")

class Character:
    
    def __init__(self,character_name,character_config,character_hello_message,max_context_messages=10):
        self.config = character_config
        self.name = character_name
        self.hello_message = character_hello_message


        
        self.context = MessagesContext(max_context_messages)
        self.context.append(self.hello_message,self.name)
        self.sampler = Petals_sampler()
        self.starter_prompt = prompt_manager.get(self.sampler.models)().get(self.config,self.name)
        
    
    def append_message(self,message_text,username):
        self.context.append(message_text,username)

    
    
        
    def get_reply(self):
        context = str(self.context)
        r = f"{context}\n{self.name}: "


        generated = self.sampler.sample(r,self.starter_prompt)
        
        if not generated:
            return
        
        generated_first_reply = generated.split("\n")[0]
        
        
        self.context.append(generated_first_reply,self.name)
        
        return f"{generated_first_reply}"
    

class CharacterFileManager:
    def from_json(self,json_file_dest):
        with open(json_file_dest) as f:
            settings = json.load(f)
        character_name,character_config,character_hello_message = settings["name"],settings["config"],settings["hello_message"]
        
        return Character(character_name,character_config,character_hello_message)
    
    def to_json(self,character,directory):
        save_name = character.name
        json_file_dest = f"{directory}{save_name}.json"
        with open(json_file_dest,"w") as f:
            settings = {"name":character.name,
                        "config":character.config,
                        "hello_message":character.hello_message,
                        }
            json.dump(settings,f)


def load_characters(dir):
    characters = {}
    manager = CharacterFileManager()
    for file in os.listdir(dir):
        try:
            character_temp = manager.from_json(f"{dir}{file}")
        except:# (IsADirectoryError,KeyError):
            continue
        characters[character_temp.name] = character_temp
    return characters

if __name__  == "__main__":
    koboldGPT = Character("KoboldGPT","""
KoboldGPT is a state-of-the-art Artificial General Intelligence. You may ask any question, or request any task, and KoboldGPT will always be able to respond accurately and truthfully
""","Hello, I am KoboldGPT, your personal AI assistant. What would you like to know?")
    #print(koboldGPT._getlog("who is chatters?"))
    koboldGPT.append_message("who are you","drime")
    koboldGPT.get_reply("","drime")