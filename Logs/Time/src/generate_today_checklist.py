import shutil
import os
import sys
import datetime
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
    folder_path = os.path.join("Logs", str(year), month)

    # Create directories if they don't exist
    os.makedirs(folder_path, exist_ok=True)

    return os.path.join(folder_path, filename)
def initialize_file(file_path, date_str, template_path):
    """
    Initialize the markdown file with the header.

    Args:
        file_path (str): Path to the file to be created.
        date_str (str): The date string to include in the header.
    """
    if os.path.exists(file_path):
        print(f"文件 {file_path} 已存在，跳过创建。")
        return False

    shutil.copy(template_path, file_path)
    return True

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

    template_path = os.path.join('Tasks', 'checklist_template.md')
    # Initialize the file if it doesn't already exist
    if not initialize_file(file_path, date_str, template_path):
        return

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("请在命令行输入正确的日期格式, 例如: python script.py 2024-08-15")
        sys.exit(1)

    date_str = sys.argv[1]
    
    create_file(date_str)