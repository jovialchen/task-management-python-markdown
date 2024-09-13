import os
import sys
import datetime

def get_intermediate_dirs_with_task(task_file, first_level_dir_path):
  """
  Gets all directory names between the task.md file and the first-level directory,
  including the task.md file itself in each directory path.

  Args:
      task_file (str): Path to the task.md file.
      first_level_dir_path (str): Path to the first-level directory.

  Returns:
      tuple: A tuple containing three elements:
          - project_name (str): Name of the project directory (highest directory).
          - intermediate_dirs (list): List of directory names in reverse order.
          - intermediate_dirs_with_task (list): List of paths to task.md in each directory.
  """

  relative_path = os.path.relpath(task_file, first_level_dir_path)
  intermediate_dirs = relative_path.split(os.path.sep)[:-2]

  project_name = intermediate_dirs[0] if intermediate_dirs else relative_path.split(os.path.sep)[-2]

  intermediate_dirs_with_task = [
      os.path.join(*intermediate_dirs[:i + 1], "task.md")
      for i in range(len(intermediate_dirs))
  ]

  return project_name, intermediate_dirs[::-1], intermediate_dirs_with_task

def filter_tasks_by_due_date(tasks, cutoff_date_str):
    """
    过滤任务,保留dueDate小于等于cutoff_date的任务

    Args:
        tasks (list): 任务列表，每个元素是一个元组
        cutoff_date_str (str): 截止日期，格式为YYYY-MM-DD

    Returns:
        list: 过滤后的任务列表
    """

    cutoff_date = datetime.datetime.strptime(cutoff_date_str, '%Y-%m-%d').date() + datetime.timedelta(days=3)
    filtered_tasks = []
    for task in tasks:
        task_due_date = datetime.datetime.strptime(task[3], '%Y-%m-%d').date()
        if task_due_date <= cutoff_date:
            filtered_tasks.append(task)
    return filtered_tasks
def parse_task_file(task_file, first_level_dir, first_level_dir_path, priority_order):
    """解析单个task.md文件，提取任务信息"""
    project_name, intermediate_dirs, intermediate_paths = get_intermediate_dirs_with_task(task_file, first_level_dir_path)
    
    print(task_file)
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
    return task_description, intermediate_dirs, intermediate_paths, due_date, priority, project_name, first_level_dir

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
    """构建任务的描述"""
    relative_path =  os.path.join('Tasks', os.path.relpath(task_file, 'Tasks'))   
    linux_style_path = "../../../" + (relative_path.replace('\\', '/'))
    if (first_level_dir == "Errands" or first_level_dir == "Birthday"):
        return (f"- [{os.path.dirname(task_file).split(os.path.sep)[-1]}](<{linux_style_path}>) "
            f"Type：{content_type or 'N/A'} | Due Date:{due_date or 'N/A'}")
    else:
        return (f"- [{os.path.dirname(task_file).split(os.path.sep)[-1]}](<{linux_style_path}>) "
            f"Type：{content_type or 'N/A'}")

def sort_tasks_by_due_date(tasks):
    """根据截止日期对任务进行排序"""
    def custom_sort(task):
        try:
            due_date_obj = datetime.datetime.strptime(task[3], "%Y-%m-%d")
            return due_date_obj
        except ValueError:
            return datetime.datetime.max  # 将没有截止日期的任务排在最后
    return sorted(tasks, key=custom_sort)

def write_tasks_to_file(tasks_by_priority, priority_order, output_file, date_str):
    """将任务写入Markdown文件"""
    with open(output_file, "a", encoding="utf8") as f_out:
        for priority in priority_order:
            if tasks_by_priority[priority]:
                f_out.write(f"## {priority} \n\n")
                for first_level_dir, tasks in tasks_by_priority[priority].items():
                    if priority == "Inattentive":
                        tasks = filter_tasks_by_due_date(tasks, date_str)
                        if not tasks:
                            continue
                        tasks = sort_tasks_by_due_date(tasks)
                    f_out.write(f"### {first_level_dir} \n\n")
                    for task_description, intermediate_dirs, intermediate_paths, due_date, priority, project_name, first_level_dir in tasks:
                        f_out.write(task_description + "\n")
                        write_subtasks(f_out, intermediate_dirs, intermediate_paths, first_level_dir)
                        f_out.write("\n")

def write_markdown_header(file):
    file.write(f"""
## Time Records for Today
|start|end|category|project|comments|type|
|---|---|---|---|---|---|
""")

def write_inattentive_tasks(tasks, file):
    file.write(f"""
## Errands Done Today\r\n 
""")
    for task_description, intermediate_dirs, intermediate_paths, due_date, priority, project_name, first_level_dir in tasks:
        print(project_name)
        file.write(f"- [ ] |{project_name}|{first_level_dir}|(@{due_date})\n")

def write_other_tasks(tasks, file):
    for task_description, intermediate_dirs, intermediate_paths, due_date, priority, project_name, first_level_dir in tasks:
        print(project_name)
        file.write(f"|||{first_level_dir}|{project_name}|no_comments|Concentrating|\n")

