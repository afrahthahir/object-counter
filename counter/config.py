# Configures dependencies for both object counting and the new prediction service.
import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo, CountPostgresRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, FindDetectedObjects

"""
Configuration and Dependency Injection Layer.
Responsible for wiring up adapters to actions based on environment variables.
"""

def dev_count_action() -> CountDetectedObjects:
    """Factory for the development count action using in-memory storage."""
    return CountDetectedObjects(dev_find_action(), CountInMemoryRepo())


def dev_find_action() -> FindDetectedObjects:
    """Factory for the development find action using a fake detector."""
    return FindDetectedObjects(FakeObjectDetector())


# Dynamically selects the repository implementation based on the DB_TYPE environment variable.
def __get_count_repo():
    """Internal helper to choose between MongoDB and Postgres for production."""
    db_type = os.environ.get('DB_TYPE', 'mongo')
    if db_type == 'postgres':
        connection_string = os.environ.get('POSTGRES_DB_URL', 'postgresql://user:pass@localhost:5432/db')
        return CountPostgresRepo(connection_string)
    
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = int(os.environ.get('MONGO_PORT', 27017))
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db)


def prod_count_action() -> CountDetectedObjects:
    """Factory for the production count action with real persistence."""
    return CountDetectedObjects(prod_find_action(), __get_count_repo())


def prod_find_action() -> FindDetectedObjects:
    """Factory for the production find action using TensorFlow Serving."""
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    model_name = os.environ.get('MODEL_NAME', 'ssd_mobilenet_v2')
    return FindDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, model_name))


def get_count_action() -> CountDetectedObjects:
    """Main entry point to get the count action for the current environment."""
    env = os.environ.get('ENV', 'dev')
    actions = {
        'dev': dev_count_action,
        'prod': prod_count_action
    }
    return actions.get(env, dev_count_action)()


def get_find_action() -> FindDetectedObjects:
    """Main entry point to get the find action for the current environment."""
    env = os.environ.get('ENV', 'dev')
    actions = {
        'dev': dev_find_action,
        'prod': prod_find_action
    }
    return actions.get(env, dev_find_action)()
