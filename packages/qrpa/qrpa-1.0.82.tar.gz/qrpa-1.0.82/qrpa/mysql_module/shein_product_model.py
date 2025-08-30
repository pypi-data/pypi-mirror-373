#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHEIN商品数据模型
使用SQLAlchemy定义SKC表、SKU表和详情表结构
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Date, DECIMAL, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

# 创建基类
Base = declarative_base()

class SheinProductSkc(Base):
    """
    SHEIN商品SKC表
    存储SKC维度的商品信息
    """
    __tablename__ = 'shein_product_skc'

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 原始数据中的ID作为skc_id
    skc_id = Column(Integer, nullable=False, unique=True, comment='原始SKC ID')

    # 店铺信息
    store_username = Column(String(50), nullable=True, comment='店铺账号')
    store_name = Column(String(100), nullable=True, comment='店铺名称')
    store_manager = Column(String(50), nullable=True, comment='店长')

    # 商品基本信息
    pic_url = Column(Text, nullable=True, comment='SKC主图')
    supplier_code = Column(String(100), nullable=True, comment='商家SKC')
    skc = Column(String(50), nullable=True, comment='平台SKC')
    spu = Column(String(50), nullable=True, comment='SPU编码')
    category_name = Column(String(100), nullable=True, comment='叶子类目')

    # 上架信息
    shelf_days = Column(Integer, nullable=True, comment='上架天数')
    shelf_date = Column(Date, nullable=True, comment='上架日期')

    # 商品标签和状态
    goods_label_list = Column(JSON, nullable=True, comment='商品标签列表')
    supply_status = Column(String(50), nullable=True, comment='供货状态')
    shelf_status = Column(Integer, nullable=True, comment='上架状态')
    goods_level = Column(String(50), nullable=True, comment='商品等级')

    # 其他字段
    group_flag = Column(Integer, nullable=True, comment='组合标志')
    goods_level_can_order_flag = Column(Integer, nullable=True, comment='商品等级可下单标志')
    stock_standard = Column(Integer, nullable=True, comment='备货标准')
    stock_warn_status = Column(Integer, nullable=True, comment='库存预警状态')

    # 销量汇总
    c7d_sale_cnt_sum = Column(Integer, nullable=True, comment='7日销量汇总')
    shein_sale_by_inventory = Column(Integer, nullable=True, comment='希音库存销售')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 定义索引
    __table_args__ = (
        Index('ix_skc_id', 'skc_id'),
        Index('ix_skc', 'skc'),
        Index('ix_spu', 'spu'),
        Index('ix_supplier_code', 'supplier_code'),
        Index('ix_store_username', 'store_username'),
    )

    def __repr__(self):
        return f"<SheinProductSkc(id={self.id}, skc='{self.skc}', spu='{self.spu}')>"

class SheinProductSku(Base):
    """
    SHEIN商品SKU表
    存储SKU维度的商品信息
    """
    __tablename__ = 'shein_product_sku'

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 原始数据中的ID作为sku_id
    sku_id = Column(Integer, nullable=False, unique=True, comment='原始SKU ID')

    # 关联SKC本地主键ID
    local_skc_id = Column(Integer, nullable=False, comment='关联的SKC本地主键ID')

    # SKU基本信息
    sort_value = Column(Integer, nullable=True, comment='排序值')
    sku_code = Column(String(50), nullable=True, comment='SKU编码')
    attr = Column(String(100), nullable=True, comment='SKU属性')
    supplier_sku = Column(String(100), nullable=True, comment='供应商SKU')

    # 销量数据
    order_cnt = Column(Integer, nullable=True, comment='今日订单数')
    total_sale_volume = Column(Integer, nullable=True, comment='今日总销量')
    c7d_sale_cnt = Column(Integer, nullable=True, comment='7日销量')
    c30d_sale_cnt = Column(Integer, nullable=True, comment='30日销量')

    # 价格成本信息
    price = Column(DECIMAL(10, 2), nullable=True, comment='价格')
    erp_cost_price = Column(DECIMAL(10, 2), nullable=True, comment='ERP成本价')
    erp_supplier_name = Column(String(100), nullable=True, comment='ERP默认供货商')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 定义索引
    __table_args__ = (
        Index('ix_sku_id', 'sku_id'),
        Index('ix_local_skc_id', 'local_skc_id'),
        Index('ix_sku_code', 'sku_code'),
        Index('ix_supplier_sku', 'supplier_sku'),
    )

    def __repr__(self):
        return f"<SheinProductSku(id={self.id}, sku_code='{self.sku_code}', attr='{self.attr}')>"

