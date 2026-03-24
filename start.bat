@echo off
title Aegis.AI Launcher
echo Starting Aegis.AI Services...

echo [1/3] Starting Django Backend...
start "Django Backend" cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver"

echo [2/3] Starting Celery Worker...
start "Celery Worker" cmd /k "cd backend && venv\Scripts\activate && celery -A config worker -l info --pool=solo"

echo [3/3] Starting Next.js Frontend...
start "Next.js Frontend" cmd /k "cd frontend && npm run dev"

echo All services are starting up in separate windows!
pause
