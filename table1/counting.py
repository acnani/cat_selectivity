import helperFcns as hf
import numpy as np
import pandas as pd

eType = 'epineural'
subjectList = hf.getSubjects(eType)

thresholdRes = {}
for iSub in subjectList:
    print iSub
    thresholdRes[iSub] = hf.getBinarySearchParams(iSub,eType)
DF = pd.DataFrame.from_dict(thresholdRes).transpose()
tmp = pd.read_csv('..\\figure2\\'+eType+'\\selective_counts.csv',index_col=0)

binarySummary = pd.concat([DF,tmp],1)
binarySummary.to_csv(eType+'_binarySearch_summary.csv')

print binarySummary

