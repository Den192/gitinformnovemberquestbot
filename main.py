import logging
import asyncio
from aiogram import Bot,Dispatcher,types,F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.command import Command
from pymongo import MongoClient
from datetime import datetime
from handlers import get_router
from handlers.admins import admin_router
from handlers.moders import moder_router
from filters.adminfilter import HasAdminRights
from filters.moderfilter import HasModerRights

mongo = MongoClient('10.8.0.1:27017',username='tgNovemberQuest',password='ogoetochtobotinforma')
db = mongo.InformNovemberQuestBot
user_id_collection = db.users


logging.basicConfig(filename="/home/gitinformnovemberquestbot/info.log", encoding='utf-8', level=logging.INFO)

bot = Bot(token="6825694742:AAFVKqf3DzvqN8_NDLeX5p-Igxam_xH-pyw")

dp=Dispatcher()
dp.message.filter(F.chat.type == "private")

class startstates(StatesGroup):
    beginstart = State()
    groupstate = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message,state:FSMContext):
    await message.answer("Привет! Это бот для квеста, в который ты сможешь присылать свои ответы.")#,reply_markup=keyboard)
    result = user_id_collection.find_one({"UserId":message.from_user.id})
    if result is None:
        await state.set_state(startstates.beginstart)
        await message.answer("Введи свое ФИО")
    else:
        await message.answer("Для продолжения нажмите на /add")

@dp.message(F.text,startstates.beginstart)
async def fio_status(message: types.Message,state:FSMContext):
    today = datetime.now()
    await state.update_data(UserId=message.from_user.id,Username=message.from_user.username,RegistrationDate=today.strftime("%d:%m:%Y/%X"),FIO=message.text)
    await state.set_state(startstates.groupstate)
    await message.answer("Введите номер группы")

@dp.message(F.text.len()==6,startstates.groupstate)
async def group_status(message:types.Message,state:FSMContext):
    data = await state.get_data()
    user_id_collection.insert_one({"UserId":data['UserId'], "username":data['Username'],"registrationDate":data['RegistrationDate'],"FIO":data['FIO'],"GroupNumber":message.text})
    await message.answer("Регистрация пройдена.")
    await message.answer("Для продолжения нажмите на /add")

@dp.message(F.text.len()!=6,startstates.groupstate)
async def group_status_mistake(message:types.Message):
    await message.answer("Ошибка в номере группы, введите еще раз")

async def main():
    admin_router.message.filter(HasAdminRights())
    moder_router.message.filter(HasModerRights())
    talk_router = get_router()
    dp.include_router(talk_router)
    dp.include_router(admin_router)
    dp.include_router(moder_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())