import os

class Config(object):
     
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8340701787:AAGpWnVrL9p4eb1hSeklvC_AiBQdRUbitCA")
    API_ID = int(os.environ.get("API_ID",20763817 ))
    API_HASH = os.environ.get("API_HASH", "07186e8f2ffe607e99eedf7eaa5e630b")
    MAX_FILE_SIZE = 2194304000
    OWNER_ID = int(os.environ.get("OWNER_ID", "7819896156"))
    
    
