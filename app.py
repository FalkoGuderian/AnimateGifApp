#!/usr/bin/env python3
"""
Animated GIF Web Generator - Flask Application

Web interface for converting videos to animated GIFs with professional UI.
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import os
import uuid
import tempfile
from werkzeug.utils import secure_filename
from threading import Thread
import time
import logging
from pathlib import Path
from functools import wraps
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import modified video processing function
from video_to_gif import convert_video_to_gif_web

app = Flask(__name__)

# Production configuration from environment variables
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'development-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024))  # 50MB default
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Configure logging based on environment
log_level = logging.INFO if os.environ.get('FLASK_ENV') == 'production' else logging.DEBUG
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Log to stdout for production containers
    ]
)
logger = logging.getLogger(__name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv', 'webm'}

# API Key Configuration - required for production
API_KEY = os.environ.get('GIF_API_KEY')
if not API_KEY and os.environ.get('FLASK_ENV') == 'production':
    logger.error("GIF_API_KEY environment variable must be set in production")
    raise ValueError("GIF_API_KEY is required in production environment")
elif not API_KEY:
    API_KEY = 'development-api-key-change-in-production'
    logger.warning("Using default API key - change in production!")

# Global progress tracking
conversion_tasks = {}

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header or form
        api_key = request.headers.get('X-API-Key') or request.form.get('api_key')

        if not api_key:
            return jsonify({
                'error': 'API key required for conversion',
                'message': 'Please provide a valid API key in the authentication section on the web page to use the video conversion service.',
                'help': 'Contact your administrator to obtain a valid API key.'
            }), 401

        if api_key != API_KEY:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid. Please check your key and try again.',
                'help': 'Make sure you have the correct API key from your administrator.'
            }), 403

        return f(*args, **kwargs)
    return decorated_function

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def cleanup_old_files():
    """Clean up temporary files older than 1 hour"""
    temp_dir = Path(tempfile.gettempdir())
    current_time = time.time()

    for file_path in temp_dir.glob("flask_gif_*"):
        if file_path.stat().st_mtime < current_time - 3600:
            try:
                file_path.unlink()
            except OSError:
                pass

def background_convert(input_path, output_path, params, job_id):
    """Run video conversion in background thread"""
    try:
        # Update progress
        conversion_tasks[job_id] = {'status': 'processing', 'progress': 0}

        # Convert video with progress callback
        success = convert_video_to_gif_web(
            input_path=input_path,
            output_path=output_path,
            fps=params.get('fps', 10),
            scale=params.get('scale', 0.5),
            start_time=params.get('start_time', 0.0),
            duration=params.get('duration', None),
            loops=params.get('loops', 0),
            speed=params.get('speed', 1.0),
            progress_callback=lambda p: update_progress(job_id, p)
        )

        if success:
            conversion_tasks[job_id].update({'status': 'completed', 'progress': 100})
        else:
            conversion_tasks[job_id].update({'status': 'failed', 'progress': 0, 'error': 'Conversion failed'})

    except Exception as e:
        logger.error(f"Conversion error for job {job_id}: {e}")
        conversion_tasks[job_id].update({'status': 'failed', 'progress': 0, 'error': str(e)})
    finally:
        # Cleanup input file after conversion
        try:
            if os.path.exists(input_path):
                os.unlink(input_path)
        except OSError:
            pass

def update_progress(job_id, progress):
    """Update conversion progress"""
    if job_id in conversion_tasks:
        conversion_tasks[job_id]['progress'] = progress

@app.route('/')
def index():
    """Main page"""
    cleanup_old_files()  # Clean up old temp files on each request
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
@require_api_key
def convert():
    """Handle video conversion request"""
    if 'video' not in request.files:
        flash('No video file provided')
        return redirect(url_for('index'))

    file = request.files['video']
    if file.filename == '':
        flash('No video selected')
        return redirect(url_for('index'))

    if not file or not allowed_file(file.filename):
        flash('Invalid file type. Please upload MP4, AVI, MOV, MKV, or WebM.')
        return redirect(url_for('index'))

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Save uploaded file temporarily
    filename = secure_filename(file.filename)
    temp_input = os.path.join(tempfile.gettempdir(), f"flask_gif_input_{job_id}_{filename}")
    file.save(temp_input)

    # Prepare output path
    output_filename = f"flask_gif_output_{job_id}.gif"
    temp_output = os.path.join(tempfile.gettempdir(), output_filename)

    # Get conversion parameters from form
    params = {
        'fps': int(request.form.get('fps', 10)),
        'scale': float(request.form.get('scale', 0.5)),
        'start_time': float(request.form.get('start_time', 0.0)),
        'duration': float(request.form.get('duration', '')) if request.form.get('duration') else None,
        'loops': int(request.form.get('loops', 0)),
        'speed': float(request.form.get('speed', 1.0))
    }

    # Start background conversion
    thread = Thread(target=background_convert, args=(temp_input, temp_output, params, job_id))
    thread.daemon = True
    thread.start()

    # Store job info
    conversion_tasks[job_id] = {
        'status': 'processing',
        'progress': 0,
        'output_filename': output_filename
    }

    return jsonify({'job_id': job_id})

@app.route('/progress/<job_id>')
def progress(job_id):
    """Get conversion progress"""
    if job_id in conversion_tasks:
        return jsonify(conversion_tasks[job_id])
    return jsonify({'error': 'Job not found'}), 404

@app.route('/download/<job_id>')
def download(job_id):
    """Download completed GIF"""
    if job_id not in conversion_tasks:
        return 'Job not found', 404

    task = conversion_tasks[job_id]
    if task.get('status') != 'completed':
        return 'Conversion not completed or failed', 400

    output_path = os.path.join(tempfile.gettempdir(), task['output_filename'])
    if not os.path.exists(output_path):
        return 'Output file not found', 404

    # Send file and schedule cleanup
    response = send_file(output_path, as_attachment=True, download_name=f"converted_gif_{int(time.time())}.gif")

    # Remove task after download (cleanup will happen automatically later)
    del conversion_tasks[job_id]

    return response

@app.route('/health')
def health():
    """Health check endpoint"""
    return 'OK', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
