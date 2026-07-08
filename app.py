import os
import cv2
import numpy as np
import vtracer
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Create a temporary folder to hold images while they are being converted
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    # This serves your index.html file
    return render_template('index.html')

@app.route('/vectorize', methods=['POST'])
def vectorize():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    # Grab the slider settings from the web interface
    color_mode = request.form.get('color_mode', 'color')
    corner_threshold = int(request.form.get('corner_threshold', 60))
    filter_speckle = int(request.form.get('filter_speckle', 4))
    
    # Secure the filename and set up input/output paths
    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    output_filename = os.path.splitext(filename)[0] + '.svg'
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
    
    # Save the uploaded raster image to the server temporarily
    file.save(input_path)
    
    try:
        # Run the vectorization engine
        vtracer.convert_image_to_svg(
            input_path,
            output_path,
            colormode=color_mode,
            hierarchical='stacked',
            mode='spline',
            filter_speckle=filter_speckle,
            corner_threshold=corner_threshold
        )
        
        # Send the generated SVG back to the browser for download
        return send_file(output_path, mimetype='image/svg+xml', as_attachment=False)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Delete the raster file immediately so your server doesn't get bloated
        if os.path.exists(input_path):
            os.remove(input_path)
        # Note: The SVG output_path is kept briefly so the browser can read it. 

if __name__ == '__main__':
    app.run(debug=True, port=5000)
