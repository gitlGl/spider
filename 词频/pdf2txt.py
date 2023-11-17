from pdfminer.high_level import extract_text
import os ,psutil,sys
#os.chdir(sys.path[0])
import multiprocessing   
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

def pdf2txt(root,file):#转换函数,多进程调用函数
 
    if  file.endswith(".PDF")  or file.endswith(".pdf"):
        print(root+file+":转换中......")
        text = extract_text(root+file)
        with open(root+file[:-4]+".txt", "w", encoding="utf-8") as f:
            f.write(text)
        print(root+file+":转换成功")
        os.remove(root+file)#转换成功后删除pdf文件

def main():#使用多进程，提高转换速度
    base_dir = "出口上市公司年报"
    file_dir_lst = []
    
    for root, dirs, files in os.walk(base_dir):
        file_dir_lst.extend([(root + "\\",file) for file in files])

    pool = multiprocessing.Pool(processes = psutil.cpu_count()+1)
    for root,file in file_dir_lst:
        pool.apply_async(pdf2txt, (root + "\\",file,))
        
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
  