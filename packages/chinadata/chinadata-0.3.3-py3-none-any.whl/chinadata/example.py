#
"""
1、安装对应库
pip install chinadata

"""


#2、
import  chinadata.ca_data as ts


ts.set_token('3a9e334456c8405c00d013914953')
pro=ts.pro_api('a9e334456c8405c00d013914953')



# 你要测量的代码块

# #查询当前所有正常上市交易的股票列表
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
print(data)

#
df = ts.pro_bar(ts_code='000007.SZ', start_date='20240817', end_date='20241215')
print(df)


df = pro.daily(ts_code='000001.SZ', start_date='20000701', end_date='20180718')
print(df)



