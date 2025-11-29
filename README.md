python -m venv myenv
pip install -r requirements.txt

create .env

.env --> SECRET_KEY = python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

py manage.py makemigrations
py manage.py makemigrations airline
py manage.py migrate
py manage.py createsample
py manage.py runserver
