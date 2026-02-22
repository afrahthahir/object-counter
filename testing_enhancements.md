# Proposed Testing Enhancements

To further ensure the reliability and quality of the Object Counter application, I recommend the following testing enhancements:

## 1. Performance and Load Testing
As an ML-heavy application, processing time and memory usage are critical.
*   **Recommendation**: Implement a `locustfile.py` to simulate multiple concurrent users uploading images.
*   **Goal**: Identify the maximum number of concurrent requests the system can handle before response times exceed acceptable thresholds (e.g., 2 seconds).

## 2. Real Infrastructure Integration Tests (System Tests)
Currently, our tests use `FakeObjectDetector` or in-memory databases.
*   **Recommendation**: Create a `tests/system/` suite that executes against the actual Docker containers (MongoDB, Postgres, and TensorFlow Serving).
*   - **Requirement**: Use `docker-compose up -d` before running these tests.
*   - **Goal**: Verify that real network connections, database schemas, and ML model outputs behave as expected.

## 3. Property-Based Testing
The prediction filtering and counting logic can have many edge cases (e.g., empty lists, NaN scores, negative coordinates).
*   **Recommendation**: Use the `Hypothesis` library in `tests/domain/test_predictions.py`.
*   **Goal**: Automatically generate a wide variety of `Prediction` data to find bugs that traditional "happy path" unit tests might miss.

## 4. Image Quality & Robustness Testing
The model's performance can vary wildly based on image quality.
*   **Recommendation**: Create a "Gold Standard" test set in `tests/robustness/`.
*   - **Data**: Include images that are blurry, overexposed, or contain rare objects.
*   - **Goal**: Measure and track the model's accuracy (mAP - Mean Average Precision) over time to ensure that model updates don't degrade quality for common use cases.

## 5. Security Testing
The application receives binary file uploads, which is a common attack vector.
*   **Recommendation**: Add tests for:
    *   **Large File Bombs**: Testing the 413 dynamic limit.
    *   **Malicious Filenames**: Ensuring PATH traversal is impossible.
    *   **Unsupported Formats**: Verifying the app correctly rejects non-image binaries (PDFs, EXEs) with a 415 or 400 error.

## Recent Improvements Made
*   **Relational Persistence Testing**: Added `tests/adapters/test_count_repo.py` using SQLite to verify the SQL logic in `CountPostgresRepo`.
*   **Negative Integration Testing**: Added `tests/entrypoints/test_webapp_errors.py` to verify error responses for missing files and invalid threshold inputs.
*   **Pytest Infrastructure**: Configured `pytest.ini` for reliable path resolution across the entire suite.
