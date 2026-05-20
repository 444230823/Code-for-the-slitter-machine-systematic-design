import csv
import os
import pandas as pd

pathWai = os.getcwd() + '\\delete.csv'
pathNei = os.getcwd() + '\\tempData.csv'
with open(pathWai, 'a+', newline='') as f:
    csv.writer(f).writerow([1,2,3,4,5])
    tempData = pd.read_csv(pathNei)
    print(str(int(tempData['lastNum'][0])).zfill(4))
    renew = pd.DataFrame([{'lastNum':'0000', 'lengthDelta':0}])
    renew.to_csv(pathNei,mode='w',index=False,header=True)
