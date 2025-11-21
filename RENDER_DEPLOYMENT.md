# Render Deployment Guide

This guide covers deploying the Animated GIF Web App to Render.com for production use.

## Prerequisites

- A [Render.com](https://render.com) account
- A GitHub or GitLab repository with this project
- API key and secret key generated for production

## Step 1: Generate Production Keys

Before deployment, generate secure keys for production:

```bash
# Generate API key (keep this secret)
python -c "import secrets; print('GIF_API_KEY=' + secrets.token_hex(32))"

# Generate Flask secret key
python -c "import secrets; print('FLASK_SECRET_KEY=' + secrets.token_hex(32))"
```

## Step 2: Set Up Render Secrets

In your Render dashboard:

1. Go to **Settings** → **Environment**
2. Add two **Environment Secrets**:

   - **gif-api-key**
     - Value: Your generated API key (without the `GIF_API_KEY=` prefix)

   - **flask-secret-key**
     - Value: Your generated Flask secret key (without the `FLASK_SECRET_KEY=` prefix)

## Step 3: Deploy from Repository

1. Go to your Render dashboard
2. Click **New** → **Web Service**
3. Connect your Git repository (GitHub/GitLab)
4. Configure the service (if not auto-detected from `render.yaml`):

   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind "0.0.0.0:$PORT" --workers 1 --timeout 300 app:app`
   - **Health Check Path**: `/health`

5. Set **Instance Type** (Free tier works for testing, upgrade for production traffic)
6. Click **Create Web Service**

## Step 4: Environment Configuration

The `render.yaml` file automatically configures:

- Production environment variables
- Environment secrets mapping
- Health check endpoints
- Proper timeouts for long-running conversions

## Step 5: Access Your App

Once deployed successfully:

1. Get your app URL from Render dashboard (e.g., `https://your-app-name.onrender.com`)
2. Visit the URL in your browser
3. Use the API key you generated to authenticate conversions

## Production Configuration

### Environment Variables
- `FLASK_ENV=production` - Enables production mode
- `GIF_API_KEY` - Required API key for conversions
- `FLASK_SECRET_KEY` - Flask session security
- `MAX_CONTENT_LENGTH=52428800` - 50MB file size limit
- `PYTHONUNBUFFERED=1` - Ensures log output in containers

### Performance Settings
- **Gunicorn Workers**: 1 worker (suitable for free tier)
- **Timeout**: 300 seconds for long video conversions
- **Health Check**: `/health` endpoint for monitoring

### File Handling
- Temporary files stored in system temp directory
- Automatic cleanup of old files (1+ hour old)
- Secure file uploads with validation

## Security Considerations

1. **API Keys**: Store securely in Render secrets, not in code
2. **HTTPS**: Render provides automatic SSL certificates
3. **File Validation**: Server validates file types and sizes
4. **Cleanup**: Temporary files are automatically removed

## Monitoring and Maintenance

### Health Checks
Use the `/health` endpoint to monitor service status:
```
curl https://your-app-name.onrender.com/health
# Should return "OK"
```

### Troubleshooting
- **Build Failures**: Check build logs in Render dashboard
- **Runtime Errors**: Check service logs for detailed error messages
- **Timeout Issues**: Long conversions may timeout on free tier (upgrade plan if needed)

## Scaling for Production

For higher traffic:

1. **Increase Workers**: Adjust `--workers` in start command
2. **Add Caching**: Consider Redis for session/file caching
3. **Upgrade Instance**: Use paid plans for more resources
4. **CDN**: Use Render's CDN for static assets

## Cost Optimization

- **Free-tier Limits**: 750 hours/month, good for testing
- **Automatic Scaling**: Render scales based on traffic
- **Resource Limits**: Monitor memory/disk usage for cost control

## Common Issues & Solutions

### "GIF_API_KEY is required in production"
- Set the `gif-api-key` secret in Render environment settings

### "Conversion Timeout"
- Upgrade to a paid plan with higher timeouts
- Optimize video processing or reduce file size limits

### "Build Failed"
- Check requirements.txt for missing dependencies
- Verify Python version compatibility (3.8+ required)

## Automatic Deployments

After initial setup, any pushes to your main branch will automatically redeploy the application.