class SheinProductDetail(Base):
    """
    SHEIN商品详情信息表
    以KV形式保存SPU维度的JSON数据
    """
    __tablename__ = 'shein_product_detail'

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # SPU编码
    spu = Column(String(50), nullable=False, comment='SPU编码')

    # 字段名称
    field_name = Column(String(100), nullable=False, comment='字段名称')

    # JSON数据
    json_data = Column(JSON, nullable=True, comment='JSON数据')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 定义索引
    __table_args__ = (
        Index('ix_spu', 'spu'),
        Index('ix_field_name', 'field_name'),
        Index('ix_spu_field', 'spu', 'field_name'),
    )

    def __repr__(self):
        return f"<SheinProductDetail(id={self.id}, spu='{self.spu}', field_name='{self.field_name}')>"

class SheinProductManager:
    """
    SHEIN商品数据管理器
    提供数据库操作相关方法
    """

    def __init__(self, database_url):
        """
        初始化数据库连接
        
        Args:
            database_url (str): 数据库连接URL，例如：
                mysql+pymysql://username:password@localhost:3306/database_name
        """
        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """
        创建数据表
        """
        Base.metadata.create_all(self.engine)
        print("数据表创建成功！")

    def drop_tables(self):
        """
        删除数据表
        """
        Base.metadata.drop_all(self.engine)
        print("数据表删除成功！")

    def _parse_date(self, date_str):
        """
        解析日期字符串
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            return None

    def _extract_goods_labels(self, goods_label_list):
        """
        提取商品标签名称列表
        """
        if not goods_label_list:
            return []
        return [label.get('name', '') for label in goods_label_list if isinstance(label, dict)]

    def upsert_product_data(self, data_list):
        """
        从JSON数据中执行upsert操作（插入或更新）
        
        Args:
            store_username (str): 店铺账号
            data_list (list): 商品数据列表
        """
        session = self.Session()
        try:
            for data in data_list:
                
                # 处理SKC数据
                skc_record = self._upsert_skc_data(session, data)
                
                # 处理SKU数据
                for sku_data in data.get('skuList', []):
                    sku_data['local_skc_id'] = skc_record.id
                    self._upsert_sku_data(session, sku_data)

            session.commit()
            print(f"成功处理 {len(data_list)} 条商品数据")

        except Exception as e:
            session.rollback()
            print(f"处理数据失败: {e}")
            raise
        finally:
            session.close()

    def _upsert_skc_data(self, session, data):
        """
        插入或更新SKC数据
        返回SKC记录对象
        """
        skc_id = data.get('id')
        existing_skc = session.query(SheinProductSkc).filter_by(skc_id=skc_id).first()

        if existing_skc:
            # 更新现有记录（保留用户备注）
            existing_skc.store_username = data.get('store_username')
            existing_skc.store_name = data.get('store_name')
            existing_skc.store_manager = data.get('store_manager')
            existing_skc.pic_url = data.get('picUrl')
            existing_skc.supplier_code = data.get('supplierCode')
            existing_skc.skc = data.get('skc')
            existing_skc.spu = data.get('spu')
            existing_skc.category_name = data.get('categoryName')
            existing_skc.shelf_days = data.get('shelfDays')
            existing_skc.shelf_date = self._parse_date(data.get('shelfDate'))
            existing_skc.goods_label_list = self._extract_goods_labels(data.get('goodsLabelList'))
            existing_skc.supply_status = data.get('supplyStatus', {}).get('name') if data.get('supplyStatus') else None
            existing_skc.shelf_status = data.get('shelfStatus', {}).get('value') if data.get('shelfStatus') else None
            existing_skc.goods_level = data.get('goodsLevel', {}).get('name') if data.get('goodsLevel') else None
            existing_skc.group_flag = data.get('groupFlag')
            existing_skc.goods_level_can_order_flag = 1 if data.get('goodsLevelCanOrderFlag') else 0
            existing_skc.stock_standard = data.get('stockStandard', {}).get('value') if data.get('stockStandard') else None
            existing_skc.stock_warn_status = data.get('stockWarnStatus', {}).get('value') if data.get('stockWarnStatus') else None
            existing_skc.c7d_sale_cnt_sum = data.get('c7dSaleCntSum')
            existing_skc.shein_sale_by_inventory = data.get('sheinSaleByInventory')
            existing_skc.updated_at = datetime.now()
            return existing_skc
        else:
            # 插入新记录
            new_skc = SheinProductSkc(
                skc_id=skc_id,
                store_username=data.get('store_username'),
                store_name=data.get('store_name'),
                store_manager=data.get('store_manager'),
                pic_url=data.get('picUrl'),
                supplier_code=data.get('supplierCode'),
                skc=data.get('skc'),
                spu=data.get('spu'),
                category_name=data.get('categoryName'),
                shelf_days=data.get('shelfDays'),
                shelf_date=self._parse_date(data.get('shelfDate')),
                goods_label_list=self._extract_goods_labels(data.get('goodsLabelList')),
                supply_status=data.get('supplyStatus', {}).get('name') if data.get('supplyStatus') else None,
                shelf_status=data.get('shelfStatus', {}).get('value') if data.get('shelfStatus') else None,
                goods_level=data.get('goodsLevel', {}).get('name') if data.get('goodsLevel') else None,
                group_flag=data.get('groupFlag'),
                goods_level_can_order_flag=1 if data.get('goodsLevelCanOrderFlag') else 0,
                stock_standard=data.get('stockStandard', {}).get('value') if data.get('stockStandard') else None,
                stock_warn_status=data.get('stockWarnStatus', {}).get('value') if data.get('stockWarnStatus') else None,
                c7d_sale_cnt_sum=data.get('c7dSaleCntSum'),
                shein_sale_by_inventory=data.get('sheinSaleByInventory')
            )
            session.add(new_skc)
            session.flush()  # 获取主键ID
            return new_skc

    def _upsert_sku_data(self, session, sku_data):
        """
        插入或更新SKU数据
        """
        sku_id = sku_data.get('id')
        existing_sku = session.query(SheinProductSku).filter_by(sku_id=sku_id).first()

        if existing_sku:
            # 更新现有记录（保留用户备注）
            existing_sku.local_skc_id = sku_data.get('local_skc_id')
            existing_sku.sort_value = sku_data.get('sortValue')
            existing_sku.sku_code = sku_data.get('skuCode')
            existing_sku.attr = sku_data.get('attr')
            existing_sku.supplier_sku = sku_data.get('supplierSku')
            existing_sku.order_cnt = sku_data.get('orderCnt')
            existing_sku.total_sale_volume = sku_data.get('totalSaleVolume')
            existing_sku.c7d_sale_cnt = sku_data.get('c7dSaleCnt')
            existing_sku.c30d_sale_cnt = sku_data.get('c30dSaleCnt')
            existing_sku.price = sku_data.get('price')
            existing_sku.erp_cost_price = sku_data.get('erp_cost_price')
            existing_sku.erp_supplier_name = sku_data.get('erp_supplier_name')
            existing_sku.updated_at = datetime.now()
        else:
            # 插入新记录
            new_sku = SheinProductSku(
                sku_id=sku_id,
                local_skc_id=sku_data.get('local_skc_id'),
                sort_value=sku_data.get('sortValue'),
                sku_code=sku_data.get('skuCode'),
                attr=sku_data.get('attr'),
                supplier_sku=sku_data.get('supplierSku'),
                order_cnt=sku_data.get('orderCnt'),
                total_sale_volume=sku_data.get('totalSaleVolume'),
                c7d_sale_cnt=sku_data.get('c7dSaleCnt'),
                c30d_sale_cnt=sku_data.get('c30dSaleCnt'),
                price=sku_data.get('price'),
                erp_cost_price=sku_data.get('erp_cost_price'),
                erp_supplier_name=sku_data.get('erp_supplier_name')
            )
            session.add(new_sku)

    def upsert_product_detail(self, spu, field_name, json_data):
        """
        插入或更新商品详情数据
        
        Args:
            spu (str): SPU编码
            field_name (str): 字段名称
            json_data (dict): JSON数据
        """
        session = self.Session()
        try:
            existing_detail = session.query(SheinProductDetail).filter_by(
                spu=spu, field_name=field_name
            ).first()

            if existing_detail:
                # 更新现有记录
                existing_detail.json_data = json_data
                existing_detail.updated_at = datetime.now()
            else:
                # 插入新记录
                new_detail = SheinProductDetail(
                    spu=spu,
                    field_name=field_name,
                    json_data=json_data
                )
                session.add(new_detail)

            session.commit()
            print(f"成功处理详情数据: spu={spu}, field_name={field_name}")

        except Exception as e:
            session.rollback()
            print(f"处理详情数据失败: {e}")
            raise
        finally:
            session.close()

    def get_skc_products(self, limit=None, offset=None):
        """
        查询SKC商品列表
        
        Args:
            limit (int): 限制返回数量
            offset (int): 偏移量
            
        Returns:
            list: SKC商品列表
        """
        session = self.Session()
        try:
            query = session.query(SheinProductSkc)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def search_products(self, **kwargs):
        """
        根据条件搜索商品
        
        Args:
            **kwargs: 搜索条件，如skc, spu, store_username等
            
        Returns:
            list: 符合条件的商品列表
        """
        session = self.Session()
        try:
            query = session.query(SheinProductSkc)

            # 根据传入的条件进行过滤
            for key, value in kwargs.items():
                if hasattr(SheinProductSkc, key) and value is not None:
                    if isinstance(value, str) and key in ['skc', 'spu', 'supplier_code', 'category_name']:
                        # 字符串字段支持模糊搜索
                        query = query.filter(getattr(SheinProductSkc, key).like(f'%{value}%'))
                    else:
                        query = query.filter(getattr(SheinProductSkc, key) == value)

            return query.all()
        finally:
            session.close()

def example_usage():
    """
    使用示例
    """
    # 数据库连接URL（请根据实际情况修改）
    database_url = "mysql+pymysql://root:123wyk@localhost:3306/lz"

    # 创建管理器实例
    manager = SheinProductManager(database_url)

    # 创建数据表
    manager.create_tables()

    # 从JSON文件导入数据
    json_file = "skc_list_GS4355889.json"

    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)
        for store_username, data_list in data_dict.items():
            manager.upsert_product_data(data_list)

    # 查询示例
    products = manager.get_skc_products(limit=10)
    for product in products:
        print(f"SKC: {product.skc}, SPU: {product.spu}, 类目: {product.category_name}")

    # 搜索示例
    search_results = manager.search_products(store_username="GS4355889", shelf_status=1)
    print(f"已上架商品数量: {len(search_results)}")

    # 详情数据示例
    # manager.upsert_product_detail("i250319906447", "attribute_template", {"template_id": "t23082580827"})

def example_usage2():
    database_url = "mysql+pymysql://root:123wyk@localhost:3306/lz"
    manager = SheinProductManager(database_url)
    manager.create_tables()
    # 从JSON文件导入数据
    json_file = "attribute_template_t23082580827.json"
    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)
        manager.upsert_product_detail("t23082580827", "attribute_template", data_dict)

if __name__ == "__main__":
    pass
    # example_usage()