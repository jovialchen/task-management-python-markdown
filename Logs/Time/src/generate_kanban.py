import os
import datetime
import re
import sqlite3
from update_due_date import update_tasks


def get_intermediate_dirs_with_task(task_file, first_level_dir_path):
    """获取task.md文件所在目录到first_level_dir_path之间的所有目录名称, 并附加task.md"""
    relative_path = os.path.relpath(task_file, first_level_dir_path)
    intermediate_dirs = relative_path.split(os.path.sep)[:-2]  # 只去掉文件名
    intermediate_dirs_with_task = []
    for i in range(len(intermediate_dirs) - 1, -1, -1):
        path = os.path.join(*intermediate_dirs[:i + 1], "task.md")
        intermediate_dirs_with_task.append(path)
    return intermediate_dirs[::-1], intermediate_dirs_with_task

def parse_task_file(task_file, first_level_dir, first_level_dir_path, priority_order):
    """解析单个task.md文件，提取任务信息"""
    intermediate_dirs, intermediate_paths = get_intermediate_dirs_with_task(task_file, first_level_dir_path)
    
    with open(task_file, "r", encoding="utf8") as f:
        lines = f.readlines()

    task_title = lines[0].replace("# 题目：", "").strip()
    priority, frequency, content_type, due_date = None, None, None, None
    
    for i, line in enumerate(lines):
        priority = extract_priority(line, lines, i, priority, priority_order)
        frequency = extract_field(line, lines, i, frequency, "**Frequency:**")
        content_type = extract_field(line, lines, i, content_type, "**Content Type:**")
        if line.startswith("## Due Date"):
            due_date = lines[i + 1].strip()

    task_description = build_task_description(task_file, first_level_dir, priority, frequency, content_type, due_date)
    task_name = os.path.dirname(task_file).split(os.path.sep)[-1]
    return task_description, intermediate_dirs, intermediate_paths, due_date, priority, task_name

def extract_priority(line, lines, index, current_priority, priority_order):
    """从任务文件中提取Priority"""
    if "**Priority:**" in line:
        for j in range(index + 1, index + 8):
            if j < len(lines):
                for p in priority_order:
                    if f"-  [x] **{p}:**" in lines[j]:
                        return p
    return current_priority

def extract_field(line, lines, index, current_value, field_name):
    """从任务文件中提取字段值（如频率、Type）"""
    if field_name in line:
        for j in range(index + 1, index + 6):
            if j < len(lines) and "-  [x]" in lines[j]:
                return lines[j].split("] ")[1].strip()
    return current_value

def build_task_description(task_file, first_level_dir, priority, frequency, content_type, due_date):
    relative_path =  os.path.join('Tasks', os.path.relpath(task_file, 'Tasks'))   
    linux_style_path = "../../" + (relative_path.replace('\\', '/'))
    """构建任务的描述"""
    return (f"- [{os.path.dirname(task_file).split(os.path.sep)[-1]}](<{linux_style_path}>)"
            f" |Priority：{priority or 'None'} | Frequency：{frequency or 'N/A'} | "
            f"Type：{content_type or 'N/A'} | Due Date:{due_date or 'N/A'}")

def sort_tasks_by_due_date(tasks):
    """根据截止日期对任务进行排序"""
    def custom_sort(task):
        try:
            due_date_obj = datetime.datetime.strptime(task[3], "%Y-%m-%d")
            return due_date_obj
        except ValueError:
            return datetime.datetime.max  # 将没有截止日期的任务排在最后
    return sorted(tasks, key=custom_sort)
def write_tasks_to_file_per_cat(tasks_by_priority, priority_order, output_dir):
    """将任务写入Markdown文件，每个一级目录对应一个文件"""
    for priority in priority_order:
        if tasks_by_priority[priority]:
            for first_level_dir, tasks in tasks_by_priority[priority].items():
                if first_level_dir in ("Excercise", "GoodHabits"):
                    continue

                # 生成文件名，例如：output_dir/first_level_dir.md
                output_file = os.path.join(output_dir, f"{first_level_dir}.md")
                write_metadata(output_file)

                with open(output_file, "a", encoding="utf8") as f_out:
                    f_out.write(f"# {priority} \n\n")
                    if priority == "Inattentive":
                        tasks = sort_tasks_by_due_date(tasks)
                    for task_description, intermediate_dirs, intermediate_paths, due_date, priority, task_name in tasks:
                        f_out.write("## "+ task_name + "\n")
                        f_out.write(task_description + "\n")
                        write_subtasks(f_out, intermediate_dirs, intermediate_paths, first_level_dir)
                        f_out.write("\n")

def write_metadata(file_path):
    """
    Append the notes and time reference template to the markdown file.

    Args:
        file_path (str): Path to the file where the notes will be appended.
    """
    with open(file_path, 'a', encoding="utf8") as f:
        f.write(
f"""---
type: Kanban
---
"""
        )
def write_tasks_to_file(tasks_by_priority, priority_order, output_file):
    write_metadata(output_file)
    """将任务写入Markdown文件"""
    with open(output_file, "a", encoding="utf8") as f_out:
        for priority in priority_order:
            if tasks_by_priority[priority]:
                f_out.write(f"# {priority} \n\n")
                for first_level_dir, tasks in tasks_by_priority[priority].items():
                    if (first_level_dir == "Excercise" or first_level_dir == "GoodHabits"):
                        continue
                    f_out.write(f"## {first_level_dir} \n\n")
                    if priority == "Inattentive":
                        tasks = sort_tasks_by_due_date(tasks)
                    for task_description, intermediate_dirs, intermediate_paths, due_date, priority, _ in tasks:
                        f_out.write(task_description + "\n")
                        write_subtasks(f_out, intermediate_dirs, intermediate_paths, first_level_dir)
                        f_out.write("\n")
