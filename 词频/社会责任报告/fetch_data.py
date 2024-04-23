import shang_jiao_suo,shen_jiao_suo,threading
if __name__ == '__main__':
    thread1 = threading.Thread(target=shang_jiao_suo.shang_jiao_suo)
    thread2 = threading.Thread(target=shen_jiao_suo.shen_jiao_suo)

    #启动线程
    thread1.start()
    thread2.start()

    # 主线程等待所有子线程执行完毕
    thread2.join()
    thread1.join()#


    print("All threads finished")