from aiogram.types import Message
from aiogram import Router, Bot , types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pymongo import MongoClient

admin_router = Router()
bot = Bot(token=)
mongo = MongoClient()
db=mongo.InformNovemberQuestBot
user_id_collection = db.users

@admin_router.message(Command("admin"))
async def AdminAnswer(message: types.Message):
    await message.answer("!!!Режим Администратора!!!", reply_markup=)
