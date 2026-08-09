# Django + MySQL + Nginx — Docker 3-Tier Application

A simple **3-tier web application deployed using Docker**, consisting of:

* **Nginx** — Reverse proxy / web server
* **Django** — Application layer
* **MySQL** — Database layer

The primary purpose of this project is to understand and practice **Docker images, containers, networks, volumes, environment variables, container communication, and Docker Compose**.

---

## 🏗️ Architecture

```text
                         Browser
                            │
                            │ HTTP :80
                            ▼
                    ┌─────────────────┐
                    │      Nginx      │
                    │  Reverse Proxy  │
                    │   Port 80       │
                    └────────┬────────┘
                             │
                             │ HTTP :8000
                             ▼
                    ┌─────────────────┐
                    │     Django      │
                    │ Application     │
                    │   Port 8000     │
                    └────────┬────────┘
                             │
                             │ MySQL :3306
                             ▼
                    ┌─────────────────┐
                    │      MySQL      │
                    │    Database     │
                    │   Port 3306     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │  mysql-data     │
                    │ Docker Volume   │
                    └─────────────────┘
```

All three containers communicate through a dedicated Docker bridge network.

---

## 🚀 Technologies Used

| Technology     | Purpose                              |
| -------------- | ------------------------------------ |
| Docker         | Containerization                     |
| Dockerfile     | Building custom images               |
| Docker Network | Container-to-container communication |
| Docker Volume  | Persistent MySQL data                |
| Docker Compose | Multi-container orchestration        |
| Django         | Application/backend layer            |
| MySQL          | Database                             |
| Nginx          | Reverse proxy                        |
| Python         | Django application                   |

---

## 📁 Project Structure

```text
django-mysql-nginx-3tier/
│
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── README.md
│
├── django-app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   │
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   │
│   └── products/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── urls.py
│       ├── views.py
│       ├── migrations/
│       └── templates/
│
└── nginx/
    ├── Dockerfile
    └── nginx.conf
```

---

# 🐳 Docker Setup

The project can be deployed in two ways:

### 1. Manual Docker commands

This approach is useful for understanding Docker fundamentals:

```text
Dockerfile
    ↓
docker build
    ↓
Docker Image
    ↓
docker run
    ↓
Container
    ↓
Docker Network
    ↓
Container-to-container communication
```

### 2. Docker Compose

Once the individual Docker concepts are understood, Docker Compose can be used to manage the complete application.

---

# 🔨 1. Build the Django Image

From the project root:

```bash
docker build -t django-3tier-app:1.0 ./django-app
```

Verify:

```bash
docker images
```

The resulting image:

```text
django-3tier-app:1.0
```

---

# 🔨 2. Build the Nginx Image

```bash
docker build -t nginx-3tier:1.0 ./nginx
```

Verify:

```bash
docker images
```

MySQL uses the official image:

```text
mysql:8.4
```

so there is no custom MySQL Dockerfile in this project.

---

# 🌐 3. Create a Docker Network

Create the application network:

```bash
docker network create three-tier-net
```

Verify:

```bash
docker network ls
```

The network allows the containers to communicate using their container names.

For example:

```text
Nginx → django:8000
Django → mysql:3306
```

Docker's internal DNS resolves these container names automatically.

---

# 💾 4. Create a MySQL Volume

Create a named volume:

```bash
docker volume create mysql-data
```

The volume is mounted inside MySQL:

```text
mysql-data
      │
      ▼
/var/lib/mysql
```

This keeps database data independent from the MySQL container lifecycle.

---

# 🗄️ 5. Run MySQL

```bash
docker run -d \
  --name mysql \
  --network three-tier-net \
  -v mysql-data:/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=rootpass \
  -e MYSQL_DATABASE=appdb \
  -e MYSQL_USER=appuser \
  -e MYSQL_PASSWORD=apppass \
  mysql:8.4
```

Check the container:

```bash
docker ps
```

Check MySQL logs:

```bash
docker logs mysql
```

---

# 🐍 6. Run Django

```bash
docker run -d \
  --name django \
  --network three-tier-net \
  -p 8000:8000 \
  -e DB_HOST=mysql \
  -e DB_PORT=3306 \
  -e DB_NAME=appdb \
  -e DB_USER=appuser \
  -e DB_PASSWORD=apppass \
  django-3tier-app:1.0
```

Django connects to MySQL using:

```text
DB_HOST=mysql
DB_PORT=3306
```

Notice that `mysql` is the **container name**, not `localhost`.

