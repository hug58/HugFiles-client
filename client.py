
import asyncio
import websockets


import json
import os
import os.path
import requests

from watchdog.observers import Observer
from pathlib import Path

#Locals
from event_handler import EventHandler,URL_API


def get_file(filename):

	'''
	Descargar y modificar la metada del archivo.
	'''

	#filename = os.path.join(file['Path'], file['Name'])
	url_file = URL_API +  filename


	with requests.get(url_file,stream= True) as r:
		r.raise_for_status()
		with open(filename,'wb') as f:
			for chunk in r.iter_content(1024):
				if chunk:
					f.write(chunk)
		






	return True


async def consumer(data):

	filename = data['Path'] + '/' + data['Name']

	if os.path.exists(filename):
		print("")
		print(data['Name'], end= "\n")
		print("")

	else:
		
		if not os.path.isdir(data['Path']):
			os.makedirs(data['Path'],exist_ok=True)
		
		get_file(filename)		

	atime = data['Acces time']
	mtime = data['Modified time']

	os.utime(filename,(atime,mtime))


async def main():

	url = "ws://localhost:7000"

	async with websockets.connect(url) as websocket:


		'''
		los eventos no registrados antes de la sincronización no se toman en
		cuenta y no se envian al server. 
		'''

		files = {}
		directory = {}
		path = ''

		async for message in websocket:

			_message = json.loads(message)


			if path == _message['Path'] or path == '':
				files[_message['Name']] = _message

			else:
				directory[path] = files
				files = {}

				'''
				Cambiando de directorio
				'''
				files[_message['Name']] = _message
				directory[_message['Path']] = files


			path = _message['Path']


			await consumer(_message)



		with open('data.json','w') as f:
			json.dump(directory,f)
			del files
			del path
			del directory



		'''
		Monitoreo del sistema de archivos
		'''

		event_handler = EventHandler()
		observer = Observer()
		path = os.path.abspath("data/files/")
		observer.schedule(event_handler, path=path, recursive=True)
		observer.start()
		
		while True:

			#data = await websocket.recv()
			#print(f'data: {data}')
			await asyncio.sleep(1)

		

asyncio.get_event_loop().run_until_complete(main())
