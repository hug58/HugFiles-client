import requests
import socketio
import asyncio
import json
import threading
import os
from urllib.parse import urljoin

from watchdog import observers
from watchdog.observers.polling import PollingObserver

from utils import event_handler  
from utils import actions
from utils.tui import TerminalInterface
from utils.api import Api
from utils import  set_folder, get_config

sio = socketio.AsyncClient()

data =  get_config()
URL =  data['url']
API_DOWNLOAD = data['api_download']
global DEFAULT_FOLDER

@sio.on('notify')
async def on_notify(metadata):
    global path_user 
    data = json.loads(metadata)


@sio.on('files')
async def on_files(data):
    """ get all files from server """
    global result
    result = ''
    try:
        message = json.loads(data)
        
        message['path_user_local'] = os.path.join(DEFAULT_FOLDER, message['path'])
        if message['status'] == 'created' or message['status'] == 'done':
            result = actions.done(API_DOWNLOAD,message)
        elif message['status'] == 'modified':
            if modified(data): 
                result = actions.created(API_DOWNLOAD,message)
                
        elif message['status'] == 'delete':
                result = actions.deleted(message)
        else:
            #TODO
            pass
        
        message = None
        
    except TypeError as err:
        #TODO: handle error
        # print("error in function on_files",data, err)
        pass

async def producer_file(message):
    """ only upload files, TODO:  deleted files"""
    if message['status'] == 'created':
        requests.post(message['url'],files = {'upload_file': open(message['path'],'rb')})
    elif message['status'] == 'modified':
        try:
            requests.put(urljoin(message['url'],message['name']), files = {'upload_file': open(message['path'],'rb')})
        except IsADirectory as err:
            print(err)
            
    elif message['status'] == 'deleted':
        pass 


async def producer_handler(path, code):
    """Load monitor files and send notifications"""
    monitorsystem = event_handler.EventHandler(path, code)
    observer = PollingObserver()
    observer.schedule(monitorsystem, path=path, recursive=True)
    observer.start()
    print('Loading Monitorsystem')
    
    while True:
        if monitorsystem.message != {}:
            _message = monitorsystem.message
            monitorsystem.message = {}
            await producer_file(_message)
        else:
            await asyncio.sleep(1)

async def main():
    global DEFAULT_FOLDER 
    DEFAULT_FOLDER = get_config()['default_folder']
    USER = get_config()['user']
    
    
    tui = TerminalInterface(DEFAULT_FOLDER, USER)
    
    tui.loop()
    set_folder(tui.path)
    
    code = tui.code 
    await sio.connect(URL)
    print(code)
    await sio.emit("join",{'code':code})
    await producer_handler(DEFAULT_FOLDER,code)
    
    await sio.wait()
        
    print("Exiting...")

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
