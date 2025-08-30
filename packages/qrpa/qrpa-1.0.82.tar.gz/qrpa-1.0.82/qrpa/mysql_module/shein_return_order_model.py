#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHEIN退货订单数据模型
使用SQLAlchemy定义退货单表和退货明细表结构
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Date, DECIMAL, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import json
import os

# 创建基类
Base = declarative_base()

class SheinReturnOrder(Base):
    """
    SHEIN退货单表
    存储退货单的基本信息
    """
    __tablename__ = 'shein_return_order'

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 原始数据中的ID作为return_id
    return_id = Column(Integer, nullable=False, unique=True, comment='原始退货单ID')

    # 退货单号（也可作为唯一标识）
    return_order_no = Column(String(50), nullable=False, unique=True, comment='退货单号')

    # 商家信息
    seller_id = Column(Integer, nullable=True, comment='商家ID')
    supplier_id = Column(Integer, nullable=True, comment='供应商ID')
    store_type = Column(Integer, nullable=True, comment='店铺类型')
    store_code = Column(String(50), nullable=True, comment='店铺编码')
    store_username = Column(String(50), nullable=True, comment='店铺账号')
    store_name = Column(String(50), nullable=True, comment='店铺别名')
    store_manager = Column(String(50), nullable=True, comment='店长')

    # 退货方式和物流信息
    return_way_type = Column(Integer, nullable=True, comment='退货方式类型')
    return_way_type_name = Column(String(50), nullable=True, comment='退货方式名称')
    return_express_company_code = Column(String(50), nullable=True, comment='退货快递公司编码')
    return_express_company_name = Column(String(100), nullable=True, comment='退货快递公司名称')
    express_no_list = Column(Text, nullable=True, comment='快递单号列表')

    # 地址信息
    return_address = Column(Text, nullable=True, comment='退货地址')
    take_parcel_address = Column(Text, nullable=True, comment='取件地址')

    # 仓库信息
    warehouse_id = Column(Integer, nullable=True, comment='仓库ID')
    warehouse_name = Column(String(100), nullable=True, comment='仓库名称')
    warehouse_en_name = Column(String(100), nullable=True, comment='仓库英文名称')
    warehouse_in_charge_phone = Column(String(50), nullable=True, comment='仓库负责人电话')
    warehouse_in_charge_person = Column(String(50), nullable=True, comment='仓库负责人')
    warehouse_detail_address = Column(Text, nullable=True, comment='仓库详细地址')

    # 退货计划和状态
    return_plan_no = Column(String(50), nullable=True, comment='退货计划号')
    return_order_type = Column(Integer, nullable=True, comment='退货单类型')
    return_order_type_name = Column(String(50), nullable=True, comment='退货单类型名称')
    return_order_status = Column(Integer, nullable=True, comment='退货单状态')
    return_order_status_name = Column(String(50), nullable=True, comment='退货单状态名称')

    # 数量和金额
    wait_return_quantity = Column(Integer, nullable=True, comment='待退货数量')
    return_quantity = Column(Integer, nullable=True, comment='退货数量')
    return_amount = Column(DECIMAL(10, 2), nullable=True, comment='退货金额')
    pricing_currency_id = Column(Integer, nullable=True, comment='定价货币ID')
    currency_code = Column(String(10), nullable=True, comment='货币代码')

    # 退货原因
    return_reason_type = Column(Integer, nullable=True, comment='退货原因类型')
    return_reason_type_name = Column(String(100), nullable=True, comment='退货原因类型名称')
    return_reason = Column(Text, nullable=True, comment='退货原因')
    reject_pic_url_list = Column(JSON, nullable=True, comment='拒绝图片URL列表')

    # 商品信息
    skc_name_list = Column(JSON, nullable=True, comment='SKC名称列表')
    supplier_code_list = Column(JSON, nullable=True, comment='供应商编码列表')
    goods_thumb = Column(Text, nullable=True, comment='商品缩略图')

    # 联系人信息
    seller_contract = Column(String(50), nullable=True, comment='卖家联系人')
    seller_contract_phone = Column(String(50), nullable=True, comment='卖家联系电话')

    # 订单相关
    seller_order_no = Column(String(50), nullable=True, comment='卖家订单号')
    seller_order_no_list = Column(JSON, nullable=True, comment='卖家订单号列表')
    seller_delivery_no = Column(String(50), nullable=True, comment='卖家发货单号')

    # 报废和质检
    return_scrap_type = Column(Integer, nullable=True, comment='退货报废类型')
    return_scrap_type_name = Column(String(50), nullable=True, comment='退货报废类型名称')
    return_dimensions = Column(Integer, nullable=True, comment='退货维度')

    # 其他标识
    stock_mode = Column(Integer, nullable=True, comment='库存模式')
    order_type = Column(Integer, nullable=True, comment='订单类型')
    skc_num = Column(Integer, nullable=True, comment='SKC数量')
    has_package = Column(Integer, nullable=True, comment='是否有包裹')
    has_report_url = Column(Integer, nullable=True, comment='是否有报告')
    is_sign = Column(Integer, nullable=True, comment='是否签收')
    is_increase = Column(Integer, nullable=True, comment='是否增长')
    can_apply_reconsider = Column(Integer, nullable=True, comment='是否可申请复议')

    # 报告链接
    qc_report_url = Column(Text, nullable=True, comment='质检报告URL')
    report_url = Column(Text, nullable=True, comment='报告URL')

    # 时间字段
    add_time = Column(DateTime, nullable=True, comment='添加时间')
    sign_time = Column(DateTime, nullable=True, comment='签收时间(物流)')
    complete_time = Column(DateTime, nullable=True, comment='出库完成时间')

    # 系统时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 用户备注字段（供后续web界面使用）
    user_notes = Column(Text, nullable=True, comment='用户备注')

    return_factotry_status = Column(Integer, nullable=True, comment='退回工厂状态,1已退回,2未退回')
    return_factotry_by = Column(String(50), nullable=True, comment='退回工厂操作人')
    financial_settlement_status = Column(Integer, nullable=True, comment='财务结算状态,1已结算,2未结算')

    # 定义索引
    __table_args__ = (
        Index('ix_return_order_no', 'return_order_no'),
        Index('ix_return_id', 'return_id'),
        Index('ix_seller_order_no', 'seller_order_no'),
    )

    def __repr__(self):
        return f"<SheinReturnOrder(id={self.id}, return_order_no='{self.return_order_no}', status='{self.return_order_status_name}')>"

