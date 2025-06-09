import cv2
import torch
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1
import firebase_admin
from firebase_admin import credentials, db

# Inisialisasi Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': '*************************************'
})

# Inisialisasi MTCNN dan FaceNet
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(image_size=160, margin=0, keep_all=False, device=device)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

# Struktur Data Akun untuk Simpan ke Firebase
def save_account_to_firebase(username, password):
    # Menyimpan akun dengan username sebagai key
    ref = db.reference('tes_account')
    
    # Cek apakah username sudah ada
    existing_account = ref.child(username).get()
    
    if existing_account:
        print(f"⚠️ Akun dengan username '{username}' sudah ada!")
    else:
        # Menyimpan data akun dengan username sebagai key
        account_data = {
            'username': username,
            'password': password
        }
        ref.child(username).set(account_data)  # Menyimpan dengan username sebagai key
        print(f"✅ Akun '{username}' berhasil ditambahkan ke Firebase!")


# Fungsi simpan embedding wajah ke Firebase
def save_face_to_firebase(username, embedding):
    data = {
        'embedding': embedding.tolist()  # Menyimpan embedding wajah dalam format list
    }
    db.reference(f"face_data/{username}").set(data)
    print(f"✅ Embedding wajah '{username}' berhasil disimpan ke Firebase!")

# Input data akun
print("Masukkan data akun terlebih dahulu:")
username = input("Username: ")
password = input("Password: ")
save_account_to_firebase(username, password)

# Ambil wajah dari kamera
cap = cv2.VideoCapture(0)
print("📷 Arahkan wajah ke kamera dan tekan [Space]...")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    cv2.imshow("Enroll Face", frame)
    key = cv2.waitKey(1)

    if key == 32:  # Space untuk ambil gambar
        face_tensor = mtcnn(frame)
        if face_tensor is not None:
            with torch.no_grad():
                embedding = resnet(face_tensor.unsqueeze(0).to(device)).squeeze(0).cpu()
            save_face_to_firebase(username, embedding)
        else:
            print("🚫 Wajah tidak terdeteksi!")
        break
    elif key == 27:  # Esc untuk keluar
        break

cap.release()
cv2.destroyAllWindows()
