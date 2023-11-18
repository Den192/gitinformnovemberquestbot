from typing import Any
from aiogram import Bot, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InputMediaPhoto
from pymongo import MongoClient
from aiogram import Router

router=Router()

mongo = MongoClient()

@router.message(Command('hello'))
async def smth(message: types.Message):
    await message.answer("Something")

