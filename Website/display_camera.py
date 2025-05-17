import streamlit as st
from streamlit_webrtc import webrtc_streamer
import av
import firebase_admin
from firebase_admin import credentials, db

if not firebase_admin._apps:
    cred = credentials.Certificate("ServiceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://projek-akhir-iot-c6b39-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })


# Variabel global
accounts_list = []

# Fungsi callback video
def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    # Tambahkan pemrosesan jika perlu
    return av.VideoFrame.from_ndarray(img, format="bgr24")

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
    
# Tempat camera 
st.header("2. Deteksi Wajah")  
camera = st.empty()

with camera:
                webrtc_streamer(
                    key="face-auth",
                    video_frame_callback=video_frame_callback,
                    media_stream_constraints={"video": True, "audio": False},
                    async_processing=True,
                )
# Proses login
if submitted:
    if fetch_data():
        found = any(account["username"] == username and account["password"] == password for account in accounts_list)
        if found:
            st.success("Login berhasil! Lanjut ke deteksi wajah langsung.")
        else:
            st.error("Username atau password salah!")
    else:
        st.error("Gagal mengambil data dari database!")
