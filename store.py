class Characters_store():
    def __init__(self,default_character=None):
        self.character_by_chat_id = {}
        self.default_character = default_character
        super().__init__()
    
    def set_characters(self,characters):
        self.character_by_name = characters
        #self.autosave()
    
    def get_default_character(self):
        if not self.default_character:
            first_key = self.character_by_name.keys()[0]
            return self.character_by_name[first_key]
        return self.default_character
    
    def get_character(self,chat_id):
        character = self.character_by_chat_id.get(chat_id,None)
        
        if not character:
            return self.get_default_character()
        
        return character
    
    def clear_character_messages(self,chat_id):
        character = self.get_character(chat_id)
        character.messages_array.arr = []
        #self.autosave()
    
    def set_character(self,chat_id,name):
        self.character_by_chat_id[chat_id] = self.character_by_name[name]
        self.clear_character_messages(chat_id)
        #self.autosave()
    
    def keys(self):
        return self.character_by_name.keys()
    
    def add_character(self,character,name):
        self.character_by_name[name] = character