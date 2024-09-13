from datetime import datetime, timedelta
import sys
import os

def process_markdown(file_path,file_path_2write, date_str):
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output = []
    
    # 定义每个二级标题的起始时间和时间增量（以分钟为单位）
    base_times = {
        '1. Morning Skincare': ('07:30:00', 1, "Enjoying"),  # 每个勾选的任务增加 1 分钟
        '2. Rinse Mouth at Noon': ('12:00:00', 3, "Enjoying"),  # 每个勾选的任务增加 2 分钟
        '3. Relaxation at Work': ('12:05:00', 3, "Enjoying"),  # 每个勾选的任务增加 3 分钟
        '1. Early Morning Pilates':('07:00:00',5,"Enjoying"),
        '1-min english presentation': ('08:20:00', 5, "Concentrating")
    }

    current_category = None
    current_sub_category = None
    current_time = None
    time_increment = 1
    checked_count = 0
    checked_items = []

    for line in lines:
        line = line.strip()

        # 检查是否是一级标题
        if line.startswith('# '):
            current_category = line[2:]
        
        # 检查是否是二级标题
        elif line.startswith('## '):
            # 如果之前有记录的勾选项目，生成对应的表格记录
            if current_sub_category and checked_count > 0:
                end_time = (current_time + timedelta(minutes=(checked_count) * time_increment)).strftime('%H:%M:%S')
                checked_items.append(f"|{date_str} {current_time.strftime('%H:%M:%S')}|{date_str} {end_time}|{current_category}|{current_sub_category}|no_comments|{time_type}|")
            
            # 开始新的一组二级标题计时
            current_sub_category = line[3:]
            checked_count = 0
            if current_sub_category in base_times:
                # 初始化开始时间和时间增量
                current_time_str, time_increment, time_type = base_times[current_sub_category]
                current_time = datetime.strptime(current_time_str, '%H:%M:%S')

        # 检查是否勾选了项目
        elif line.startswith('- [x]') or line.startswith('- [X]'):
            checked_count += 1

    # 对最后一个二级标题生成记录（如果有勾选项目）
    if current_sub_category and checked_count > 0:
        end_time = (current_time + timedelta(minutes=(checked_count) * time_increment)).strftime('%H:%M:%S')
        checked_items.append(f"|{date_str} {current_time.strftime('%H:%M:%S')}|{date_str} {end_time}|{current_category}|{current_sub_category}|no_comments|{time_type}|")

    # 将勾选的项目表格添加到文件末尾
    with open(file_path_2write, 'a', encoding='utf-8') as f:
        f.write('\n\n')
        f.write('以下是勾选的项目表格:\n\n')
        for item in checked_items:
            f.write(item + '\n')
def create_folder_structure(date_obj):
    """
    Create the folder structure based on the given date object.

    Args:
        date_obj (datetime): Parsed datetime object.
    
    Returns:
        str: The full path of the file to be created.
    """
    year = date_obj.year
    month = f"{year}{date_obj.month:02d}"
    filename = f"{date_obj.strftime('%Y-%m-%d')}_checklist.md"
    filename_2write = f"{date_obj.strftime('%Y-%m-%d')}.md"
    folder_path = os.path.join("Logs", str(year), month)

    # Create directories if they don't exist
    os.makedirs(folder_path, exist_ok=True)

    return os.path.join(folder_path, filename), os.path.join(folder_path, filename_2write)
# 使用函数
if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("请在命令行输入正确的日期格式, 例如: python script.py 2024-08-15")
        sys.exit(1)

    date_str = sys.argv[1]
    
    # Parse the date string
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    # Create folder structure and get the file path
    file_path,file_path_2write = create_folder_structure(date_obj)

    process_markdown(file_path, file_path_2write, date_str)

