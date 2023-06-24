from flask import Flask, request
from flask_cors import CORS
import torch
from torchvision import models, transforms
from PIL import Image

# Load the pre-trained ImageNet model
model = models.resnet50(pretrained=True)
model.eval()

# Define the transformations for image preprocessing
preprocess = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Define the class labels
with open('imagenet_class.txt') as f:
    lines = f.readlines()

labels = [line.strip()[1:-2] for line in lines]

app = Flask(__name__)
CORS(app)

@app.route('/images', methods=['POST'])
def images():
    if 'file' not in request.files:
        return 'No file uploaded', 400

    file = request.files['file']
    image = Image.open(file)
    image = preprocess(image)
    image = image.unsqueeze(0)

    # Pass the image through the model
    with torch.no_grad():
        outputs = model(image)

    # Get the predicted class
    _, predicted = torch.max(outputs, 1)
    class_index = predicted.item()

    # Convert class index to a human-readable label
    predicted_label = labels[class_index]

    return f'Predicted class: {predicted_label}'

if __name__ == '__main__':
    app.run(debug=True)
