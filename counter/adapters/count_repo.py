# Adapters for persisting object counts across different storage backends.
from typing import List

from pymongo import MongoClient

from counter.domain.models import ObjectCount
from counter.domain.ports import ObjectCountRepo


class CountInMemoryRepo(ObjectCountRepo):

    def __init__(self):
        self.store = dict()

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        if object_classes is None:
            return list(self.store.values())

        return [self.store.get(object_class) for object_class in object_classes]

    def update_values(self, new_values: List[ObjectCount]):
        for new_object_count in new_values:
            key = new_object_count.object_class
            try:
                stored_object_count = self.store[key]
                self.store[key] = ObjectCount(key, stored_object_count.count + new_object_count.count)
            except KeyError:
                self.store[key] = ObjectCount(key, new_object_count.count)


class CountMongoDBRepo(ObjectCountRepo):

    def __init__(self, host, port, database):
        self.__host = host
        self.__port = port
        self.__database = database

    def __get_counter_col(self):
        client = MongoClient(self.__host, self.__port)
        db = client[self.__database]
        counter_col = db.counter
        return counter_col

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        counter_col = self.__get_counter_col()
        query = {"object_class": {"$in": object_classes}} if object_classes else None
        counters = counter_col.find(query)
        object_counts = []
        for counter in counters:
            object_counts.append(ObjectCount(counter['object_class'], counter['count']))
        return object_counts

    def update_values(self, new_values: List[ObjectCount]):
        counter_col = self.__get_counter_col()
        for value in new_values:
            counter_col.update_one({'object_class': value.object_class}, {'$inc': {'count': value.count}}, upsert=True)


from sqlalchemy import create_engine, Column, String, Integer, select
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class ObjectCountEntity(Base):
    __tablename__ = 'object_counts'
    object_class = Column(String, primary_key=True)
    count = Column(Integer, default=0)


# Relational database adapter using SQLAlchemy for PostgreSQL/MySQL support.
class CountPostgresRepo(ObjectCountRepo):
    def __init__(self, connection_string):
        self.__engine = create_engine(connection_string)
        Base.metadata.create_all(self.__engine)
        self.__session_factory = sessionmaker(bind=self.__engine)

    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        with self.__session_factory() as session:
            query = select(ObjectCountEntity)
            if object_classes:
                query = query.filter(ObjectCountEntity.object_class.in_(object_classes))
            
            items = session.execute(query).scalars().all()
            return [ObjectCount(item.object_class, item.count) for item in items]

    def update_values(self, new_values: List[ObjectCount]):
        with self.__session_factory() as session:
            for value in new_values:
                item = session.get(ObjectCountEntity, value.object_class)
                if item:
                    item.count += value.count
                else:
                    item = ObjectCountEntity(object_class=value.object_class, count=value.count)
                    session.add(item)
            session.commit()

