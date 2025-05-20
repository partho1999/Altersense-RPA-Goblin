# Altersense RPA

## Run the project

```bash
docker-compose --env-file .env up --build
docker-compose run web python3 manage.py makemigrations
docker-compose run web python3 manage.py migrate
docker-compose run web python3 manage.py createsuperuser
```

## The project will be available at

`http://localhost:8008`
