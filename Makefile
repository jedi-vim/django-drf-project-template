clean:
	rm -rf dist
	rm -rf *.egg.info
	find . -type f -name *.pyc -exec rm -f {} \;

docker-build:
	docker-compose stop
	docker-compose rm
	docker-compose build 

docker-run:
	docker-compose up ecommerce_backend-api docker_db

dev-install: clean
	poetry install 

dev-makemigrations:
	DJANGO_SETTINGS_MODULE=config.settings.development \
	python manage.py makemigrations

dev-migrate:
	DJANGO_SETTINGS_MODULE=config.settings.development \
	python manage.py migrate

dev-run:
	DJANGO_SETTINGS_MODULE=config.settings.development \
	python manage.py runserver

dev-shell:
	DJANGO_SETTINGS_MODULE=config.settings.development \
	python manage.py shell
	
dev_db-up:
	docker-compose up development_db

dev_db-initialize:
	python -m ecommerce_backend.initialize_db

test_db-up:
	docker-compose up test_db

test_db-stop:
	docker-compose stop test_db

lint: clean
	flake8 ecommerce_backend
	pylint ecommerce_backend
	isort ecommerce_backend --check

test: lint
	pytest
