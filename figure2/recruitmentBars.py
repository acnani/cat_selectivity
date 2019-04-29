import helperFcns as hf
from helperFcns import plt
import seaborn as sns
import pandas as pd
import numpy as np

eType = 'epineural'

collapseCuffs = True
ignoreCuffs = ['BiFem']

cuffChildrenDict = hf.getInnervationChildren()
cuffParentsDict = hf.getInnervationParents()
colorList = hf.colorOrder

subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()
coactivationDF = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

selectiveDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject','Threshold','Dynamic Range','Threshold (nC)','Dynamic Range (nC)','type'])
nonSelectiveDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject','type'])
agonistDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject','type'])

numChan = {}
coactivationDict_perDRG = {}
for iDRG in hf.allDRG:
    coactivationDF_perDRG = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

    for subject in subjectList:
        numChan.setdefault(subject,{'selectiveElec':0, 'activeElec':0, })
        seshPerDRG = hf.sessionPerDRG(subject, eType)  # add argument for penetrating vs epineural

        if iDRG in seshPerDRG.keys():

            # iterate over each session
            for iSesh in seshPerDRG[iDRG]:
                threshDict = hf.thresholdPerCuff(subject, iSesh, ignoreCuffs, collapseCuffs)
                threshChans = sorted(threshDict.keys())
                discardChans = hf.getSingleAmplitudeChannels(subject, iSesh)
                allStimChans = [chans for chans in threshChans if chans not in discardChans]

                for iStimChan in allStimChans:
                    cuffThresholds = threshDict[iStimChan]

                    # print cuffThresholds
                    allRecruitedCuffs = cuffThresholds.keys()

                    if cuffThresholds:
                        # coactivation matrix
                        numChan[subject]['activeElec'] += 1
                        threshAmp = min(cuffThresholds.values())
                        coactivatedCuffs = [x for x in cuffThresholds.keys() if cuffThresholds[x] <= threshAmp]

                        for iTargetCuff in coactivatedCuffs:
                            for iCoactive in coactivatedCuffs:
                                coactivationDF_perDRG.loc[iTargetCuff, iCoactive] += 1

                        # selectivity counts
                        cuffThresholds.pop("Sciatic_Proximal", None)
                        cuffThresholds.pop("Femoral_Proximal", None)
                        threshAmp = min(cuffThresholds.values())
                        coactivatedCuffs = [x for x in cuffThresholds.keys() if cuffThresholds[x] <= threshAmp]
                        # remove all ancestors of the recruited nerves
                        for iCuff in coactivatedCuffs:
                            res = cuffParentsDict[iCuff]
                            while res != '':
                                if res in coactivatedCuffs: coactivatedCuffs.remove(res)
                                res = cuffParentsDict[res]

                        # selective recruitment
                        if len(coactivatedCuffs) == 1:
                            numChan[subject]['selectiveElec'] += 1
                            selectiveCuffLabel = coactivatedCuffs[0]
                            print subject + ' ' + str(iSesh) + ' ' + str(iStimChan) + ' selective for ' + hf.allCuffs_mdf[selectiveCuffLabel]

                            thresh_nC = hf.convertCurrentToCharge(threshAmp, subject, iSesh)
                            # TODO: avoid diff with parents for instances where parent threshold is higher than child
                            rangeList = []
                            for xKey in cuffThresholds.keys():
                                if (cuffThresholds[xKey] > threshAmp):
                                    if xKey in hf.agonists.keys():
                                        if not(selectiveCuffLabel == hf.agonists[xKey]):
                                            rangeList.append(cuffThresholds[xKey] - threshAmp)
                                    else:
                                        rangeList.append(cuffThresholds[xKey] - threshAmp)

                            if rangeList:
                                dynamicRange = min(rangeList)
                                dynamicRange_nC = hf.convertCurrentToCharge(thresh_nC, subject, iSesh)
                            else:
                                dynamicRange = 0.0
                                dynamicRange_nC = 0.0
                            selectiveDF = selectiveDF.append(
                                                {'DRG': iDRG, 'nerve': hf.allCuffs_mdf[selectiveCuffLabel], 'subject': subject,
                                                 'Threshold': threshAmp, 'Dynamic Range': dynamicRange,
                                                 'Threshold (nC)': thresh_nC, 'Dynamic Range (nC)': dynamicRange_nC,
                                                 'type': 'selective'
                                                 }, ignore_index=True)

                        # children, siblings or unrelated coactivated cuffs left
                        else:
                            # print coactivatedCuffs
                            for x in coactivatedCuffs:
                                if x in hf.agonists.keys():
                                    if hf.agonists[x] in coactivatedCuffs:
                                        agonistDF = agonistDF.append(
                                            {'DRG': iDRG, 'nerve': hf.allCuffs_mdf[x], 'subject': subject, 'type':'agonist'},
                                            ignore_index=True)
                                    else:
                                        nonSelectiveDF = nonSelectiveDF.append(
                                            {'DRG': iDRG, 'nerve': hf.allCuffs_mdf[x], 'subject': subject,
                                             'type': 'non-selective'},
                                            ignore_index=True)

                                else:
                                    nonSelectiveDF = nonSelectiveDF.append(
                                        {'DRG': iDRG, 'nerve': hf.allCuffs_mdf[x], 'subject': subject, 'type':'non-selective'},
                                        ignore_index=True)

                    else:
                        print 'no results for this session'

    coactivationDict_perDRG[iDRG] = coactivationDF_perDRG
    coactivationDF += coactivationDF_perDRG



