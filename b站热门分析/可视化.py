import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

def 散点图(df):
    # 将时间列转换为时间戳类型
    df['时间'] = pd.to_datetime(df['时间'],format="%Y-%m-%d")

    # 按照时间列对 DataFrame 进行排序
    sorted_df = df.sort_values(by='时间')
    sorted_df['时间'] = sorted_df['时间'].dt.strftime('%Y-%m-%d')
    # 提取前十行需要绘制的数据
    x = sorted_df['时间'].head(100)
    y = sorted_df['播放量'].head(100)
    
    # 绘制散点图
    plt.figure(figsize=(10, 10))
    plt.scatter(x, y)
    plt.xlabel('时间')
    plt.ylabel('播放量')
    plt.title('按时间排序前100个数据')
  

def 饼图(df):
    # 对'视频分类'列进行分组
    grouped = df.groupby('视频分类').size()

    # 计算每个组的占比
    grouped_percent = grouped / grouped.sum()

    # 将占比低于1%的归类为"其他"
    grouped_percent['其他(占比低于百分之一)'] = grouped_percent[grouped_percent < 0.01].sum()
    grouped_percent = grouped_percent[grouped_percent >= 0.01]

    # 绘制饼状图
    plt.figure(figsize=(10, 10))  # 设置图形大小
    plt.pie(grouped_percent, labels=grouped_percent.index, autopct='%1.1f%%')
    plt.title('视频分类',color = "blue",fontweight = 'bold')
    plt.axis('equal')  # 使饼状图为正圆形

      
def 柱形图(df):
    # 按照需要排序的列进行排序
    df_sorted = df.sort_values(by='播放量',ascending=False)

    # 提取需要绘制柱形图的两列数据
    column1_data = df_sorted['播放量'].head(30)
    column2_data = df_sorted['up主'].head(30)

    # 绘制柱形图
    plt.figure(figsize=(10, 10))  # 设置图形大小
    plt.bar(column2_data,column1_data)
    # 添加 x 轴标签和标题
    plt.xticks( rotation=90)
    plt.xlabel('UP主')
    plt.title('top30播放量')

def 折线图(df):
    # 按照指定列进行分组并求和
    summed = df.groupby('视频分类')['收藏'].sum()

    # 按照降序排序
    summed_sorted = summed.sort_values(ascending=False).head(30)

    # 绘制折线图
    plt.figure(figsize=(10, 10))  # 设置图形大小
    plt.xticks( rotation=90)
    plt.plot(summed_sorted.index, summed_sorted.values)

    # 添加 x 轴标签、y 轴标签和标题
    plt.xlabel('视频分类')
    plt.ylabel('收藏数量')
    plt.title('top30分类收藏')

        
def 回归(df):
    # 提取需要分析的列数据
    x = df[ '收藏'].values.reshape(-1, 1)  # 提取多个列数据
    y = df['播放量'].values

    # 创建线性回归模型
    model = LinearRegression()

    # 拟合模型
    model.fit(x, y)

    # 进行预测
    y_pred = model.predict(x)
    y_pred = np.round(y_pred).astype(int)
    # 计算残差
    #residuals = y - y_pred

    # 计算均方误差（MSE）
    #mse = mean_squared_error(y, y_pred)

    # 创建包含两个子图的图形

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 10))
    yfit =[ model.intercept_ + model.coef_ *i for i in x] 
    # 绘制线性回归分析图
    ax1.scatter(x, y, color='blue', label='真实值')
    ax1.plot(x, yfit, color='red', linewidth=2, label='线性回归线')
    ax1.set_xlabel('收藏')
    ax1.set_ylabel('播放量')
    ax1.set_title('线性回归分析')
    ax1.legend()

    # 绘制柱形图
    ax2.bar([i for i in range(1, 120, 4)], y[:30], color='blue', label='真实值')
    ax2.bar([i for i in range(2, 120, 4)], y_pred[:30], color='red',  label='预测值')
    ax2.set_xlabel('Index')
    ax2.set_ylabel('播放量')
    ax2.set_title('30个真实值与预测值比较')
    ax2.legend()

    


if __name__ == '__main__':
    df = pd.read_csv('data.csv')
    散点图(df)
    折线图(df)
    饼图(df)
    柱形图(df)
    回归(df)
    plt.show()
   



