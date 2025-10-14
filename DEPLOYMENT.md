# Deployment Guide for Agtegra Tractors Hours Dashboard

## Deploy to Render

### Prerequisites
1. Create a [Render account](https://render.com) (free tier available)
2. Have your code in a Git repository (GitHub, GitLab, or Bitbucket)

### Step 1: Prepare Your Repository

Your project now includes the necessary deployment files:
- `Procfile` - Tells Render how to start your app
- `runtime.txt` - Specifies Python version
- `.streamlit/config.toml` - Streamlit configuration for production
- `requirements.txt` - Python dependencies

### Step 2: Push to Git Repository

1. Initialize git repository (if not already done):
```bash
git init
git add .
git commit -m "Initial commit - Agtegra Tractors Hours Dashboard"
```

2. Create a repository on GitHub/GitLab/Bitbucket and push:
```bash
git remote add origin https://github.com/yourusername/agtegra-tractors-hours.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render

1. **Log in to Render**: Go to [render.com](https://render.com) and sign in
2. **Create New Web Service**: Click "New" → "Web Service"
3. **Connect Repository**: Connect your GitHub/GitLab/Bitbucket account and select your repository
4. **Configure Deployment**:
   - **Name**: `agtegra-tractors-hours`
   - **Region**: Choose closest to your location
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Instance Type**: Free (for testing) or Starter ($7/month)

5. **Environment Variables** (Optional):
   - Add any environment variables if needed
   - `STREAMLIT_SERVER_HEADLESS=true`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false`

6. **Deploy**: Click "Create Web Service"

### Step 4: Access Your Dashboard

Once deployed (usually takes 2-5 minutes), you'll get a URL like:
`https://agtegra-tractors-hours.onrender.com`

### Alternative Deployment Options

#### Streamlit Community Cloud (Free)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub repository
3. Select your repository and main file (`app.py`)
4. Deploy with one click

#### Railway (Alternative)
1. Go to [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will auto-detect the Python app and deploy

### Troubleshooting

**Common Issues:**
1. **Port Issues**: Make sure your app uses `$PORT` environment variable
2. **Dependencies**: Ensure all packages are in `requirements.txt`
3. **File Paths**: Use relative paths in your code
4. **Memory Limits**: Free tiers have memory restrictions

**Logs**: Check deployment logs in Render dashboard for any errors

### Production Considerations

1. **Custom Domain**: You can add a custom domain in Render settings
2. **HTTPS**: Render provides free SSL certificates
3. **Environment Variables**: Store sensitive data as environment variables
4. **Scaling**: Upgrade to paid plans for better performance
5. **Monitoring**: Set up health checks and monitoring

### Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **Streamlit Deployment**: [docs.streamlit.io/streamlit-community-cloud](https://docs.streamlit.io/streamlit-community-cloud)

Your Agtegra Tractors Hours dashboard is ready for deployment! 🚀