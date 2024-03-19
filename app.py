from flask import Flask, request, jsonify
from ultralytics import YOLO
import os

app = Flask(__name__)
model_manga = YOLO('manga.pt')
model_manhwa = YOLO('manhwa.pt')

@app.route('/detect_boxes', methods=['POST'])
def detect_boxes():
    directory_path = request.json['directory_path']
    style = request.json['style']
    files = os.listdir(directory_path)

    image_files = [file for file in files if file.endswith(('png', 'jpg', 'jpeg', 'webp'))]
    image_files = list(map(lambda image: os.path.join(directory_path, image), image_files))

    boxes_data = []
    for image in image_files:
        if style == 'Manga':
            results = model_manga(image)
        else:
            results = model_manhwa(image)

        for result in results:
            if len(result.boxes) > 0:
                boxes = []
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    boxes.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
                boxes_data.append({'filename': image, 'boxes': boxes})
            else:
                boxes_data.append({'filename': image, 'boxes': []})

    return jsonify({'images': boxes_data})

if __name__ == '__main__':
    app.run(debug=True)
