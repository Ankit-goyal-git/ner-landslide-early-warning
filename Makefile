.PHONY: setup data train test run-backend run-frontend run

setup:
	pip install -r requirements.txt
	cd frontend && npm install

data:
	python scripts/profile_dataset.py
	python scripts/clean_landslide_data.py
	python scripts/create_features.py

train:
	python scripts/train_model.py
	python scripts/evaluate_model.py

test:
	python -m pytest tests/ -v

run-backend:
	python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm run dev

run:
	@echo "Starting full system in dual processes..."
