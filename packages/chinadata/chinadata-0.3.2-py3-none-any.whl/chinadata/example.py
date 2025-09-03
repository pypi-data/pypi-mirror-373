#
"""
1、安装对应库
pip install chinadata

"""
#2、
import  chinadata.ca_data as ts


ts.set_token('5821074c7482c04e8d39da5c8313')
pro=ts.pro_api('d55821074c7482c04e8d39da5c8313')

# #查询当前所有正常上市交易的股票列表
data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
print(data)
#
#
df = ts.pro_bar(ts_code='000007.SZ', start_date='20240817', end_date='20241215')
print(df)

df = pro.daily(ts_code='000001.SZ', start_date='20000701', end_date='20180718')
print(df)


