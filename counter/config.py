# Configures dependencies for both object counting and the new prediction service.
import os

from counter.adapters.count_repo import CountMongoDBRepo, CountInMemoryRepo, CountPostgresRepo
from counter.adapters.object_detector import TFSObjectDetector, FakeObjectDetector
from counter.domain.actions import CountDetectedObjects, FindDetectedObjects


def dev_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(dev_find_action(), CountInMemoryRepo())


def dev_find_action() -> FindDetectedObjects:
    return FindDetectedObjects(FakeObjectDetector())


# Dynamically selects the repository implementation based on the DB_TYPE environment variable.
def __get_count_repo():
    db_type = os.environ.get('DB_TYPE', 'mongo')
    if db_type == 'postgres':
        connection_string = os.environ.get('POSTGRES_DB_URL', 'postgresql://user:pass@localhost:5432/db')
        return CountPostgresRepo(connection_string)
    
    mongo_host = os.environ.get('MONGO_HOST', 'localhost')
    mongo_port = int(os.environ.get('MONGO_PORT', 27017))
    mongo_db = os.environ.get('MONGO_DB', 'prod_counter')
    return CountMongoDBRepo(host=mongo_host, port=mongo_port, database=mongo_db)


def prod_count_action() -> CountDetectedObjects:
    return CountDetectedObjects(prod_find_action(), __get_count_repo())


def prod_find_action() -> FindDetectedObjects:
    tfs_host = os.environ.get('TFS_HOST', 'localhost')
    tfs_port = os.environ.get('TFS_PORT', 8501)
    model_name = os.environ.get('MODEL_NAME', 'ssd_mobilenet_v2')
    return FindDetectedObjects(TFSObjectDetector(tfs_host, tfs_port, model_name))


def get_count_action() -> CountDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    count_action_fn = f"{env}_count_action"
    return globals()[count_action_fn]()


def get_find_action() -> FindDetectedObjects:
    env = os.environ.get('ENV', 'dev')
    find_action_fn = f"{env}_find_action"
    return globals()[find_action_fn]()
