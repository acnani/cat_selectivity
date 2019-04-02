import pymongo
import plotly
from plotly import tools
import plotly.graph_objs as go
import math
from helperFcns import CVPerAmplitude, sessionPerDRG, getCVperAmp, flatten,epineuralSessions, penetratingSessions, allDRG, getCVatThresh
import seaborn as sns; sns.set(style="white", color_codes=True)
from scipy import stats
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

eType = 'epineural'


if eType == 'epineural':
    seshDict = epineuralSessions
elif eType == 'penetrating':
    seshDict = penetratingSessions

for nerve in ['Sciatic', 'Femoral']:
    tmpAllDRG = {'Conduction Velocity': [], 'Stimulation Amplitude': []}
    for drg in allDRG:
        tmp = {'Conduction Velocity': [], 'Stimulation Amplitude': []}
        for iSub in seshDict.keys():
            CVdict = getCVperAmp(iSub, seshDict[iSub], nerve, drg)
            # CVdict = getCVatThresh(iSub, seshDict[iSub], nerve, drg)
            if CVdict:
                for iKey in CVdict.keys():
                    uniqCVs = CVdict[iKey]
                    numCVs = len(uniqCVs)
                    tmp['Stimulation Amplitude'].extend([iKey] * numCVs)
                    tmp['Conduction Velocity'].extend(uniqCVs)
                    tmpAllDRG['Stimulation Amplitude'].extend([iKey] * numCVs)
                    tmpAllDRG['Conduction Velocity'].extend(uniqCVs)

        tmpDF = pd.DataFrame(tmp)
        # if tmpDF.size:
        #     g = sns.jointplot('Stimulation Amplitude', 'Conduction Velocity', data=tmpDF, kind="reg", color="b", height=7, ylim=(0, 140), xlim=(-2, 400),)
        #     g.savefig("%s_%s_CV.png" % (nerve, drg))

    tmpAllDRGDF = pd.DataFrame(tmpAllDRG)
    g = sns.jointplot('Stimulation Amplitude', 'Conduction Velocity', data=tmpAllDRGDF, kind="reg", color="b", height=7, ylim=(0, 140), xlim=(-2, 400))
    g.fig.suptitle('%s nerve' %nerve)
    g.savefig("%s_CV.png" % (nerve))

print 'done'
