# 导入依赖
import os,psutil,xlrd,sys
import pandas as pd
import multiprocessing
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))
#import jieba
# 获取关键词列表
#os.chdir(sys.path[0])
def getKeyWordList():
    key_word = []
    with xlrd.open_workbook(keyword_dir) as book:
            sheets = book.sheets()
            for sheet in sheets:
                rows = sheet.nrows
                for i in range(rows):
                    list1 = sheet.row_values(rowx=i)
                    key_word.append((list1[0]))
    return key_word
def getKeyWordData(text_path,filer_name,key_word):
    # 读取文本
    key_word_data = {}
    path_filename = text_path + filer_name
    with  open(path_filename, "r", encoding='utf-8') as f:
        txt = f.read()
        # 使用精确模式对文本进行分词
        #words = jieba.lcut(txt)
        # 通过键值对的形式存储词语及其出现的次数
        year = filer_name[:-8]
        year  = year[-4:]#获取年份
        filer_name = filer_name[:-13]#获取公司代码
        key_word_data['公司代码'] = filer_name+'年报'
        key_word_data['年份'] = year
        for wd in key_word:
            key_word_data[wd] =txt.count(wd)#统计关键词出现次数
            
    return key_word_data   
def statistics(root,files,key_word):
   
    datas = []
    for filename in files:
        if filename.endswith(".txt"):
            key_word_data = getKeyWordData( root,filename,key_word)
            #os.remove("年度报告/"+folder_name+"/"+filename)
            print(filename+"分析完成")
            datas.append(key_word_data)
        else:
            print(filename+"不是txt文件")
   #把数据数据写入csv文件
    # if len(datas) == 0:
    #     return
    df = pd.DataFrame(datas)     
    if not os.path.exists(cipin_dir) :
        print("test")
        df.to_csv(cipin_dir, mode='a', index=False,header=True,encoding="gbk")
    else:
        df.to_csv(cipin_dir, mode='a', index=False, header=False,encoding="gbk")
    # for filename in files:
    #     if filename.endswith(".txt"):   
    #         os.remove(root +filename)
       
# 主函数
def main():
    key_word = getKeyWordList()
   
    pool = multiprocessing.Pool(processes = psutil.cpu_count()+1)#使用多进程，提高统计速度
    for root, dirs, files in os.walk(base_dir):
        pool.apply_async(statistics, (root + '\\',files,key_word))#

    pool.close()
    pool.join()
    

base_dir = "出口上市公司年报"
keyword_dir =  "关键词.xls"
cipin_dir =  "词频统计.csv"


if __name__ == '__main__':
    main()
   


