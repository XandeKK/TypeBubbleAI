from ultralytics import YOLO
import asyncio
import websockets
import json
import os
import autoload as Autoload

def sanitize_images(files, directory):
    images = [file for file in files if file.endswith(('png', 'jpg', 'jpeg', 'webp'))]
    try:
        images = sorted(images, key=lambda x: int(x.split('.')[0]))
    except ValueError:
        print("There is an image with a non-numeral name")
    images = list(map(lambda image: os.path.join(directory, image), images))

    return images

class Server:
    def __init__(self, model_path):
        if not os.path.exists(model_path):
            raise Exception(f"The file {model_path} does not exist!")
    
        self.model = YOLO(model_path)

    async def infer(self, websocket):
        async for message in websocket:
            if not self.is_valid_message(message):
                await websocket.send(json.dumps({'error': 'This is not a valid message!'}))
                continue

            data = json.loads(message)
            files = os.listdir(data['directory_path'])
            images = sanitize_images(files, data['directory_path'])

            for image in images:
                print(image)
                results = self.model(image)

                for result in results:
                    if len(result.boxes) > 0:
                        boxes = []
                        
                        for box in result.boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            boxes.append({'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})

                        await websocket.send(json.dumps({'filename': image, 'boxes': boxes, 'status' : 'boxes'}))
                    else:
                        await websocket.send(json.dumps({'filename': image, 'boxes': [], 'status' : 'boxes'}))
            await websocket.send(json.dumps({'status' : 'finished'}))


    async def main(self):
        self.stop = asyncio.Future()
        # Maybe it's better to check if the port is available for use
        self.server = await websockets.serve(self.infer, 'localhost', 9876) #9876
        try:
            print("Server started")
            Autoload.load_finished = True
            await self.stop
        except asyncio.exceptions.CancelledError:
            print("Server closed")

    def run(self):
        asyncio.run(self.main())

    def close(self):
        self.server.close()
        self.stop.cancel()

    def is_valid_message(self, message):
        if 'directory_path' in message:
            return True
        return False
