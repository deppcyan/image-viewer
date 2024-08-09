from flask import Flask, render_template, request, send_from_directory
import os
from PIL import Image

app = Flask(__name__)
BASE_DIR = '/Users/johnny/dataset'  # Change this to the base directory path
PER_PAGE = 50

def get_image_info(image_path):
    try:
        with Image.open(image_path) as img:
            return img.format, img.size  # (format, (width, height))
    except Exception as e:
        return None

@app.route('/')
@app.route('/<path:subpath>')
def index(subpath=''):
    dir_path = os.path.join(BASE_DIR, subpath)
    if not os.path.exists(dir_path):
        return "Directory not found", 404

    files = []
    directories = []
    
    for entry in os.listdir(dir_path):
        entry_path = os.path.join(dir_path, entry)
        if os.path.isdir(entry_path):
            directories.append(entry)
        elif os.path.isfile(entry_path):
            files.append(entry)
    
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    images_info = [(f, get_image_info(os.path.join(dir_path, f))) for f in image_files]

    # Pagination
    page = int(request.args.get('page', 1))
    total_images = len(images_info)
    total_pages = (total_images + PER_PAGE - 1) // PER_PAGE
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    images_info_paginated = images_info[start:end]

    return render_template('index.html', directories=directories, images=images_info_paginated, current_path=subpath, page=page, total_pages=total_pages)

@app.route('/images/<path:subpath>/<path:filename>')
def serve_image(subpath, filename):
    file_path = os.path.join(BASE_DIR, subpath, filename)
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(BASE_DIR, subpath), filename)
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