class SheinReturnOrderDetail(Base):
    """
    SHEIN退货包裹明细表
    存储退货包裹中具体商品的详细信息
    """
    __tablename__ = 'shein_return_order_detail'

    # 主键ID
    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')

    # 关联退货单ID
    return_order_id = Column(Integer, nullable=False, comment='关联退货单ID')

    # 包裹信息
    express_code = Column(String(50), nullable=True, comment='快递编码')
    delivery_time = Column(DateTime, nullable=True, comment='发货时间')
    self_pick_start_time = Column(DateTime, nullable=True, comment='自提开始时间')
    supplier_category_type_flag = Column(Integer, nullable=True, comment='供应商分类类型标志')

    # 包裹基本信息
    package_name = Column(String(50), nullable=True, comment='包裹名称')
    return_box_no = Column(String(50), nullable=True, comment='退货箱号')

    # 商品信息
    img_path = Column(Text, nullable=True, comment='商品图片路径')
    skc = Column(String(50), nullable=True, comment='SKC编码')
    skc_copy_flag = Column(Integer, nullable=True, comment='SKC复制标志')
    supplier_code = Column(String(100), nullable=True, comment='供应商编码')

    # SKU详细信息
    platform_sku = Column(String(50), nullable=True, comment='平台SKU')
    supplier_sku = Column(String(100), nullable=True, comment='供应商SKU')
    suffix_zh = Column(String(100), nullable=True, comment='中文后缀')
    return_quantity = Column(Integer, nullable=True, comment='退货数量')

    # 时间戳
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 用户备注字段
    detail_notes = Column(Text, nullable=True, comment='明细备注')

    erp_supplier_name = Column(String(50), nullable=True, comment='erp默认供货商')
    erp_cost_price = Column(DECIMAL(10, 2), nullable=True, comment='erp成本价')

    sign_quantity = Column(Integer, nullable=True, comment='仓库签收数量')
    sign_at = Column(DateTime, nullable=True, comment='仓库签收时间,sign_quantity字段变动时更新')
    return_factotry_status = Column(Integer, nullable=True, comment='退回工厂状态,1已退回,2未退回')
    return_factotry_by = Column(String(50), nullable=True, comment='退回工厂操作人')
    financial_settlement_status = Column(Integer, nullable=True, comment='财务结算状态,1已结算,2未结算')

    # 定义索引
    __table_args__ = (
        Index('ix_supplier_sku', 'supplier_sku'),
        Index('ix_return_order_id', 'return_order_id'),
    )

    def __repr__(self):
        return f"<SheinReturnOrderDetail(id={self.id}, skc='{self.skc}', return_quantity={self.return_quantity})>"

