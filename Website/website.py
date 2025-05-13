import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, db

if not firebase_admin._apps:
    cred = credentials.Certificate("ServiceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': '*********'
    })


# Variabel global
username_db = []
password_db = []

# Ambil data dari Firebase
def fetch_data():
    try:
        ref = db.reference("account")
        current_data = ref.get()
        if current_data:
            username = current_data.get("username")
            password = current_data.get("password")
            if username and password:
                username_db.append(username)
                password_db.append(password)
                return True
        return False
    except Exception as e:
        print(f"Error fetching data: {e}")
        return False

# Judul aplikasi
st.title("🔐 Sistem Autentikasi Wajah Langsung")

# Langkah 1: Form Login
st.header("1. Masukkan Username dan Password")
with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")

# Proses login
if submitted:
    if fetch_data():
        if username in username_db and password in password_db:
            st.success("Login berhasil! Lanjut ke deteksi wajah langsung.")
            # Di sini kamu bisa mengaktifkan deteksi wajah jika diperlukan
        else:
            st.error("Username atau password salah!")
    else:
        st.error("Gagal mengambil data dari database!")
