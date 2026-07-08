import os
import tempfile
import vtracer
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vectorize', methods=['POST'])
def vectorize():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    color_mode = request.form.get('color_mode', 'color')
    corner_threshold = int(request.form.get('corner_threshold', 60))
    filter_speckle = int(request.form.get('filter_speckle', 4))
    
    # FIX: Use Python's tempfile library for safe cloud server storage
    temp_dir = tempfile.gettempdir()
    filename = secure_filename(file.filename)
    input_path = os.path.join(temp_dir, filename)
    output_path = os.path.join(temp_dir, os.path.splitext(filename)[0] + '.svg')
    
    try:
        # 1. Save the file to the cloud's temporary directory
        file.save(input_path)
        
        # 2. Run the math engine
        vtracer.convert_image_to_svg(
            input_path,
            output_path,
            colormode=color_mode,
            hierarchical='stacked',
            mode='spline',
            filter_speckle=filter_speckle,
            corner_threshold=corner_threshold
        )
        
        # 3. Send it back to the browser
        return send_file(output_path, mimetype='image/svg+xml', as_attachment=False)
        
    except Exception as e:
        # This prints the exact error into your Render logs so we can see it if it fails again
        print(f"VECTORIZATION ERROR: {str(e)}") 
        return jsonify({'error': str(e)}), 500
        
    finally:
        # Clean up the heavy raster file so your server doesn't get bloated
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
