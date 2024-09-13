import sqlite3
import pandas as pd
import os
import datetime
from weekly_monthlly_yearly_utils import time_distribution_graph, create_time_pie_chart
def return_df_and_file_path(date_str):
    # 连接数据库
    db_path = os.path.join('Logs',  "time_records.db")
    conn = sqlite3.connect(db_path)  # 替换为你的数据库文件名
    cursor = conn.cursor()

    # 将输入日期转换为 datetime 对象
    input_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')

    # 计算上一个星期的起始日期和结束日期
    start_date = input_date - datetime.timedelta(days=input_date.weekday()) - datetime.timedelta(days=7)
    end_date = start_date + datetime.timedelta(days=6)
    print(start_date)
    print(end_date)

    # 查询数据库
    cursor.execute('''
        SELECT * FROM time_records
        WHERE date BETWEEN ? AND ?
    ''', (start_date.date(), end_date.date()))
    results = cursor.fetchall()
    print(results)

    # 创建 DataFrame
    df = pd.DataFrame(results, columns=['id', 'start_time', 'end_time', 'date', 'category', 'task_name', 'comments', 'time_type'])

    # 生成 Markdown 文件
    file_name_prefix = f"week_{start_date.strftime('%Y-%m-%d')}"
    file_folder_path = os.path.join('Logs', input_date.strftime('%Y'), input_date.strftime('%Y%m'))
    conn.close()
    return df, file_name_prefix, file_folder_path
def write_into_markdown(text, file_folder_path, file_name_prefix):
    import markdown

    # 生成图片文件名称
    file_name_piechart_timetype = file_name_prefix + "_piechart_timetype.png"
    file_name_piechart_category = file_name_prefix + "_piechart_category.png"
    file_name_time_dist = file_name_prefix + "_time_dist.png"
    md_content = f"""---
Created: {date_str}
type: Logs
---
"""
    # 构造 Markdown 内容
    md_content += f""" ![{file_name_piechart_timetype.split('/')[-1]}]({file_name_piechart_timetype})
![{file_name_piechart_category.split('/')[-1]}]({file_name_piechart_category})
![{file_name_time_dist.split('/')[-1]}]({file_name_time_dist})

    {text}
    """

    # 写入 Markdown 文件
    md_file_path = os.path.join(file_folder_path, f"{file_name_prefix}.md")
    with open(md_file_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

if __name__ == '__main__':

    import sys
    date_str = sys.argv[1]
    df, file_name_prefix, file_folder_path = return_df_and_file_path(date_str)    #basic_pic()
    time_distribution_graph(df, file_folder_path, file_name_prefix)
    markdown_info = create_time_pie_chart(df, file_folder_path, file_name_prefix)
    write_into_markdown(markdown_info, file_folder_path, file_name_prefix)
