from flask import Flask, request, jsonify
import your_model_module

app = Flask(__name__)

@app.route('/classify', methods=['POST'])
def classify_image():
    file = request.files['image']
    image = your_model_module.preprocess_image(file)  # 预处理图像
    result = your_model_module.predict(image)  # 使用您的模型进行预测
    return jsonify(result)

if __name__ == '__main__':
    app.run()