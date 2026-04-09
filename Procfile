web: python manage.py collectstatic --noinput && gunicorn backend.wsgi:application
release: python manage.py migrate