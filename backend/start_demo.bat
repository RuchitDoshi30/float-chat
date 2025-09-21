@echo off
echo 🌊 Ocean Chat Backend 2.0 - Demo Setup
echo.

echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🔧 Setting up environment...
if not exist .env (
    copy .env.example .env
    echo ✅ Environment file created
) else (
    echo ✅ Environment file already exists
)

echo.
echo 🚀 Starting Ocean Chat Backend...
echo.
echo Available at: http://localhost:8000
echo Docs at: http://localhost:8000/docs
echo.

python main.py