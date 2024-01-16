import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import os
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path)) 
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
# 读取数据整理到一个DataFrame中
df_1115 = pd.read_excel("成绩素材 -1115 测验.xlsx")
df_1122 = pd.read_excel("成绩素材 -1122 测验.xlsx")
df_1213 = pd.read_excel("成绩素材 -1213 测验.xlsx")

df_combined = pd.concat([df_1115, df_1122, df_1213])

# 1. 完成班级相对成绩计算；小组相对成绩计算
df_combined['班级相对成绩'] = (df_combined['综合成绩'] / df_combined.groupby('班级')['综合成绩'].transform('mean')) * 100
df_combined['小组相对成绩'] = (df_combined['综合成绩'] / df_combined.groupby('组号')['综合成绩'].transform('mean')) * 100

# 2. 统计小组相对成绩的专业、班级、文理分布情况
group_major_distribution = df_combined.groupby('组号')['专业'].value_counts()
group_class_distribution = df_combined.groupby('组号')['班级'].value_counts()
group_science_art_distribution = df_combined.groupby('组号')['文理'].value_counts()

# 3. 图形展示班级小组相对成绩情况
st.title('成绩分析程序')
# 全体学生的综合成绩统计
overall_stats = df_combined['综合成绩'].describe()

# 4. 综合成绩按照文理、专业、班级分别统计平均、中位数、最高、方差值
# 按文理科分组的综合成绩统计
science_stats = df_combined[df_combined['文理'] == '理科'].groupby('专业')['综合成绩'].describe()
science_stats.columns = [f'理科专业_{col}' for col in science_stats.columns]

art_stats = df_combined[df_combined['文理'] == '文科'].groupby('专业')['综合成绩'].describe()
art_stats.columns = [f'文科专业_{col}' for col in art_stats.columns]

# 按专业分组的综合成绩统计
major_stats = df_combined.groupby('专业')['综合成绩'].describe()
major_stats.columns = [f'专业_{col}' for col in major_stats.columns]

# 按班级分组的综合成绩统计
class_stats = df_combined.groupby('班级')['综合成绩'].describe()
class_stats.columns = [f'班级_{col}' for col in class_stats.columns]

# 修改为不同的列名
major_stats.columns = [f'专业统计_{col}' for col in major_stats.columns]
class_stats.columns = [f'班级统计_{col}' for col in class_stats.columns]

# 合并统计结果
stats_comparison = pd.concat([overall_stats, science_stats, art_stats, major_stats, class_stats], axis=1)

# 5. 最早最晚综合成绩和相对成绩变化值、变化率的分布情况
df_combined['平均成绩']=df_combined[['考试']].mean(axis=1)
#计算每个同学的最早、最晚综合成绩变化分值、变化率两列数据，并统计该变化的分布情况
df_combined['最早成绩']=df_combined[['考试']].min(axis=1)
df_combined['最晚成绩']=df_combined[['考试']].max(axis=1)
df_combined['成绩变化分值']=df_combined['最晚成绩']-df_combined['最早成绩']
df_combined['成绩变化率']=(df_combined['最晚成绩']-df_combined['最早成绩'])/df_combined['最早成绩']

# 统计成绩变化率分布情况
score_change_distribution=df_combined['成绩变化率'].describe()

# 计算每个同学的最早、最晚班级相对成绩的变化分值、变化率，并统计变化率的分布情况
class_max = df_combined.groupby('班级')['考试'].transform('max')
df_combined['班级最高成绩'] = class_max
df_combined['班级相对成绩'] = df_combined['考试'] / df_combined['班级最高成绩'] * 100
df_combined['最早班级相对成绩'] = df_combined.groupby('学号')['班级相对成绩'].transform('min')
df_combined['最晚班级相对成绩'] = df_combined.groupby('学号')['班级相对成绩'].transform('max')
df_combined['班级相对成绩变化分值'] = df_combined['最晚班级相对成绩'] - df_combined['最早班级相对成绩']
df_combined['班级相对成绩变化率'] = (df_combined['最晚班级相对成绩'] - df_combined['最早班级相对成绩']) / df_combined['最早班级相对成绩']

# 统计班级相对成绩变化率分布情况
class_score_change_distribution = df_combined['班级相对成绩变化率'].describe()

menu = st.sidebar.selectbox('选择功能', ['班级相对成绩计算', '小组相对成绩计算', '统计分布情况', '图形展示', '统计统计值', '分数段统计','综合成绩展示','最早最晚成绩展示'])

if menu == '班级相对成绩计算':
    st.write(df_combined[['学号', '学生姓名', '班级', '综合成绩', '班级相对成绩']])

elif menu == '小组相对成绩计算':
    st.write(df_combined[['学号', '学生姓名', '组号', '综合成绩', '小组相对成绩']])

elif menu == '统计分布情况':
    st.write('小组相对成绩的专业分布:')
    st.write(group_major_distribution)
    st.write('小组相对成绩的班级分布:')
    st.write(group_class_distribution)
    st.write('小组相对成绩的文理分布:')
    st.write(group_science_art_distribution)

elif menu == '图形展示':
    st.write('班级相对成绩箱线图:')
    fig, ax = plt.subplots(figsize=(10, 10))
    #ax.set_ylabel () #设置y轴标签字体大小
    df_combined.boxplot(column='班级相对成绩', by='班级', vert=False, ax=ax,fontsize=15)
    st.pyplot(fig)

    st.write('小组相对成绩箱线图:')
    fig, ax = plt.subplots(figsize=(10, 10))
   
    df_combined.boxplot(column='小组相对成绩', by='组号', vert=False, ax=ax)
    st.pyplot(fig)

elif menu == '统计统计值':
    st.write('综合成绩的统计值:')
    st.write(df_combined['综合成绩'].describe())

elif menu == '分数段统计':
    bins = [0, 60, 70, 80, 90, 101]
    labels = ['0-60', '60-70', '70-80', '80-90', '90-100']
    df_combined['分数段'] = pd.cut(df_combined['综合成绩'], bins=bins, labels=labels, right=False)
    st.write('按专业统计分数段分布:')
    st.write(df_combined.groupby('专业')['分数段'].value_counts())
    st.write('按班级统计分数段分布:')
    st.write(df_combined.groupby('班级')['分数段'].value_counts())

elif menu == '综合成绩展示':
    st.write('综合成绩的统计值对比:')
    st.write(stats_comparison)
    # 使用柱状图对比展示综合成绩结果
    fig, ax = plt.subplots(figsize=(10, 10))
    stats_comparison.T[['mean', '50%', 'max', 'std']].plot(kind='bar', ax=ax)
    plt.title('综合成绩统计对比')
    plt.xlabel('分组')
    plt.ylabel('数值')
    plt.legend(title='统计值', loc='upper right')
    st.pyplot(fig)

elif menu == '最早最晚成绩展示':
    st.write("班级相对成绩变化率描述统计信息:")
    st.write(class_score_change_distribution)
    # 绘制变化分布的曲线
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.hist(df_combined['班级相对成绩变化率'], bins=20, color='green', edgecolor='black')
    ax.set_title('班级相对成绩变化率分布')
    ax.set_xlabel('变化率 (%)')
    ax.set_ylabel('频数')

    fig.tight_layout()
    st.pyplot(fig)
    

#streamlit run streamlit/main.py 