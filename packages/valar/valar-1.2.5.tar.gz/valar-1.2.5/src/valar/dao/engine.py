import pymongo
from django.apps import apps
from django.conf import settings
from urllib.parse import urlparse
from minio import Minio
from pymongo.synchronous.collection import Collection

from ..classes.singleton_meta import SingletonMeta
from ..classes.valar_minio import ValarMinio
from ..models.core import VModel, VTree


class ValarEngine(metaclass=SingletonMeta):

    def __init__(self):
        orm_engine = {}
        for model in apps.get_models():
            meta = getattr(model, '_meta')
            app = meta.app_label
            if app not in ['sessions']:
                entity = f'{app}.{model.__name__}'
                orm_engine[entity] = model
        self.orm_engine = orm_engine

        # mon
        if hasattr(settings, 'MONGO_URI'):
            self.mongo_client = pymongo.MongoClient(
                settings.MONGO_URI,
                **{
                    'maxPoolSize': 10,
                    'minPoolSize': 0,
                    'maxIdleTimeMS': 10000,
                    'connectTimeoutMS': 10000,
                    'socketTimeoutMS': 10000,
                    'serverSelectionTimeoutMS': 10000,
                }
            )
            self.mongo_engine = self.mongo_client[settings.BASE_APP]
        else:
            self.mongo_client = None
            self.mongo_engine = None

        # minio
        if hasattr(settings, 'MINIO_URL'):
            parsed = urlparse(settings.MINIO_URL)
            endpoint = f'{parsed.hostname}:{parsed.port}'
            access_key = parsed.username
            secret_key = parsed.password
            self.minio_engine = Minio(
                endpoint=endpoint,
                access_key=access_key,
                secret_key=secret_key,
                secure=False
            )
        else:
            self.minio_engine = None

    def get_orm_model(self, entity) -> VModel:
        return self.orm_engine[entity]

    def get_mongo_collection(self, entity) -> Collection:
        return self.mongo_engine[entity]

    def get_minio_bucket(self, entity):
        return ValarMinio(self.minio_engine, entity) if self.minio_engine else None

    # def meta_tree(self):
    #     mapping = {}
    #     names = self.mongo_engine.list_collection_names()
    #
    #     for entity, model in self.orm_engine.items():
    #         app, value = entity.split('.')
    #         is_tree = issubclass(model, VTree)
    #         meta = getattr(model, '_meta')
    #         name = meta.verbose_name
    #
    #         node = mapping.get(app, {'label': app, 'value': app, 'db': 'orm', 'children': []})
    #         node['children'].append({"label": name, "value": value, 'isTree': is_tree})
    #         mapping[app] = node
    #     return list(mapping.values())
