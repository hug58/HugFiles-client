import requests
import os.path


def __modified(url, message):
    """Firing the "created" and "modified" events can generate errors"""
    filename = os.path.join(message['path'],message['name'])
    try:
        _modified_file = os.path.getmtime(filename)
        if _modified_file != message['modified time']:
            _file_download(url,message)
            return f'Modified file {message["name"]}'
        else:
            return
    except:
        return


def done(url,message):
    """ This function is responsible verify if the file exists and if was created in size of the client or verify if it sent to the server"""
    filename = os.path.join(message['path'],message['name'])
    if not os.path.exists(filename):
        created(url,message)
    else:
        if modified(message): 
            created(url,message)
        else:
            return f'File without modified {message["name"]}'


def modified(message):
    """verify event modified and created event"""
    filename = os.path.join(message['path'],message['name'])
    try:
        _modified_file = os.path.getmtime(filename)
        if _modified_file != message['modified time']:
            return True
        else:
            return False
    except:
        return True


def created(url,message):
    """upload a file to the server"""
    filename = os.path.join(message['path'],message['name'])
    if not os.path.isdir(message['path']):
        os.makedirs(message['path'], exist_ok=True)
    try:
        _file_download(url,filename)
        print(f'Downloading {filename} ...')
        atime = message['acces time']
        mtime = message['modified time']
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
