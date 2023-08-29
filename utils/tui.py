import os
from utils import URL_BASE
from .api import Api
from colorama import init, Fore

class TerminalInterface:
    def __init__(self):
        self._email = None
        self._path = None
        self._connected = False
        self._code = None
        self.api = Api(URL_BASE)
        init()  # Inicializar colorama
        
    def submit_email(self):
        color = Fore.RED
        self._email = email

        while True:
            email = input("Input your email: ")
            if email and email != "":
                self._code = self.api.get_token(email)
                if self._code:
                    break

            print(f"{color}Please select a valid email {color}█{Fore.RESET}" )
            

        

    def select_folder(self):
        color = Fore.RED
        
        while True:
            folder_path = input("Select Directory: ")
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                self._path = folder_path
                break
            
            print(f"{color}Please select a folder that exists {color}█{Fore.RESET}" )
            
        
    def toggle_connection(self):
        self._connected = not self._connected
        self.draw_connection_circle()

    def draw_connection_circle(self):
        color = Fore.GREEN if self._connected else Fore.RED
        print(f"{color}Connection Status: {color}█{Fore.RESET}")
        
    def loop(self):
        self.draw_connection_circle()
        
        while True:
            self.select_folder()
            self.submit_email()
            
            if self._path != None and self._email != None:
                self.toggle_connection()
                break
            

                
    @property
    def email(self):
        return self._email
    
    @property
    def path(self):
        return self._path
    
    @property
    def code(self):
        return self._code
