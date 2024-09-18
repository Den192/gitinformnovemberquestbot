from os import getenv
from dotenv import load_dotenv
from typing import Any
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pymongo import MongoClient
from aiogram import Router
from datetime import datetime

router=Router()



mongo = MongoClient(getenv("MONGO_IP_PORT"),username=getenv("MONGO_USERNAME"),password=getenv("MONGO_PASSWORD"))
db = mongo.InformNovemberQuestBot
user_id_collection = db.users
challenges = db.challenges
useranswer = db.useranswers

class ChallengeState(StatesGroup):
    challengestart = State()
    challengeaddanswer = State()

async def challengeskeyboard():
    Keyboard = ReplyKeyboardBuilder()
    cursor = challenges.find({},{"_id":0,"challengenumber":1})
    list_cursor = [result for result in cursor]
    editedcursor = [result["challengenumber"] for result in list_cursor]
    for i in range(0,len(editedcursor)):
        Keyboard.button(text=f"{editedcursor[i]}")
    Keyboard.adjust(3)
    Keyboard.row(types.KeyboardButton(text="Отменить"))
    return Keyboard.as_markup(resize_keyboard=True)
@router.message(Command("add"))
async def StartMessage(message: types.Message, state:FSMContext):
    await message.answer("Привет! Этот бот создан для участия в мартовском квесте ФИТУ!.\nДля продолжения выберите задание, на которое хотите добавить ответ",reply_markup=await challengeskeyboard())
    await state.set_state(ChallengeState.challengestart)

@router.message(ChallengeState.challengestart,F.text!="Отменить")
async def GetMessage(message: types.Message, state:FSMContext):
    cursor = challenges.find({},{"_id":0,'challengenumber':1})
    list_cursor = [result for result in cursor]
    editedcursor = [result["challengenumber"] for result in list_cursor]
    if message.text not in editedcursor:
        await message.answer("Выбрано неверное задание, повторите попытку",reply_markup=await challengeskeyboard())
        await state.clear()
        del cursor,list_cursor,editedcursor
        return
    else:
        answers = list(useranswer.find({"userid":message.from_user.id,"challengenumber":message.text},{"_id":1}))
        if len(answers)!=0:
            await message.answer("Ответ на задание уже был введен! Для продолжения нажмите /add",reply_markup=types.ReplyKeyboardRemove())
            await state.clear()
            return
        else:
            challenesearch = challenges.find({"challengenumber":message.text},{"_id":0,"hint":1})
            await message.answer("Выбрано задание "+message.text+"\nПодсказка от авторов:\n"+challenesearch[0]["hint"]+"\nВведите свой ответ"+"\n\nЕсли в задании несколько ответов, вводите их все за один раз!!!",reply_markup=types.ReplyKeyboardRemove())
            await state.update_data(challengenumber = message.text)
            await state.set_state(ChallengeState.challengeaddanswer)
    del cursor,list_cursor,editedcursor

@router.message(ChallengeState.challengeaddanswer,F.text!="/cancel" or F.text!="Отменить")
async def AddingAnswer(message:types.Message,state:FSMContext):
    data = await state.get_data()
    today = datetime.now()
    useranswer.insert_one({"userid":message.from_user.id,"username":message.from_user.username,"challengenumber":data["challengenumber"],"answer":message.text,"moderchecked":None,"answertime":today.strftime("%d:%m:%Y/%X")})
    await state.clear()
    await message.answer("Ваш ответ принят! Для добавления ответов, нажмите /add")

@router.message(ChallengeState.challengeaddanswer,F.text=="/cancel")
@router.message(ChallengeState.challengestart,F.text=="Отменить" or F.text=="/cancel")
async def MessageCancel(message:types.Message,state:FSMContext):
    await message.answer("Действие было отменено. Для продолжения нажмите /add",reply_markup=types.ReplyKeyboardRemove())
    await state.clear()