import sqlite3
import datetime
import os

def update_tasks():
    db_file = os.path.join("Logs", "errands.db")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # 获取最新20条任务
    cursor.execute("SELECT * FROM errands ORDER BY id DESC LIMIT 20")

    tasks = cursor.fetchall()

    for task in tasks:
        task_id, task_name, category, original_due_date, completed = task
        markdown_file = os.path.join("Tasks", category, task_name, "task.md")
        due_date = datetime.datetime.strptime(original_due_date, "%Y-%m-%d")
        old_due_date = due_date.strftime("%Y-%m-%d")

        print(markdown_file)
        # 检查 Markdown 文件是否存在并读取内容
        if os.path.exists(markdown_file):
            with open(markdown_file, 'r', encoding="utf8") as f:
                content = f.read()

            # 查找 Frequency 部分
            frequency_start = content.find("* **Frequency:**")
            if frequency_start != -1:
                frequency_end = content.find("\n", frequency_start)
                frequency_line = content[frequency_start:]
                frequency = frequency_line.split("[x]")[1].strip()

                # 更新 Due Date 部分
                new_due_date = None
                if frequency.startswith( "Once"):
                    new_due_date = "#completed"
                    completed = 1
                elif frequency.startswith("Weekly"):
                    due_date = due_date + datetime.timedelta(days=7)
                    new_due_date = due_date.strftime("%Y-%m-%d")
                elif frequency.startswith("Monthly"):
                    due_date = due_date.replace(month=datetime.datetime.now().month + 1)
                    new_due_date = due_date.strftime("%Y-%m-%d")
                elif frequency.startswith("Yearly"):
                    due_date = due_date.replace(year=datetime.datetime.now().year + 1)
                    new_due_date = due_date.strftime("%Y-%m-%d")

                if new_due_date:
                    new_content = content.replace(f"## Due Date\n{old_due_date}", f"## Due Date\n{new_due_date}")
                    with open(markdown_file, 'w', encoding="utf8") as f:
                        f.write(new_content)
                    print(f"updated {markdown_file}")
    conn.commit()
    conn.close()

# 示例用法
#db_file = os.path.join("Logs", "errands.db")
#update_tasks(db_file)