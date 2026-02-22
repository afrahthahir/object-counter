# NIQ Innovation Enablement - Object Counter Challenge

The goal of this repo is to demonstrate how to apply Hexagonal Architecture in a Machine Learning based system.
This application consists of a Flask API that receives an image and a threshold and returns the number of objects detected, as well as detailed object predictions.

## 🚀 Quick Start (Automated with Makefile)

To simplify the setup, use the provided `Makefile`.

### 1. Setup Environment
```bash
make setup
source .venv/bin/activate
```

### 2. Download and Extract Model
```bash
make download-model
```

### 3. Run Dependencies (Docker)
```bash
make run-tf    # Starts TensorFlow Serving
make run-db    # Starts MongoDB
```

### 4. Run the Application
```bash
make run       # Runs in dev mode (uses Fake detector)
# OR
make run-prod  # Runs in production mode (requires TF and DB)
```

### 5. Run Tests
```bash
make test
```

---

## 🏗️ Architecture

The application is composed of three layers:

- **entrypoints**: Exposes the API and receives requests.
- **adapters**: Communicates with external services (TF Serving, MongoDB, PostgreSQL).
- **domain**: Business logic (orchestrating detections and counts).

Features added in this version:
- New `/object-prediction` endpoint for detailed JSON results.
- Relational database support (PostgreSQL).
- Image preprocessing (scaling) for better performance.
- Consolidated task automation via `Makefile`.

## 📡 API Usage

### Object Count
Returns an overall summary of detected objects.
```bash
curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://localhost:5000/object-count
```

### Object Prediction
Returns a detailed list of every object with its score and box coordinates.
```bash
curl -F "threshold=0.9" -F "file=@resources/images/boy.jpg" http://localhost:5000/object-prediction
```

## 🧪 Testing

We use `pytest` for testing. The suite includes:
- **Unit Tests**: Domain logic verification with mocks.
- **Integration Tests**: Webapp and database adapter verification (using SQLite for SQL tests).

```bash
make test
```

---

## 🐳 Docker Compose (Alternative)

For a fully containerized deployment of the entire stack:

```bash
docker-compose up --build
```

---

## 📂 Documentation

- [Proposed Improvements](./improvements.md): Detailed list of all architectural and performance enhancements.
- [Proposed Multi-Model Support](./multi_model_support.md): Roadmap for supporting multiple internal models.
- [Proposed Testing Roadmap](./testing_enhancements.md): Proposals for future testing strategies (E2E, Load, Security).