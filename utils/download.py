import requests
import os.path


def __modified(url, message):
	'''Si se dispara el evento "created" y "modified" puede generar errores'''

	filename = os.path.join(message['path'],message['name'])

	try:
		_modified_file = os.path.getmtime(filename)

		if _modified_file != message['modified time']:
			_file_download(url,message)
			return f'Modified file {message["name"]}'
		else:
			return
	except:
		pass  # de esta forma no hay que volver a modificar el archivo


def done(url,message):
	'''Funcion para comprobar si el archivo/file existe, y si se ha creado en el lado del cliente o si viene del servidor'''
	filename = os.path.join(message['path'],message['name'])

	if not os.path.exists(filename):
		#Si el archivo no existe en el cliente, entonces bajar archivo
		created(url,message)
	else:
		#Si archivo/carpeta ha sido modificado en el server, entonces volver a bajar
		if modified(message): 
			created(url,message)
		else:
			return f'File without modified {message["name"]}'


def modified(message):
	'''Si se dispara el evento "created" y "modified" puede generar errores'''
	filename = os.path.join(message['path'],message['name'])
	
	try:
		_modified_file = os.path.getmtime(filename)

		if _modified_file != message['modified time']:
			return True

		else:
			return False
	except:
		return True  # de esta forma no hay que volver a modificar el archivo


def created(url,message):
	''' Sube el archivo al server'''
	
	filename = os.path.join(message['path'],message['name'])

	
	if not os.path.isdir(message['path']): #Comprueba si el directorio existe, sino crearlo
		os.makedirs(message['path'], exist_ok=True)

	try:
		_file_download(url,filename) #Descargando archivo
		print(f'Descargando {filename} ...')
		# Modificando las fechas mtime y atime en el archivo
		atime = message['acces time']
		mtime = message['modified time']
		#configurar metadata del archivo
		os.utime(filename, (atime, mtime))

		return f'save: {message["name"]}'

	except:
		print(url,filename)
		return f'No se ha podido descargar el archivo correctamente {message["name"]}'




def deleted(message):
	'''Eliminar archivos'''

	filename = os.path.join(message['path'],message['name'])

	if not os.path.exists(filename):

		oldname = os.path.join(message["path"],message["oldname"])

		os.rename(oldname, filename)
		return f'{message["oldname"]} ha sido cambiado a {message["name"]}'
	else:
		return 'Ha sido eliminado el archivo'


def _file_download(url,filename):
	'''Descargar y modificar la metada del archivo.'''

	url_file = os.path.join(url,filename)

	with requests.get(url_file, stream=True) as r:
		r.raise_for_status()
		with open(filename, 'wb') as f:
			for chunk in r.iter_content(1024):
				if chunk:
					f.write(chunk)
