from datetime import datetime
import json
import time
import telebot
import os
import subprocess
from telebot import types
import signal, pickle, sys
from config import Settings
from datahelp import help
from clearml import Task, Logger

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

client = telebot.TeleBot(settings.TOKEN)

path = settings.PATHS


if os.path.exists('settings.pkl'):
    with open('settings.pkl', 'rb') as f:
        users = pickle.load(f)
else:
    remember = {}

@client.message_handler(commands=["start"])
def application(message):
    rmk = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    rmk.add(types.KeyboardButton("weights"), types.KeyboardButton("cfg"),types.KeyboardButton("data"), types.KeyboardButton("hyp"),types.KeyboardButton("epochs"), types.KeyboardButton("batch-size"),types.KeyboardButton("img"), types.KeyboardButton("rect"),types.KeyboardButton("resume"), types.KeyboardButton("nosave"),types.KeyboardButton("noval"), types.KeyboardButton("noautoanchor"),types.KeyboardButton("noplots"), types.KeyboardButton("evolve"),types.KeyboardButton("bucket"), types.KeyboardButton("cache"),types.KeyboardButton("image-weights"), types.KeyboardButton("device"),types.KeyboardButton("multi-scale"), types.KeyboardButton("single-cls"),types.KeyboardButton("optimizer"), types.KeyboardButton("sync-bn"),types.KeyboardButton("workers"), types.KeyboardButton("project"),types.KeyboardButton("name"), types.KeyboardButton("exist-ok"),types.KeyboardButton("quad"), types.KeyboardButton("cos-lr"),types.KeyboardButton("label-smoothing"), types.KeyboardButton("patience"),types.KeyboardButton("freeze"), types.KeyboardButton("save-period"), types.KeyboardButton("seed"), types.KeyboardButton("local_rank"), types.KeyboardButton("entity"), types.KeyboardButton("upload_dataset"), types.KeyboardButton("bbox_interval"), types.KeyboardButton("artifact_alias"), types.KeyboardButton("STOP"))
    dict = {}
    msg = client.send_message(message.chat.id, "Выберете аргумент", reply_markup=rmk)
    client.register_next_step_handler(msg, user_answer,dict)

def user_answer(message,dict):
    if (message.text == "weights" or message.text == "cfg" or message.text == "data" or message.text == "hyp" or message.text == "epochs" or message.text == "batch-size" or message.text == "img" or message.text == "rect" or message.text == "resume" or message.text == "nosave" or message.text == "noval" or message.text == "noautoanchor" or message.text == "noplots" or message.text == "evolve" or message.text == "bucket" or message.text == "cache" or message.text == "image-weights" or message.text == "device" or message.text == "multi-scale" or message.text == "single-cls" or message.text == "optimizer" or message.text == "sync-bn" or message.text == "workers" or message.text == "project" or message.text == "name" or message.text == "exist-ok" or message.text == "quad" or message.text == "cos-lr" or message.text == "label-smoothing" or message.text == "patience" or message.text == "freeze" or message.text == "save-period" or message.text == "seed" or message.text == "local_rank" or message.text == "entity" or message.text == "upload_dataset" or message.text == "bbox_interval" or message.text == "artifact_alias"):
        rmk = types.ReplyKeyboardMarkup(resize_keyboard=True)
        global remember
        if message.text in remember:
            print(remember)
            if (len(remember[message.text]) > 6):
                x = min(remember[message.text], key=remember[message.text].get)
                del remember[message.text][x]
            if (remember[message.text]):
                for key in remember[message.text]:
                    rmk.add(types.KeyboardButton(key))
        else : remember[message.text] = {}
        msg = client.send_message(message.chat.id, f"{message.text} : {help[message.text]}\nВпишите ваши данные:", reply_markup=rmk)
        client.register_next_step_handler(msg, user_req,dict , message.text)
    elif message.text == "STOP":
        result = "python train.py "
        for key, value in dict.items():
            result += f"--{key} {value} "
        rmk = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        rmk.add(types.KeyboardButton("Да"),types.KeyboardButton("Нет"))
        msg = client.send_message(message.chat.id, f"Запустить команду?:\n" + result,reply_markup=rmk)
        client.register_next_step_handler(msg, user_finish, result)
    else:
        client.send_message(message.chat.id, "Ошибка аргумента")

