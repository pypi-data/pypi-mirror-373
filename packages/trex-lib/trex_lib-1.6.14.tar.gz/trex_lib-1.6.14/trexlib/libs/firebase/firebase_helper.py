import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

gis_init = False

def create_firestore_client():
    if gis_init is False:
        cred = credentials.Certificate('lalapos-525b4-firebase-adminsdk-deon0-84b2fc920d.json')
        firebase_admin.initialize_app(cred)
        gis_init = True
    
    return firestore.client()
    
