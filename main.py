import os
import requests
import socketio
import asyncio
import json
import requests

from watchdog import observers


#Locals
from utils import event_handler  
from utils.download import done,deleted,modified,created



sio = socketio.AsyncClient()


URL = os.getenv("URL")
global messages_files
messages_files = [] 


@sio.on('connect')
async def connect():
    global path_user
    print('Connection established')


@sio.on('notify')
async def on_notify(metadata):
    global path_user 
    data = json.loads(metadata)
    path_user = data["path"]
    print(data, type(data))


@sio.on('files')
async def on_files(data):
    """ get all files from server """
    global result
    result = ''
    try:
        data = json.loads(data)
        messages_files.append(data)
        if data['status'] == 'created' or data['status'] == 'done':
            result = done(URL,data)
        elif data['status'] == 'modified':
            if modified(data): 
                result = created(URL,data)
        elif data['status'] == 'delete':
            result = deleted(data)
    except TypeError as err:
        #TODO: handle error
        print(data, err)

async def producer_file(message):
    """ only upload files, TODO: modified and deleted files"""
    if message['status'] == 'created':
        requests.post(message['url'],files = {'upload_file': open(message['path'],'rb')})
    elif message['status'] == 'modified':
        pass
    elif message['status'] == 'deleted':
        pass 


async def producer_handler(_path='data/files/', path_user=None):
    """Load monitor files and send notifications"""
    monitorsystem = event_handler.EventHandler(URL, path_user)
    observer = observers.Observer()
    observer.schedule(monitorsystem, path=_path, recursive=True)
    observer.start()
    print('Loading Monitorsystem')
    while True:
        if monitorsystem.message != {}:
            _message = monitorsystem.message
            monitorsystem.message = {}
            print(_message)
            try:
                messages_files.remove(_message)
            except ValueError:
                monitorsystem.message = {}
                await producer_file(_message)
        else:
            await asyncio.sleep(1)

async def main():
    DEFAULT_FOLDER = os.getenv("DEFAULT_FOLDER")
    if not os.path.isdir(DEFAULT_FOLDER):
        os.makedirs(DEFAULT_FOLDER, exist_ok=True)
    await sio.connect(URL)
    data = {"email":os.getenv("EMAIL")}
    respond = requests.post(URL + "/token", json=data, headers={'Content-Type': 'application/json'})
    if respond.status_code == 200:
        path_user = respond.json()["path"]
        print(path_user)
    else:
        return 
    await producer_handler(_path=DEFAULT_FOLDER, path_user=path_user)
    await sio.wait()

if __name__ == '__main__':
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
