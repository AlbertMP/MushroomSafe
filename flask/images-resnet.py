from flask import Flask, request, jsonify
from flask_cors import CORS
from torchvision import transforms
from PIL import Image
import torch.nn as nn
from efficientnet_pytorch import EfficientNet
import pandas as pd
import torch
from torch import nn
from torchvision.models import resnet50
from torchvision.datasets import ImageFolder
from torchvision.transforms import transforms
from torch.utils.data import DataLoader
from torch.utils.data import random_split
import time
import numpy as np
import matplotlib.pyplot as plt
from torchvision.ops import FeaturePyramidNetwork
import torch.nn.functional as F
from torchvision.ops import FeaturePyramidNetwork

import warnings

# Ignore all UserWarnings
warnings.filterwarnings("ignore", category=UserWarning)


class ResNetFPN(nn.Module):
    def __init__(self, num_classes):
        super(ResNetFPN, self).__init__()
        
        # Load pretrained ResNet model
        self.backbone = resnet50(pretrained=True)
        
        # Get the output size of different layers in ResNet
        self.conv1 = self.backbone.conv1
        self.bn1 = self.backbone.bn1
        self.relu = self.backbone.relu
        self.maxpool = self.backbone.maxpool
        self.layer1 = self.backbone.layer1
        self.layer2 = self.backbone.layer2
        self.layer3 = self.backbone.layer3
        self.layer4 = self.backbone.layer4
        
        # Use Feature Pyramid Network
        self.fpn = FeaturePyramidNetwork(in_channels_list=[256, 512, 1024, 2048],
                                          out_channels=256)
        
        # Classification layers for each FPN output
        self.fc1 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU())
        self.fc2 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU())
        self.fc3 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU())
        self.fc4 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU())
        # self.fc1 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU(), nn.Dropout(0.5))
        # self.fc2 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU(), nn.Dropout(0.5))
        # self.fc3 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU(), nn.Dropout(0.5))
        # self.fc4 = nn.Sequential(nn.Linear(256, num_classes), nn.ReLU(), nn.Dropout(0.5))
        
        # Final classification layer
        self.fc_final = nn.Linear(num_classes * 4, num_classes)

        # self.weights = nn.Parameter(torch.ones(4, dtype=torch.float32), requires_grad=True)  # Learnable weights

    def forward(self, x):
        # ResNet part
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.maxpool(x)
        x1 = self.layer1(x)
        x2 = self.layer2(x1)
        x3 = self.layer3(x2)
        x4 = self.layer4(x3)
        
        # FPN part
        features = self.fpn({"0": x1, "1": x2, "2": x3, "3": x4})
        
        # Classification part
        out1 = self.fc1(F.adaptive_avg_pool2d(features["0"], (1, 1)).view(x.size(0), -1))
        out2 = self.fc2(F.adaptive_avg_pool2d(features["1"], (1, 1)).view(x.size(0), -1))
        out3 = self.fc3(F.adaptive_avg_pool2d(features["2"], (1, 1)).view(x.size(0), -1))
        out4 = self.fc4(F.adaptive_avg_pool2d(features["3"], (1, 1)).view(x.size(0), -1))
        
        # Concatenate the classification results of each FPN output
        out = torch.cat((out1, out2, out3, out4), dim=1)
        # weights = F.softmax(self.weights, dim=0)
        # out = torch.cat([out1 * weights[0], out2 * weights[1], out3 * weights[2], out4 * weights[3]], dim=1)
        
        # Final classification
        out = self.fc_final(out)
        
        return out


# Load the saved EfficientNet-B5 model and metrics
saved_model_path = "../model/results/resnet_aug_weightfpn_epoch25_lr5e-05_bs150.pt"
model_metrics = torch.load(saved_model_path, map_location=torch.device('cpu'))

# Extract the model state dict and metrics
model_state_dict = model_metrics["model_state_dict"]

# Initialize the EfficientNet-B5 model
model = ResNetFPN(106)

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
