import json
from pydantic import BaseSettings
import telebot
import os
import subprocess
from telebot import types
import signal, pickle, sys

class Settings(BaseSettings):
    TOKEN:str
    PATHS:str
    class Config:
        env_file = '.env'

settings = Settings(_env_file='.env', _env_file_encoding='utf-8')

comand = "python train.py data"

client = telebot.TeleBot(settings.TOKEN)

path = settings.PATHS

content = os.listdir(path + "\data")

help = {"weights": "WEIGHTS initial weights path",
  "cfg" :"CFG model.yaml path",
  "data": "DATA dataset.yaml path",
  "hyp": "HYP hyperparameters path",
  "epochs": "EPOCHS total training epochs",
  "batch-size": "BATCH_SIZE total batch size for all GPUs, -1 for autobatch",
  "img":"IMGSZ train, val image size (pixels)",
  "rect": "rectangular training",
  "resume": "[RESUME] resume most recent training",
  "nosave": "only save final checkpoint",
  "noval": "only validate final epoch",
  "noautoanchor": "disable AutoAnchor",
  "noplots": "save no plot files",
  "evolve": "[EVOLVE] evolve hyperparameters for x generations",
  "bucket": "BUCKET gsutil bucket",
  "cache": "[CACHE] image cache ram/disk",
  "image-weights": "use weighted image selection for training",
  "device DEVICE": "cuda device, i.e. 0 or 0,1,2,3 or cpu",
  "multi-scale": "vary img-size +/- 50%",
  "single-cls": "train multi-class data as single-class",
  "optimizer": "{SGD,Adam,AdamW} optimizer",
  "sync-bn": "use SyncBatchNorm, only available in DDP mode",
  "workers": "WORKERS max dataloader workers (per RANK in DDP mode)",
  "project": "PROJECT save to project/name",
  "name": "NAME save to project/name",
  "exist-ok": "existing project/name ok, do not increment",
  "quad": "quad dataloader",
  "cos-lr": "cosine LR scheduler",
  "label-smoothing": "LABEL_SMOOTHING Label smoothing epsilon",
  "patience": "PATIENCE EarlyStopping patience (epochs without improvement)",
  "freeze": "FREEZE [FREEZE ...] Freeze layers: backbone=10, first3=0 1 2",
  "save-period": "SAVE_PERIOD Save checkpoint every x epochs (disabled if < 1)",
  "seed": "SEED Global training seed",
  "local_rank": "LOCAL_RANK Automatic DDP Multi-GPU argument, do not modify",
  "entity": "ENTITY Entity",
  "upload_dataset": "[UPLOAD_DATASET] Upload data, val option",
  "bbox_interval": "BBOX_INTERVAL Set bounding-box image logging interval",
  "artifact_alias": "ARTIFACT_ALIAS Version of dataset artifact to use"
  }

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
        os.chdir(path)
        returned_output = subprocess.check_output(comand)
        # client.send_message(message.chat.id, returned_output.decode("utf-8"))
        client.send_message(message.chat.id,"В процессе...")
    else:
        client.send_message(message.chat.id,"Отменяю")

def handler(**args):
    with open('settings.pkl', 'wb') as f:
        pickle.dump(remember, f)
    sys.exit(0)

signal.signal(signal.SIGTERM, handler)
# client.enable_save_next_step_handlers(delay=2)
# client.load_next_step_handlers()
client.polling()
