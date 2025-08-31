from .api import server
from bottle import static_file
from pathlib import Path

def activate_integrated_frontend():

    current_path = Path(__file__).parent.resolve()

    @server.get("/")
    def frontend():
        return static_file("index.html", root=Path(current_path,"frontend"))
    
    @server.get('/static/<filepath:path>')
    def server_static(filepath):
        return static_file(filepath, root=Path(current_path,"frontend"))