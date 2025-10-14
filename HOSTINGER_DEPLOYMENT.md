# Hostinger Deployment Guide for Agtegra Tractors Hours

## 🚀 Deploy Your Dashboard to Hostinger

### Prerequisites
- Hostinger hosting account with Python support
- cPanel access
- Domain name configured

### Step 1: Prepare Files for Upload

Your project now includes:
- ✅ `app_flask.py` - Flask version of the dashboard
- ✅ `templates/index.html` - Web interface
- ✅ `wsgi.py` - WSGI application file
- ✅ `.htaccess` - Apache configuration
- ✅ `requirements.txt` - Python dependencies

### Step 2: Upload Files to Hostinger

1. **Access cPanel**:
   - Login to your Hostinger account
   - Open cPanel for your domain

2. **Upload Files**:
   - Go to **File Manager**
   - Navigate to `public_html/` (or your domain folder)
   - Upload these files:
     ```
     app_flask.py
     wsgi.py
     .htaccess
     requirements.txt
     templates/
     └── index.html
     ```

### Step 3: Install Python Dependencies

1. **Access Terminal** (if available):
   ```bash
   pip install -r requirements.txt
   ```

2. **Or use Python Selector** in cPanel:
   - Go to **Python Selector**
   - Create/Select Python 3.8+ environment
   - Install packages from requirements.txt

### Step 4: Configure Python Application

1. **In cPanel Python Selector**:
   - **Application root**: `/public_html/`
   - **Application URL**: `yourdomain.com`
   - **Application startup file**: `wsgi.py`
   - **Application Entry point**: `application`

2. **Set Environment Variables** (if needed):
   - `FLASK_ENV=production`
   - `FLASK_APP=app_flask.py`

### Step 5: Configure Domain

1. **Domain Settings**:
   - Point your domain to the application
   - Ensure Python is enabled for your domain

2. **SSL Certificate**:
   - Enable SSL in cPanel for HTTPS access

### Alternative: Manual Setup

If automatic setup doesn't work:

1. **Create Python App**:
   - Use cPanel's **Setup Python App**
   - Choose Python 3.8+
   - Set application root to your domain folder

2. **Update Configuration**:
   - Edit the auto-generated startup file
   - Point it to your `wsgi.py`

### Step 6: Test Your Application

1. **Visit your domain**: `https://yourdomain.com`
2. **Test file upload** with sample CSV
3. **Verify all features work**:
   - CSV upload and processing
   - Interactive charts
   - Data table display
   - CSV export

### Troubleshooting

**Common Issues:**

1. **500 Internal Server Error**:
   - Check file permissions (755 for directories, 644 for files)
   - Verify Python path in wsgi.py
   - Check error logs in cPanel

2. **Module Import Errors**:
   - Ensure all dependencies are installed
   - Check Python version compatibility
   - Verify file paths

3. **File Upload Issues**:
   - Check upload_max_filesize in .htaccess
   - Verify directory permissions
   - Check available disk space

### File Structure on Server

```
public_html/
├── app_flask.py          # Main Flask application
├── wsgi.py              # WSGI entry point
├── .htaccess            # Apache configuration
├── requirements.txt     # Python dependencies
└── templates/
    └── index.html       # Web interface
```

### Performance Optimization

1. **Enable Compression**:
   - Add gzip compression in .htaccess
   - Optimize static files

2. **Caching**:
   - Enable browser caching
   - Use CDN for static assets

3. **Database** (optional):
   - For large datasets, consider MySQL integration
   - Store uploaded data persistently

### Security Considerations

1. **File Upload Security**:
   - Validate file types
   - Limit file sizes
   - Scan uploaded files

2. **Access Control**:
   - Add authentication if needed
   - Restrict sensitive endpoints

### Your Live Dashboard

Once deployed, your Agtegra Tractors Hours dashboard will be accessible at:
**`https://yourdomain.com`**

Features available:
- 🚜 **Drag-and-drop CSV upload**
- 📊 **Interactive visualizations**
- 🎯 **900-hour milestone tracking**
- 📋 **Data table with filtering**
- 💾 **CSV export functionality**
- 📱 **Mobile-responsive design**

### Support

- **Hostinger Documentation**: Check their Python hosting guides
- **Error Logs**: Available in cPanel under "Error Logs"
- **Support**: Contact Hostinger support for server-specific issues