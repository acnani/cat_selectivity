import helperFcns as hf
from helperFcns import plt
import seaborn as sns
import pandas as pd

eType = 'epineural'
collapseCuffs = True
ignoreCuffs = ['BiFem']

cuffChildrenDict = hf.getInnervationChildren()
cuffParentsDict = hf.getInnervationParents()
colorList = hf.colorOrder

subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()
coactivationDF = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

selectiveDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject'])
nonSelectiveDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject'])
numChan = {}
for iDRG in hf.allDRG:
    coactivationDF_perDRG = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

    for subject in subjectList:
        numChan.setdefault(subject,{'selectiveElec':0, 'activeElec':0, })
        # returns all sessions per DRG per subject
        seshPerDRG = hf.sessionPerDRG(subject, eType)  # add argument for penetrating vs epineural

        if iDRG in seshPerDRG.keys():

            # iterate over each session
            for iSesh in seshPerDRG[iDRG]:
                threshDict = hf.thresholdPerCuff(subject, iSesh, ignoreCuffs, collapseCuffs)
                allStimChans = sorted(threshDict.keys())

                for iStimChan in allStimChans:
                    numChan[subject]['activeElec'] += 1
                    cuffThresholds = threshDict[iStimChan]
                    allRecruitedCuffs = cuffThresholds.keys()

                    for iTargetCuff in allRecruitedCuffs:
                        targetCuffThreshold = cuffThresholds[iTargetCuff]

                        # populate DF for coactivation matrix
                        coactivatedCuffs = []
                        for iRecruitedCuff in allRecruitedCuffs:
                            if cuffThresholds[iRecruitedCuff] <= targetCuffThreshold:
                                coactivationDF_perDRG.loc[iTargetCuff, iRecruitedCuff] += 1
                                if iRecruitedCuff != iTargetCuff:
                                    coactivatedCuffs.append(iRecruitedCuff)

                    # progressively decimate coactivated Cuffs

                        # remove all ancestors of the current nerve
                        cuffParents = []
                        res = cuffParentsDict[iTargetCuff]
                        while res != '':
                            cuffParents.append(res)
                            if res in coactivatedCuffs: coactivatedCuffs.remove(res)
                            res = cuffParentsDict[cuffParents[-1]]
                            # print res

                        cuffChildren = []
                        if iTargetCuff in cuffChildrenDict.keys():
                            cuffChildren = cuffChildrenDict[iTargetCuff]

                        #  after removing all parents. if there are no coactivated cuffs: selective
                        if len(coactivatedCuffs) == 0:
                            numChan[subject]['selectiveElec'] += 1
                            print subject + ' ' + str(iSesh) + ' ' + str(iStimChan) + ' selective for ' + hf.allCuffs_mdf[iTargetCuff]
                            selectiveDF = selectiveDF.append({'DRG': iDRG, 'nerve': hf.allCuffs_mdf[iTargetCuff], 'subject': subject},ignore_index=True)

                        # children, siblings or unrelated coactivated cuffs left
                        #
                        else:
                            coactivatedSiblings = []    # agonists can be a subset of this
                            coactivatedChildren = []
                            coactivatedUnrelated = []
                            for x in coactivatedCuffs:
                                if x in cuffChildrenDict[cuffParentsDict[iTargetCuff]]:
                                    coactivatedSiblings.append(x)

                                elif x in cuffChildren:
                                    coactivatedChildren.append(x)

                                else:
                                    coactivatedUnrelated.append(x)

                            if len(coactivatedSiblings) >1: #len(coactivatedSiblings) != 0 and len(coactivatedUnrelated) != 0:
                                nonSelectiveDF = nonSelectiveDF.append({'DRG': iDRG, 'nerve': hf.allCuffs_mdf[iTargetCuff], 'subject': subject},ignore_index=True)


    coactivationDF += coactivationDF_perDRG
    tmp = coactivationDF_perDRG.loc[:, (coactivationDF_perDRG != 0).any(axis=0)]
    tmp2 = tmp.loc[(tmp != 0).any(axis=1), :]
    tmp2.index = [hf.allCuffs_mdf[i] for i in tmp2.columns]
    tmp2.columns = tmp2.index
    sns.heatmap(tmp2/tmp2.max(), annot=False, fmt=".1f", linewidths=.5)
    plt.savefig(eType + '/' + iDRG + '_coactivation.pdf')
    plt.savefig(eType + '/' + iDRG + '_coactivation.png')
    plt.close()
print numChan
pd.DataFrame.from_dict(numChan).transpose().to_csv('selective_counts.csv')

tmp3 = coactivationDF.loc[:, (coactivationDF != 0).any(axis=0)]
tmp4 = tmp3.loc[(tmp3 != 0).any(axis=1), :]
tmp4.index = [hf.allCuffs_mdf[i] for i in tmp4.columns]
tmp4.columns = tmp4.index
sns.heatmap(tmp4/tmp4.max(), annot=False, fmt=".1f",)
plt.savefig(eType + '/' + 'allDRG_coactivation.pdf')
plt.savefig(eType + '/' + 'allDRG_coactivation.png')
plt.close()

f,ax3 = plt.subplots(3, 1, figsize=(9, 12))
sns.countplot(x='nerve',hue='DRG',order=tmp4.index,data=selectiveDF, ax=ax3[0])
sns.countplot(x='nerve',order=tmp4.index,data=selectiveDF, ax=ax3[1])
sns.countplot(x='DRG',hue='subject',order=hf.allDRG,data=selectiveDF, ax=ax3[2])

plt.savefig(eType + '/' + 'selectiveCounts.pdf')
plt.savefig(eType + '/' + 'selectiveCounts.png')
plt.close()

# f,axes = plt.subplots(3, 1, figsize=(9, 12))
# sns.countplot(x='nerve',hue='DRG',order=tmp4.index,data=nonSelectiveDF, ax=axes[0])
# sns.countplot(x='nerve',order=tmp4.index,data=nonSelectiveDF, ax=axes[1])
# sns.countplot(x='DRG',hue='subject',order=hf.allDRG,data=nonSelectiveDF, ax=axes[2])
# plt.savefig(eType + '/' + 'nonselectiveCounts.pdf')
# plt.savefig(eType + '/' + 'nonselectiveCounts.png')
# plt.close()


# import plotly
# import plotly.graph_objs as go
# import numpy as np
# from plotly import tools
# data = [go.Heatmap(z=tmp2, y=tmp2.index,x=tmp2.index,colorscale=hf.parula)]
# plotly.offline.plot({'data':data, 'layout':go.Layout(title=eType+' coactivation matrix')},filename=eType+'_test.html',auto_open=True)
