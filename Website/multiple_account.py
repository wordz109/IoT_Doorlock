import streamlit as st
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import cv2
import numpy as np
import firebase_admin
from firebase_admin import credentials, db

if not firebase_admin._apps:
    cred = credentials.Certificate("ServiceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': '*****************'
    })


# Variabel global
accounts_list = []

# Ambil data dari Firebase
def fetch_data():
    try:
        ref = db.reference("tes_account")
        accounts = ref.get()
        if accounts:
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
        found = any(account["username"] == username and account["password"] == password for account in accounts_list)
        if found:
            st.success("Login berhasil! Lanjut ke deteksi wajah langsung.")
            # Di sini kamu bisa mengaktifkan deteksi wajah jika diperlukan
        else:
            st.error("Username atau password salah!")
    else:
        st.error("Gagal mengambil data dari database!")

