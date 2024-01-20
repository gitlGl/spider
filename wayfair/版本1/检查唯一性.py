import openpyxl,os
from collections import Counter
current_file_path = os.path.abspath(__file__)
os.chdir(os.path.dirname(current_file_path)) 
workbook = openpyxl.load_workbook("测试.xlsx")

# 获取所有 sheet 的名字列表
sheet_names = workbook.sheetnames
print(sheet_names)

# 遍历所有 sheet
list_data = []
for sheet_name in sheet_names:
    sheet =  workbook[sheet_name]
    t =  [str(cell.value) for cell in sheet['A'] if cell.value ]
    list_data.extend(t)
    print(len(t))
   
for i in list_data:
    if i is not None:
        if len(i[2:]) != 9:
            print(i)#
set_data = set([i[2:] for i in list_data])
#print(set_data)
print(len(list_data),len(set_data))
c = dict(Counter(list_data))
#print(c)
for index,vulue in c.items():
    if vulue  >= 2:
        print("cfnsja",index,vulue)


  