
import re
import requests
import os
from utils import get_config
from pathlib import Path

from watchdog import events
from datetime import datetime, timedelta
from urllib.parse import urljoin

class EventHandler(events.FileSystemEventHandler):
    """
    Class dedicated to the different events of the file monitor, each event performs http requests to upload the files, 
    (GET,POST,PUT,DELETE) and then sends the notifications to the server to replicate the messages.
    """
    pattern = re.compile('(.+)/(.+)')
    
    def __init__(self,path, code):
        self.last_modified = datetime.now()
        self.message = {}
        self.url = get_config()['url']
        self.code = f"data/{code}"
        self.path = path
        
    def on_any_event(self, event):
        """
			TODO
        """
        result = re.search(self.pattern, event.src_path)
        if datetime.now() - self.last_modified < timedelta(seconds=1):
            return
        else:
            self.last_modified = datetime.now()
            
        relative_path = os.path.relpath(event.src_path,self.path)
        relative_path = str(Path(relative_path).parent)
        code = f"{self.code}/{relative_path}"
        
        self.message = {
			'status': event.event_type,
			'path': event.src_path,
			'name': result.group(2),
			'url': urljoin(self.url,code),
		}
        if event.event_type == 'created':
            pass