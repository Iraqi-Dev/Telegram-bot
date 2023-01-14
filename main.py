import json
import telebot
from telebot import types, util
from decouple import config

BOT_TOKEN = config("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

#//bot_data={
#//    "name": ["DefenderPy", "DefenderPython"]
#//}

text_messages={
    "startMsg" : "اهلا انا بوت DefenderPython من صنع @jafarAli1230",
    "welcomeNewMember" :
             u"اهلا بك {name} في المجموعة",
    "goodBye":
    u"العضو {name} غادر المجموعة",
    "leave": "لقد تم اضافتي الى مجموعة غير المجموعة التي صممت لها, وداعاً",
    #//"called": "كيف يمكنني المساعدة؟"
    "warn": u"🚫لقد استعمل {name}  احدى الكلمات المحظورة"
        u"تبقى لديك {safeCounter} فرص اذا تم تجاوز العدد سيتم طردك",
    "kicked": u"لقد تم طرد العضو {name} صاحب المعرف {username} بسبب مخالفته لاحد قوانين المجموعة"
}

text_blacklist = {
    "offensive": ["امك","كلب","زربة","خرة","سچاچ","گواد", "گحبة", "حقير", "كسلان", "مطي", "انچب", "ساقط", "حيوان"]
}

def handleNewUserData(message):
    id = str(message.new_chat_member.user.id)
    name = message.new_chat_member.user.first_name
    username = message.new_chat_member.user.username

    with open("data.json","r") as jsonFile:
        data = json.load(jsonFile)
    jsonFile.close()

    users = data["users"]
    if id not in users:
        print("new user detected")
        users[id] = {"safeCounter":5}
        users[id]["username"] = username
        users[id]["name"] = name
        print("new user data saved")

    data["users"] = users
    with open("data.json","w") as editedFile:
        json.dump(data,editedFile,indent=3)
    editedFile.close()

def handleOffensiveMessage(message):
    id = str(message.from_user.id)
    name = message.from_user.first_name
    username = message.from_user.username
    with open("data.json","r") as jsonFile:
        data = json.load(jsonFile)
    jsonFile.close()
    
    users = data["users"]
    if id not in users:
        print("new user detected")
        users[id] = {"safeCounter":5}
        users[id]["username"] = username
        users[id]["name"] = name
        print("new user data saved")
    
    for index in users:
        if index == id:
            print("guilty user founded")
            users[id]["safeCounter"] -= 1


    safeCounterFromJson = users[id]["safeCounter"]
    if safeCounterFromJson == 0:
        bot.kick_chat_member(message.chat.id,id)
        bot.send_message(message.chat.id, text_messages["kicked"].format(name=name, username=username))
    else:
        bot.send_message(message.chat.id, text_messages["warn"].format(name=name, safeCounter = safeCounterFromJson))

    data["users"] = users
    with open("data.json","w") as editedFile:
        json.dump(data,editedFile,indent=3)
    editedFile.close()

    return bot.delete_message(message.chat.id,message.message_id)

@bot.message_handler(commands=["start", "help"])
def startBot(message):
    bot.send_message(message.chat.id, text_messages["startMsg"])

@bot.chat_member_handler()
def handleUserUpdates(message:types.ChatMemberUpdated):
    newResponse = message.new_chat_member
    if newResponse.status == "member":
        handleNewUserData(message=message)
        bot.send_message(message.chat.id, text_messages["welcomeNewMember"].format(name=newResponse.user.first_name))
    if newResponse.status == "left":
        bot.send_message(message.chat.id, text_messages["goodBye"].format(name=newResponse.user.first_name))

@bot.my_chat_member_handler()
def leave(message:types.ChatMemberUpdated):
    update = message.new_chat_member
    if update.status == "member":
        bot.send_message(message.chat.id, text_messages["leave"])
        bot.leave_chat(message.chat.id)

@bot.message_handler(func=lambda m:True)
def reply(message):
    words = message.text.split()
#//    if words[0] in bot_data["name"]:
#//        bot.reply_to(message, text_messages["called"])
    for word in words:
        if word in text_blacklist["offensive"]:
            handleOffensiveMessage(message=message)

        

bot.infinity_polling(allowed_updates=util.update_types)