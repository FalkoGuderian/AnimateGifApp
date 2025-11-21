# Animated GIF Generator with API Key Authentication

A Flask web application for converting videos to animated GIFs with secure API key authentication.

<img width="872" height="556" alt="image" src="https://github.com/user-attachments/assets/d5dcdd77-c75e-4ee3-94c6-048421ec4239" />

## Status

🟢 **Live Demo:** https://animategifapp.onrender.com/
- ✅ API key authentication working
- ✅ Video conversion with speed control functional
- ✅ Real-time progress tracking active
- ✅ Secure environment variable configuration loaded

## Features

- 🖼️ Convert videos to animated GIFs
- 🔐 **Secure API key authentication** (required for all conversions)
- ⚡ **Speed control** (0.1x to 4.0x playback speed for file size optimization)
- 🎛️ **Advanced conversion settings** (FPS, scale, start time, duration, loops)
- 📱 **Responsive web interface** with professional design
- 🔄 **Real-time conversion progress** with detailed status updates
- 🧹 **Automatic cleanup** of temporary files
- ✅ **Input validation** and error handling

### Authentication & Settings
<img width="882" height="788" alt="image" src="https://github.com/user-attachments/assets/0ebe4d91-502f-4707-a168-3442f39040b5" />

## Supported Formats

- MP4, AVI, MOV, MKV, WebM
- Maximum file size: 50MB

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

#### Option A: Using .env file (Recommended)

```bash
cp .env.example .env
```

Edit `.env` with your secure API key:

```bash
# Generate a secure API key (recommended)
python -c "import secrets; print(secrets.token_hex(32))"

# Update .env file
GIF_API_KEY=your-generated-secure-api-key-here
FLASK_SECRET_KEY=your-flask-secret-key-here
```

#### Option B: Environment Variables

```bash
export GIF_API_KEY="your-secure-api-key-here"
export FLASK_SECRET_KEY="your-flask-secret-key-here"
```

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:8000` in your browser.

## API Key Authentication

The application requires an API key for video conversion. This provides:

- 🔒 **Security**: Prevents unauthorized access
- 📊 **Rate Limiting**: Ability to track usage
- 🛡️ **Access Control**: Only authorized users can convert videos

### Setting the API Key

1. **Environment Variable**: Set `GIF_API_KEY` environment variable
2. **Web Interface**: Enter the API key in the authentication field on the main page

### API Key in Requests

The API key can be provided via:
- **HTTP Header**: `X-API-Key: your-api-key`
- **Form Field**: `api_key=your-api-key`

## Usage

1. **Open** the web application
2. **Enter API Key** in the authentication section (required)
3. **Upload** a video file
4. **Configure** conversion settings:
   - **Frame Rate**: Animation smoothness (10-15 recommended)
   - **Scale Factor**: Size reduction (0.3-0.7 for web optimization)
   - **Speed Multiplier**: Playback speed (2.0 = 2x faster, smaller files)
   - **Start Time/Duration**: Video segment selection
   - **Loop Count**: Playback repetitions
5. **Click** "Convert to GIF"
6. **Monitor** progress and download when complete

## Conversion Parameters

| Parameter | Range | Description |
|-----------|-------|-------------|
| FPS | 1-30 | Frames per second (smoothness vs file size) |
| Scale | 0.1-1.0 | Size reduction factor |
| Start Time | 0+ | Seconds from video start |
| Duration | 0+ | Clip length in seconds |
| Loops | 0+ | Repetition count (0 = infinite) |
| Speed | 0.1-4.0 | Playback multiplier (2.0 = 2x faster) |

## Security Notes

- ✅ API keys are stored securely in environment variables
- ✅ File uploads are validated for type and size
- ✅ Temporary files are automatically cleaned up
- ✅ HTTPS recommended for production deployment

## Troubleshooting

**"Conversion Failed" Error**
- Check that your API key is correct
- Ensure video file is valid and under 50MB
- Verify supported format (MP4, AVI, MOV, MKV, WebM)

**"API key required" Error**
- Set the `GIF_API_KEY` environment variable
- Enter the correct API key in the web interface

## Production Deployment

For production deployment to Render.com, see the detailed [Render Deployment Guide](RENDER_DEPLOYMENT.md).

### Quick Production Setup

1. **Generate secure keys** (run locally):
   ```bash
   python -c "import secrets; print('GIF_API_KEY=' + secrets.token_hex(32))"
   python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
   ```

2. **Deploy to Render** following the [step-by-step guide](RENDER_DEPLOYMENT.md)

3. **Configure API key** in Render environment secrets as `gif-api-key`

### Production Features

- ✅ **Gunicorn WSGI server** for production serving
- ✅ **Environment-based configuration** (no hardcoded secrets)
- ✅ **Health checks** for monitoring
- ✅ **Automatic HTTPS** via Render
- ✅ **Secure file handling** with validation
- ✅ **Automatic cleanup** of temporary files

## License

See LICENSE file in the parent directory.
