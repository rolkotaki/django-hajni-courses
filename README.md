# Django Hajni Courses
[![Run Tests](https://github.com/rolkotaki/django-hajni-courses/actions/workflows/run_tests.yml/badge.svg)](https://github.com/rolkotaki/django-hajni-courses/actions/workflows/run_tests.yml)
[![codecov](https://codecov.io/gh/rolkotaki/django-hajni-courses/graph/badge.svg?token=8OETE8FHJJ)](https://codecov.io/gh/rolkotaki/django-hajni-courses)
<br><br>Website for a teacher providing online courses.
<br>It's available in the following address: https://kepzesmindenkinek.eu/
<br><br>(I substantially reused code from my other, more detailed and worked out [repository](https://github.com/rolkotaki/django-dog-grooming).)

## Description

This website is intended to satisfy the needs of a Hungarian teacher giving online courses.<br>
The main feautres of the website are:
* Sign up and log in
* Personal data and password change
* Apply for courses
* Contact

## Run With Docker Compose

Download the source code and go to the root of the repository.<br>
Run docker compose to start a clean instance of the website. The database data is mapped into the `docker/postgres_data` folder, so changes will be kept if you 
run it again.
```
docker-compose up -d
```
Open in the browser: [127.0.0.1:8000](http://127.0.0.1:8000/)

Stop and remove all containers:
```
docker-compose down
```

## Run Locally

The settings expect you to have PostgreSQL, so make sure that you have it running either locally or in a Docker container 
for example. You can use the image from the docker compose file.<br>
Run the following init script to prepare the application database user and the database:
```
CREATE DATABASE hajni_courses_website;
CREATE USER hajni_courses_user WITH password 'yoursecretpassword';
ALTER ROLE hajni_courses_user SET client_encoding TO 'utf8';
ALTER ROLE hajni_courses_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE hajni_courses_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hajni_courses_website TO hajni_courses_user;
ALTER DATABASE hajni_courses_website OWNER TO hajni_courses_user;
ALTER ROLE hajni_courses_user createdb;
```
*Feel free to use a different database and change the database settings in the `settings.py`.*<br>

For emails I use [MailerSend](https://www.mailersend.com/), but feel free to use what you prefer and change the settings and your code accordingly.

Download the source code and go to the root of the repository.<br>

Add a `config.yml` file to store your database and email config or use environment variables *(check the settings in the `settings.py`)*:
```
postgresql_hajni_courses:
  name: hajni_courses_website
  user: hajni_courses_user
  password: yoursecretpassword
  host: localhost
  port: 5432
  test_db_name: hajni_courses_website_test

hajni_courses_email:
  mailersend_api_key: YOUR_API_KEY
  sender: sender@mail.com
  admins:
    first_admin_name: first_admin@mail.com
```

Create the virtual environment and install the requirements:
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```
Apply the migrations:
```
python3 manage.py migrate
```
Create the superuser:
```
python3 manage.py createsuperuser
```
Run the server (by default it will run on port 8000):
```
python3 manage.py runserver
```
Open in the browser: [127.0.0.1:8000](http://127.0.0.1:8000/)

## Run Tests

Run all the tests from the repository root:
```
python3 manage.py test
```
Run tests with coverage:
```
coverage run manage.py test
coverage html
```

## Multilanguage Management

Currently, the website is only in Hungarian, but it's prepared to add another langauge (or more) easily.

<br>
Python version used for the development: Python 3.12.1