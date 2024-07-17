import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate(r"C:\Users\arnav\Downloads\StrabinetAuthKey.json") #Arnav & Vib, edit this path to the path of the auth key I sent you on your system
firebase_admin.initialize_app(cred)