def user_req(message,dict,arg):
    dict[arg] = message.text
    global remember
    if (message.text in remember[arg]):
        remember[arg][message.text] += 1
    else : remember[arg][message.text] = 1
    print(dict)    
    rmk = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    rmk.add(types.KeyboardButton("weights"), types.KeyboardButton("cfg"),types.KeyboardButton("data"), types.KeyboardButton("hyp"),types.KeyboardButton("epochs"), types.KeyboardButton("batch-size"),types.KeyboardButton("img"), types.KeyboardButton("rect"),types.KeyboardButton("resume"), types.KeyboardButton("nosave"),types.KeyboardButton("noval"), types.KeyboardButton("noautoanchor"),types.KeyboardButton("noplots"), types.KeyboardButton("evolve"),types.KeyboardButton("bucket"), types.KeyboardButton("cache"),types.KeyboardButton("image-weights"), types.KeyboardButton("device"),types.KeyboardButton("multi-scale"), types.KeyboardButton("single-cls"),types.KeyboardButton("optimizer"), types.KeyboardButton("sync-bn"),types.KeyboardButton("workers"), types.KeyboardButton("project"),types.KeyboardButton("name"), types.KeyboardButton("exist-ok"),types.KeyboardButton("quad"), types.KeyboardButton("cos-lr"),types.KeyboardButton("label-smoothing"), types.KeyboardButton("patience"),types.KeyboardButton("freeze"), types.KeyboardButton("save-period"), types.KeyboardButton("seed"), types.KeyboardButton("local_rank"), types.KeyboardButton("entity"), types.KeyboardButton("upload_dataset"), types.KeyboardButton("bbox_interval"), types.KeyboardButton("artifact_alias"), types.KeyboardButton("STOP"))
    msg = client.send_message(message.chat.id, json.dumps(dict), reply_markup=rmk)
    client.register_next_step_handler(msg, user_answer, dict)

def user_finish(message,comand):
    if message.text == "Да":
        client.send_message(message.chat.id,"В процессе...") 
        os.chdir(path)
        # task = Task.init(project_name = "TelegramBotYolov5",task_name = "testTask2" + datetime.now().strftime("%H:%M:%S"))
        # time.sleep(10)
        # returned_output = subprocess.check_output(comand)
        p = subprocess.Popen(comand, 
                             stdout=subprocess.PIPE, # перенаправление стандартного вывода
                             stderr=subprocess.STDOUT, # и вывода ошибок
                             )
        # Логгируем сообщение об окончании обучения в ClearML
        while True:
            output = p.stdout.readline()
            if output == '' and p.poll() is not None:
                break
            if output:
                client.send_message(message.chat.id, output.strip())

        Logger.current_logger().report_text('Обучение YOLOv5 завершено!')
        # while p.poll() == None:
        #     print(p.stdout.readline())
        # p.wait()
        # output = p.communicate()[0]      
        
        # print(output)
        # p.terminate() 
        # client.send_message(message.chat.id,"Готово")   
        # send_message(message,output)
        # task.set_completed() 
        # task.close()
    else:
        client.send_message(message.chat.id,"Отменяю")

def send_message(message,text):
    if len(text) >= 4096:
        while i < len(text): 
            if i+4094 < len(text): 
                time.sleep(2)
                client.send_message(message.chat.id,text[i:i+4094]) 
            else: 
                time.sleep(2)
                client.send_message(message.chat.id,text[i:len(text)]) 
                i += 4094
    else: client.send_message(message.chat.id, text)

def handler():
    with open('settings.pkl', 'wb') as f:
        pickle.dump(remember, f)
    sys.exit(0)


def create_clearml_task():
    # Генерируем уникальное имя задачи на основе текущей даты и времени
    now = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    task_name = f'YOLOv5 training ({now})'

    # Создаем задачу на ClearML
    task = Task.init(project_name="TelegramBotYolov5", task_name=task_name)

    return task

# Создаем первую задачу на ClearML
task = create_clearml_task()

signal.signal(signal.SIGTERM, handler)

client.enable_save_next_step_handlers(delay=2)
client.load_next_step_handlers()
client.polling()
