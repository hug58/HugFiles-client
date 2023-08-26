
import re
import requests

from watchdog import events
from datetime import datetime, timedelta

class EventHandler(events.FileSystemEventHandler):
    """
    Class dedicated to the different events of the file monitor, each event performs http requests to upload the files, 
    (GET,POST,PUT,DELETE) and then sends the notifications to the server to replicate the messages.
    """
    pattern = re.compile('(.+)/(.+)')
    
    def __init__(self,url, path_user):
        self.last_modified = datetime.now()
        self.message = {}
        self.url = url 
        self.path_user = path_user
    def on_any_event(self, event):
        """
			TODO
        """
        result = re.search(self.pattern, event.src_path)
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        else:
            self.last_modified = datetime.now()
        self.message = {
			'status': event.event_type,
			'path': event.src_path,
			'name': result.group(2),
			'url': f"{self.url}/{result.group(1)}/{self.path_user}" ,
		}
        if event.event_type == 'created':
            pass