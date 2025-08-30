import json

from .mysql_module.shein_return_order_model import SheinReturnOrderManager
from .mysql_module.shein_product_model import SheinProductManager
from .fun_base import log

class SheinMysql:
    def __init__(self, config):
        self.config = config

    def upsert_shein_return_order(self, json_file):
        log(f'当前使用的数据库: {self.config.db.database_url}')
        # 创建管理器实例
        manager = SheinReturnOrderManager(self.config.db.database_url)
        # 创建数据表
        manager.create_tables()
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            dict = json.load(f)
            for store_username, data_list in dict.items():
                manager.upsert_return_order_data(store_username, data_list)

    def upsert_shein_product(self, json_file):
        log(f'当前使用的数据库: {self.config.db.database_url}')
        # 创建管理器实例
        manager = SheinProductManager(self.config.db.database_url)
        # 创建数据表
        manager.create_tables()
        with open(json_file, 'r', encoding='utf-8') as f:
            file_list = json.load(f)
            for store_username, store_skc_list_file in file_list.items():
                with open(store_skc_list_file, 'r', encoding='utf-8') as f:
                    dict_store_skc_list = json.load(f)
                    for store_username, data_list in dict_store_skc_list.items():
                        manager.upsert_product_data(data_list)

    def upsert_shein_product_info(self, json_file):
        log(f'当前使用的数据库: {self.config.db.database_url}')
        # 创建管理器实例
        manager = SheinProductManager(self.config.db.database_url)
        # 创建数据表
        manager.create_tables()
        with open(json_file, 'r', encoding='utf-8') as f:
            file_list = json.load(f)
            for store_username, store_spu_list in file_list.items():
                for spu in store_spu_list:
                    product_detail_file = f'{self.config.auto_dir}/shein/product_detail/product_detail_{spu}.json'
                    attribute_file = f'{self.config.auto_dir}/shein/attribute/attribute_template_{spu}.json'
                    with open(product_detail_file, 'r', encoding='utf-8') as f:
                        data_list = json.load(f)
                        manager.upsert_product_detail(spu, 'product_detail', data_list)
                    with open(attribute_file, 'r', encoding='utf-8') as f:
                        data_list = json.load(f)
                        manager.upsert_product_detail(spu, 'attribute_template', data_list)
