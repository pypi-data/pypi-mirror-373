from .api import server
from bottle import static_file
from pathlib import Path

def activate_integrated_frontend(custom_path:str = None):

    if custom_path == None:
        front_path = Path(__file__).parent.resolve()
        front_path = Path(front_path,"frontend")
    else:
        front_path = Path(custom_path).resolve()

    @server.get("/")
    def frontend():
        return static_file("index.html", root=front_path)
    
    @server.get('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root=front_path)