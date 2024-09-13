import sys
import os
import sqlite3
import pandas as pd
import datetime
import re
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from update_due_date import update_tasks

plt.rcParams['font.family'] = 'SimHei'  # 或其他支持汉字的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def read_data_from_db(date_str):
    time_records_db = os.path.join('Logs', 'time_records.db')
    # 假设您已经建立了数据库连接
    conn = sqlite3.connect(time_records_db)
    cursor = conn.cursor()
    date_str = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    # 执行查询语句
    cursor.execute("SELECT * FROM time_records WHERE date = ?", (date_str, ))

    # 获取查询结果
    data = cursor.fetchall()
    conn.close()
    return data

def draw_todays_data(data, date_str, folder_path):
    # 设置颜色映射
    colors = {'Technical': '#ffadad', 'Work': '#ffd6a5', 'GoodHabits': '#fdffb6', 'Excercise': '#caffbf', 'Parenting': '#9bf6ff', 'SoftSkills': '#a0c4ff', 'Art': '#bdb2ff'}
    # 定义状态的排序
    status_order = ['Bystanding', 'Meeting', 'Discussing', 'Presenting', 'Enjoying', 'Concentrating']
    # 处理数据
    df = pd.DataFrame(data, columns=['id', 'start_time', 'end_time', 'date', 'category', 'task', 'comment', 'status'])
    # 将时间列转换为datetime格式
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    # 创建画布
    #fig, ax = plt.subplots(figsize=(12, 6))
    fig, ax = plt.subplots(figsize=(18, 9))  # 调整图形尺寸
    ax.set_facecolor('#000300')

    # 绘制每个数据点
    for index, row in df.iterrows():
        start = row['start_time']
        end = row['end_time']
        status = row['status']
        category = row['category']
        color = colors.get(category, 'gray')  # 如果类别不存在，使用灰色

        # 计算状态在status_order中的索引
        status_index = status_order.index(status)

        # 绘制矩形
        ax.barh(status_index, end - start, left=start, height=0.5, color=color, alpha=0.8)

    # 设置坐标轴
    ax.set_yticks(range(len(status_order)))
    ax.set_yticklabels(status_order)
    ax.set_xlabel('时间')
    ax.set_ylabel('状态')

    # 设置x轴时间格式
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    # 设置标题
    ax.set_title('时间状态分布图')

    # 设置网格线颜色为白色
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='white')    # 显示网格

    # 旋转x轴标签
    plt.xticks(rotation=45)
    # 调整横轴范围，自动适应数据范围
    plt.xlim(df['start_time'].min(), df['end_time'].max())

    # 设置x轴时间格式，显示更详细的时间信息
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))

    # 调整矩形高度，避免重叠
    ax.barh(status_index, end - start, left=start, height=0.4, color=color, alpha=0.8)

    # 显示网格，更清晰地显示数据
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    # 创建颜色标签
    patches = []
    for category, color in colors.items():
        patch = mpatches.Patch(color=color, label=category)
        patches.append(patch)
    # 添加图例
    plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    img_path = os.path.join(folder_path, f"{date_str}.png")
    plt.savefig(img_path, bbox_inches='tight', dpi=300)

def create_or_connect_db(db_name):
    """Create or connect to a SQLite database."""
    return sqlite3.connect(os.path.join('Logs', db_name))

