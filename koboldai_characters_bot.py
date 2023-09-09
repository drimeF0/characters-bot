import time
import telebot
import os
import random
import json
from telebot.asyncio_storage import StateMemoryStorage
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot import asyncio_filters

from telebot.async_telebot import AsyncTeleBot

from characters import Character,load_characters,CharacterFileManager
from utils import split_command, FixedSizeArray
from store import Characters_store 
import random
from config import *


top_n_messages = FixedSizeArray(50)

telebot_token = open("token.txt","r").read()
bot = AsyncTeleBot(telebot_token,state_storage=StateMemoryStorage())




koboldGPT = Character("KoboldGPT","""
KoboldGPT is a state-of-the-art Artificial General Intelligence. You may ask any question, or request any task, and KoboldGPT will always be able to respond accurately and truthfully
""","Hello, I am KoboldGPT, your personal AI assistant. What would you like to know?")


characters_by_name = load_characters(CHARACTERS_PATH)

characters = Characters_store(koboldGPT)
characters.set_characters(characters_by_name)



class is_for_me(telebot.asyncio_filters.SimpleCustomFilter):
    key = "is_for_me"
    @staticmethod
    async def check(message: telebot.types.Message):
        me_id = await bot.get_me()
        if not message.reply_to_message:
            return
        if not message.reply_to_message.from_user.id == me_id.id:
            return
        if "AI_CREATION_TEXT" in message.reply_to_message.text:
            return
        return True

class is_mkchar(telebot.asyncio_filters.SimpleCustomFilter):
    key = "is_mkchar"
    @staticmethod
    async def check(message: telebot.types.Message):
        me_id = await bot.get_me()
        if not message.reply_to_message:
            return
        if not message.reply_to_message.from_user.id == me_id.id:
            return
        if not "AI_CREATION_TEXT" in message.reply_to_message.text:
            return
        return True





class Create_char(StatesGroup):
    name = State()
    desc = State()
    hello_message = State()




@bot.message_handler(commands = ['start',"help","about"])
async def start_help_command(message):
    
    chat_id = message.chat.id
    character = characters.get_character(chat_id)
    
    msg = await bot.reply_to(message,
    f"""
    был создан c лобовью к чачу https://t.me/drimeF0.
    используется апи lite.koboldai.net
    текущие модели: {character.sampler.models}
    текущий персонаж: {character.name}
    
    чтобы его использовать, достаточно ответить на любое сообщение бота
    """)
    top_n_messages.append(msg)

@bot.message_handler(commands = ['getchars'])
async def getchars_command(message):
    stt = "\n".join([f"`{key}`" for key in characters.keys()])
    st = f"""текущие персонажи:\n {stt} """
    msg = await bot.reply_to(message,st,  parse_mode="markdown")
    top_n_messages.append(msg)


@bot.message_handler(commands = ["setchar"])
async def setchar_command(message):
    
    chat_id = message.chat.id
    
    cmd = split_command(message)
    if not cmd:
        return
    
    name = cmd[1]
    
    if name in characters.keys():
        characters.set_character(chat_id,name)
        hello_message = characters.get_character(chat_id).hello_message
        await bot.reply_to(message,f"{hello_message}")
        return

#delete all messages stored in top_n_messages
@bot.message_handler(commands = ["clear_messages"])
async def clear_messages_command(message):
    for msg in top_n_messages.arr:
        try:
            await bot.delete_message(msg.chat.id,msg.message_id)
        except:
            pass
    top_n_messages.arr = []
    
@bot.message_handler(commands = ["clear"])
async def clear_messages_command(message):
    chat_id = message.chat.id
    characters.clear_character_messages(chat_id)
    await bot.reply_to(message,"готово.")


    
#character creation processing

@bot.message_handler(commands = ["mkchar"])
async def create_character_registration(message):   
    await bot.reply_to(message,"AI_CREATION_TEXT напишите имя персонажа")
    await bot.set_state(message.from_user.id, Create_char.name, message.chat.id)

@bot.message_handler(state=Create_char.name, is_mkchar=True)
async def create_character_name(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['name'] = message.text
    await bot.reply_to(message,"AI_CREATION_TEXT напишите описание персонажа")
    await bot.set_state(message.from_user.id, Create_char.desc, message.chat.id)

@bot.message_handler(state=Create_char.desc,is_mkchar=True)
async def create_character_desc(message):
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['desc'] = message.text
    await bot.reply_to(message,"AI_CREATION_TEXT напишите первое сообщение персонажа")
    await bot.set_state(message.from_user.id, Create_char.hello_message, message.chat.id)

@bot.message_handler(state=Create_char.hello_message,is_mkchar=True)
async def create_character(message):
    global character
    global characters
    hello_message = message.text
    async with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        name = data['name']
        desc = data['desc']
    manager = CharacterFileManager()
    character = Character(name,desc,hello_message)
    characters.add_character(character,name)
    manager.to_json(character=character,directory=CHARACTERS_PATH)
    await bot.reply_to(message,f"персонаж {name} был создан!")

#end of character creation processing





@bot.message_handler(content_types=["text"],is_for_me=True)
async def auto_answer(message):
    chat_id = message.chat.id
    character = characters.get_character(chat_id)
    await bot.send_chat_action(message.chat.id, "typing")
    character.append_message(message.text,message.from_user.username)
    generated = character.get_reply()
    
    if generated:
       msg = await bot.reply_to(message,generated,parse_mode="markdown")
       top_n_messages.append(msg)





import asyncio

bot.add_custom_filter(is_for_me())
bot.add_custom_filter(is_mkchar())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))


while True:
    try:
        print("bot is started")
        asyncio.run(bot.polling(non_stop=True, interval=1, timeout=0))
    except:
        print("bot is crashed")
        time.sleep(5)
