import pymongo
import plotly
from plotly import tools
import plotly.graph_objs as go
import math
import helperFcns as hf
import seaborn as sns; sns.set(style="white", color_codes=True)
from scipy import stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

eType = 'epineural'
stimUnits = 'charge'
subjectList = hf.getSubjects(eType)




tmpAllCV_DF = pd.DataFrame({'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[]})
for nerve in ['Femoral', 'Sciatic']:
    tmpAllDRG_DF = pd.DataFrame({'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[]})
    for iSub in subjectList:
        seshPerDRG = hf.sessionPerDRG(iSub, eType)
        for drg in seshPerDRG.keys():
            tmpAllDRG_DF = tmpAllDRG_DF.append(hf.getCVperAmp(iSub, seshPerDRG[drg], nerve, stimUnits),ignore_index=True)

    hf.generateCVPlots(tmpAllDRG_DF,nerve, stimUnits)
    tmpAllCV_DF = tmpAllCV_DF.append(tmpAllDRG_DF)

hf.generateCVPlots(tmpAllCV_DF, 'combined',stimUnits)

print 'done'
