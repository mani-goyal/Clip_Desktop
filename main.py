import os
from supabase import create_client
from realtime.connection import Socket
import pyperclip
import clipboard_monitor
import threading
from constants import *

'''
    0 : Initial state
    1 : Setting in DB
    2 : Reading from DB
'''
mode = 0

def DbCallback(payload):
    global mode
    if(mode == 1):
        mode=0
        return
    
    print("DB Callback: ", payload)
    mode=2
    pyperclip.copy(payload['record']['text'])
    spam = pyperclip.paste()

# response = supabase.table('ClipBoard_Data').select("*").execute()
# print(response)

def process_text(text):
    global mode
    if(mode==2):
        mode=0
        return
    print("got text = ", end="")
    print(text)
    supabase_client = create_client(SUPABASE_URL, SUPABASE_API_KEY)
    mode = 1
    supabase_client.table('ClipBoard_Data').insert({"text": text}).execute()

clipboard_monitor.on_update(print)
clipboard_monitor.on_text(process_text)

threading.Thread(target=clipboard_monitor.wait)

URL = f"wss://{SUPABASE_ID}.supabase.co/realtime/v1/websocket?apikey={SUPABASE_API_KEY}&vsn=1.0.0"


while(True):
    try:
        s = Socket(URL)
        s.connect()
        channel_1 = s.set_channel("realtime:*")
        channel_1.join().on("INSERT", DbCallback)
        s.listen()
    except Exception as e:
        pass

