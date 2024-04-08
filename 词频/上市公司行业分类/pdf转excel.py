import pandas as pd
import tabula

# 读取整个PDF文件并将所有页面的表格转换为DataFrame列表
tables = tabula.read_pdf('0208_01.pdf', pages='all', pandas_options={'header': None}, multiple_tables=True, lattice=True)

# 去掉每页表格的第一行
for table in tables:
    if not table.empty:
        table.drop(0, inplace=True)

# 合并所有表格到一个 DataFrame 中
combined_df = pd.concat(tables, ignore_index=True)

# 将合并后的 DataFrame 写入 Excel 文件的同一个工作表
combined_df.to_excel('output.xlsx', index=False, header=False)
