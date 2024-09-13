---
Created: n/a
Completed: n/a
type: Supporting
revisit_frequency: None
last_revisit_date: n/a
next_revisit_date: n/a
---
import os
import shutil

# 定义根目录和模板文件的路径
root_dir = os.path.join("Tasks")
template_file = os.path.join(root_dir, "template.md")
# print (os.getcwd())
# 遍历根目录下的第一级目录
for first_level_dir in os.listdir(root_dir):
    first_level_dir_path = os.path.join(root_dir, first_level_dir)
    
    # 检查是否是文件夹
    if os.path.isdir(first_level_dir_path):
        # 遍历第二级及以下的目录
        for dirpath, dirnames, filenames in os.walk(first_level_dir_path):
            # 排除第一级目录
            if dirpath == first_level_dir_path:
                continue
            
            # 检查当前文件夹是否已有 task.md
            task_file = os.path.join(dirpath, "task.md")
            if "task.md" in filenames:
                os.remove(task_file)

print("任务已完成！")