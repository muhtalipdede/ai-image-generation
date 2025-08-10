from google.cloud import firestore
import os
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
db = firestore.Client(project="ai-image-generation-local")

def seed():
    db.collection("sizes").document("512x512").set({"cost":1})
    db.collection("sizes").document("1024x1024").set({"cost":3})
    db.collection("sizes").document("1024x1792").set({"cost":4})
    # styles, colors
    for s in ["realistic","anime","oil painting","sketch","cyberpunk","watercolor"]:
        db.collection("styles").document(s).set({"name":s})
    for c in ["vibrant","monochrome","pastel","neon","vintage"]:
        db.collection("colors").document(c).set({"name":c})
    db.collection("models").document("A").set({"placeholderUrl":"https://placehold.co/512x512?text=A","failRate":0.05})
    db.collection("models").document("B").set({"placeholderUrl":"https://placehold.co/512x512?text=B","failRate":0.05})
    # users
    db.collection("users").document("user_test1").set({"displayName":"Test1","credits":10})
    db.collection("users").document("user_test2").set({"displayName":"Test2","credits":2})
if __name__=="__main__":
    seed()
    print("seed done")
