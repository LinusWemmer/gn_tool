redis-server &  # Start Redis in the background
gunicorn --bind "0.0.0.0:80" "__init__:app"  # Start your Flask app
