# 🥘 Recipe Management API

A Django-based RESTful API for managing and sharing recipes. This project is part of the ALX Software Engineering curriculum.

## 🚀 Features

- User authentication (with superuser access)
- Recipe creation, update, and deletion
- Ingredient and category management (planned)
- REST API using Django Rest Framework (DRF)

---

## 🧰 Tech Stack

- Python 3.12
- Django
- Django Rest Framework (DRF)
- SQLite (default, switchable to PostgreSQL)
- Docker (optional, planned)

---

## ⚙️ Setup Instructions

### 1. Clone the repository

git clone https://github.com/Selaelo2/recipe-management-api.git
cd recipe-management-api

python -m venv venv
.\venv\Scripts\activate

 ### Install dependencies
pip install -r requirements.txt

### Apply migrations

python manage.py makemigrations
python manage.py migrate

### Create a superuser
python manage.py createsuperuser

### Run the development server
python manage.py runserver





