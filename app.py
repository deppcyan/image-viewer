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

def get_image_tags(tag_path):
    try:
        with open(tag_path, 'r') as file:
            tags = file.read().strip()
            return tags
    except Exception as e:
        return ''

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
    
    images_info = []
    for f in image_files:
        image_path = os.path.join(dir_path, f)
        tag_path = os.path.splitext(image_path)[0] + '.txt'
        tags = get_image_tags(tag_path)
        info = get_image_info(image_path)
        images_info.append((f, info, tags))
    
    return render_template('index.html', directories=directories, images=images_info,
                           current_path=subpath, page=page, total_pages=total_pages)

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
    tag_path = os.path.splitext(file_path)[0] + '.txt'
    if os.path.exists(file_path):
        os.remove(file_path)
    if os.path.exists(tag_path):
        os.remove(tag_path)
    return redirect(url_for('index', subpath=subpath))

if __name__ == '__main__':
    app.run(debug=True)
