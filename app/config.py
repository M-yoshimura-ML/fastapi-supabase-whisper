import os
import socket

from dotenv import load_dotenv

load_dotenv()
socket.getaddrinfo('localhost', 8080)
DATABASE_URL = os.getenv("DATABASE_URL")
