import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2

# Fungsi untuk menampilkan/menghilangkan password
def toggle_password_visibility():
    if entry_password.cget('show') == '':
        entry_password.config(show='*')
        toggle_button.config(text='Show')
    else:
        entry_password.config(show='')
        toggle_button.config(text='Hide')

# Fungsi yang dijalankan saat tombol Login ditekan
def login():
    username = entry_username.get()
    password = entry_password.get()
    print(f"Login attempt - Username: {username}, Password: {password}")

# Fungsi untuk membaca frame dari kamera dan menampilkannya ke GUI
def update_camera():
    ret, frame = cap.read()  # Baca frame dari webcam
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Konversi dari BGR ke RGB
        img = Image.fromarray(frame)  # Ubah menjadi format gambar PIL
        img = img.resize((400, 300))  # Ubah ukuran ke 400x300
        imgtk = ImageTk.PhotoImage(image=img)  # Ubah ke format ImageTk
        camera_label.imgtk = imgtk  # Simpan referensi agar tidak dihapus oleh garbage collector
        camera_label.configure(image=imgtk)  # Tampilkan gambar di label kamera
    camera_label.after(10, update_camera)  # Perbarui gambar setiap 10 ms

# Fungsi untuk handle saat window ditutup
def on_closing():
    cap.release()  # Lepaskan akses ke webcam
    root.destroy()  # Tutup jendela aplikasi

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
