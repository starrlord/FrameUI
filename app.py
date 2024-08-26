from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
import random
import time
from samsungtvws import SamsungTVWS
import urllib.parse
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Scheduler initialization
scheduler = BackgroundScheduler()
scheduler.start()

# Set default folder path and uploaded files path
FOLDER_PATH = './images/'
UPLOAD_LIST_PATH = './uploaded_files.json'

# Initialize uploaded files list
if os.path.isfile(UPLOAD_LIST_PATH):
    with open(UPLOAD_LIST_PATH, 'r') as f:
        uploaded_files = json.load(f)
else:
    uploaded_files = []

# Read IP from environment variable or set a default
FRAMETV_IP = 'TV_IP_ADDRESS'
tv_ip = os.getenv(FRAMETV_IP, '')

# Global variable to store the next image set time
next_image_set_time = None

# Function to perform the image randomization
def randomize_images(tv_ip, interval):
    global next_image_set_time
    images = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.jpeg')]
    if not images:
        return

    # Pick a random image
    random_image = random.choice(images)
    
    # Set the random image on the TV
    tv = SamsungTVWS(tv_ip)
    
    if not tv.art().supported():
        print('Your TV does not support art mode.')
        return

    file_path = os.path.join(FOLDER_PATH, random_image)
    remote_filename = None

    for uploaded_file in uploaded_files:
        if uploaded_file['file'] == file_path:
            remote_filename = uploaded_file['remote_filename']
            break

    if remote_filename is None:
        with open(file_path, 'rb') as f:
            data = f.read()
        try:
            if random_image.endswith('.jpg'):
                remote_filename = tv.art().upload(data, file_type='JPEG', matte="none")
            elif random_image.endswith('.jpeg'):
                remote_filename = tv.art().upload(data, file_type='JPEG', matte="none")
            elif random_image.endswith('.png'):
                remote_filename = tv.art().upload(data, file_type='PNG', matte="none")
            uploaded_files.append({'file': file_path, 'remote_filename': remote_filename})
            with open(UPLOAD_LIST_PATH, 'w') as f:
                json.dump(uploaded_files, f)
        except Exception as e:
            print(f'Error: {e}')
            return

    tv.art().select_image(remote_filename, show=True)
    print(f'Image {random_image} set successfully.')

    # Update the next image set time
    next_image_set_time = time.time() + interval

# Home route to render gallery
@app.route('/')
def index():
    images = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.jpg') or f.endswith('.png')]
    return render_template('index.html', images=images, tv_ip=tv_ip)

# Route to serve images
@app.route('/images/<filename>')
def serve_image(filename):
    decoded_filename = urllib.parse.unquote(filename)  # Decode the filename
    return send_from_directory(FOLDER_PATH, decoded_filename)

# API route to set the image on FrameTV
@app.route('/set_image', methods=['POST'])
def set_image():
    data = request.json
    filename = urllib.parse.unquote(data['filename'])  # Decode the filename
    tv_ip = data['tv_ip']

    tv = SamsungTVWS(tv_ip)

    if not tv.art().supported():
        print('Your TV does not support art mode.')
        return

    file_path = os.path.join(FOLDER_PATH, filename)
    remote_filename = None

    for uploaded_file in uploaded_files:
        if uploaded_file['file'] == file_path:
            remote_filename = uploaded_file['remote_filename']
            break

    if remote_filename is None:
        with open(file_path, 'rb') as f:
            data = f.read()
        try:
            if filename.endswith('.jpg'):
                remote_filename = tv.art().upload(data, file_type='JPEG', matte="none")
            elif filename.endswith('.jpeg'):
                remote_filename = tv.art().upload(data, file_type='JPEG', matte="none")
            elif filename.endswith('.png'):
                remote_filename = tv.art().upload(data, file_type='PNG', matte="none")
            uploaded_files.append({'file': file_path, 'remote_filename': remote_filename})
            with open(UPLOAD_LIST_PATH, 'w') as f:
                json.dump(uploaded_files, f)
        except Exception as e:
            print(f'Error: {e}')
            return

    tv.art().select_image(remote_filename, show=True)
    print(f'Image {filename} set successfully.')

    return jsonify({'success': True, 'filename': filename})

# API route to set the environment variable for TV IP
@app.route('/set_tv_ip', methods=['POST'])
def set_tv_ip():
    data = request.json
    new_ip = data.get('tv_ip')
    
    if new_ip:
        os.environ[FRAMETV_IP] = new_ip  # Set the environment variable
        return jsonify({'success': True, 'new_ip': new_ip})
    else:
        return jsonify({'error': 'Invalid IP address'}), 400

# API route to start randomizing images at intervals
@app.route('/start_randomize', methods=['POST'])
def start_randomize():
    data = request.json
    interval = data.get('interval')
    tv_ip = os.getenv(FRAMETV_IP)

    if not tv_ip:
        return jsonify({'error': 'IP address is not set.'}), 400

    if not interval or not isinstance(interval, int) or interval <= 0:
        return jsonify({'error': 'Invalid interval value.'}), 400

    # Clear any existing job
    scheduler.remove_all_jobs()

    # Schedule a new job
    scheduler.add_job(func=randomize_images, trigger='interval', seconds=interval, args=[tv_ip, interval])

    # Set the next image set time
    global next_image_set_time
    next_image_set_time = time.time() + interval

    return jsonify({'success': True, 'message': f'Randomization started with an interval of {interval} seconds.', 'next_image_time': next_image_set_time})

# API route to get current status (time left and current image)
@app.route('/current_status', methods=['GET'])
def current_status():
    global next_image_set_time

    # Determine time left until next image is set
    if next_image_set_time:
        time_left = max(0, int(next_image_set_time - time.time()))
    else:
        time_left = None

    # Get the last set image (we'll just take the last file in the uploaded files list for simplicity)
    current_image = uploaded_files[-1]['file'] if uploaded_files else None

    return jsonify({
        'time_left': time_left,
        'current_image': current_image
    })

if __name__ == '__main__':
    app.run(debug=True, port=7980)
