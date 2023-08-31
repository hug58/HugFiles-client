import requests
import os

from urllib.parse import urljoin


def __modified(url, message):
    """Firing the "created" and "modified" events can generate errors"""
    filename = os.path.join(message['path'],message['name'])
    try:
        _modified_file = os.path.getmtime(filename)
        if _modified_file != message['modified_at']:
            _file_download(url,message)
            return f'Modified file {message["name"]}'
        else:
            return
    except:
        return


def done(url,message):
    """ This function is responsible verify if the file exists and if was created in size of the client or verify if it sent to the server"""
    filename = os.path.join(message['path_user_local'], message['name'])
    if not os.path.exists(filename) and not os.path.isfile(filename):
        return created(url,message)
    elif os.path.isfile(filename):
        _modified_file = os.path.getmtime(filename)
        if int(_modified_file) != int(message['modified_at']):
            return f'File without modified {message["name"]}'
        return created(url,message)
    else:
        return f'is not a file {message["name"]}'

def modified(message):
    """verify event modified and created event"""
    filename = os.path.join(message['path_user_local'],message['name'])
    _modified_file = os.path.getmtime(filename)
    if round(_modified_file) != message['modified_at']:
        return True
    return False



def created(url,message):
    """upload a file to the server"""
    filename = os.path.join(message['path'],message['code'],message['name'])
    if message['path_user_local'] != "":
        os.makedirs(message['path_user_local'], exist_ok=True)
    try:
        _file_download(url,message)
        if 'created_at' in message and 'modified_at' in message:
            atime = message['created_at']
            mtime = message['modified_at']
            filename = os.path.join(message['path_user_local'],message['name'])
            os.utime(filename, (atime, mtime))
        else:
            return "Could not update the file"
        return f'save: {message["name"]}'
    except:
        # print(url,filename)
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


def _file_download(url,message):
    '''Descargar y modificar la metada del archivo.'''
    code = f"{message['code']}/"
    url_file = urljoin(url,code)
    path = os.path.join(message['path'],message['name'])
    url_file = urljoin(url_file,path)
    
    with requests.get(url_file, stream=True) as r:
        r.raise_for_status()
        filename = f"{message['path_user_local']}/{message['name']}"
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(1024):
                if chunk:
                    f.write(chunk)