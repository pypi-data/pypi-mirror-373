import urllib.parse

from xcmap.datasources import DataSource
from xcmap.datasources.config import MongoConfig
from mongoengine import connect


class MongoDataSource(DataSource):
    def connect(self, config: MongoConfig):
        username = urllib.parse.quote_plus(config.user_name)
        password = urllib.parse.quote_plus(config.password)
        if username:
            return connect(
                host=f'mongodb://{username}:{password}@{config.url_str}/{config.db_name}?'
                     f'authSource={config.auth_db}',
                maxPoolSize=config.max_pool_size, minPoolSize=config.min_pool_size)
        return connect(
            host=f'mongodb://{config.url_str}/{config.db_name}',
            maxPoolSize=config.max_pool_size, minPoolSize=config.min_pool_size)
