from typing import Union, Dict, Any
from os import environ
from aiogram.filters import BaseFilter
from aiogram.types import Message
from pymongo import MongoClient

mongo = MongoClient(environ["MONGO_IP_PORT"],username=environ["MONGO_USERNAME"],password=environ["MONGO_PASSWORD"])
db=mongo.InformNovemberQuestBot
admin_collection = db.moderators

class HasModerRights(BaseFilter):
    async def __call__(self, message: Message) -> Union[bool, Dict[str, Any]]:
        # Если entities вообще нет, вернётся None,
        # в этом случае считаем, что это пустой список
        cursor = admin_collection.find({},{"_id":0,'UserId': 1})
        list_cursor = [result for result in cursor]
        editedcursor = [result["UserId"] for result in list_cursor]

        if message.from_user.id in editedcursor:
            return True
        else:
            return False