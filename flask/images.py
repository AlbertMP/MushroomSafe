from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from torchvision import transforms
from PIL import Image
import torch.nn as nn
from efficientnet_pytorch import EfficientNet
import pandas as pd

# Load the saved EfficientNet-B5 model and metrics
saved_model_path = "./efficientnetb5_epoch10_lr0.0001_bs10.pt"
model_metrics = torch.load(saved_model_path, map_location=torch.device('cpu'))

# Extract the model state dict and metrics
model_state_dict = model_metrics["model_state_dict"]

# Initialize the EfficientNet-B5 model
model = EfficientNet.from_pretrained('efficientnet-b5')
model._fc = nn.Linear(model._fc.in_features, 106)

# Load the model state dict
model.load_state_dict(model_state_dict)
model.eval()

# Define the transformations for image preprocessing
preprocess = transforms.Compose([
    transforms.Resize((456, 456)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Read the Excel file
excel_file = './MO106.xlsx'
df = pd.read_excel(excel_file)

# Extract the folder names from the 'Folder Name' column
folder_names = df['Folder Name'].tolist()

# Define a function to process the folder names and generate class labels
def generate_class_labels(folder_names):
    class_labels = []
    for folder_name in folder_names:
        class_label = folder_name.title()  # Convert to uppercase as class labels
        class_labels.append(class_label)
    return class_labels

# Generate the class labels
labels = generate_class_labels(folder_names)

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

    # Get the corresponding row from the DataFrame
    row = df.loc[class_index]

    # Extract required column values
    predicted_label = labels[class_index]
    edible = row['Type (e: edible, i: inedible)']
    reference = row['Reference Website']
    note = row['Note']

    # Create the response dictionary
    response = {
        'predicted_class': predicted_label,
        'edible': edible,
        'reference': reference,
        'note': note
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=50000)
