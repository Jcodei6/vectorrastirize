import os
import uuid
from flask import Flask, render_template, request, jsonify, send_file
import vtracer

app = Flask(__name__)
# Set up folders for temporary uploads and outputs
UPLOAD_FOLDER = 'temp_uploads'
OUTPUT_FOLDER = 'temp_outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Serve the main HTML page
    return render_template('index.html')

@app.route('/vectorize', methods=['POST'])
def vectorize():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Grab user settings from the frontend sliders
    colormode = request.form.get('colormode', 'color')
    mode = request.form.get('mode', 'spline')
    color_precision = int(request.form.get('color_precision', 6))
    corner_threshold = int(request.form.get('corner_threshold', 60))

    # Save the uploaded file temporarily
    file_id = str(uuid.uuid4())
    input_ext = os.path.splitext(file.filename)[1]
    input_path = os.path.join(UPLOAD_FOLDER, f"{file_id}{input_ext}")
    output_path = os.path.join(OUTPUT_FOLDER, f"{file_id}.svg")
    
    file.save(input_path)

    try:
        # Run the vectorization engine
        vtracer.convert_image_to_svg(
            input_path, 
            output_path,
            colormode=colormode,
            mode=mode,
            color_precision=color_precision,
            corner_threshold=corner_threshold,
            hierarchical='stacked'
        )
        
        # Clean up the input file
        if os.path.exists(input_path):
            os.remove(input_path)
            
        # Return the URL where the user can download the SVG
        return jsonify({'success': True, 'svg_url': f'/download/{file_id}.svg'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
