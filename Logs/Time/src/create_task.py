import os
import shutil

# 定义一级目录的特殊处理规则
special_rules_global = {
    "Birthday": {"Frequency": "Yearly", "Content Type": "Errand", "Priority":"Inattentive"},
    "Errands": {"Content Type": "Errand", "Priority":"Inattentive"},
    "Excercise": {"Content Type": "Practice", "Frequency":"Daily", "Priority":"Everyday" },
    "GoodHabits": {"Content Type": "Practice", "Frequency":"Daily", "Priority":"Everyday"}
}


def apply_special_rules(first_level_name, special_rules):
    """
    Apply the special rules based on the first-level directory name.

    Args:
        first_level_name (str): The name of the first-level directory.
        special_rules (dict): Dictionary containing special rules.

    Returns:
        tuple: frequency, content_type, and priority for the first-level directory.
    """
    rules = special_rules.get(first_level_name, {})
    frequency = rules.get("Frequency", "")
    content_type = rules.get("Content Type", "")
    priority = rules.get("Priority", "")
    return frequency, content_type, priority

def update_task_file(task_file, folder_name, frequency, content_type, priority):
    """
    Update the task.md file with the appropriate content based on folder name and special rules.

    Args:
        task_file (str): Path to the task.md file.
        folder_name (str): The name of the current folder.
        frequency (str): Frequency value from special rules.
        content_type (str): Content type value from special rules.
        priority (str): Priority value from special rules.
    """
    with open(task_file, "r+", encoding="utf8") as f:
        content = f.read()
        f.seek(0, 0)

        # Add the title and update the content with special rules
        new_content = f"# Title: {folder_name}\n" + content
        if frequency:
            new_content = new_content.replace(f"-  [ ] {frequency}", f"-  [x] {frequency}")
        if content_type:
            new_content = new_content.replace(f"-  [ ] {content_type}", f"-  [x] {content_type}")
        if priority:
            new_content = new_content.replace(f"-  [ ] **{priority}", f"-  [x] **{priority}")

        f.write(new_content)

def process_directory(root_dir, first_level_dir, template_file, special_rules):
    """
    Process each subdirectory under the first-level directory to update task.md files.

    Args:
        root_dir (str): Path to the root directory for all tasks.
        first_level_dir (str): Path to the first-level directory.
        template_file (str): Path to the template.md file.
        special_rules (dict): Dictionary containing special rules for specific directories.
    """
    first_level_dir_path = os.path.join(root_dir, first_level_dir)

    if not os.path.isdir(first_level_dir_path):
        return

    for dirpath, _, filenames in os.walk(first_level_dir_path):
        if dirpath == first_level_dir_path:
            continue  # Skip the first-level directory itself

        task_file = os.path.join(dirpath, "task.md")
        if "task.md" not in filenames:
            shutil.copy(template_file, task_file)  # Copy template.md if task.md doesn't exist
            print(f"file created {dirpath}")
        else:
            #print(f'file exist {dirpath}')
            continue

        # Get the folder name and first-level directory name
        folder_name = os.path.basename(dirpath)
        first_level_name = os.path.basename(first_level_dir_path)

        # Apply special rules
        frequency, content_type, priority = apply_special_rules(first_level_name, special_rules)

        # Update task.md file
        update_task_file(task_file, folder_name, frequency, content_type, priority)

def main():
    """
    Main function to start the process of updating task.md files in all directories.
    """
    # Define root directory and template file path
    root_dir = os.path.join("Tasks")
    template_file = os.path.join(root_dir, "template.md")

    special_rules = special_rules_global
    # Iterate through each first-level directory in the root directory
    for first_level_dir in os.listdir(root_dir):
        process_directory(root_dir, first_level_dir, template_file, special_rules)

    print("任务已完成！")

if __name__ == "__main__":
    main()
