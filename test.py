# from playwright.sync_api import Playwright, sync_playwright, expect
# import time,os

# current_file_path = os.path.abspath(__file__)
# os.chdir(os.path.dirname(current_file_path))  

# def run(playwright: Playwright) -> None:
#     browser = playwright.firefox.launch(headless=False)
#     context = browser.new_context()
#     page = context.new_page()
#     page.goto('http://epub.cnipa.gov.cn/')
#     page.wait_for_load_state("networkidle")

  
#     time.sleep(30)
#     locator = page.locator('#searchStr').fill("test")
#     time.sleep(30)
#     #storage = context.storage_state(path="state.json")#保存cookies到文件备用

#     # ---------------------
#     context.close()
#     browser.close()


# with sync_playwright() as playwright:
#     run(playwright)
    
#冒泡排序
def bubble_sort(arr):
    n = len(arr)
    # 遍历所有数组元素
    for i in range(n):
        # 最后i个元素已经排好序，无需再比较
        for j in range(0, n-i-1):
            # 交换如果元素是逆序的
            if arr[j] > arr[j+1] :
                arr[j], arr[j+1] = arr[j+1], arr[j]
                
# 测试冒泡排序
arr = [64, 34, 25, 12, 22, 11, 90]
bubble_sort(arr)
print("排序后的数组：")
for i in range(len(arr)):
    print("%d" %arr[i])
                
                

# 快速排序
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    else:
        pivot = arr[0]
        less = [x for x in arr[1:] if x <= pivot]
        greater = [x for x in arr[1:] if x > pivot]
        return quick_sort(less) + [pivot] + quick_sort(greater)
    
# 测试快速排序
arr = [64, 34, 25, 12, 22, 11, 90]
sorted_arr = quick_sort(arr)
print("排序后的数组：")
for i in range(len(sorted_arr)):
    print("%d" %sorted_arr[i])
    
#解释快排





   
