# 🎬 Videoflix

Videoflix is a Django-based video streaming platform with JWT authentication, HLS video streaming, and email-based user registration.

This guide provides step-by-step instructions to set up the project locally using Docker.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Clone the repository](#clone-the-repository)
3. [Environment Variables](#environment-variables)
4. [Docker Setup](#docker-setup)
5. [Running the Project](#running-the-project)
6. [Accessing the Application](#accessing-the-application)
7. [Additional Notes](#additional-notes)

---

## Prerequisites

Before setting up the project, make sure the following are installed:

- [Git](https://git-scm.com/)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Optional: Python 3.11+ if running locally without Docker

---

## Clone the repository

Clone the GitHub repository to your local machine:

```bash
git clone https://github.com/jorohx84/videoflix.backend.git

cd videoflix
```

## Installation

### 1. Create a virtual environment
```bash
python -m venv env
```
### 2. Start Enviroment
 
Linux/MacOS:

```bash
source env/bin/activate 
```

Windows:

```bash
venv\Scripts\activate  
```

### 3. Install dependencies:

```bash
pip install -r requirements.txt

```




## Environment Variables

The project uses environment variables for configuration. Copy the example .env.example to .env:

```bash
cp .env.template .env

```

Edit .env and set your configuration values:

```bash

SECRET_KEY=your_django_secret_key
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword
DB_HOST=db
DB_PORT=5432

REDIS_LOCATION=redis://redis:6379/1

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_email_password
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@videoflix.com

```
## Docker Setup

The project uses Docker for all services, including:

- **PostgreSQL** database
- **Redis** for background tasks
- **Django** application server

If you don't have Docker installed, download and install **Docker Desktop** from [here](https://www.docker.com/products/docker-desktop/).

> **Note:** Make sure Docker Desktop is running before you try to build or start containers, otherwise the containers cannot be created.

### Build and start the containers:

```bash
docker compose up --build

```

### Running the Project
Apply migrations
```bash
docker compose exec web python manage.py migrate

```

Create a superuser

```bash
docker compose exec web python manage.py createsuperuser
```

Start background worker (RQ)

```bash
docker compose exec web python manage.py rqworker
```

