# Django + MySQL + Nginx — Docker 3-Tier Application

A simple 3-tier Docker project:

```text
Browser
   |
   v
Nginx :80
   |
   v
Django :8000
   |
   v
MySQL :3306
```

The goal of this project is to practice Docker images, containers, networks, volumes,
environment variables, health checks, manual image builds, and Docker Compose.

## Project structure

```text
django-mysql-nginx-3tier/
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── README.md
├── django-app/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── products/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── urls.py
│       ├── views.py
│       ├── migrations/
│       │   └── __init__.py
│       └── templates/
│           └── products/
│               └── index.html
└── nginx/
    ├── Dockerfile
    └── nginx.conf
```

## Application

The Django application reads products from MySQL and displays them in a web page.

Default URL after deployment:

```text
http://localhost
```

## 1. Build the Django image manually

From the project root:

```bash
docker build -t django-3tier-app:1.0 ./django-app
```

Check it:

```bash
docker images
```

## 2. Build the Nginx image manually

```bash
docker build -t nginx-3tier:1.0 ./nginx
```

Check it:

```bash
docker images
```

The MySQL image is pulled from Docker Hub, so you do not need to build it yourself.

## 3. Create a Docker network

```bash
docker network create three-tier-net
```

Check it:

```bash
docker network ls
```

## 4. Start MySQL manually

```bash
docker volume create mysql-data
```

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
docker logs mysql
```

Wait until MySQL is ready.

## 5. Start Django manually

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

Check:

```bash
docker ps
docker logs django
```

Run Django migrations:

```bash
docker exec django python manage.py migrate
```

Create sample products:

```bash
docker exec django python manage.py shell -c "from products.models import Product; Product.objects.get_or_create(name='Laptop', price=75000); Product.objects.get_or_create(name='Keyboard', price=2500); Product.objects.get_or_create(name='Mouse', price=1200)"
```

Test Django directly:

```text
http://localhost:8000
```

## 6. Start Nginx manually

```bash
docker run -d \
  --name nginx \
  --network three-tier-net \
  -p 80:80 \
  nginx-3tier:1.0
```

Now open:

```text
http://localhost
```

The request path is:

```text
Browser
  -> Nginx container
  -> django container
  -> mysql container
```

Important: inside the Docker network, Nginx reaches Django using the container name:

```text
http://django:8000
```

Django reaches MySQL using:

```text
mysql:3306
```

The container names become DNS names on the user-created Docker network.

## 7. Inspect the Docker setup

See all containers:

```bash
docker ps
```

See the network:

```bash
docker network inspect three-tier-net
```

See the volume:

```bash
docker volume inspect mysql-data
```

See images:

```bash
docker images
```

See logs:

```bash
docker logs nginx
docker logs django
docker logs mysql
```

## 8. Stop and remove the manual setup

```bash
docker stop nginx django mysql
```

```bash
docker rm nginx django mysql
```

The MySQL data remains because it is stored in the named volume.

To delete the database volume too:

```bash
docker volume rm mysql-data
```

## 9. Docker Compose setup

After understanding the manual Docker commands, use Compose to automate the same architecture.

Build and start everything:

```bash
docker compose up -d --build
```

Check:

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

Create sample data:

```bash
docker compose exec django python manage.py shell -c "from products.models import Product; Product.objects.get_or_create(name='Laptop', price=75000); Product.objects.get_or_create(name='Keyboard', price=2500); Product.objects.get_or_create(name='Mouse', price=1200)"
```

Open:

```text
http://localhost
```

Stop:

```bash
docker compose down
```

Stop and delete volumes:

```bash
docker compose down -v
```

## 10. Useful Docker learning commands

```bash
docker image ls
docker ps -a
docker inspect django
docker inspect mysql
docker network inspect three-tier-net
docker volume ls
docker stats
```

Enter a running container:

```bash
docker exec -it django sh
```

Enter MySQL:

```bash
docker exec -it mysql mysql -uappuser -papppass appdb
```

## 11. Rebuild after changing Django code

If you modify the Django source code:

```bash
docker compose up -d --build django
```

If you modify Nginx configuration:

```bash
docker compose up -d --build nginx
```

## 12. GitHub

Before pushing:

```bash
git init
git add .
git commit -m "Initial Docker 3-tier Django MySQL Nginx application"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Do not commit passwords or production secrets. The example values in this learning project are intentionally simple and are for local practice only.
