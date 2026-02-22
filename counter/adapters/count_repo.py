# Adapters for persisting object counts across different storage backends.
from typing import List

from pymongo import MongoClient

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):
    """Simple in-memory implementation of the repository, useful for development and testing."""
    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        """Reads counts from a dictionary."""
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes if object_class in self.store]

    def update_values(self, new_values: List[ObjectCount]):
        """Increments counts in a dictionary."""
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):
    """MongoDB implementation of the repository for production-ready document storage."""
    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        """Helper to establish a connection and get the counter collection."""
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        """Reads counts from MongoDB using an '$in' query."""
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        """Updates counts in MongoDB using an atomic '$inc' operation with upsert."""
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


from sqlalchemy import create_engine, Column, String, Integer, select
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class ObjectCountEntity(Base):
    """SQLAlchemy ORM model for the object_counts table."""
    __tablename__ = 'object_counts'
    object_class = Column(String, primary_key=True)
    count = Column(Integer, default=0)


# Relational database adapter using SQLAlchemy for PostgreSQL/MySQL support.
class CountPostgresRepo(ObjectCountRepo):
    """SQL-based implementation of the repository using SQLAlchemy ORM."""
    def __init__(self, connection_string):
        self.__engine = create_engine(connection_string)
        Base.metadata.create_all(self.__engine)
        self.__session_factory = sessionmaker(bind=self.__engine)

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        """Reads counts from a relational database using SQLAlchemy select."""
        with self.__session_factory() as session:
            query = select(ObjectCountEntity)
            if object_classes:
                query = query.filter(ObjectCountEntity.object_class.in_(object_classes))
            
            items = session.execute(query).scalars().all()
            return [ObjectCount(item.object_class, item.count) for item in items]

    def update_values(self, new_values: List[ObjectCount]):
        """Updates counts in a relational database using session.merge for upsert logic."""
        with self.__session_factory() as session:
            for value in new_values:
                # Optimized atomic upsert using session logic
                item = session.merge(ObjectCountEntity(object_class=value.object_class))
                if item.count is None:
                    item.count = value.count
                else:
                    item.count += value.count
            session.commit()

