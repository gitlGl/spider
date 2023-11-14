from pdfminer.high_level import extract_text
import os ,psutil,sys
os.chdir(sys.path[0])
import multiprocessing          
def pdf2txt(file_name_lst):#转换函数,多进程调用函数
    for filename in file_name_lst:
        if  filename.endswith(".PDF")  or filename.endswith(".pdf"):
            print(folder_name+filename+":转换中......")
            text = extract_text(folder_name+filename)
            with open(folder_name+filename[:-4]+".txt", "w", encoding="utf-8") as f:
                f.write(text)
            print(folder_name+filename+":转换成功")
            os.remove(folder_name+filename)#转换成功后删除pdf文件

def main():#使用多进程，提高转换速度
    base_dir = "出口上市公司年报/"
    pool = multiprocessing.Pool(processes = psutil.cpu_count()+1)
    for _,folder_name_lst,file_name_lst in os.walk(base_dir):
        pool.apply_async(pdf2txt, (file_name_lst,))
        
    pool.close()
    pool.join()

if __name__ == '__main__':
    #main()
    test = os.walk(r"C:\Users\Administrator\Desktop\金融")
    print(next(test))
    print(next(test))
    