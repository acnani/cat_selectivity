import helperFcns as hf
from helperFcns import plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly

eType = 'epineural'

collapseCuffs = True
ignoreCuffs = ['BiFem']

cuffChildrenDict = hf.getInnervationChildren()
cuffParentsDict = hf.getInnervationParents()
colorList = hf.colorOrder

subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()

selectiveDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject','Threshold','Dynamic Range','Threshold (nC)','Dynamic Range (nC)','type','binarySearchRes'])
nonSelectiveDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject','type'])
agonistDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject','type'])

numChan = {}
for iDRG in hf.allDRG:

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
                binaryRes = hf.convertCurrentToCharge(hf.binarySearchResolutionbySession[subject][iSesh], subject,iSesh)

                for iStimChan in allStimChans:
                    cuffThresholds = threshDict[iStimChan]
                    maxAmp = hf.maxAmplitudePerSession(subject, iSesh)

                    # print cuffThresholds
                    allRecruitedCuffs = cuffThresholds.keys()

                    if cuffThresholds:
                        numChan[subject]['activeElec'] += 1

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
                            else:
                                dynamicRange = maxAmp - threshAmp

                            dynamicRange_nC = hf.convertCurrentToCharge(dynamicRange, subject, iSesh)
                            selectiveDF = selectiveDF.append(
                                                {'DRG': iDRG, 'nerve': hf.allCuffs_mdf[selectiveCuffLabel], 'subject': subject,
                                                 'Threshold': threshAmp, 'Dynamic Range': dynamicRange,
                                                 'Threshold (nC)': thresh_nC, 'Dynamic Range (nC)': dynamicRange_nC, 'binarySearchRes':binaryRes,
                                                 'type': 'selective', 'stimChan':iStimChan,
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

print numChan
pd.DataFrame.from_dict(numChan).transpose().to_csv(eType + '/selective_counts.csv')
selectiveDF.to_csv(eType + '/selectiveDF.csv', index=False)

# # selective, non selective and agonist counts
concatData = selectiveDF.append(agonistDF).append(nonSelectiveDF, ignore_index=True)
barOrder = ['Tib','dTib','MG','LG','CP','dCP','Sensory','Sph','VL','VM','Srt'] #[x for x in hf.allCuffs_mdf.values() if x in concatData['nerve'].unique()]

f,ax3 = plt.subplots(figsize=(9, 6))
sns.countplot(x='nerve',hue='type',hue_order=['selective','non-selective','agonist'], order=barOrder,data=concatData)
plt.savefig(eType + '/selectiveCounts.pdf')
plt.savefig(eType + '/selectiveCounts.png')
plt.close()


# polar plot of selective recruitment
data = []
for iDRG in ['DRG - L5', 'DRG - L6', 'DRG - L7']:
    nerveCounts = selectiveDF[selectiveDF['DRG'] == iDRG].nerve.value_counts()
    polarVals = []
    for iKey in barOrder:
        if iKey in nerveCounts.keys():
            polarVals.append(nerveCounts[iKey])
        else:
            polarVals.append(0)

    data.append(
        go.Scatterpolar(
          name = iDRG,
          r = polarVals,
          theta = barOrder,
          fill = "toself"
        ),)

layout = go.Layout(
    polar = dict(
      radialaxis = dict(
        angle = 45
      ),
      angularaxis = dict(
        direction = "clockwise",
        period = 6
      )
    ),)
fig = go.Figure(data=data, layout=layout)
# plotly.offline.plot(fig, filename=eType+'\\polarSelectivity.html')
plotly.plotly.image.save_as(fig, filename=eType+'\\polarSelectivity.pdf')
plotly.plotly.image.save_as(fig, filename=eType+'\\polarSelectivity.png')



# # threshold and DR distributions in uA
DR = selectiveDF['Dynamic Range (nC)']
DR = DR[DR>0]
TH = selectiveDF['Threshold (nC)']
maxVal_thresh = int(max(selectiveDF['Threshold (nC)']))
if eType == 'penetrating':
    binSize_thresh = 0.3
    binSize_DR = 0.15
else:
    binSize_thresh = 3
    binSize_DR = 0.28

maxVal_DR = int(max(DR))

f,ax4 = plt.subplots(1, 2, figsize=(12, 5))
sns.distplot(TH, bins=np.arange(0, maxVal_thresh, binSize_thresh) , kde=False,ax=ax4[0]) # range(0,maxVal_thresh,stepSize_thresh)
ax4[0].plot([np.median(TH), np.median(TH)], [0, 2], linewidth=2)
ax4[0].text(0, 0, np.median(TH))
sns.distplot(DR, bins=np.arange(0,maxVal_DR,binSize_DR), kde=False,ax=ax4[1])
ax4[1].plot([np.median(DR), np.median(DR)], [0, 2], linewidth=2)
ax4[1].text(0, 0, np.median(DR))
ax4[1].set(xlim=(None,6.2))

TH.to_csv(eType + '/thresholds.csv',header=['vals'])
DR.to_csv(eType + '/dynamicRanges.csv',header=['vals'])

plt.savefig(eType + '/thresh_DR_charge.pdf')
plt.savefig(eType + '/thresh_DR_charge.png')
plt.close()



# # threshold and DR distributions in uA
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

# # non selective counts per animal
# f,axes = plt.subplots(3, 1, figsize=(9, 12))
# sns.countplot(x='nerve',hue='DRG',order=barOrder,data=nonSelectiveDF, ax=axes[0])
# sns.countplot(x='nerve',order=barOrder,data=nonSelectiveDF, ax=axes[1])
# sns.countplot(x='DRG',hue='subject',order=hf.allDRG,data=nonSelectiveDF, ax=axes[2])
# plt.savefig(eType + '/' + 'nonselectiveCounts.pdf')
# plt.savefig(eType + '/' + 'nonselectiveCounts.png')
# plt.close()

print 'finished'