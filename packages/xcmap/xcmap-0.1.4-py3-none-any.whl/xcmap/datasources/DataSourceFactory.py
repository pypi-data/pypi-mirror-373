from xcmap.datasources.mongodb import MongoDataSource


def create_data_source(source_type):
    if source_type == 'mongo':
        return MongoDataSource()
    # elif source_type == 'mysql':
    #     return MySQLDataSource()
    else:
        raise ValueError('Invalid data source type')
