
import os
import os.path
import requests
import json

from watchdog.events import FileSystemEventHandler
from pathlib import Path


URL_API = 'http://127.0.0.1:5000/api/'



class EventHandler(FileSystemEventHandler):
	"""docstring for EventHandler"""

	foulder = 'files'


	def __init__(self):
		pass

	def on_created(self,event):



		path = event.src_path.split(self.foulder)
		path =  'data/files/' + path[1]
		path = Path(path)

		print(path)


		if os.path.isfile(event.src_path):

			url = URL_API + path._srt 
			url = url.replace('\\','/')

			files = {'upload_file': open(event.src_path,'rb')}
			requests.post(url,files = files)

		else:
			pass




	def on_deleted(self,event):

		path = event.src_path.split('data')
		path = 'data' + path[1]
		path = Path(path)


		if os.path.isfile:

			url = URL_API + str(path).replace('\\','/') + path.name
			requests.delete(url)

		else:
			pass



	def on_modified(self,event):

		path = event.src_path.split("data")
		path =  'data' + path[1]
		path = Path(path)
		path = str(path.parent).replace('\\','/') + '/' + path.name




		if os.path.isfile(path):


			with open('data.json','r') as f:
				data = json.load(f)


			url = URL_API + path


			files = {'upload_file': open(event.src_path,'rb')}
			requests.put(url,files = files)


		else:
			pass #Foulders
