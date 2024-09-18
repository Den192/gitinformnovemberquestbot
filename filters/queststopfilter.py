from typing import Callable, Dict, Any, Awaitable
from os import environ
from aiogram import BaseMiddleware
from aiogram.types import Message
from pymongo import MongoClient
mongo = MongoClient(environ["MONGO_IP_PORT"],username=environ["MONGO_USERNAME"],password=environ["MONGO_PASSWORD"])
db = mongo.InformNovemberQuestBot
queststop = db.StoppingQuest
moders = db.moderators
admins = db.adminlist

async def flatlist(list):
    listtocreate = [result for result in list]
    editedlist = [result["UserId"] for result in listtocreate]
    return editedlist

# Это будет outer-мидлварь на любые колбэки
class StopQuestMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        StoppingQuest = list(queststop.find())
        
        if StoppingQuest[0]["queststopstatus"] is True:
            if event.from_user.id in await flatlist(moders.find({},{"_id":0,"UserId":1})) or await flatlist(admins.find({},{"_id":0,"UserId":1})):
                return await handler(event,data)
            else:
                await event.answer("К сожалению, квест закончился, ожидайте ответа!")
                return
        else:
            return await handler(event,data)
        userid = event.from_user.id 
        cursor = blacklist.find({},{"_id":0,'UserId': 1})
        list_cursor = [result for result in cursor]
        editedcursor = [result["UserId"] for result in list_cursor]
        if userid in editedcursor:
            await event.answer("Вы были забанены!!!", show_alert=True)
            return
        else:
            return await handler(event,data)
