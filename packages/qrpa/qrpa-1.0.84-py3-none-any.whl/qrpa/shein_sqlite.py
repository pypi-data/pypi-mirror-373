from .fun_base import log

import sqlite3
from datetime import datetime, timedelta
import os
import sys


auto_dir = 'D:/auto'
db_file = f'{auto_dir}/shein/db/shein_sku_sales.db'

# log(db_file)


def main(args):
    init_db()
    # exists_sales_1_days_ago('653231597')
    # log(get_last_week_sales('6960380466'))
    # log(get_sales('6960380466', '2025-02-25', '2025-03-04'))
    # log(get_near_week_sales('I46mraado10r'))
    # log(get_last_week_sales('I46mraado10r','2025-03-08','2025-03-14'))
    # create_indexes()

def init_db():
    # 获取文件夹路径
    folder_path = os.path.dirname(db_file)
    # 如果文件夹不存在，则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        log(f"文件夹已创建: {folder_path}")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skc TEXT,
            date TEXT,
            skc_sale INTEGER,
            skc_order INTEGER,
            sku TEXT,
            attr_name TEXT,
            sku_sale INTEGER,
            sku_order INTEGER
        )
    ''')
    conn.commit()
    conn.close()
    log('新建数据库成功', db_file)

init_db()

def insert_sales(skc, date, skc_sale, skc_order, sku, attr_name, sku_sale, sku_order):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 1 FROM sales WHERE sku = ? AND date = ?
    ''', (sku, date))

    if cursor.fetchone() is None:
        cursor.execute('''
            INSERT INTO sales (skc, date, skc_sale, skc_order, sku, attr_name, sku_sale, sku_order)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (skc, date, skc_sale, skc_order, sku, attr_name, sku_sale, sku_order))
        conn.commit()

    conn.close()

def get_sales(sku, start_date, end_date):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT SUM(sku_sale), SUM(sku_order) FROM sales WHERE sku = ? AND date BETWEEN ? AND ?
    ''', (sku, start_date, end_date))

    result = cursor.fetchone()  # 获取查询结果
    sales_num = result[0] if result[0] is not None else 0
    orders_num = result[1] if result[1] is not None else 0

    conn.close()

    log('get_sales:', sku, start_date, end_date, sales_num, orders_num)
    return sales_num, orders_num  # 返回销售量和订单量的元组

def get_last_week_sales(sku):
    today = datetime.today().date()
    # last_week_start = today - timedelta(days=today.weekday() + 14)
    last_week_start = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")
    last_week_end = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
    # log('远7天',last_week_start,last_week_end,sku)
    return get_sales(sku, str(last_week_start), str(last_week_end))

def get_near_week_sales(sku):
    today = datetime.today().date()
    # last_week_start = today - timedelta(days=today.weekday() + 14)
    last_week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    last_week_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # log('远7天',last_week_start,last_week_end,sku)
    return get_sales(sku, str(last_week_start), str(last_week_end))

def get_last_month_sales(sku):
    today = datetime.today().date()
    # first_day_of_this_month = today.replace(day=1)
    # last_month_end = first_day_of_this_month - timedelta(days=1)
    # last_month_start = last_month_end.replace(day=1)
    last_month_start = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d")
    last_month_end = (datetime.now() - timedelta(days=31)).strftime("%Y-%m-%d")
    # log('远30天',last_month_start,last_month_end,sku)
    return get_sales(sku, str(last_month_start), str(last_month_end))

def get_near_month_sales(sku):
    today = datetime.today().date()
    # first_day_of_this_month = today.replace(day=1)
    # last_month_end = first_day_of_this_month - timedelta(days=1)
    # last_month_start = last_month_end.replace(day=1)
    last_month_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    last_month_end = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    # log('远30天',last_month_start,last_month_end,sku)
    return get_sales(sku, str(last_month_start), str(last_month_end))

def exists_sales_1_days_ago(skc):
    conn = sqlite3.connect(db_file)  # 替换成你的数据库文件
    cursor = conn.cursor()
    date_threshold = (datetime.today().date() - timedelta(days=1)).isoformat()
    # 使用 str.format() 格式化 SQL
    sql = '''
        SELECT 1 FROM sales WHERE skc = '{skc}' AND date = '{date}' LIMIT 1
    '''.format(skc=skc, date=date_threshold)
    log("exists_sales_1_days_ago:", sql.strip())  # 打印 SQL 语句
    cursor.execute('''
        SELECT 1 FROM sales WHERE skc = ? AND date <= ? LIMIT 1
    ''', (skc, date_threshold))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def create_indexes():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    # 创建 spu + date 联合索引
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_sales_skc_date ON sales (skc, date);
    ''')
    # 创建 sku + date 唯一索引
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_sales_sku_date_unique ON sales (sku, date);
    ''')
    conn.commit()  # 提交更改
    conn.close()  # 关闭连接
    log("索引创建成功！")

init_db()

if __name__ == '__main__':
    main(sys.argv)