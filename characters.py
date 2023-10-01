from sampler_kobold import kobold_sampler
#from sampler_autogptq import Autogptq_sampler
#from sampler_petals import Petals_sampler
from utils import FixedSizeArray
import os
import json
import prompt_manager

class UserMessage:

    def __init__(self,message_text,username):
        self.message_text = message_text
        self.username = username
    
    def __str__(self):
        return f"<|user|>{self.username}: {self.message_text}"

    def __repl__(self):
        return f"<|user|>{self.username}: {self.message_text}"


class ModelMessage:

    def __init__(self,message_text,username):
        self.message_text = message_text
        self.username = username
    
    def __str__(self):
        return f"<|model|>{self.username}: {self.message_text}"

    def __repl__(self):
        return f"<|model|>{self.username}: {self.message_text}"


class MessagesContext:

    def __init__(self,max_size):
        self.fixed_size_array = FixedSizeArray(max_size=max_size)
    
    def __str__(self):
        result = "\n".join(map(str,self.fixed_size_array.arr))
        return result
    
    def append(self,message):
        self.fixed_size_array.append(message)
    
    def clear(self):
        self.fixed_size_array.clear()


class Character:
    
    def __init__(self,character_name,character_config,character_hello_message,max_context_messages=10):
        self.config = character_config
        self.name = character_name
        self.hello_message = ModelMessage(character_hello_message,self.name)


        
        self.context = MessagesContext(max_context_messages)
        self.sampler = kobold_sampler()
        starter_prompt_class = prompt_manager.get(self.sampler.models)()
        print(f"name: {self.name} selects {type(starter_prompt_class)}")
        self.starter_prompt = starter_prompt_class.get(self.config,self.name)
        self.clear_context()
        
    
    def append_message(self,message_text,username):
        msg = UserMessage(message_text,username)
        self.context.append(msg)
    
    def clear_context(self):
        self.context.clear()
        self.context.append(self.hello_message)
    
    def random_hello_message(self):
        self.context.clear()
        to_generate = f"<|model|>{self.name}: "
        generated = self.sampler.sample(to_generate,self.starter_prompt)
        generated_hello_message = generated.split("\n")[0]
        generated_hello_message = generated_hello_message.split("<|user|>")[0]
        tmp_helo_message = ModelMessage(generated_hello_message,self.name)
        self.context.append(tmp_helo_message)
        return generated_hello_message
    
    def impersonate(self,username):
        context = str(self.context)
        to_generate = f"{context}\n<|user|>{username}: "
        generated = self.sampler.sample(to_generate,self.starter_prompt)
        user_fake_message = generated.split("\n")[0]
        user_fake_message = user_fake_message.split("<|model|>")[0]
        return user_fake_message


    
    
        
    def get_reply(self):
        context = str(self.context)
        r = f"{context}\n<|model|>{self.name}: "


        generated = self.sampler.sample(r,self.starter_prompt)
        
        if not generated:
            return
        
        generated_first_reply = generated.split("\n")[0]
        generated_first_reply = generated_first_reply.split("<|user|>")[0]
        
        msg = ModelMessage(generated_first_reply,self.name)
        self.context.append(msg)
        
        return f"{generated_first_reply}"
    

class CharacterFileManager:
    def load(self,json_file_dest):
        with open(json_file_dest) as f:
            settings = json.load(f)
        character_name,character_config,character_hello_message = settings["name"],settings["config"],settings["hello_message"]
        
        return Character(character_name,character_config,character_hello_message)
    
    def save(self,character,directory):
        save_name = character.name
        json_file_dest = f"{directory}{save_name}.json"
        with open(json_file_dest,"w") as f:
            settings = {"name":character.name,
                        "config":character.config,
                        "hello_message":character.hello_message.message_text,
                        }
            json.dump(settings,f)


def load_characters(dir):
    characters = {}
    manager = CharacterFileManager()
    for file in os.listdir(dir):
        try:
            character_temp = manager.load(f"{dir}{file}")
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
    print(koboldGPT.get_reply())
    print(koboldGPT.random_hello_message())