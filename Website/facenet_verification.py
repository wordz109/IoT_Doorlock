# verify_face.py
from facenet_pytorch import MTCNN, InceptionResnetV1
import cv2
import torch
import numpy as np
from scipy.spatial.distance import cosine

# Load data
saved_embedding = np.load('saved_embedding.npy')

# Setup
mtcnn = MTCNN(image_size=160, margin=0)
model = InceptionResnetV1(pretrained='vggface2').eval()

cap = cv2.VideoCapture(1)

while True:
    ret, frame = cap.read()
    face = mtcnn(frame)

    if face is not None:
        embedding = model(face.unsqueeze(0)).detach().numpy()
        distance = cosine(saved_embedding.flatten(), embedding.flatten())


        if distance < 0.6:
            label = f"Match ({distance:.2f})"
            color = (0, 255, 0)
        else:
            label = f"No Match ({distance:.2f})"
            color = (0, 0, 255)

        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow("Verifikasi Wajah", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