# generate figures
tmp3 = coactivationDF.loc[:, (coactivationDF != 0).any(axis=0)]
tmp4 = tmp3.loc[(tmp3 != 0).any(axis=1), :]
activeNerves = tmp4.columns
tmp4.index = [hf.allCuffs_mdf[i] for i in activeNerves]
tmp4.columns = tmp4.index
tmp4 = tmp4.div(tmp4.max(axis=1), axis=0)
sns.heatmap(tmp4, annot=False, fmt=".1f",)
plt.yticks(rotation=0)
plt.savefig(eType + '/allDRG_coactivation.pdf')
plt.savefig(eType + '/allDRG_coactivation.png')
plt.close()

for iDRG in hf.allDRG:
    coactivationDF_perDRG = coactivationDict_perDRG[iDRG][activeNerves]
    tmp2 = coactivationDict_perDRG[iDRG].loc[activeNerves, activeNerves]
    tmp2.index = [hf.allCuffs_mdf[i] for i in tmp2.columns]
    tmp2.columns = tmp2.index
    tmp2 = tmp2.div(tmp2.max(axis=1), axis=0)

    zm = np.ma.masked_less(tmp2.fillna(99).values,98)
    x = np.arange(len(tmp2.columns) + 1)
    y = np.arange(len(tmp2.index) + 1)
    sns.heatmap(tmp2, annot=False, fmt=".1f", linewidths=.5)
    plt.pcolor(x, y, zm, hatch='//', alpha=0.)
    plt.yticks(rotation=0)
    plt.savefig(eType + '/' + iDRG + '_coactivation.pdf')
    plt.savefig(eType + '/' + iDRG + '_coactivation.png')
    plt.close()

print numChan
pd.DataFrame.from_dict(numChan).transpose().to_csv(eType + '/selective_counts.csv')

tmp5 = selectiveDF.append(agonistDF).append(nonSelectiveDF, ignore_index=True)
f,ax3 = plt.subplots(2, 1, figsize=(6, 12))
sns.countplot(x='nerve',hue='DRG',order=tmp4.index,data=selectiveDF, ax=ax3[0])
# sns.countplot(x='nerve',order=tmp4.index,data=selectiveDF, ax=ax3[1])
sns.countplot(x='nerve',hue='type',hue_order=['selective','non-selective','agonist'], order=tmp4.index,data=tmp5,ax=ax3[1])
# sns.countplot(x='DRG',hue='subject',order=hf.allDRG,data=selectiveDF, ax=ax3[2])
plt.savefig(eType + '/selectiveCounts.pdf')
plt.savefig(eType + '/selectiveCounts.png')
plt.close()



DR = selectiveDF['Dynamic Range (nC)']
DR = DR[DR>0]
TH = selectiveDF['Threshold (nC)']
maxVal_thresh = int(max(selectiveDF['Threshold (nC)']))
if eType == 'penetrating':
    binSize_thresh = 0.3
    binSize_DR = 0.05
else:
    binSize_thresh = 3
    binSize_DR = 0.28

maxVal_DR = int(max(DR))

f,ax4 = plt.subplots(1, 2, figsize=(12, 5))
sns.distplot(TH, bins=np.arange(0, maxVal_thresh, binSize_thresh) , kde=False,ax=ax4[0]) # range(0,maxVal_thresh,stepSize_thresh)
ax4[0].text(0, 0, np.median(TH))
sns.distplot(DR, bins=np.arange(0,maxVal_DR,binSize_DR), kde=False,ax=ax4[1])
ax4[1].text(0, 0, np.median(DR))
plt.savefig(eType + '/thresh_DR_charge.pdf')
plt.savefig(eType + '/thresh_DR_charge.png')
plt.close()


# DR = selectiveDF['Dynamic Range']
# DR = DR[DR>0]
# TH = selectiveDF['Threshold']
# maxVal_thresh = int(max(TH))
# numSteps_thresh = 20
# maxVal_DR = int(max(DR))
# numSteps_DR = 10
# f,ax4 = plt.subplots(1, 2, figsize=(12, 6))
# sns.distplot(TH,bins=np.linspace(0,maxVal_thresh,numSteps_thresh),kde=False,ax=ax4[0])
# ax4[0].text(0, 0, np.median(TH))
# sns.distplot(DR, bins=np.linspace(0,maxVal_DR,numSteps_DR), kde=False,ax=ax4[1])
# ax4[1].text(0, 0, np.median(DR))
# plt.savefig(eType + '/thresh_DR_amplitude.pdf')
# plt.savefig(eType + '/thresh_DR_amplitude.png')
# plt.close()


# f,axes = plt.subplots(3, 1, figsize=(9, 12))
# sns.countplot(x='nerve',hue='DRG',order=tmp4.index,data=nonSelectiveDF, ax=axes[0])
# sns.countplot(x='nerve',order=tmp4.index,data=nonSelectiveDF, ax=axes[1])
# sns.countplot(x='DRG',hue='subject',order=hf.allDRG,data=nonSelectiveDF, ax=axes[2])
# plt.savefig(eType + '/' + 'nonselectiveCounts.pdf')
# plt.savefig(eType + '/' + 'nonselectiveCounts.png')
# plt.close()

print 'finished'