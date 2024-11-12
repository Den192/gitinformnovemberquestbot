from os import getenv, name
from dotenv import load_dotenv
from pathlib import Path
if name == 'nt':
    load_dotenv(dotenv_path=Path(r'F:\Programming\gitInformNovemberQuestBot\.env'))
else:
    load_dotenv(dotenv_path=Path("/home/gitinformnovemberquestbot/.env"))
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
class DeleteAnswerState(StatesGroup):
    deleteanswerstart = State()
    deleteanswerconfirmation = State()

async def YesNoKeyboard():
    kb = ReplyKeyboardBuilder()
    kb.button(text="Да")
    kb.button(text="Нет")
    kb.adjust(2)
    return kb.as_markup(resize_keyboard = True)

async def challengeskeyboard(userid):
    Keyboard = ReplyKeyboardBuilder()
    userquest = list(user_id_collection.find({"UserId":userid},{"_id":0,"challenges":1}))
    if userquest and "challenges" in userquest[0]:
        for challenge in userquest[0]["challenges"]:
            if challenge[1] == False:
               first_false_challenge = int(challenge[0])
               break
        else:
            first_false_challenge = None
    else:
        first_false_challenge = None 
    cursor = challenges.find({},{"_id":0,"challengenumber":1})
    list_cursor = [result for result in cursor]
    editedcursor = [result["challengenumber"] for result in list_cursor]
    if first_false_challenge == None:
        first_false_challenge = len(editedcursor)
    for i in range(0,first_false_challenge):
        Keyboard.button(text=f"{editedcursor[i]}")
    Keyboard.adjust(3)
    Keyboard.row(types.KeyboardButton(text="Удалить ответ"))
    Keyboard.row(types.KeyboardButton(text="Отменить"))
    return Keyboard.as_markup(resize_keyboard=True)

async def deletechallengeskeyboard(userid):
    Keyboard = ReplyKeyboardBuilder()
    cursor = useranswer.find({"userid":userid},{"_id":0,"challengenumber":1})
    list_cursor = [result for result in cursor]
    editedcursor = [result["challengenumber"] for result in list_cursor]
    for i in range(0,len(editedcursor)):
        Keyboard.button(text=f"{editedcursor[i]}")
    Keyboard.adjust(3)
    Keyboard.row(types.KeyboardButton(text="Отменить"))
    return Keyboard.as_markup(resize_keyboard=True)

@router.message(Command("add"))
async def StartMessage(message: types.Message, state:FSMContext):
    await message.answer("Привет! Этот бот создан для участия в квесте ФИТУ!.\nДля продолжения выберите задание, на которое хотите добавить ответ",reply_markup=await challengeskeyboard(message.from_user.id))
    await state.set_state(ChallengeState.challengestart)

@router.message(ChallengeState.challengestart,F.text=="Удалить ответ")
async def DeleteAnswer(message:types.Message,state:FSMContext):
    cursor = list(useranswer.find({"userid":message.from_user.id},{"_id":0,"challengenumber":1}))
    if len(cursor) == 0:
        await message.answer("Еще ни на одно задание не был введен ответ. Для продолжения нажмите /add",reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        del cursor
        return
    await message.answer("Выберите задание, на которое хотите удалить ответ",reply_markup=await deletechallengeskeyboard(message.from_user.id))
    await state.set_state(DeleteAnswerState.deleteanswerstart)

@router.message(F.text!='Удалить ответ',ChallengeState.challengestart)
@router.message(F.text!="Отменить",ChallengeState.challengestart)
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
            challenesearch = challenges.find({"challengenumber":message.text},{"_id":0,"hint":1,"answer":1})
            await message.answer("Выбрано задание "+message.text+"\nПодсказка от авторов:\n"+challenesearch[0]["hint"]+"\nВведите свой ответ"+"\n\nЕсли в задании несколько ответов, вводите их все за один раз!!!",reply_markup=types.ReplyKeyboardRemove())
            await state.update_data(challengenumber = message.text,answer = challenesearch[0]["answer"])
            await state.set_state(ChallengeState.challengeaddanswer)
    del cursor,list_cursor,editedcursor

@router.message(ChallengeState.challengeaddanswer,F.text!="Отменить")
@router.message(ChallengeState.challengeaddanswer,F.text!="/cancel")
async def AddingAnswer(message:types.Message,state:FSMContext):
    data = await state.get_data()
    today = datetime.now()
    data = await state.get_data()
    if data["answer"] == message.text:
        index = next(i for i, challenge in enumerate(list(user_id_collection.find({"UserId":message.from_user.id}, {"_id": 0, "challenges": 1}))[0]["challenges"]) if challenge[0] == data["challengenumber"])
        user_id_collection.update_one({"UserId":message.from_user.id},{"$set":{f"challenges.{index}.1":True}})
        useranswer.insert_one({"userid":message.from_user.id,"username":message.from_user.username,"challengenumber":data["challengenumber"],"answer":message.text,"moderchecked":True,"answertime":today.strftime("%d:%m:%Y/%X")})
    else:
        useranswer.insert_one({"userid":message.from_user.id,"username":message.from_user.username,"challengenumber":data["challengenumber"],"answer":message.text,"moderchecked":None,"answertime":today.strftime("%d:%m:%Y/%X")})
    await state.clear()
    await message.answer("Ваш ответ принят! Для добавления ответов, нажмите /add")

@router.message(ChallengeState.challengestart,F.text=="Удалить ответ")
async def DeleteAnswer(message:types.Message,state:FSMContext):
    cursor = useranswer.find({"userid":types.Message.from_user.id},{"_id":0,"challengenumber":1})
    if cursor[0] == {}:
        await message.answer("Еще ни на одно задание не был введен ответ. Для продолжения нажмите /add")
        await state.clear()
        del cursor
        return
    await message.answer("Выберите задание, на которое хотите удалить ответ",reply_markup=await deletechallengeskeyboard())
    await state.set_state(DeleteAnswerState.deleteanswerstart)

@router.message(DeleteAnswerState.deleteanswerstart,F.text!="Отменить")
async def DeleteAnswerConfirm(message:types.Message,state:FSMContext):
    await message.answer("Вы выбрали задание под номером "+message.text+"\n\nВы точно хотите удалить?",reply_markup=await YesNoKeyboard())
    await state.update_data(TaskNumber = message.text)
    await state.set_state(DeleteAnswerState.deleteanswerconfirmation)

@router.message(DeleteAnswerState.deleteanswerconfirmation,F.text=="Да")
async def DeleteAnswerTrue(message:types.Message,state:FSMContext):
    data = await state.get_data()
    useranswer.delete_one({"userid":message.from_user.id,"challengenumber":data["TaskNumber"]})
    await message.answer("Ответ был удален\nДля продолжения нажмите /add",reply_markup=types.ReplyKeyboardRemove())
    await state.clear()

@router.message(DeleteAnswerState.deleteanswerstart,F.text=="Отменить")
@router.message(DeleteAnswerState.deleteanswerconfirmation,F.text=="Нет")
@router.message(ChallengeState.challengeaddanswer,F.text=="/cancel")
@router.message(ChallengeState.challengestart,F.text=="Отменить" or F.text=="/cancel")
async def MessageCancel(message:types.Message,state:FSMContext):
    await message.answer("Действие было отменено. Для продолжения нажмите /add",reply_markup=types.ReplyKeyboardRemove())
    await state.clear()