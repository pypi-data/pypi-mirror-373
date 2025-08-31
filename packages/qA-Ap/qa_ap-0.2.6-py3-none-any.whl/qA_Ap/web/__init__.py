from .api import server
from bottle import static_file
from pathlib import Path

def activate_integrated_frontend(custom_path:Path = None):

    front_path = Path(__file__).parent.resolve() if custom_path == None else custom_path

    @server.get("/")
    def frontend():
        return static_file("index.html", root=Path(front_path,"frontend"))
    
    @server.get('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root=Path(front_path,"frontend"))