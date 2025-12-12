# Deployment Guide

## Streamlit Cloud (Recommended)

### Prerequisites

- GitHub account
- Repository pushed to GitHub

### Steps

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select your repository: `alanjonesit/FitNotes2Hevy`
5. Set main file path: `app.py`
6. Click "Deploy"

Your app will be live at: `https://[your-app-name].streamlit.app`

### Configuration

Streamlit Cloud automatically:

- Installs dependencies from `requirements.txt`
- Runs `app.py`
- Provides HTTPS
- Auto-deploys on git push

## Local Installation

### For Development

```bash
# Clone repository
git clone https://github.com/alanjonesit/FitNotes2Hevy.git
cd FitNotes2Hevy

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install web dependencies
pip install -e ".[web]"

# Run web app
streamlit run app.py
```

### For CLI Usage Only

```bash
pip install -e .
python scripts/convert.py -i your_file.csv
```

## Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[web]"

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t fitnotes2hevy .
docker run -p 8501:8501 fitnotes2hevy
```