---

# 🗃️ 7. Run Django Migrations

```bash
docker exec django python manage.py migrate
```

This creates the required Django database tables inside MySQL.

---

# 📦 8. Add Sample Data

Sample products can be added directly through MySQL.

Enter the MySQL container:

```bash
docker exec -it mysql bash
```

Connect to MySQL:

```bash
mysql -uappuser -papppass appdb
```

Then:

```sql
INSERT INTO products_product (name, price)
VALUES
('Laptop', 75000),
('Keyboard', 2500),
('Mouse', 1200),
('Monitor', 15000);
```

Verify:

```sql
SELECT * FROM products_product;
```

Exit:

```sql
exit;
```

Then:

```bash
exit
```

---

# 🌐 9. Run Nginx

```bash
docker run -d \
  --name nginx \
  --network three-tier-net \
  -p 80:80 \
  nginx-3tier:1.0
```

Nginx forwards requests to:

```text
http://django:8000
```

The complete request flow is now:

```text
Browser
   │
   │ localhost:80
   ▼
Nginx
   │
   │ django:8000
   ▼
Django
   │
   │ mysql:3306
   ▼
MySQL
```

Open the application:

```text
http://localhost
```

---

# 🔍 Useful Docker Commands

### List running containers

```bash
docker ps
```

### List all containers

```bash
docker ps -a
```

### List images

```bash
docker images
```

### View container logs

```bash
docker logs nginx
docker logs django
docker logs mysql
```

### Inspect the network

```bash
docker network inspect three-tier-net
```

### Inspect the volume

```bash
docker volume inspect mysql-data
```

### Enter a running container

```bash
docker exec -it django sh
```

### View Docker resource usage

```bash
docker stats
```

---

# 🧩 Docker Compose

After understanding the manual Docker setup, the entire application can be managed using Docker Compose.

Build and start the application:

```bash
docker compose up -d --build
```

Check services:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs -f
```

Run migrations:

```bash
docker compose exec django python manage.py migrate
```

Open:

```text
http://localhost
```

Stop the application:

```bash
docker compose down
```

Stop the application and remove its volumes:

```bash
docker compose down -v
```

---

# 🔄 Rebuilding After Code Changes

If Django source code or its Dockerfile changes:

```bash
docker compose up -d --build django
```

If the Nginx configuration or Dockerfile changes:

```bash
docker compose up -d --build nginx
```

This demonstrates the typical Docker development cycle:

```text
Source Code
     ↓
Dockerfile
     ↓
docker build
     ↓
New Image
     ↓
Recreate Container
     ↓
Updated Application
```

---

# 💡 Docker Concepts Demonstrated

This project provides hands-on practice with:

### Images

Building custom Django and Nginx images:

```bash
docker build
```

### Containers

Running application components independently:

```bash
docker run
```

### Networks

Connecting containers:

```bash
docker network create
```

### Volumes

Persisting database data:

```bash
docker volume create
```

### Environment Variables

Passing database configuration to Django:

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

### Container Communication

```text
nginx → django
django → mysql
```

### Port Mapping

```text
Host :80   → Nginx :80
Host :8000 → Django :8000
```

### Docker Compose

Managing the complete multi-container application:

```bash
docker compose up -d --build
```

---

# 🧹 Cleanup

To stop and remove manually created containers:

```bash
docker stop nginx django mysql
```

```bash
docker rm nginx django mysql
```

The MySQL data remains because it is stored in:

```text
mysql-data
```

To remove the volume as well:

```bash
docker volume rm mysql-data
```

For the Compose deployment:

```bash
docker compose down
```

To remove the database volume too:

```bash
docker compose down -v
```

---

# 🎯 Learning Objective

The main objective of this project is not to build a complex Django application.

Instead, it demonstrates how a traditional 3-tier application can be **containerized and connected using Docker**.

The key concepts explored are:

```text
Dockerfile
   ↓
Docker Image
   ↓
Docker Container
   ↓
Docker Network
   ↓
Container Communication
   ↓
Docker Volume
   ↓
Persistent Database
   ↓
Docker Compose
```

This provides a foundation for moving toward more advanced Docker topics such as **multi-stage builds, Docker Swarm, Kubernetes, container registries, CI/CD pipelines, and production deployments**.

---

## ⚠️ Note

The database credentials included in this project are intentionally simple and are meant **only for local Docker learning**.

For production environments, credentials should be managed using secure mechanisms such as environment secrets, Docker secrets, or an external secrets manager.
