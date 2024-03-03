from pymongo import MongoClient

mongo = MongoClient()
db = mongo.InformNovemberQuestBot
useranswers = db.useranswers

useranswersmoder = list(useranswers.find({"moderchecked":False},{"_id":0,"userid":1,"challengenumber":1,"answer":1}))

print(1)