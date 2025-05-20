import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import firebase_admin
from firebase_admin import credentials, db
from ultralytics import YOLO
import numpy as np
import cv2

# Inisialisasi Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("ServiceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://projek-akhir-iot-c6b39-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

accounts_list = []

def fetch_data():
    try:
        ref = db.reference("tes_account")
        accounts = ref.get()
        if accounts:
            accounts_list.clear()
            for user_id, creds in accounts.items():
                username = creds.get("username")
                password = creds.get("password")
                if username and password:
                    accounts_list.append({
                        "username": username,
                        "password": password
                    })
            return True
        return False
    except Exception as e:
        print(f"Error fetching data: {e}")
        return False

# Load YOLO model
model = YOLO("best.pt")

# Global variable to store logged-in username
logged_in_username = None

def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")

    # Jalankan deteksi YOLO
    results = model(img)
    
    # Cek apakah ada objek dengan label yang cocok dengan username login
    match_found = False
    for result in results[0].boxes:
        class_id = int(result.cls[0].cpu().numpy())
        label = model.names[class_id]
        
        # Jika label sama dengan username yang login -> tanda cocok
        if logged_in_username and label == logged_in_username:
            match_found = True
            # Gambar kotak hijau untuk yang cocok
            x1, y1, x2, y2 = result.xyxy[0].cpu().numpy().astype(int)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, f"{label} MATCH!", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
        else:
            # Kotak merah untuk deteksi lain
            x1, y1, x2, y2 = result.xyxy[0].cpu().numpy().astype(int)
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
            cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
    
    if logged_in_username and not match_found:
        print("Wajah tidak cocok dengan user yang login!")

    return av.VideoFrame.from_ndarray(img, format="bgr24")

# Streamlit UI
st.title("🔐 Sistem Autentikasi Wajah Langsung")

st.header("1. Masukkan Username dan Password")
with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

st.header("2. Deteksi Wajah")
camera = st.empty()

if submitted:
    if fetch_data():
        found = any(account["username"] == username and account["password"] == password for account in accounts_list)
        if found:
            st.success("Login berhasil! Lanjut ke deteksi wajah langsung.")
            logged_in_username = username  # Set username global yang login

            with camera:
                webrtc_streamer(
                    key="face-auth",
                    video_frame_callback=video_frame_callback,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True,
                )
        else:
            st.error("Username atau password salah!")
    else:
        st.error("Gagal mengambil data dari database!")
