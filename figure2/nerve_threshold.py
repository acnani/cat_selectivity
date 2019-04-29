import helperFcns as hf
from helperFcns import plt
import seaborn as sns
import pandas as pd

eType = 'penetrating'

collapseCuffs = True
ignoreCuffs = ['BiFem']

subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()
coactivationDF = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

for iDRG in hf.allDRG:
    coactivationDF_perDRG = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

    for subject in subjectList:
        # returns all sessions per DRG per subject
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
                    allRecruitedCuffs = cuffThresholds.keys()

                    for iTargetCuff in allRecruitedCuffs:
                        targetCuffThreshold = cuffThresholds[iTargetCuff]

                        # populate DF for coactivation matrix
                        for iRecruitedCuff in allRecruitedCuffs:
                            if cuffThresholds[iRecruitedCuff] <= targetCuffThreshold:
                                coactivationDF_perDRG.loc[iTargetCuff, iRecruitedCuff] += 1

    coactivationDF += coactivationDF_perDRG
    tmp = coactivationDF_perDRG.loc[:, (coactivationDF_perDRG != 0).any(axis=0)]
    tmp2 = tmp.loc[(tmp != 0).any(axis=1), :]
    tmp2.index = [hf.allCuffs_mdf[i] for i in tmp2.columns]
    tmp2.columns = tmp2.index
    sns.heatmap(tmp2/tmp2.max(), annot=False, fmt=".1f", linewidths=.5,center=0.8)
    plt.savefig(eType + '/nerveThresh/' + iDRG + '_coactivation.pdf')
    plt.savefig(eType + '/nerveThresh/' + iDRG + '_coactivation.png')
    plt.close()


tmp3 = coactivationDF.loc[:, (coactivationDF != 0).any(axis=0)]
tmp4 = tmp3.loc[(tmp3 != 0).any(axis=1), :]
tmp4.index = [hf.allCuffs_mdf[i] for i in tmp4.columns]
tmp4.columns = tmp4.index
sns.heatmap(tmp4/tmp4.max(), annot=False, fmt=".1f",)
plt.savefig(eType + '/nerveThresh/allDRG_coactivation.pdf')
plt.savefig(eType + '/nerveThresh/allDRG_coactivation.png')
plt.close()

print 'finished'