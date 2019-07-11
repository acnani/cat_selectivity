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

coactivationDict_perDRG = {}
for iDRG in hf.allDRG:
    coactivationDF_perDRG = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

    for subject in subjectList:
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

                    # print cuffThresholds
                    allRecruitedCuffs = cuffThresholds.keys()

                    if cuffThresholds:
                        # coactivation matrix
                        threshAmp = min(cuffThresholds.values())
                        #
                        coactivatedCuffs = [x for x in cuffThresholds.keys() if cuffThresholds[x] <= threshAmp]

                        for iTargetCuff in coactivatedCuffs:
                            for iCoactive in coactivatedCuffs:
                                coactivationDF_perDRG.loc[iTargetCuff, iCoactive] += 1

    coactivationDict_perDRG[iDRG] = coactivationDF_perDRG
    coactivationDF += coactivationDF_perDRG


# # remove zero rows and columns
tmp3 = coactivationDF.loc[:, (coactivationDF != 0).any(axis=0)]
tmp4 = tmp3.loc[(tmp3 != 0).any(axis=1), :]
activeNerves = tmp4.columns
tmp4.index = [hf.allCuffs_mdf[i] for i in activeNerves]
tmp4.columns = tmp4.index


# # generate non normalized figures
# sns.heatmap(tmp4, annot=True, fmt="d",)
# plt.yticks(rotation=0)
# plt.savefig(eType + '/allDRG_coactivation_nonNorm.pdf')
# plt.savefig(eType + '/allDRG_coactivation_nonNorm.png')
# plt.close()

for iDRG in hf.allDRG:
    coactivationDF_perDRG = coactivationDict_perDRG[iDRG][activeNerves]
    tmp2 = coactivationDict_perDRG[iDRG].loc[activeNerves, activeNerves]
    tmp2.index = [hf.allCuffs_mdf[i] for i in tmp2.columns]
    tmp2.columns = tmp2.index

    zm = np.ma.masked_less(tmp2.fillna(99).values,98)
    x = np.arange(len(tmp2.columns) + 1)
    y = np.arange(len(tmp2.index) + 1)
    sns.heatmap(tmp2, annot=True, fmt="d") # linewidths=.5
    plt.pcolor(x, y, zm, hatch='//', alpha=0.)
    plt.yticks(rotation=0)
    plt.savefig(eType + '/' + iDRG + '_coactivation.pdf')
    plt.savefig(eType + '/' + iDRG + '_coactivation.png')
    plt.close()


# # generate normalized figures
tmp4 = tmp4.div(tmp4.max(axis=1), axis=0)
tmp4.to_csv(eType+'/coactivation_norm.csv')

sns.heatmap(tmp4)
plt.yticks(rotation=0)
plt.savefig(eType + '/allDRG_coactivation.pdf')
plt.savefig(eType + '/allDRG_coactivation.png')
plt.close()

# for iDRG in hf.allDRG:
#     coactivationDF_perDRG = coactivationDict_perDRG[iDRG][activeNerves]
#     tmp2 = coactivationDict_perDRG[iDRG].loc[activeNerves, activeNerves]
#     tmp2.index = [hf.allCuffs_mdf[i] for i in tmp2.columns]
#     tmp2.columns = tmp2.index
#     tmp2 = tmp2.div(tmp2.max(axis=1), axis=0)
#
#     zm = np.ma.masked_less(tmp2.fillna(99).values,98)
#     x = np.arange(len(tmp2.columns) + 1)
#     y = np.arange(len(tmp2.index) + 1)
#     sns.heatmap(tmp2, annot=False, fmt=".1f", linewidths=.5)
#     plt.pcolor(x, y, zm, hatch='//', alpha=0.)
#     plt.yticks(rotation=0)
#     plt.savefig(eType + '/' + iDRG + '_coactivation_norm.pdf')
#     plt.savefig(eType + '/' + iDRG + '_coactivation_norm.png')
#     plt.close()


print 'finished'