#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
店铺销售明细数据模型
使用SQLAlchemy定义store_sales_detail表结构
"""

from sqlalchemy import and_
from sqlalchemy import create_engine, Column, Integer, String, Date, DECIMAL, UniqueConstraint
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from datetime import datetime, timedelta

from sqlalchemy import distinct

# 创建基础类
Base = declarative_base()

# 定义模型类
class SheinStoreSalesDetail(Base):
    __tablename__ = 'store_sales_detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    store_username = Column(String(255), nullable=True)
    store_name = Column(String(255), nullable=True)
    day = Column(Date, nullable=True)
    sales_num = Column(Integer, nullable=True)
    sales_num_inc = Column(Integer, nullable=True)
    sales_amount = Column(DECIMAL(10, 2), nullable=True)
    sales_amount_inc = Column(DECIMAL(10, 2), nullable=True)
    visitor_num = Column(Integer, nullable=True)
    visitor_num_inc = Column(Integer, nullable=True)
    bak_A_num = Column(Integer, nullable=True)
    bak_A_num_inc = Column(Integer, nullable=True)
    new_A_num = Column(Integer, nullable=True)
    new_A_num_inc = Column(Integer, nullable=True)
    on_sales_product_num = Column(Integer, nullable=True)
    on_sales_product_num_inc = Column(Integer, nullable=True)
    wait_shelf_product_num = Column(Integer, nullable=True)
    wait_shelf_product_num_inc = Column(Integer, nullable=True)
    upload_product_num = Column(Integer, nullable=True)
    upload_product_num_inc = Column(Integer, nullable=True)
    sold_out_product_num = Column(Integer, nullable=True)
    shelf_off_product_num = Column(Integer, nullable=True)
    remark = Column(String(255), nullable=True)

    __table_args__ = (
        UniqueConstraint('store_username', 'day', name='uq_store_day'),
    )

    def __repr__(self):
        return f"<SheinStoreSalesDetail(store_username={self.store_username}, store_name={self.store_name}, day={self.day})>"

class SheinStoreSalesDetailManager:
    """
    店铺销售明细数据管理器
    提供数据库操作相关方法
    """

    # database_url = f"mysql+pymysql://{config.mysql_username}:{config.mysql_password}@{config.mysql_host}:{config.mysql_port}/{config.mysql_database}"

    def __init__(self, database_url=None):
        """
        初始化数据库连接
        
        Args:
            database_url (str): 数据库连接URL，例如：
                mysql+pymysql://username:password@localhost:3306/database_name
        """
        if database_url is None:
            database_url = self.database_url

        self.engine = create_engine(database_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """
        创建数据表
        """
        Base.metadata.create_all(self.engine)
        print("✅ 数据表检查并创建完毕（如不存在则自动创建）")

    def drop_tables(self):
        """
        删除数据表
        """
        Base.metadata.drop_all(self.engine)
        print("数据表删除成功！")

    def get_session(self):
        """
        创建会话
        
        Returns:
            session: SQLAlchemy会话对象
        """
        return self.Session()

    def get_all_records(self):
        """
        查询所有记录
        
        Returns:
            list: 所有销售明细记录列表
        """
        session = self.get_session()
        try:
            records = session.query(SheinStoreSalesDetail).all()
            return records
        finally:
            session.close()

    def get_records_by_username_and_day(self, username, query_day):
        """
        查询特定用户名和日期的记录
        
        Args:
            username (str): 店铺用户名
            query_day (date): 查询日期
            
        Returns:
            list: 符合条件的记录列表
        """
        session = self.get_session()
        try:
            records = session.query(SheinStoreSalesDetail).filter(
                SheinStoreSalesDetail.store_username == username,
                SheinStoreSalesDetail.day == query_day
            ).all()
            return records
        finally:
            session.close()

    def get_records_sorted_by_sales_amount(self):
        """
        查询记录并按销售金额排序
        
        Returns:
            list: 按销售金额倒序排列的记录列表
        """
        session = self.get_session()
        try:
            records = session.query(SheinStoreSalesDetail).order_by(SheinStoreSalesDetail.sales_amount.desc()).all()
            return records
        finally:
            session.close()

    def get_limited_records(self, limit):
        """
        查询并限制结果数量
        
        Args:
            limit (int): 限制的记录数量
            
        Returns:
            list: 限制数量的记录列表
        """
        session = self.get_session()
        try:
            records = session.query(SheinStoreSalesDetail).limit(limit).all()
            return records
        finally:
            session.close()

    def get_records_by_usernames(self, usernames):
        """
        查询多个店铺用户名的记录
        
        Args:
            usernames (list): 店铺用户名列表
            
        Returns:
            list: 符合条件的记录列表
        """
        session = self.get_session()
        try:
            records = session.query(SheinStoreSalesDetail).filter(
                SheinStoreSalesDetail.store_username.in_(usernames)
            ).all()
            return records
        finally:
            session.close()

    def record_to_dict(self, record):
        """
        将记录转换为字典
        
        Args:
            record: SQLAlchemy记录对象
            
        Returns:
            dict: 记录字典
        """
        return {column.name: getattr(record, column.name) for column in record.__table__.columns}

    def get_records_by_condition(self, filter_condition, order_by=None):
        """
        公共查询函数（包含排序功能）
        
        Args:
            filter_condition: SQLAlchemy过滤条件
            order_by: 排序条件
            
        Returns:
            list: 符合条件的记录列表
        """
        session = self.get_session()
        try:
            # 执行查询，添加排序功能
            query = session.query(SheinStoreSalesDetail).filter(filter_condition)

            # 如果传入了排序条件，则加入排序
            if order_by is not None:
                query = query.order_by(order_by)

            # 获取查询结果
            records = query.all()
            return records

        except Exception as e:
            import traceback
            print("数据库错误:", e)
            traceback.print_exc()
            return []

        finally:
            # 确保会话关闭
            session.close()

    def get_distinct_store_sales_list(self):
        """
        获取 distinct 的 store_username 和 store_name
        
        Returns:
            list: 唯一店铺用户名列表
        """
        session = self.get_session()
        try:
            # 执行 distinct 查询，选择唯一的 store_username 和 store_name
            records = session.query(
                distinct(SheinStoreSalesDetail.store_username)
            ).all()

            # 转换查询结果为二维列表格式
            result = [[record[0], ''] for record in records]
            return result

        finally:
            # 确保会话关闭
            session.close()

    def get_one_day_records(self, yesterday, order_by=None):
        """
        获取单日数据
        
        Args:
            yesterday (str): 日期字符串，格式：'YYYY-MM-DD'
            order_by: 排序条件，默认按销售数量倒序
            
        Returns:
            list: 指定日期的记录列表
        """
        if order_by is None:
            order_by = SheinStoreSalesDetail.sales_num.desc()

        # 将字符串日期转换为 datetime.date 对象
        yesterday_date = datetime.strptime(yesterday, '%Y-%m-%d').date()

        # 定义查询条件
        filter_condition = SheinStoreSalesDetail.day == yesterday_date

        # 使用公共查询函数，传入排序条件
        return self.get_records_by_condition(filter_condition, order_by)

    def get_one_month_records(self, year, month, username, order_by=None):
        """
        获取某年某月的数据
        
        Args:
            year (int): 年份
            month (int): 月份
            username (str): 店铺用户名
            order_by: 排序条件，默认按日期升序
            
        Returns:
            list: 指定月份的记录列表
        """
        if order_by is None:
            order_by = SheinStoreSalesDetail.day.asc()

        # 将年份和月份格式化为日期（构造该月的第一天）
        first_day_of_month = datetime(year, month, 1).date()

        # 获取该月的最后一天
        last_day_of_month = (first_day_of_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        # 定义查询条件：查询指定年份和月份的记录
        filter_condition = and_(
            SheinStoreSalesDetail.day >= first_day_of_month,
            SheinStoreSalesDetail.day <= last_day_of_month,
            SheinStoreSalesDetail.store_username == username,
        )

        # 使用公共查询函数，传入排序条件
        return self.get_records_by_condition(filter_condition, order_by)

    def get_records_as_dict(self, username, query_day_str):
        """
        获取指定用户名和日期的记录并转换为字典
        
        Args:
            username (str): 店铺用户名
            query_day_str (str): 查询日期字符串，格式：'YYYY-MM-DD'
            
        Returns:
            dict: 记录字典，如果没有记录则返回空字典
        """
        # 将字符串日期转换为 datetime.date 对象
        query_day = datetime.strptime(query_day_str, '%Y-%m-%d').date()
        # 获取数据库会话
        session = self.get_session()
        try:
            # 查询特定条件的记录
            records = session.query(SheinStoreSalesDetail).filter(
                SheinStoreSalesDetail.store_username == username,
                SheinStoreSalesDetail.day == query_day
            ).all()
            # 如果没有记录，返回一个空字典
            if not records:
                return {}
            # 将记录转换为字典
            records_dict = [
                {column.name: getattr(record, column.name) for column in SheinStoreSalesDetail.__table__.columns}
                for record in records
            ]

            return records_dict[0]

        finally:
            session.close()

    def insert_data(self, data_list):
        """
        插入多条数据
        
        Args:
            data_list (list): 要插入的数据列表，每个元素为字典格式
        """
        # 获取会话
        session = self.get_session()
        try:
            # 将字典转换为模型对象并插入
            records = []
            for data in data_list:
                record = SheinStoreSalesDetail(**data)  # 将字典解包为关键字参数
                records.append(record)
            # 将所有记录添加到会话
            session.add_all(records)
            # 提交事务
            session.commit()
            print(f"成功插入 {len(records)} 条数据")
        except Exception as e:
            # 如果发生错误，回滚事务
            session.rollback()
            print(f"插入数据时发生错误: {e}")
            #raise
        finally:
            # 关闭会话
            session.close()

if __name__ == '__main__':
    # 新的管理器方式示例（取消注释以运行测试）
    pass
