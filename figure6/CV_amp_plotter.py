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




# violin plots for selectivity only
collapseCuffs = True
ignoreCuffs = ['BiFem']

cuffParentsDict = hf.getInnervationParents()
colorList = hf.colorOrder

subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()
coactivationDF = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

# selectiveDF = pd.DataFrame(columns=['DRG', 'nerve', 'subject','Threshold','Dynamic Range','Threshold (nC)','Dynamic Range (nC)','type'])

coactivationDict_perDRG = {}
for iDRG in hf.allDRG:
    coactivationDF_perDRG = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)

    for subject in subjectList:
        # numChan.setdefault(subject,{'selectiveElec':0, 'activeElec':0, })
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
                        threshAmp = min(cuffThresholds.values())
                        coactivatedCuffs = [x for x in cuffThresholds.keys() if cuffThresholds[x] <= threshAmp]

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

                        # selective recruitment find CV
                        if len(coactivatedCuffs) == 1:
                            selectiveCuffLabel = coactivatedCuffs[0]
                            print subject + ' ' + str(iSesh) + ' ' + str(iStimChan) + ' selective for ' + hf.allCuffs_mdf[selectiveCuffLabel]

                            if hf.allCuffs_mdf[selectiveCuffLabel] in ['VL', 'VM', 'Sph', 'Srt']:
                                tmpObj = hf.db[hf.collection].find(
                                    {'mdf_def.mdf_type': 'CV', 'mdf_metadata.session': iSesh,
                                     'mdf_metadata.stimChan': iStimChan, 'mdf_metadata.location': 'Femoral'}).distinct('mdf_metadata.cv')

                            else:
                                tmpObj = hf.db[hf.collection].find(
                                    {'mdf_def.mdf_type': 'CV', 'mdf_metadata.session': iSesh,
                                     'mdf_metadata.stimChan': iStimChan, 'mdf_metadata.location': 'Sciatic'}).distinct('mdf_metadata.cv')




tmp = tmpAllCV_DF.append(tmpAllCV_Thresh, ignore_index=True)
sns.violinplot(x="Stimulation Amplitude", y="Conduction Velocity", orient='h', hue="Threshold", data=tmp,
               palette="muted", order=[120, 80, 60, 48, 40, 34], split=True, ax=violinAx[2])
violinAx[2].set_title('all trunks')
f.savefig(eType+"_"+stimUnits+"_CV_violinPlot.png")
f.savefig(eType+"_"+stimUnits+"_CV_violinPlot.pdf")
print 'done'
