.PHONY: setup-env setup-model run-tfserving run-mongo run-app test help

# Variables
PYTHON = python3
PIP = pip
VENV = .venv
ACTIVATE = . $(VENV)/bin/activate

help:
	@echo "Available commands:"
	@echo "  make setup        - Create virtualenv and install dependencies"
	@echo "  make download-model - Download and prepare the SSD MobileNet model"
	@echo "  make run-tf        - Start TensorFlow Serving in Docker"
	@echo "  make run-db        - Start MongoDB in Docker"
	@echo "  make run-postgres  - Start PostgreSQL in Docker"
	@echo "  make run           - Run the application with Fake background"
	@echo "  make run-prod      - Run the application in production mode"
	@echo "  make test          - Run all tests"

setup:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "Setup complete. Use 'source $(VENV)/bin/activate' to enter the environment."

download-model:
	mkdir -p tmp/model/ssd_mobilenet_v2/1
	curl -L -o tmp/model.tar.gz http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v2_coco_2018_03_29.tar.gz
	tar -xzvf tmp/model.tar.gz -C tmp
	mv tmp/ssd_mobilenet_v2_coco_2018_03_29/saved_model/saved_model.pb tmp/model/ssd_mobilenet_v2/1/
	chmod -R 777 tmp/model
	rm tmp/model.tar.gz
	rm -rf tmp/ssd_mobilenet_v2_coco_2018_03_29
	@echo "Model downloaded and extracted to tmp/model/"

run-tf:
	@num_physical_cores=$$(lscpu --all --parse=SOCKET,CORE | grep -v '^#' | uniq | wc -l); \
	docker run --rm -d \
		--name=tfserving \
		-p 8501:8501 \
		--mount type=bind,source=$$(pwd)/tmp/model,target=/models \
		-e OMP_NUM_THREADS=$$num_physical_cores \
		-e TENSORFLOW_INTRA_OP_PARALLELISM=$$num_physical_cores \
		-e MODEL_NAME=ssd_mobilenet_v2 \
		tensorflow/serving
	@echo "TensorFlow Serving is starting..."

run-db:
	docker run --rm --name test-mongo -p 27017:27017 -d mongo:latest
	@echo "MongoDB is starting..."

run-postgres:
	docker run --rm --name test-postgres -p 5432:5432 -e POSTGRES_PASSWORD=pass -d postgres:latest
	@echo "PostgreSQL is starting..."

run:
	$(ACTIVATE) && export PYTHONPATH=. && $(PYTHON) -m counter.entrypoints.webapp

run-prod:
	$(ACTIVATE) && export PYTHONPATH=. && ENV=prod $(PYTHON) -m counter.entrypoints.webapp

test:
	$(ACTIVATE) && export PYTHONPATH=. && pytest
