import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import firebase_admin
from firebase_admin import credentials, db
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
from scipy.spatial.distance import cosine

# Inisialisasi firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("ServiceAccountKey.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': '***************************'
    })

# Setup facenet
mtcnn = MTCNN(image_size=160, margin=0)
model = InceptionResnetV1(pretrained='vggface2').eval()

# Variabel global
accounts_list = []
user_embedding = None  # Menyimpan embedding user yang login

# Fungsi untuk menampilkan/menghilangkan password
def toggle_password_visibility():
    if entry_password.cget('show') == '':
        entry_password.config(show='*')
        toggle_button.config(text='Show')
    else:
        entry_password.config(show='')
        toggle_button.config(text='Hide')

# Ambil embedding dari Firebase berdasarkan username
def fetch_embedding(username):
    try:
        ref = db.reference(f"face_data/{username}/embedding")
        embedding = ref.get()
        if embedding:
            return np.array(embedding)
        else:
            return None
    except Exception as e:
        print(f"Error fetching embedding: {e}")
        return None

# Fungsi yang dijalankan saat tombol Login ditekan
def login():
    global user_embedding
    username = entry_username.get()
    password = entry_password.get()
    if fetch_data():
        found = any(account["username"] == username and account["password"] == password for account in accounts_list)
        if found:
            # Ambil embedding user saat login sukses
            embedding = fetch_embedding(username)
            if embedding is not None:
                user_embedding = embedding
                label_status.config(text=f"Login berhasil! Lanjut ke Verifikasi", fg="green")
                #messagebox.showinfo('Berhasil',"Login berhasil! Lanjut ke deteksi wajah langsung.")
            else:
                user_embedding = None
                label_status.config(text="Login berhasil, tapi embedding wajah tidak ditemukan!", fg="orange")
                #messagebox.showwarning('Peringatan',"Login berhasil, tapi embedding wajah tidak ditemukan!")
        else:
            user_embedding = None
            label_status.config(text="Username atau password salah!", fg="red")
            #messagebox.showwarning('Salah',"Username atau password salah!")
    else:
        user_embedding = None
        label_status.config(text="Gagal mengambil data dari database!", fg="red")
        messagebox.showerror('Error',"Gagal mengambil data dari database!")
        
    print(f"Login attempt - Username: {username}, Password: {password}")

# Fungsi untuk membaca frame dari kamera dan menampilkannya ke GUI
previous_status_verification = None  # Untuk menyimpan status sebelumnya
def update_camera():
    global previous_status_verification
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        if user_embedding is not None:
            recognized, dist = detect_and_recognize(frame, user_embedding)

            if recognized:
                status_text = "Wajah cocok!"
                status_color = (0, 255, 0)
                current_status = "diizinkan"
            else:
                status_text = "Wajah tidak cocok!"
                status_color = (255, 0, 0)
                current_status = "ditolak"

            # Hanya kirim ke Firebase jika statusnya berubah
            if current_status != previous_status_verification:
                try:
                    ref_status = db.reference("status")
                    ref_status.set({
                        "status": current_status
                    })
                    previous_status_verification = current_status  # Update status sebelumnya
                except Exception as e:
                    print(f"Error uploading verification status: {e}")

        else:
            status_text = "Belum login"
            status_color = (255, 255, 0)
            previous_status_verification = None  # Reset jika user keluar

        # Tampilkan teks status di frame
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

        img = Image.fromarray(frame)
        img = img.resize((400, 300))
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)

    camera_label.after(10, update_camera)
# Fungsi deteksi wajah dan verifikasi embedding
def detect_and_recognize(frame, saved_embedding, threshold=0.6):
    # Deteksi wajah (ambil bounding box dan crop wajah)
    face = mtcnn(frame)
    if face is not None:
        # Hitung embedding dari wajah yang terdeteksi
        embedding_live = model(face.unsqueeze(0)).detach().numpy().flatten()
        # Hitung jarak cosine antara embedding live dan saved
        distance = cosine(saved_embedding, embedding_live)
        recognized = distance < threshold
        return recognized, distance
    else:
        # Wajah tidak terdeteksi
        return False, float('inf')

# Fungsi untuk handle saat window ditutup
def on_closing():
    cap.release()  # Lepaskan akses ke webcam
    root.destroy()  # Tutup jendela aplikasi

# Ambil data dari Firebase
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

# Mulai program utama
root = tk.Tk()
root.title("Project Door Lock")

# Judul besar di bagian atas
label_big = tk.Label(root, text="🔐 Sistem Autentikasi Wajah Langsung", font=("Helvetica", 24))
label_big.pack(pady=(10, 5))

# Frame untuk input username dan password
frame_inputs = tk.Frame(root)
frame_inputs.pack(pady=(5, 10))

# Input Username
label_username = tk.Label(frame_inputs, text="Username :", font=("Helvetica", 12))
entry_username = tk.Entry(frame_inputs, width=30)
label_username.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
entry_username.grid(row=0, column=1, pady=5)

# Input Password + tombol show/hide
label_password = tk.Label(frame_inputs, text="Password :", font=("Helvetica", 12))
entry_password = tk.Entry(frame_inputs, width=30, show='*')
toggle_button = ttk.Button(frame_inputs, text='Show', width=6, command=toggle_password_visibility)
label_password.grid(row=1, column=0, sticky="w", padx=(0, 5), pady=5)
entry_password.grid(row=1, column=1, pady=5, sticky="w")
toggle_button.grid(row=1, column=2, padx=(5, 0), pady=5)

# Tombol Login
button1 = ttk.Button(root, text="Login", command=login)
button1.pack(pady=10)

# Label untuk status login dan verifikasi wajah
label_status = tk.Label(root, text="", font=("Helvetica", 14))
label_status.pack(pady=5)

# Frame untuk tampilan kamera
frame_camera = tk.Frame(root, width=400, height=300, bg="black")
frame_camera.pack(pady=10)
frame_camera.pack_propagate(False)  # Agar frame tidak mengecil otomatis

# Label untuk menampilkan gambar dari kamera
camera_label = tk.Label(frame_camera)
camera_label.pack()

# Mulai akses webcam (kamera default)
cap = cv2.VideoCapture(0)

# Mulai update kamera
update_camera()

# Tangani event saat jendela ditutup
root.protocol("WM_DELETE_WINDOW", on_closing)

# Jalankan loop utama GUI
root.mainloop()
