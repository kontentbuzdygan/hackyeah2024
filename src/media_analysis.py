import dotenv
from openai import Client

dotenv.load_dotenv()

client = Client()

with open("C:\\Users\\mikolajs\\Downloads\\catcut_HY_2024_film_01.wav", "rb") as f:
    print(client.audio.transcriptions.create(file=f, model="whisper-1", language="pl", prompt="Słuchaj audio do końca i nie usuwaj niczego. Nie poddawaj audio własnej interpretacji"))
