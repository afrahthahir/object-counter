# Supporting Multiple Internal Models

To support multiple internally trained models in this Hexagonal Architecture setup, the following changes would be required across the various layers:

## 1. Adapter Layer (`counter/adapters`)

### Model-to-Label Mapping
Different models usually have different target classes. The `TFSObjectDetector` currently hardcodes the COCO label map.
*   **Change**: Modify `TFSObjectDetector` to accept a `label_map_path` in its constructor.
*   **Change**: Create a mapping or directory structure (e.g., `counter/resources/label_maps/`) to store unique JSON label maps for each internal model.

### Dynamic Service URL
*   **Change**: Since TensorFlow Serving URLs include the model name (`/v1/models/{model}:predict`), the `TFSObjectDetector` is already well-positioned to handle this. It just needs the model name passed dynamically during instantiation or execution.

## 2. API & Entrypoint Layer (`counter/entrypoints`)

### Request Parameters
Currently, the client only sends `threshold` and `file`.
*   **Change**: Update the `/object-count` and `/object-prediction` endpoints to accept an optional `model_name` parameter (via form-data or query string).
*   **Fallback**: Define a "default" model in the configuration if no name is provided by the client.

## 3. Domain Layer (`counter/domain`)

### Port Refactoring
The `ObjectDetector` port currently assumes a single model context.
*   **Option A (Simple)**: Pass the `model_name` into the `predict` method of the `ObjectDetector` interface.
*   **Option B (Flexible)**: Implement a `ModelRegistry` action that acts as a factory, returning the specific `ObjectDetector` instance configured for the requested internal model.

## 4. Configuration Layer (`counter/config.py`)

*   **Change**: Replace the single `MODEL_NAME` environment variable with a more robust configuration (e.g., a JSON config file or a comma-separated list of active models).
*   **Change**: Update the `get_find_action` logic to support retrieving actions by model name.

## 5. Infrastructure & Setup

### TensorFlow Serving Configuration
TFS can serve multiple models simultaneously using a `model_config_list`.
*   **Change**: Create a `models.config` file:
    ```protobuf
    model_config_list {
      config {
        name: 'model_a'
        base_path: '/models/model_a/'
        model_platform: 'tensorflow'
      }
      config {
        name: 'model_b'
        base_path: '/models/model_b/'
        model_platform: 'tensorflow'
      }
    }
    ```
*   **Change**: Update `docker-compose.yml` or the Docker run command to mount this config file and use the `--model_config_file` flag instead of the `MODEL_NAME` env variable.

### Directory Structure
Organize the `tmp/model` directory to house multiple versions or distinct models:
```
tmp/model/
  model_a/
    1/ (saved_model.pb)
  model_b/
    1/ (saved_model.pb)
```

## 6. Testing Strategy
*   **Change**: Add new integration tests in `tests/entrypoints/` that specifically call the API with different `model_name` parameters to verify that the routing and label mapping work correctly for each distinct model.