def write_checklist_to_file(tasks_by_priority, priority_order, output_file):
    write_metadata(output_file)
    """将任务写入Markdown文件"""
    with open(output_file, "a", encoding="utf8") as f_out:
        for priority in priority_order:
            if tasks_by_priority[priority]:
                f_out.write(f"# {priority} \n\n")
                for first_level_dir, tasks in tasks_by_priority[priority].items():
                    if (first_level_dir == "Excercise" or first_level_dir == "GoodHabits"):
                        continue
                    f_out.write(f"## {first_level_dir} \n\n")
                    if priority == "Inattentive":
                        tasks = sort_tasks_by_due_date(tasks)
                    for task_description, intermediate_dirs, intermediate_paths, due_date, priority, task_name in tasks:
                        f_out.write(f"- [ ] |{task_name}|{first_level_dir}|(@{due_date})" + "\n")
                        f_out.write("\n")

def write_subtasks(f_out, intermediate_dirs, intermediate_paths,first_level_dir):
    """写入子任务"""
    indent = "  "
    for intermediate_dir, intermediate_path in zip(intermediate_dirs, intermediate_paths):
        file_path = os.path.join(first_level_dir, intermediate_path)
        relative_path = os.path.join("Tasks", file_path)
        linux_style_path = "../../" + (relative_path.replace('\\', '/'))
        f_out.write(f"{indent}- is subtask to [{intermediate_dir}](<{linux_style_path}>)\n")
        indent += "  "

def collect_tasks(task_dir, priority_order):
    tasks_by_priority = {priority: {} for priority in priority_order}
    
    for first_level_dir in filter(lambda d: os.path.isdir(os.path.join(task_dir, d)), os.listdir(task_dir)):
        first_level_dir_path = os.path.join(task_dir, first_level_dir)

        for dirpath, _, filenames in os.walk(first_level_dir_path):
            if "task.md" in filenames:
                task_file = os.path.join(dirpath, "task.md")
                task_info = parse_task_file(task_file, first_level_dir, first_level_dir_path, priority_order)
                task_description, intermediate_dirs, intermediate_paths, due_date, priority, _ = task_info
                
                if priority:
                    tasks_by_priority[priority].setdefault(first_level_dir, []).append(task_info)
    
    return tasks_by_priority

def remove_all_files(directory):
    file_path = os.path.join(directory, 'everything_kanban.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'checklist_kanban.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'Technical.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'Parenting.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'Work.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'Birthday.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'Errands.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'SoftSkills.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")
    file_path = os.path.join(directory, 'Art.md')
    if os.path.isfile(file_path):
        os.remove(file_path)
        print(f"已删除文件: {file_path}")

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

def create_or_connect_db(db_name):
    """Create or connect to a SQLite database."""
    return sqlite3.connect(os.path.join('Logs', db_name))

def write_database_from_checklist(table_errands ):
    """Main function to write to the database and log contents."""
    # Connect to databases
    conn_errands = create_or_connect_db('errands.db')

    # Create tables
    create_errands_table(conn_errands)


    # Clear and insert data into errands
    clear_and_insert_errands(conn_errands, table_errands)
    conn_errands.commit()

    # Log contents for debugging
    #log_table_contents(conn_errands, "errands")

    # Close database connections
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
    new_status = 1 if status == 'x' else 0
    result.append((name, cat, date, new_status))
  return result

def extract_tables_from_markdown(file_path):
    """提取Markdown文件中的表格，逐行匹配正则表达式

    Args:
        file_path: Markdown文件路径。

    Returns:
        一个包含所有提取到的表格的列表。
    """

    table_errands = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:

            # 匹配表格任务的正则表达式
            errand_match = re.match(r'- \[(x| )\] \|(.+?)\|(.+?)\|\(@(\d{4}-\d{2}-\d{2})\)', line)
            if errand_match:
                table_errands.append(errand_match.groups())
    if table_errands != []:
        table_errands = convert_status(table_errands)
    return table_errands


def main():
    task_dir = "Tasks"
    kanban_dir = os.path.join("Logs", "Kanban")
    output_file = os.path.join(kanban_dir, "everything_kanban.md")
    checklist_file = os.path.join(kanban_dir, "checklist_kanban.md")

    tables = extract_tables_from_markdown(checklist_file)
    write_database_from_checklist(tables)
    update_tasks()


    remove_all_files(kanban_dir)
    priority_order = ["Critical", "High", "Everyday", "Pending", "Inattentive", "Medium", "Low"]
    
    tasks_by_priority = collect_tasks(task_dir, priority_order)
    write_tasks_to_file(tasks_by_priority, priority_order, output_file)
    write_tasks_to_file_per_cat(tasks_by_priority, priority_order, kanban_dir)
    write_checklist_to_file(tasks_by_priority, priority_order, checklist_file)

    print(f"任务已导出到 {output_file} 文件中！")

if __name__ == "__main__":
    main()



