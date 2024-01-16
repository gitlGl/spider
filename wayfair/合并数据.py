import csv,os
from openpyxl.styles import PatternFill
from openpyxl import load_workbook

current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path))  

local_file = "测试 11.6 11.8 11.13.xlsx"
sheet_name = "测试1"

server_file = f"{sheet_name}.csv"

def get_po_num(local_file):
    # 加载 Excel 文件
    workbook = load_workbook(local_file)
    sheet = sheet = workbook[sheet_name]
    return [float(cell.value) for cell in sheet['D']]

# 获取CSV文件数据
def get_data(server_file):
    with open(server_file, 'r') as file:
        reader = csv.reader(file)
        
        list_data = []
        for row in reader:
           list_data.append(float(row[1]))
        return list_data
 
server_datas = get_data(server_file)
local_datas = get_po_num(local_file)

workbook = load_workbook(local_file)
sheet = sheet = workbook[sheet_name]

for index,(server_data,local_data) in enumerate(zip(server_datas,local_datas)):
    # 指定行列插入数据
    sheet.cell(row=index, column=5, value=server_data)
    
    if server_data < local_data:
        # 创建填充对象并设置颜色
        fill = PatternFill(fill_type='solid', fgColor='00FF00')  # 绿色填充
        #填充行为绿色
        sheet.row_dimensions[index].fill = fill
        # # 将填充应用于指定的单元格
        # sheet.cell(row=index, column=3).fill = fill
 
workbook.save(local_file)
        




