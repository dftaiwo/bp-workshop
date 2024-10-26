import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image
import io

app = Flask(__name__)

# Configure Google Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'files[]' not in request.files:
        return jsonify({"error": "No files uploaded"})
    
    files = request.files.getlist('files[]')
    if not files or files[0].filename == '':
        return jsonify({"error": "No selected files"})
    
    images = []
    for file in files:
        if file and allowed_file(file):
            image_data = Image.open(file.stream)
            images.append(image_data)
    
    if not images:
        return jsonify({"error": "No valid image files"})
    
    response = analyze_multiple_images(images)
    return jsonify({"result": response.text})


def analyze_multiple_images(images):
    prompt = "Analyze the attached images of digital blood pressure monitors. For each image, extract the following three key values from the display:\
1. **Systolic**: The upper blood pressure reading (usually the larger number).\
2. **Diastolic**: The lower blood pressure reading (usually the smaller number).\
3. **Pulse**: The heart rate reading, typically labeled as Pulse or represented by a heart symbol.\
Provide a high-level summary for a non-medical person, easy to understand in one sentence, followed by another sentence with a recommendation on what to do next, if any.\
Provide the results in a JSON object with the following keys: readings (an array of objects, each containing systolic, diastolic, pulse for each image), summary"

    return model.generate_content([prompt] + images,
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )

def allowed_file(file_object):
    filename = file_object.filename
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

