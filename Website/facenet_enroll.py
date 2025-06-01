# save_face_embedding.py
from facenet_pytorch import MTCNN, InceptionResnetV1
import cv2
import torch
import numpy as np

# Setup
mtcnn = MTCNN(image_size=160, margin=0)
model = InceptionResnetV1(pretrained='vggface2').eval()

# Capture from webcam
cap = cv2.VideoCapture(1)
print("Tekan 's' untuk menyimpan wajah...")

while True:
    ret, frame = cap.read()
    cv2.imshow("Ambil Wajah", frame)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        face = mtcnn(frame)
        if face is not None:
            embedding = model(face.unsqueeze(0)).detach().numpy()
            np.save('saved_embedding.npy', embedding)
            print("Wajah disimpan sebagai embedding.")
            break
        else:
            print("Wajah tidak terdeteksi!")

cap.release()
cv2.destroyAllWindows()
