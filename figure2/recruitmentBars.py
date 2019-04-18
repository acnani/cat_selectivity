import helperFcns as hf
from helperFcns import plt
import seaborn as sns
import pandas as pd

eType = 'penetrating'
collapseCuffs = True
ignoreCuffs = ['BiFem']

cuffChildrenDict = hf.getInnervationChildren()
cuffParentsDict = hf.getInnervationParents()
colorList = hf.colorOrder

subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()
coactivationDF = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

selectiveDF = pd.DataFrame(columns=['DRG', 'nerve'])
nonSelectiveDF = pd.DataFrame(columns=['DRG', 'nerve'])

for iDRG in hf.allDRG:
    coactivationDF_perDRG = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

    for subject in subjectList:
        # returns all sessions per DRG per subject
        seshPerDRG = hf.sessionPerDRG(subject, eType)  # add argument for penetrating vs epineural

        if iDRG in seshPerDRG.keys():

            # iterate over each session
            for iSesh in seshPerDRG[iDRG]:
                threshDict = hf.thresholdPerCuff(subject, iSesh, ignoreCuffs, collapseCuffs)
                allActiveChans = sorted(threshDict.keys())

                for iStimChan in allActiveChans:
                    stimChanDict = threshDict[iStimChan]
                    allRecruitedCuffs = stimChanDict.keys()
                    for iActiveCuff in allRecruitedCuffs:
                        activeChanIdx = targetNerveLabels.index(iActiveCuff)         # row
                        activeChanAmp = stimChanDict[iActiveCuff]

                        coactivatedCuffIdx = [targetNerveLabels.index(val) for val in allRecruitedCuffs if stimChanDict[val] <= activeChanAmp]   # allow counting iActiveCuff so that diagonal is unity

                        for coactiveCuff in allRecruitedCuffs:
                            if stimChanDict[coactiveCuff] <= activeChanAmp:
                                coactivationDF_perDRG.loc[iActiveCuff, coactiveCuff] += 1

                        coactivatedCuffs = [val for val in allRecruitedCuffs if stimChanDict[val] <= activeChanAmp and val !=iActiveCuff]

                        # check if parent nerve of active nerve is coactivated
                        cuffParent = [cuffParentsDict[iActiveCuff]]                 # list of all parents of the active cuff up to the trunk
                        if cuffParent[0] != '':
                            cuffParent.append(cuffParentsDict[cuffParent[0]])
                        notParentCoactive = [value for value in coactivatedCuffs if value not in cuffParent]        # non-parent nerves that are coactivated with the active cuff

                        # check if active nerve has a child and whether it is coactivated
                        if iActiveCuff in cuffChildrenDict.keys():
                            cuffChild = cuffChildrenDict[iActiveCuff]
                            notChild = [value for value in notParentCoactive if value not in cuffChild]
                            notParentCoactive = notChild

                        if len(notParentCoactive)==0:
                            selectiveDF = selectiveDF.append({'DRG':iDRG,'nerve':hf.allCuffs_mdf[iActiveCuff]},ignore_index=True)
                        else:
                            nonSelectiveDF = nonSelectiveDF.append({'DRG':iDRG,'nerve':hf.allCuffs_mdf[iActiveCuff]},ignore_index=True)

    coactivationDF += coactivationDF_perDRG
    tmp = coactivationDF_perDRG.loc[:, (coactivationDF_perDRG != 0).any(axis=0)]
    tmp2 = tmp.loc[(tmp != 0).any(axis=1), :]
    tmp2.index = [hf.allCuffs_mdf[i] for i in tmp2.columns]
    tmp2.columns = tmp2.index
    sns.heatmap(tmp2/tmp2.max(), annot=False, fmt=".1f", linewidths=.5,cmap="Blues_r")
    plt.savefig(eType + '/' + iDRG + '_coactivation.pdf')
    plt.savefig(eType + '/' + iDRG + '_coactivation.png')
    plt.close()

tmp3 = coactivationDF.loc[:, (coactivationDF != 0).any(axis=0)]
tmp4 = tmp3.loc[(tmp3 != 0).any(axis=1), :]
tmp4.index = [hf.allCuffs_mdf[i] for i in tmp4.columns]
tmp4.columns = tmp4.index
sns.heatmap(tmp4/tmp4.max(), annot=False, fmt=".1f",)
plt.savefig(eType + '/' + 'allDRG_coactivation.pdf')
plt.savefig(eType + '/' + 'allDRG_coactivation.png')
plt.close()

f,ax3 = plt.subplots(2, 1, figsize=(9, 8))
sns.countplot(x='nerve',hue='DRG',order=tmp4.index,data=selectiveDF, ax=ax3[0])
sns.countplot(x='nerve',order=tmp4.index,data=selectiveDF, ax=ax3[1])
plt.savefig(eType + '/' + 'selectiveCounts.pdf')
plt.savefig(eType + '/' + 'selectiveCounts.png')
plt.close()

f,axes = plt.subplots(2, 1, figsize=(9, 8))
sns.countplot(x='nerve',hue='DRG',order=tmp4.index,data=nonSelectiveDF, ax=axes[0])
sns.countplot(x='nerve',order=tmp4.index,data=nonSelectiveDF, ax=axes[1])
plt.savefig(eType + '/' + 'nonselectiveCounts.pdf')
plt.savefig(eType + '/' + 'nonselectiveCounts.png')
plt.close()


# import plotly
# import plotly.graph_objs as go
# import numpy as np
# from plotly import tools
# data = [go.Heatmap(z=tmp2, y=tmp2.index,x=tmp2.index,colorscale=hf.parula)]
# plotly.offline.plot({'data':data, 'layout':go.Layout(title=eType+' coactivation matrix')},filename=eType+'_test.html',auto_open=True)
