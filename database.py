# Cursos Pro Android by Skueletor ©️ 2021

import motor.motor_asyncio
from config import Config

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    async def add_chat_list(self, chat_id, ch_id=None):
        get_chat = await self.is_chat_exist(chat_id)
        if get_chat:
            chat_list = list(get_chat.get("chats"))
            if ch_id != None and int(ch_id) in chat_list:
                return True, f"{ch_id} ya se encuentra en la lista blanca."
            elif ch_id == None:
                return False,""
            elif ch_id is not None:
                chat_list.append(int(ch_id))
                await self.col.update_one({'id': chat_id}, {'$set': {'chats': chat_list}})
                return True, f"{ch_id}, ha sido agregado a la lista blanca."
        a_chat = {"id":int(chat_id),"chats":[ch_id]}
        await self.col.insert_one(a_chat)
        return False,""

    async def is_chat_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user if user else False

    async def get_chat_list(self, chat_id):
        get_chat = await self.is_chat_exist(chat_id)
        if get_chat:
            return get_chat.get("chats",[])
        else:
            return False

    async def del_chat_list(self, chat_id, ch_id=None):
        get_chat = await self.is_chat_exist(chat_id)
        if get_chat:
            chat_list = list(get_chat.get("chats"))
            if ch_id != None and ch_id in chat_list:
                chat_list.remove(int(ch_id))
                await self.col.update_one({'id': chat_id}, {'$set': {'chats': chat_list}})
                return True, f"{ch_id}, ha sido removido de la lista blanca."
            elif int(ch_id) not in chat_list:
                return True, f"{ch_id}, no se encuentra en la lista blanca."

   

db = Database(Config.DATABASE_URL, "whitelist_chats")
