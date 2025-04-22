from flask import Flask, render_template, request, jsonify
import face_recognition
import os
import numpy as np
from PIL import Image
import io
import base64

app = Flask(__name__)

# Загрузка эталонных лиц
def load_known_faces():
    known_faces = {}
    for filename in os.listdir("label_images"):
        # Проверяем, что это файл, а не папка
        file_path = os.path.join("label_images", filename)
        if not os.path.isfile(file_path):
            continue
            
        # Проверяем расширение файла (опционально)
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            continue
            
        # Имя файла без расширения - это метка
        label = os.path.splitext(filename)[0]
        
        # Загружаем изображение и кодируем лицо
        image = face_recognition.load_image_file(file_path)
        encodings = face_recognition.face_encodings(image)
        
        # Добавляем кодировки в словарь
        if encodings:
            if label not in known_faces:
                known_faces[label] = []
            known_faces[label].extend(encodings)
            
    return known_faces

KNOWN_FACES = load_known_faces()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify():
    data = request.json
    image_data = data['image'].split(',')[1]
    image = Image.open(io.BytesIO(base64.b64decode(image_data)))
    image = np.array(image)
    
    # Поиск лиц на снимке
    face_locations = face_recognition.face_locations(image)
    if not face_locations:
        return jsonify({"error": "Лицо не обнаружено"}), 400
        
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    for label, encodings in KNOWN_FACES.items():
        for encoding in encodings:
            matches = face_recognition.compare_faces([encoding], face_encodings[0])
            if True in matches:
                return jsonify({"user": label})
    
    return jsonify({"error": "Пользователь не распознан"}), 401

if __name__ == '__main__':
    app.run(debug=True)