'''
測試讀取.hap檔
'''
from data_loader import data_loader
import os

data = data_loader(data_name='train/chr22_train_TWB_100.hap')
print(data)
mypath = os.path.dirname(os.path.abspath(__file__))
print(mypath)
print(os.path.abspath(os.getcwd()))
print(os.listdir(mypath))