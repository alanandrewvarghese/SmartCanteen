# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-5ag^#^0oq#s4#m+xhjivahzwj%oi=#tywub_x#6c=euy_$a#0v'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # Set to False in production

ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Add the appropriate hosts for production

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Or your database engine (e.g., postgresql, sqlite3)
        'NAME': 'canteen',  # Your database name
        'USER': 'root',  # Your database username
        'PASSWORD': 'root',  # Your database password
        'HOST': 'localhost',  # Your database host
        'PORT': '3306',  # Your database port
    }
}
