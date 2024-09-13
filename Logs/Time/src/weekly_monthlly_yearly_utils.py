import os
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'SimHei'  # 或其他支持汉字的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def time_distribution_graph(df, file_folder_path, file_name_prefix):
    # 将 start_time 和 end_time 转换为 pandas 的 datetime 对象
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])

    # 提取日期和时间，用于后续绘图
    df['start_hour'] = df['start_time'].dt.time
    df['end_hour'] = df['end_time'].dt.time
    df['date'] = pd.to_datetime(df['date']).dt.date

    # 创建颜色映射
    colors = {'Technical': '#ffadad', 'Work': '#ffd6a5', 'GoodHabits': '#fdffb6',
            'Excercise': '#caffbf', 'Parenting': '#9bf6ff', 'SoftSkills': '#a0c4ff', 'Art': '#bdb2ff'}

    # 创建画布和子图
    fig, ax = plt.subplots(figsize=(10, 6))

    # 对每一天绘制活动
    for index, row in df.iterrows():
        # 获取活动的起止时间
        start = pd.Timestamp.combine(pd.Timestamp(row['date']), row['start_hour'])
        end = pd.Timestamp.combine(pd.Timestamp(row['date']), row['end_hour'])
        
        # 绘制活动条
        ax.barh(row['date'], (end - start).seconds / 3600, left=start.hour + start.minute / 60,
                color=colors.get(row['category'], '#ffffff'), edgecolor='black')

    # 设置时间格式化和标签
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=60))  # 每小时一个刻度
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))  # 24小时制
    plt.xticks(rotation=45)

    # 设置标题和轴标签
    ax.set_xlabel('Time (24-hour format)')
    ax.set_ylabel('Date')
    plt.title('Daily Activities Timeline')
    ax.set_facecolor('#000300')

    # 显示图表
    plt.tight_layout()
    #plt.show()
    file_name = file_name_prefix + "_time_dist.png"
    img_path = os.path.join(file_folder_path, file_name)
    plt.savefig(img_path, bbox_inches='tight', dpi=300)

def create_time_pie_chart(df, file_folder_path, file_name_prefix):
    string = ""
    # 计算每个记录的时长（单位：秒）
    df['duration'] = (pd.to_datetime(df['end_time']) - pd.to_datetime(df['start_time'])).dt.total_seconds()

    # 计算总时长
    total_duration = df['duration'].sum()
    string += f"共花费的时间：{total_duration/3600}小时"
    string += f"平均每日花费时间：{total_duration/3600/7}小时"

    # 按类别分组并计算时长
    category_durations = df.groupby('category')['duration'].sum()
    string += f"\n每个类别的时长:\nBy {category_durations/3600}"

    colors_category = {'Technical': '#ffadad', 'Work': '#ffd6a5', 'GoodHabits': '#fdffb6', 'Excercise': '#caffbf', 'Parenting': '#9bf6ff', 'SoftSkills': '#a0c4ff', 'Art': '#bdb2ff'}
    # 绘制类别饼图
    plt.figure(figsize=(8, 6))
    plt.pie(category_durations, labels=category_durations.index, autopct='%1.1f%%', colors=[colors_category[category] for category in category_durations.index])
    print("category_durations.index:", category_durations.index)
    print("colors_category.keys():", colors_category.keys())


    #plt.pie(category_durations, labels=category_durations.index, autopct='%1.1f%%')
    # 添加右上角的标签
    #plt.legend(loc='upper right', labels=colors_category.keys())
    plt.title("不同类别所占用的时间比例")
    #plt.show()
    file_name = file_name_prefix + "_piechart_category.png"
    img_path = os.path.join(file_folder_path, file_name)
    plt.savefig(img_path, bbox_inches='tight', dpi=300)

    # 按活动类型分组并计算时长
    time_type_durations = df.groupby('time_type')['duration'].sum()
    string += f"\n每个活动类型的时长:\nBy {time_type_durations/3600}"

    # 创建活动类型的颜色字典
    time_type_colors = {'Concentrating': '#e66101', 'Enjoying': '#fdb462', 'Presenting': '#b2df8a',
                       'Discussing': '#33a02c', 'Meeting': '#1f78b4', 'Bystanding': '#6a3d9a'}
    # 绘制活动类型饼图
   
    plt.figure(figsize=(8, 6))
    plt.pie(time_type_durations, labels=time_type_durations.index, autopct='%1.1f%%', colors=[time_type_colors[category] for category in time_type_durations.index])
    print("time_type_durations.index:", time_type_durations.index)
    plt.title("不同活动类型所占用时间比例")
   
   
    file_name = file_name_prefix + "_piechart_timetype.png"
    img_path = os.path.join(file_folder_path, file_name)
    plt.savefig(img_path, bbox_inches='tight', dpi=300)

    print(string)
    return string
