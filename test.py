
from pymongo import MongoClient

# Подключение к базе данных
client = MongoClient('10.8.0.1:27017',username='tgNovemberQuest',password='ogoetochtobotinforma')
db = client["InformNovemberQuestBot"]

# Получение коллекций
users_collection = db["users"]
useranswers_collection = db["useranswers"]
challenges_collection = db["challenges"]

# Список для хранения результатов
results = []

# Получение всех пользователей
users = users_collection.find({})

# Проверка каждого пользователя
for user in users:
    # Получение ответов пользователя
    user_answers = useranswers_collection.find({"userid": user["UserId"]})

    # Проверка, ответил ли пользователь на все задания
    all_answered = True
    for challenge in challenges_collection.find({}):
        challenge_number = challenge["challengenumber"]
        if not useranswers_collection.find_one({"userid": user["UserId"], "challengenumber": challenge_number}):
            all_answered = False
            break

    # Проверка, все ли ответы пользователя проверены
    if all_answered:
        all_moderated = True
        for answer in user_answers:
            if not answer["moderchecked"]:
                all_moderated = False
                break

        # Если все ответы пользователя проверены, добавляем его в список
        if all_moderated:
            results.append([user["UserId"], user["username"], user["registrationDate"], user["FIO"], user["GroupNumber"]])

# Вывод результатов
for result in results:
    print(result)
