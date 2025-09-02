# Website Status Checker

A simple Django app to check if websites are up or down with live screenshots.

## Features
- Check website status (up/down)
- Response time monitoring
- Live website screenshots
- Clean Google-like interface

## Installation

1. Clone and setup:
```bash
django-admin startproject website_checker
cd website_checker
django-admin startapp checker
```

2. Install requirements:
```bash
pip install Django requests
```

3. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Start server:
```bash
python manage.py runserver
```

5. Open http://127.0.0.1:8000/

## Usage
1. Enter any website URL (google.com, https://github.com, etc.)
2. Click "Check Status"
3. View results with screenshot

## Requirements
- Django 4.2.7
- requests 2.31.0

That's it! Simple and fast website monitoring.