import helperFcns as hf
import seaborn as sns; sns.set(style="white", color_codes=True)
import pandas as pd
from helperFcns import plt

eType = 'epineural'
stimUnits = 'amplitude'
subjectList = hf.getSubjects(eType)
f2, violinAx = plt.subplots(1, 2, figsize=(14, 5))


# all amplitudes
tmpAllCV_DF = pd.DataFrame({'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[],'Threshold':[]})
tmpAllCV_Thresh = pd.DataFrame({'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[],'Threshold':[]})
i = 0
f, violinAx = plt.subplots(1, 3, figsize=(21, 5))

for nerve in ['Femoral', 'Sciatic']:
    tmpAllDRG_DF = pd.DataFrame({'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[],'Threshold':[]})
    tmpThresh_DF = pd.DataFrame({'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[],'Threshold':[]})
    for iSub in subjectList:
        seshPerDRG = hf.sessionPerDRG(iSub, eType)
        for drg in seshPerDRG.keys():
            tmpAllDRG_DF = tmpAllDRG_DF.append(hf.getCVperAmp(iSub, seshPerDRG[drg], nerve, stimUnits),ignore_index=True)
            threshDF = hf.getCVatThresh(iSub, seshPerDRG[drg], nerve, stimUnits)
            if not threshDF.empty:
                tmpThresh_DF = tmpThresh_DF.append(threshDF, ignore_index=True)

    # hf.generateCVPlots(tmpAllDRG_DF,nerve, stimUnits, rootFolder)
    tmp2 = tmpAllDRG_DF.append(tmpThresh_DF, ignore_index=True)
    sns.violinplot(x="Stimulation Amplitude", y="Conduction Velocity", orient='h', hue="Threshold", data=tmp2,
                   palette="muted", order=[120, 80, 60, 48, 40, 34], split=True, ax=violinAx[i])
    violinAx[i].set_title(nerve)
    i += 1

    tmpAllCV_DF = tmpAllCV_DF.append(tmpAllDRG_DF, ignore_index=True)
    tmpAllCV_Thresh = tmpAllCV_Thresh.append(tmpThresh_DF, ignore_index=True)

tmp = tmpAllCV_DF.append(tmpAllCV_Thresh, ignore_index=True)
sns.violinplot(x="Stimulation Amplitude", y="Conduction Velocity", orient='h', hue="Threshold", data=tmp,
               palette="muted", order=[120, 80, 60, 48, 40, 34], split=True, ax=violinAx[2])
violinAx[2].set_title('all trunks')
f.savefig(eType+"_"+stimUnits+"_CV_violinPlot.png")
f.savefig(eType+"_"+stimUnits+"_CV_violinPlot.pdf")
print 'done'
