from pdfminer.high_level import extract_text
import os ,psutil,sys
#os.chdir(sys.path[0])
import multiprocessing   
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

def pdf2txt(root,files):#转换函数,多进程调用函数
   # print(root)
    #print(file_name_lst)
    for filename in files:
        if  filename.endswith(".PDF")  or filename.endswith(".pdf"):
            print(root+filename+":转换中......")
            text = extract_text(root+filename)
            with open(root+filename[:-4]+".txt", "w", encoding="utf-8") as f:
                f.write(text)
            print(root+filename+":转换成功")
            os.remove(root+filename)#转换成功后删除pdf文件

def main():#使用多进程，提高转换速度
    base_dir = "出口上市公司年报"
    pool = multiprocessing.Pool(processes = psutil.cpu_count()+1)
    for root, dirs, files in os.walk(base_dir):
        pool.apply_async(pdf2txt, (root + "\\",files,))
        
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
  