def create_time_records_table(conn):
    """Create the time_records table if it doesn't exist."""
    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS time_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            start_time DATETIME,
            end_time DATETIME,
            date DATE,
            category TEXT,
            task_name TEXT,
            comments TEXT, 
            time_type TEXT 
        );
    '''
    conn.execute(create_table_sql)

def create_errands_table(conn):
    """Create the errands table if it doesn't exist."""
    create_table_sql = '''
        CREATE TABLE IF NOT EXISTS errands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT,
            category TEXT,
            due_date TEXT,
            completed INTEGER
        );
    '''
    conn.execute(create_table_sql)

def clear_time_records(conn, date_str):
    """Delete existing records from time_records for a given date."""
    delete_sql = "DELETE FROM time_records WHERE date = ?"
    conn.execute(delete_sql, (date_str,))

def insert_time_records(conn, tables):
    """Insert new records into time_records."""
    insert_sql = """
        INSERT INTO time_records (start_time, end_time, date, category, task_name, comments, time_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    for record in tables:
        start_time, end_time, category, task_name, comments, time_type = record
        date = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').date()
        conn.execute(insert_sql, (start_time, end_time, date, category, task_name, comments, time_type))

def clear_and_insert_errands(conn, table_errands):
    """Clear and insert errands based on completion status."""
    delete_sql_incomplete = "DELETE FROM errands WHERE completed = ?"
    conn.execute(delete_sql_incomplete, (0,))

    delete_sql_specific = "DELETE FROM errands WHERE task_name = ? AND category = ?"
    insert_sql = """
        INSERT INTO errands (task_name, category, due_date, completed) 
        VALUES (?, ?, ?, ?)
    """
    
    for task_name, category, due_date, completed in table_errands:
        if completed:
            conn.execute(delete_sql_specific, (task_name, category))
            conn.execute(insert_sql, (task_name, category, due_date, completed))

def log_table_contents(conn, table_name):
    """Log the contents of a given table."""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    print(f"Table: {table_name}")

def write_database(file_path, table_errands, tables, date_str):
    """Main function to write to the database and log contents."""
    # Connect to databases
    conn_time_records = create_or_connect_db('time_records.db')
    conn_errands = create_or_connect_db('errands.db')

    # Create tables
    create_time_records_table(conn_time_records)
    create_errands_table(conn_errands)

    # Clear old data and insert new data into time_records
    clear_time_records(conn_time_records, date_str)
    insert_time_records(conn_time_records, tables)
    conn_time_records.commit()

    # Clear and insert data into errands
    clear_and_insert_errands(conn_errands, table_errands)
    conn_errands.commit()

    # Log contents for debugging
    log_table_contents(conn_time_records, "time_records")
    log_table_contents(conn_errands, "errands")

    # Close database connections
    conn_time_records.close()
    conn_errands.close()

def convert_status(data):
  """
  将列表中元组的第三个元素（状态）转换为数字。

  Args:
    data: 待转换的列表。

  Returns:
    转换后的列表。
  """

  result = []
  for item in data:
    status, name, cat, date = item
    new_status = 1 if (status == 'x' or status == 'X') else 0
    result.append((name, cat, date, new_status))
  return result

def extract_tables_from_markdown(file_path):
    """提取Markdown文件中的表格，逐行匹配正则表达式

    Args:
        file_path: Markdown文件路径。

    Returns:
        一个包含所有提取到的表格的列表。
    """

    tables = []
    table_errands = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            # 匹配表格的正则表达式
            table_match = re.match(r'\|(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\|(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\|(.+?)\|(.+?)\|(.+?)\|(.+?)\|', line)
            if table_match:
                tables.append(table_match.groups())

            # 匹配表格任务的正则表达式
            errand_match = re.match(r'- \[(x|X| )\] .*\|(.+?)\|(.+?)\|\(\@(\d{4}-\d{2}-\d{2})\).*', line)
            if errand_match:
                table_errands.append(errand_match.groups())
    if table_errands != []:
        table_errands = convert_status(table_errands)
    return tables, table_errands

def read_file(date_str):
    """
    根据输入的日期字符串创建对应的Markdown文件。

    Args:
        date_str (str): 日期字符串，格式为YYYY-MM-DD。
    """

    # 解析日期字符串
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')

    # 构造文件夹路径和文件名
    year = date_obj.year
    month = f"{year}{date_obj.month:02d}"
    filename = f"{date_str}.md"
    folder_path = os.path.join("Logs", str(year), month)

    # 创建文件夹
    os.makedirs(folder_path, exist_ok=True)

    # 创建文件
    file_path = os.path.join(folder_path, filename)
    if not os.path.exists(file_path):
        print(f"文件 {file_path} 不存在。")
        return None
    else:
        return file_path, folder_path
def todays_report(data, date_str, folder_path):
    markdown_output =  f"""---
Created: {date_str}
type: Logs
---
"""
    report_path = os.path.join(folder_path, f"{date_str}_report.md")
    # 计算总时间
    time_per_category = {}
    total_time = 0

    for entry in data:
        start_time_str = entry[1]
        end_time_str = entry[2]
        category = entry[7]  # 最后一栏分类

        # 解析时间字符串为 datetime 对象
        start_time = datetime.datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        # 计算时间差（以秒为单位）
        duration = (end_time - start_time).total_seconds()

        # 累加时间到对应分类
        if category in time_per_category:
            time_per_category[category] += duration
        else:
            time_per_category[category] = duration

        # 累加到总时间
        total_time += duration

    # 输出每个分类的总时间（以小时为单位）
    for category, time_seconds in time_per_category.items():
        markdown_output += f"Category __'{category}'__ total time: {time_seconds / 3600:.2f} hours\n"

    # 输出总时间
    markdown_output += f"__Total time__: {total_time / 3600:.2f} hours\n"
    markdown_output += f"![Figure for today's time usage]({date_str}.png)\n"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("请在命令行输入正确的日期格式, 例如: python script.py 2024-08-15")
        sys.exit(1)

    date_str = sys.argv[1]
    
    file_path, folder_path = read_file(date_str)
    tables, table_errands = extract_tables_from_markdown(file_path)
    write_database(file_path, table_errands, tables, date_str)
    data = read_data_from_db(date_str)
    draw_todays_data(data, date_str, folder_path)
    todays_report(data, date_str, folder_path)
    update_tasks()

    print(f"report completed for {date_str}")