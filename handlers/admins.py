from aiogram.types import Message
from aiogram import Router, Bot , types, F
from aiogram.filters.command import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from pymongo import MongoClient

admin_router = Router()
#bot = Bot(token=)
mongo = MongoClient('10.8.0.1:27017',username='tgNovemberQuest',password='ogoetochtobotinforma')
db=mongo.InformNovemberQuestBot
user_id_collection = db.users
challenges = db.challenges
blacklist = db.blacklist

class addchallengestate(StatesGroup):
    startaddchallenge = State()
    startaddhint = State()
class banstate(StatesGroup):
    startban=State()
    endban=State()
class unbanstate(StatesGroup):
    startunban=State()


async def KeyboardMain():
    Keyboard = ReplyKeyboardBuilder()
    Keyboard.button(text="Добавить задание"),
    Keyboard.button(text="Забанить"),
    Keyboard.button(text="Разбанить"),
    Keyboard.button(text="История"),
    Keyboard.adjust(4)
    Keyboard.row(types.KeyboardButton(text="Подвести итоги"))
    Keyboard.row(types.KeyboardButton(text="Отменить"))
    return Keyboard.as_markup(resize_keyboard=True)

async def keyboardBuilder(BanUnban):
    builder = ReplyKeyboardBuilder()
    if BanUnban == True:
        cursor = user_id_collection.find({},{"_id":0,'username': 1})
    elif BanUnban == False:
        cursor = blacklist.find({},{"_id":0,'username': 1})
    list_cursor = [result for result in cursor]
    editedcursor = [result["username"] for result in list_cursor]
    for i in range(0,len(editedcursor)):
        builder.button(text=f"{editedcursor[i]}")
    builder.adjust(3)
    builder.row(types.KeyboardButton(text="Отменить"))
    return builder.as_markup(resize_keyboard=True)

@admin_router.message(Command("admin"))
async def AdminAnswer(message: types.Message,state:FSMContext):
    await message.answer("!!!Режим Администратора!!!", reply_markup=await KeyboardMain())
    await state.clear()
@admin_router.message(F.text=="Добавить задание")
async def addchallenge(message:types.Message,state:FSMContext):
    cursor = challenges.find({},{"_id":0,'challengenumber': 1})
    list_cursor = [result for result in cursor]
    editedcursor = [result["challengenumber"] for result in list_cursor]
    listToStr = ' '.join([str(elem) for elem in editedcursor])
    await message.answer("Введите номер задания, в данный момент существуют: "+listToStr,reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(addchallengestate.startaddchallenge)
    del cursor,list_cursor,editedcursor,listToStr
@admin_router.message(addchallengestate.startaddchallenge)
async def textchallenge(message:types.Message,state:FSMContext):
    await message.answer("Введите подсказку для пользователей")
    await state.set_state(addchallengestate.startaddhint)
    await state.update_data(challengenumber = message.text)
@admin_router.message(addchallengestate.startaddhint)
async def hintchallenge(message:types.Message,state:FSMContext):
    data = await state.get_data()
    challenges.insert_one({"challengenumber":data["challengenumber"],"hint":message.text})
    await message.answer("Задание под номером "+data["challengenumber"]+" успешно добавлено!\nДля продолжения нажмите /admin или /start")
    await state.clear()


@admin_router.message(F.text.lower()=="забанить")
async def BanUser(message:types.Message,state:FSMContext):
    await state.set_state(banstate.startban)
    await message.answer("Выберите пользователя для бана", reply_markup=await keyboardBuilder(True))
@admin_router.message(banstate.startban, F.text != '/cancel',F.text.lower()!="отменить")
async def UserIdBan(message: types.Message,state:FSMContext):
    useridindb = list(user_id_collection.find({'username': message.text}))
    if len(useridindb)==0:
        await message.answer("Такой пользователь не существует!!")
        return
    result = blacklist.find_one({"userid":useridindb[0]["UserId"]})
    if result is None:
        blacklist.insert_one({"UserId":useridindb[0]["UserId"],"username":message.text})
        await message.answer(f"Пользователь {message.text} был забанен.",reply_markup=types.ReplyKeyboardRemove())
    else:
        await message.answer(f"Пользователь {message.text} уже забанен!!!",reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Для дальнейшей работы, нажмите /admin или /start")
    await state.clear()
    del result,useridindb
@admin_router.message(F.text.lower()=="разбанить")
async def Unban(message:types.Message,state:FSMContext):
    await state.set_state(unbanstate.startunban)
    await message.answer("Выберите пользователя для разбана", reply_markup=await keyboardBuilder(False))
@admin_router.message(unbanstate.startunban,F.text != '/cancel',F.text.lower()!="отменить")
async def NextUnban(message:types.Message,state:FSMContext):
    useridindb = list(blacklist.find({'username': message.text}))
    if len(useridindb)==0:
        await message.answer("Пользователя нет в списке!!")
        await state.clear()
        return
    result = blacklist.find_one({"UserId":useridindb[0]["UserId"]})
    if result is not None:
        blacklist.delete_one({"UserId":useridindb[0]["UserId"]})
    await message.answer(f"Пользователь {message.text} был разбанен.",reply_markup=types.ReplyKeyboardRemove())
    await message.answer("Для дальнейшей работы, нажмите /admin или /start")
    await state.clear()
    del result,useridindb

@admin_router.message(banstate.startban,F.text.lower()==("отменить"))
@admin_router.message(banstate.endban,F.text.lower()==("отменить"))
@admin_router.message(unbanstate.startunban,F.text.lower()==("отменить"))
async def PhotoCancel(message: types.Message, state:FSMContext):
    await message.answer("Действие отменено, начните сначала",reply_markup=types.ReplyKeyboardRemove())
    await message.answer(text="Выберите действие",reply_markup=await KeyboardMain())
    await state.clear()

@admin_router.message(F.text=="Отменить")
async def Exit(message:types.Message):
    await message.answer("Для дальнейшей работы нажмите /start или /admin", reply_markup=types.ReplyKeyboardRemove())