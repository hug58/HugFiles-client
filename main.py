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


#######################URL del server#######################
URL = 'http://localhost:5000'
#URL = 'https://hug-files.herokuapp.com/'

############################################################

global messages_files
messages_files = [] #guardar los mensajes del server y luego procesarlos, de esta forma evito re-enviar un archivo

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

	except TypeError as e:
		print(e)


async def producer_file(message):

	if message['status'] == 'created':
		requests.post(message['url'],files = {'upload_file': open(message['path'],'rb')})	

	elif message['status'] == 'modified':
		pass

	elif message['status'] == 'deleted':
		pass


async def producer_handler(_path='data/files/', path_user=None):
	print('Producing %s' % path_user)
	monitorsystem = event_handler.EventHandler(URL, path_user)
	observer = observers.Observer()

	observer.schedule(monitorsystem, path=_path, recursive=True)
	observer.start()

	print('Iniciando Monitor')

	while True:

		if monitorsystem.message != {}:

			# enviando msg al server
			_message = monitorsystem.message
			monitorsystem.message = {}

			print(_message)


			try:
				messages_files.remove(_message)
				#await sio.emit('notify',_message)
				print('Ya notificado')

			except ValueError:
				#debo confimar que no se esta reenviando un archivo
				monitorsystem.message = {}
				await producer_file(_message)


		else:
			# Sino esperar 1 seg
			await asyncio.sleep(1)


async def main():
	# Carpeta predeterminada (por el momento), la idea a futuro es que el usuario pueda configurar esto a su gusto
	DEFAULT_FOLDER = 'data/files/'
	# Generando la carpeta predeterminada sino existe
	if not os.path.isdir(DEFAULT_FOLDER):
		os.makedirs(DEFAULT_FOLDER, exist_ok=True)

	await sio.connect(URL)
	data = {"email":"prueba@mail.com"}
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
