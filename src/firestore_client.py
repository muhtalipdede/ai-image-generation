from google.cloud import firestore
import os

def get_db():
    if os.environ.get("FIRESTORE_EMULATOR_HOST"):
        return firestore.Client(project="ai-image-generation-local")
    else:
        raise RuntimeError("FIRESTORE_EMULATOR_HOST is not set. Please start the Firestore emulator and set the environment variable.")
