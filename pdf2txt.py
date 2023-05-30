from pdfminer.high_level import extract_text
import os ,psutil
import multiprocessing          
def pdf2txt(folder_name):#转换函数,多进程调用函数
    list_filename = os.listdir(folder_name)
    for filename in list_filename:
            if  filename.endswith(".PDF")  or filename.endswith(".pdf"):
                print(folder_name+filename+":转换中......")
                text = extract_text(folder_name+filename)
                with open(folder_name+filename[:-4]+".txt", "w", encoding="utf-8") as f:
                    f.write(text)
                print(folder_name+filename+":转换成功")
                os.remove(folder_name+filename)#转换成功后删除pdf文件

def main():#使用多进程，提高转换速度
    base_dir = "出口上市公司年报/"
    list_folder_name = next(os.walk(base_dir))[1]
    pool = multiprocessing.Pool(processes = psutil.cpu_count()+1)
    for folder_name in list_folder_name:
        pool.apply_async(pdf2txt, (base_dir+folder_name+'/',))
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()
   
    