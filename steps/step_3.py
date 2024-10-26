import os
from flask import Flask, render_template, request, jsonify
from PIL import Image
import io
import google.generativeai as genai
app = Flask(__name__)


# Configure Google Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')


@app.route('/', methods=['GET'])
def index():
    return render_template('steps.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    
    if not file or not allowed_file(file):
        return jsonify({"error": "Invalid file type"})

    # A valid image is uploaded, so now let's process it
    
    image_data = Image.open(file.stream)
    response = analyze_image(image_data)            
    return jsonify({"result": response.text})



def analyze_image(image):
    prompt = "Analyze the attached image of a digital blood pressure monitor. Extract the following three key values from the display:\
1. **Systolic**: The upper blood pressure reading (usually the larger number).\
2. **Diastolic**: The lower blood pressure reading (usually the smaller number).\
3. **Pulse**: The heart rate reading, typically labeled as Pulse or represented by a heart symbol.\
High level summary for a non-medical person, easy to understand in one sentence, followed by another sentence with a recommendation on what to do next, if any\
Provide the results in a JSON object with the following keys: systolic, diastolic, pulse, summary"

    return model.generate_content([prompt, image],
        generation_config=genai.GenerationConfig(
            response_mime_type="application/json"
        )
    )

     
def allowed_file(file_object):
    # Check if the filename has an extension in the allowed list and is a valid image
    filename = file_object.filename
    if not '.' in filename or filename.rsplit('.', 1)[1].lower() not in {'png', 'jpg', 'jpeg', 'gif'}:
        return False
    
    try:
        # Attempt to open and verify the image
        img = Image.open(file_object.stream)
        img.verify()  # Verify that it's a valid image file
        file_object.stream.seek(0)  # Reset file pointer
        return True
    except Exception as e:
        # If any exception occurs during image verification, consider the file invalid
        return False

if __name__ == '__main__':
     app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
