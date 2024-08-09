from flask import Flask, render_template, request, send_from_directory, redirect, url_for
import os
from PIL import Image

app = Flask(__name__)
BASE_DIR = '/Users/johnny/dataset'  # Change this to the base directory path

def get_image_info(image_path):
    try:
        with Image.open(image_path) as img:
            return img.format, img.size  # (format, (width, height))
    except Exception as e:
        return None

@app.route('/')
@app.route('/<path:subpath>')
@app.route('/<path:subpath>/page/<int:page>')
def index(subpath='', page=1):
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
    total_images = len(image_files)
    images_per_page = 50
    total_pages = (total_images + images_per_page - 1) // images_per_page

    if page < 1: page = 1
    if page > total_pages: page = total_pages

    start = (page - 1) * images_per_page
    end = start + images_per_page
    image_files = image_files[start:end]
    
    images_info = [(f, get_image_info(os.path.join(dir_path, f))) for f in image_files]
    
    start_page = max(1, page - 5)
    end_page = min(total_pages, page + 4)
    
    return render_template('index.html', directories=directories, images=images_info,
                           current_path=subpath, page=page, total_pages=total_pages,
                           start_page=start_page, end_page=end_page)

@app.route('/images/<path:subpath>/<path:filename>')
def serve_image(subpath, filename):
    file_path = os.path.join(BASE_DIR, subpath, filename)
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(BASE_DIR, subpath), filename)
    else:
        return "File not found", 404

@app.route('/delete/<path:subpath>/<path:filename>', methods=['POST'])
def delete_image(subpath, filename):
    file_path = os.path.join(BASE_DIR, subpath, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return redirect(url_for('index', subpath=subpath))
    else:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True)
