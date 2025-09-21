#!/bin/bash
# SIH Demo Setup Script (Windows PowerShell version)

# Create: demo_setup.ps1

Write-Host "🌊 Setting up OceanChat for SIH Demo..." -ForegroundColor Cyan

# Navigate to project directory
Set-Location "C:\Users\ruchit\SIH\SIH 2025\ocean-chat-v2\ocean-chat-backend-v2"

# Start backend server
Write-Host "🚀 Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-Command", "cd backend; python main.py" -WindowStyle Minimized

# Wait for backend to start
Start-Sleep -Seconds 10

# Start frontend
Write-Host "🎨 Starting frontend..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-Command", "cd frontend; streamlit run app.py" -WindowStyle Minimized

# Wait for frontend to start
Start-Sleep -Seconds 15

# Open browser
Write-Host "🌐 Opening OceanChat..." -ForegroundColor Yellow
Start-Process "http://localhost:8501"

# Test API endpoint
Write-Host "🔍 Testing API..." -ForegroundColor Magenta
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" -Method Get
    Write-Host "✅ API Status: " -NoNewline -ForegroundColor Green
    Write-Host $response.status -ForegroundColor White
} catch {
    Write-Host "❌ API Test Failed" -ForegroundColor Red
}

Write-Host "🎯 Demo setup complete! Ready for SIH presentation!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host "Backend: http://localhost:8000" -ForegroundColor Cyan

# Keep window open
Read-Host "Press Enter to continue..."