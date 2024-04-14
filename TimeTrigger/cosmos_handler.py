class CosmosHandler:
    def __init__(self):
        self.client

    def get_cosmos_client(self):
        return self.client

    def get_cosmos_db(self, db_name):
        return self.client.get_database_client(db_name)

    def get_cosmos_container(self, db_name, container_name):
        return self.get_cosmos_db(db_name).get_container_client(container_name)

    def create_cosmos_container(self, db_name, container_name):
        return self.get_cosmos_db(db_name).create_container_if_not_exists(id=container_name, partition_key=PartitionKey(path='/id'))

    def get_cosmos_container_items(self, db_name, container_name):
        return list(self.get_cosmos_container(db_name, container_name).query_items(query='SELECT * FROM c'))

    def get_cosmos_container_item(self, db_name, container_name, item_id):
        return self.get_cosmos_container(db_name, container_name).read_item(item=item_id, partition_key=item_id)

    def create_cosmos_container_item(self, db_name, container_name, item):
        return self.get_cosmos_container(db_name, container_name).create_item(body=item)

    def update_cosmos_container_item(self, db_name, container_name, item):
        return self.get_cosmos_container(db_name, container_name).replace_item(item=item['id'], body=item)

    def delete_cosmos_container_item(self, db_name, container_name, item_id):
        return self.get_cosmos_container(db_name, container_name).delete_item(item=item_id, partition_key=item_id)
    
    def get_cosmos_container_items_by_where(self, db_name, container_name, query):
        where = " ".join(f"c.{key} = @{key}" for key in query.keys())
        params = [{"name": f"@{key}", "value": query[key]} for key in query.keys()]
        return list(self.get_cosmos_container(db_name, container_name).query_items(
            query="SELECT * FROM c WHERE " + where,
            parameters=params,
            enable_cross_partition_query=True
            ))