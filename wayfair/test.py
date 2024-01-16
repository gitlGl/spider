
from playwright.sync_api import Playwright, sync_playwright
from openpyxl import load_workbook
import time,os,random,csv

current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

local_file = "测试 11.6 11.8 11.13.xlsx"
sheet_name = "测试1"

server_file = f"{sheet_name}.csv"
process_file = f"{sheet_name}.txt"
detail_data_file = f"{sheet_name}-detail.csv"

def random_sleep(min_time, max_time):
    sleep_time = random.uniform(min_time, max_time)
    time.sleep(sleep_time)
    
def readTxt(process_file):# 读取已下载的公司代码
    if not os.path.exists(process_file):
        with open(process_file, "w") as f:
            f.write('')
    with open(process_file, "r") as f:
        data = f.read().splitlines()
        return set(data) 
     
def get_po_num(local_file):
    # 加载 Excel 文件
    workbook = load_workbook(local_file)
    # 选择第一个工作表
    sheet = sheet = workbook[sheet_name]
    return [str(cell.value) for cell in sheet['A']]

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    # 加载本地cookies，免登陆
    context = browser.new_context(storage_state="state.json")
    
    # 打开页面继续操作
    page = context.new_page()
    print("test")
    page.goto('https://partners.wayfair.com/v/finance/payment/payments_summary/display')
    page.wait_for_load_state("networkidle")
    
    process_num = readTxt(process_file)
    list_number = get_po_num(local_file)
    
    for po_number in list_number:
        if po_number  in process_num:
            print(f"查询：{po_number}，跳过")
            continue
        
        page.locator('input[name="poNumber"]').fill(po_number)
        page.locator('button:text("Search")').click()
        page.wait_for_load_state("networkidle")
        div_elements = page.query_selector_all('div.rt-tbody')
        
        if not div_elements:
            with open(server_file,"a+",newline = '') as csv_f:
                    csv.writer(csv_f).writerow([po_number,0])
                     
            with open(detail_data_file,"a+",newline = '') as csv_f:
                csv.writer(csv_f).writerow([po_number,0])
            
            print(f"进度{po_number}")
            continue
            
        # 遍历所有 div 元素并输出文本内容
        for div_element in div_elements:
            for div_element in div_elements:
                divs = div_element.query_selector_all('div.rt-tr-group')
                
            data_list = [] 
            for div in divs:
                 div_datas = div.query_selector_all('div.rt-td')
                 data = [item.text_content() for item in div_datas]
                 data_list.append(data)
                 
            sum_money = sum(float(data[3][1:].replace(",","")) for data in  data_list)
                              
            with open(server_file,"a+",newline = '') as csv_f:
                    csv.writer(csv_f).writerow([po_number,str(sum_money)]) 
                    
            with open(detail_data_file,"a+",newline = '') as csv_f:
                csv.writer(csv_f).writerow([po_number,str(sum_money)])
                for data in data_list:
                    csv.writer(csv_f).writerow(data)
                      
            
        with open(process_file, "a") as f:
            f.write(f"{po_number}\n") # 将内容追加到到文件尾部
        print(f"进度{po_number}")
        
        random_sleep(1,3)
        
    #page.pause()  # 打断点看是不是已经登录了

    context.close()
    browser.close()



with sync_playwright() as playwright:
    run(playwright)