class SheinReturnOrderManager:
    """
    SHEIN退货订单数据管理器
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

    def _parse_datetime(self, datetime_str):
        """
        解析datetime字符串
        """
        if not datetime_str:
            return None
        try:
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        except:
            return None

    def upsert_return_order_data(self, store_username, data_list):
        """
        从JSON文件中读取数据并执行upsert操作（插入或更新）
        
        Args:
            json_file_path (str): JSON文件路径
        """
        session = self.Session()
        try:

            for data in data_list:
                data['store_username'] = store_username
                # 检查是否已存在该退货单
                existing_order = session.query(SheinReturnOrder).filter_by(
                    return_id=data.get('id')
                ).first()

                if existing_order:
                    # 更新现有记录（只更新非备注字段，保留用户添加的备注）
                    self._update_return_order(session, existing_order, data)
                else:
                    # 插入新记录
                    self._insert_return_order(session, data)

            session.commit()
            print(f"成功处理 {len(data_list)} 条退货单数据")

        except Exception as e:
            session.rollback()
            print(f"处理数据失败: {e}")
            raise
        finally:
            session.close()

    def _insert_return_order(self, session, data):
        """
        插入新的退货单记录
        """
        # 创建退货单主记录
        return_order = SheinReturnOrder(
            return_id=data.get('id'),
            return_order_no=data.get('returnOrderNo'),
            seller_id=data.get('sellerId'),
            supplier_id=data.get('supplierId'),
            store_username=data.get('store_username'),
            store_name=data.get('store_name'),
            store_manager=data.get('store_manager'),
            store_type=data.get('storeType'),
            store_code=data.get('storeCode'),
            return_way_type=data.get('returnWayType'),
            return_way_type_name=data.get('returnWayTypeName'),
            return_express_company_code=data.get('returnExpressCompanyCode'),
            return_express_company_name=data.get('returnExpressCompanyName'),
            express_no_list=data.get('expressNoList'),
            return_address=data.get('returnAddress'),
            take_parcel_address=data.get('takeParcelAddress'),
            warehouse_id=data.get('warehouseId'),
            warehouse_name=data.get('warehouseName'),
            warehouse_en_name=data.get('warehouseEnName'),
            warehouse_in_charge_phone=data.get('warehouseInChargePhone'),
            warehouse_in_charge_person=data.get('warehouseInChargePerson'),
            warehouse_detail_address=data.get('warehouseDetailAddress'),
            return_plan_no=data.get('returnPlanNo'),
            return_order_type=data.get('returnOrderType'),
            return_order_type_name=data.get('returnOrderTypeName'),
            return_order_status=data.get('returnOrderStatus'),
            return_order_status_name=data.get('returnOrderStatusName'),
            wait_return_quantity=data.get('waitReturnQuantity'),
            return_quantity=data.get('returnQuantity'),
            return_amount=data.get('returnAmount'),
            pricing_currency_id=data.get('pricingCurrencyId'),
            currency_code=data.get('currencyCode'),
            return_reason_type=data.get('returnReasonType'),
            return_reason_type_name=data.get('returnReasonTypeName'),
            return_reason=data.get('returnReason'),
            reject_pic_url_list=data.get('rejectPicUrlList'),
            skc_name_list=data.get('skcNameList'),
            supplier_code_list=data.get('supplierCodeList'),
            goods_thumb=data.get('goodsThumb'),
            seller_contract=data.get('sellerContract'),
            seller_contract_phone=data.get('sellerContractPhone'),
            seller_order_no=data.get('sellerOrderNo'),
            seller_order_no_list=data.get('sellerOrderNoList'),
            seller_delivery_no=data.get('sellerDeliveryNo'),
            return_scrap_type=data.get('returnScrapType'),
            return_scrap_type_name=data.get('returnScrapTypeName'),
            return_dimensions=data.get('returnDimensions'),
            stock_mode=data.get('stockMode'),
            order_type=data.get('orderType'),
            skc_num=data.get('skcNum'),
            has_package=data.get('hasPackage'),
            has_report_url=data.get('hasReportUrl'),
            is_sign=data.get('isSign'),
            is_increase=data.get('isIncrease'),
            can_apply_reconsider=data.get('canApplyReconsider'),
            qc_report_url=data.get('qc_report_url'),
            report_url=data.get('report_url'),
            add_time=self._parse_datetime(data.get('addTime')),
            sign_time=self._parse_datetime(data.get('signTime')),
            complete_time=self._parse_datetime(data.get('completeTime'))
        )

        session.add(return_order)
        session.flush()  # 获取主键ID

        # 插入明细记录
        self._insert_return_order_details(session, return_order.id, data.get('return_box_detail', []))

    def _update_return_order(self, session, existing_order, data):
        """
        更新现有的退货单记录（保留用户备注,只更新下面这些替换的）
        """

        # 更新主记录字段（除了用户备注）
        existing_order.return_order_no = data.get('returnOrderNo')
        existing_order.seller_id = data.get('sellerId')
        existing_order.supplier_id = data.get('supplierId')
        existing_order.store_type = data.get('storeType')
        existing_order.store_code = data.get('storeCode')
        existing_order.return_way_type = data.get('returnWayType')
        existing_order.return_way_type_name = data.get('returnWayTypeName')
        existing_order.return_express_company_code = data.get('returnExpressCompanyCode')
        existing_order.return_express_company_name = data.get('returnExpressCompanyName')
        existing_order.express_no_list = data.get('expressNoList')
        existing_order.return_address = data.get('returnAddress')
        existing_order.take_parcel_address = data.get('takeParcelAddress')
        existing_order.warehouse_id = data.get('warehouseId')
        existing_order.warehouse_name = data.get('warehouseName')
        existing_order.warehouse_en_name = data.get('warehouseEnName')
        existing_order.warehouse_in_charge_phone = data.get('warehouseInChargePhone')
        existing_order.warehouse_in_charge_person = data.get('warehouseInChargePerson')
        existing_order.warehouse_detail_address = data.get('warehouseDetailAddress')
        existing_order.return_plan_no = data.get('returnPlanNo')
        existing_order.return_order_type = data.get('returnOrderType')
        existing_order.return_order_type_name = data.get('returnOrderTypeName')
        existing_order.return_order_status = data.get('returnOrderStatus')
        existing_order.return_order_status_name = data.get('returnOrderStatusName')
        existing_order.wait_return_quantity = data.get('waitReturnQuantity')
        existing_order.return_quantity = data.get('returnQuantity')
        existing_order.return_amount = data.get('returnAmount')
        existing_order.pricing_currency_id = data.get('pricingCurrencyId')
        existing_order.currency_code = data.get('currencyCode')
        existing_order.return_reason_type = data.get('returnReasonType')
        existing_order.return_reason_type_name = data.get('returnReasonTypeName')
        existing_order.return_reason = data.get('returnReason')
        existing_order.reject_pic_url_list = data.get('rejectPicUrlList')
        existing_order.skc_name_list = data.get('skcNameList')
        existing_order.supplier_code_list = data.get('supplierCodeList')
        existing_order.goods_thumb = data.get('goodsThumb')
        existing_order.seller_contract = data.get('sellerContract')
        existing_order.seller_contract_phone = data.get('sellerContractPhone')
        existing_order.seller_order_no = data.get('sellerOrderNo')
        existing_order.seller_order_no_list = data.get('sellerOrderNoList')
        existing_order.seller_delivery_no = data.get('sellerDeliveryNo')
        existing_order.return_scrap_type = data.get('returnScrapType')
        existing_order.return_scrap_type_name = data.get('returnScrapTypeName')
        existing_order.return_dimensions = data.get('returnDimensions')
        existing_order.stock_mode = data.get('stockMode')
        existing_order.order_type = data.get('orderType')
        existing_order.skc_num = data.get('skcNum')
        existing_order.has_package = data.get('hasPackage')
        existing_order.has_report_url = data.get('hasReportUrl')
        existing_order.is_sign = data.get('isSign')
        existing_order.is_increase = data.get('isIncrease')
        existing_order.can_apply_reconsider = data.get('canApplyReconsider')
        existing_order.qc_report_url = data.get('qc_report_url')
        existing_order.report_url = data.get('report_url')
        existing_order.add_time = self._parse_datetime(data.get('addTime'))
        existing_order.sign_time = self._parse_datetime(data.get('signTime'))
        existing_order.complete_time = self._parse_datetime(data.get('completeTime'))
        existing_order.updated_at = datetime.now()

        # 不更新 明细记录
        # # 删除旧的明细记录
        # session.query(SheinReturnOrderDetail).filter_by(return_order_id=existing_order.id).delete()

        # # 插入新的明细记录
        # self._insert_return_order_details(session, existing_order.id, data.get('return_box_detail', []))

    def _insert_return_order_details(self, session, return_order_id, return_box_details):
        """
        插入退货明细记录
        """
        for box_detail in return_box_details:
            express_code = box_detail.get('expressCode')
            delivery_time = self._parse_datetime(box_detail.get('deliveryTime'))
            self_pick_start_time = self._parse_datetime(box_detail.get('selfPickStartTime'))
            supplier_category_type_flag = 1 if box_detail.get('supplierCategoryTypeFlag') else 0

            for box in box_detail.get('boxList', []):
                package_name = box.get('packageName')
                return_box_no = box.get('returnBoxNo')

                for goods in box.get('goods', []):
                    img_path = goods.get('imgPath')
                    skc = goods.get('skc')
                    skc_copy_flag = goods.get('skcCopyFlag')
                    supplier_code = goods.get('supplierCode')

                    for detail in goods.get('details', []):
                        detail_record = SheinReturnOrderDetail(
                            return_order_id=return_order_id,
                            express_code=express_code,
                            delivery_time=delivery_time,
                            self_pick_start_time=self_pick_start_time,
                            supplier_category_type_flag=supplier_category_type_flag,
                            package_name=package_name,
                            return_box_no=return_box_no,
                            img_path=img_path,
                            skc=skc,
                            skc_copy_flag=skc_copy_flag,
                            supplier_code=supplier_code,
                            platform_sku=detail.get('platformSku'),
                            supplier_sku=detail.get('supplierSku'),
                            suffix_zh=detail.get('suffixZh'),
                            return_quantity=detail.get('returnQuantity'),
                            erp_supplier_name=detail.get('erp_supplier_name'),
                            erp_cost_price=detail.get('erp_cost_price')
                        )
                        session.add(detail_record)

    def get_return_orders(self, limit=None, offset=None):
        """
        查询退货单列表
        
        Args:
            limit (int): 限制返回数量
            offset (int): 偏移量
            
        Returns:
            list: 退货单列表
        """
        session = self.Session()
        try:
            query = session.query(SheinReturnOrder)
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def search_return_orders(self, **kwargs):
        """
        根据条件搜索退货单
        
        Args:
            **kwargs: 搜索条件，如return_order_no, seller_id等
            
        Returns:
            list: 符合条件的退货单列表
        """
        session = self.Session()
        try:
            query = session.query(SheinReturnOrder)

            # 根据传入的条件进行过滤
            for key, value in kwargs.items():
                if hasattr(SheinReturnOrder, key) and value is not None:
                    query = query.filter(getattr(SheinReturnOrder, key) == value)

            return query.all()
        finally:
            session.close()

    def update_user_notes(self, return_order_id, notes):
        """
        更新用户备注
        
        Args:
            return_order_id (int): 退货单ID
            notes (str): 备注内容
        """
        session = self.Session()
        try:
            order = session.query(SheinReturnOrder).filter_by(id=return_order_id).first()
            if order:
                order.user_notes = notes
                order.updated_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

def example_usage():
    """
    使用示例
    """
    # 数据库连接URL（请根据实际情况修改）
    database_url = "mysql+pymysql://root:123wyk@localhost:3306/lz"

    # 创建管理器实例
    manager = SheinReturnOrderManager(database_url)

    # 创建数据表
    manager.create_tables()

    # 从JSON文件导入数据
    json_file = "shein_return_order_list_2025-08-17_2025-08-19.json"

    # 读取JSON文件
    with open(json_file, 'r', encoding='utf-8') as f:
        dict = json.load(f)
        for store_username, data_list in dict.items():
            manager.upsert_return_order_data(store_username, data_list)

    # 查询示例
    orders = manager.get_return_orders(limit=10)
    for order in orders:
        print(f"退货单号: {order.return_order_no}, 状态: {order.return_order_status_name}")

    # 搜索示例
    search_results = manager.search_return_orders(return_order_status=4)
    print(f"已全部出库的订单数量: {len(search_results)}")

    # 更新备注示例
    # if orders:
    #     manager.update_user_notes(orders[0].id, "这是一个测试备注")

if __name__ == "__main__":
    pass
    example_usage()