def write_records_to_file(tasks_by_priority, priority_order, output_file, date_str):
    """Writes tasks to a Markdown file."""

    with open(output_file, "a", encoding="utf8", newline='') as f_out:
        tasks_inattentive = []
        tasks_else = []
        for priority in priority_order:
            if tasks_by_priority[priority]:
                for first_level_dir, tasks in tasks_by_priority[priority].items():
                    if priority == "Inattentive":
                        tasks = filter_tasks_by_due_date(tasks, date_str)
                        tasks = sort_tasks_by_due_date(tasks)
                        tasks_inattentive.extend(tasks)
                    else:
                        tasks_else.extend(tasks)
        write_inattentive_tasks(tasks_inattentive, f_out)
        write_markdown_header(f_out)
        write_other_tasks(tasks_else, f_out)

def write_subtasks(f_out, intermediate_dirs, intermediate_paths,first_level_dir):
    """写入子任务"""
    indent = "  "
    for intermediate_dir, intermediate_path in zip(intermediate_dirs, intermediate_paths):
        relative_path =  os.path.join('Tasks', first_level_dir, intermediate_path)
        linux_style_path = "../../../" + (relative_path.replace('\\', '/'))
        f_out.write(f"{indent}- is subtask to [{intermediate_dir}](<{linux_style_path}>)\n")
        indent += "  "

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
    filename = f"{date_obj.strftime('%Y-%m-%d')}.md"
    folder_path = os.path.join("Logs", str(year), month)

    # Create directories if they don't exist
    os.makedirs(folder_path, exist_ok=True)

    return os.path.join(folder_path, filename)

def write_metadata(file_path, date_str):
    """
    Append the notes and time reference template to the markdown file.

    Args:
        file_path (str): Path to the file where the notes will be appended.
    """
    with open(file_path, 'a', encoding="utf8") as f:
        f.write(
f"""---
Created: {date_str}
type: Logs
---
"""
        )

def initialize_file(file_path, date_str):
    """
    Initialize the markdown file with the header.

    Args:
        file_path (str): Path to the file to be created.
        date_str (str): The date string to include in the header.
    """
    if os.path.exists(file_path):
        print(f"文件 {file_path} 已存在，跳过创建。")
        return False

    write_metadata(file_path, date_str)
    with open(file_path, 'a', encoding="utf8") as f:
        f.write(f"# {date_str} 日志\n")
    
    return True


def gather_tasks(root_dir, priority_order):
    """
    Gather tasks by priority from the specified directory.

    Args:
        root_dir (str): The root directory where tasks are stored.
        priority_order (list): List of priorities in the desired order.

    Returns:
        dict: A dictionary of tasks categorized by priority.
    """
    tasks_by_priority = {priority: {} for priority in priority_order}
    
    for first_level_dir in os.listdir(root_dir):
        first_level_dir_path = os.path.join(root_dir, first_level_dir)
        if os.path.isdir(first_level_dir_path):
            for dirpath, _, filenames in os.walk(first_level_dir_path):
                if "task.md" in filenames:
                    task_file = os.path.join(dirpath, "task.md")
                    task_info = parse_task_file(task_file, first_level_dir, first_level_dir_path, priority_order)
                    task_description, intermediate_dirs, intermediate_paths, due_date, priority, project_name, first_level_dir = task_info
                    
                    if priority and priority not in ["Medium", "Low"]:
                        if first_level_dir not in tasks_by_priority[priority]:
                            tasks_by_priority[priority][first_level_dir] = []
                        tasks_by_priority[priority][first_level_dir].append(task_info)
    
    return tasks_by_priority


def append_notes_and_time_references(file_path, date_str):
    """
    Append the notes and time reference template to the markdown file.

    Args:
        file_path (str): Path to the file where the notes will be appended.
    """
    with open(file_path, 'a', encoding="utf8") as f:
        f.write(
            f"""## Notes for Today
!!! question What am I grateful for today? 
!!! My answer

!!! question Did I make progress towards my goals today? 
!!! My answer

!!! abstract My EX BER BER TEA Everyday Tracker {date_str}
    - [ ] 1-min presentation
    - [ ] 英语复习

## Reference for Time Type
- **Concentrating**: Focusing one's attention on something.
- **Enjoying**: Don't have to put all attention on. For practices.
- **Presenting**: Showing or offering something for consideration.
- **Discussing**: Talking about something in order to reach a decision.
- **Meeting**: Coming together for a planned purpose.
- **Bystanding**: Watching something without getting involved.

"""
        )




def create_file(date_str):
    """
    Create the markdown file for the given date, gather tasks, and append records.

    Args:
        date_str (str): The date string in the format YYYY-MM-DD.
    """
    # Parse the date string
    date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')

    # Create folder structure and get the file path
    file_path = create_folder_structure(date_obj)

    # Initialize the file if it doesn't already exist
    if not initialize_file(file_path, date_str):
        return

    # Define task priorities and root directory
    priority_order = ["Critical", "High", "Everyday", "Pending", "Inattentive", "Medium", "Low"]
    root_dir = "Tasks"

    # Gather tasks by priority
    tasks_by_priority = gather_tasks(root_dir, priority_order)
    # Write tasks to the file
    #write_tasks_to_file(tasks_by_priority, priority_order, file_path, date_str)

    # Append notes and time references
    append_notes_and_time_references(file_path, date_str)

    # Write time records to the file
    write_records_to_file(tasks_by_priority, priority_order, file_path, date_str)

    print(f"任务已导出到 {file_path} 文件中！")


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("请在命令行输入正确的日期格式, 例如: python script.py 2024-08-15")
        sys.exit(1)

    date_str = sys.argv[1]
    
    create_file(date_str)
