import os
from fastapi.templating import Jinja2Templates

# Thư mục gốc chứa các file giao diện HTML (Templates / Views)
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
