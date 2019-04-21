# plots innervation trees where node size is the number of channels activating the nerve
# returns 2 graphs 1) tree per drg per subject and 2) tree aggregated across subjects

import plotly
from plotly import tools
import helperFcns as hf
import numpy as np

eType = 'epineural'
collapseCuffs = True
ignoreCuffs = ['BiFem']

cuffParentsDict = hf.getInnervationParents()
cuffCoord = hf.getInnervationTreeCoords()
subjectList = hf.getSubjects(eType)
allDRG = hf.allDRG
targetNerveLabels = hf.allCuffs_mdf.keys()

numChanDict= dict.fromkeys(allDRG,{})
meanAmpDict = dict.fromkeys(allDRG,{})
for drg in allDRG:
    numChanDict[drg] = dict.fromkeys(targetNerveLabels,0)
    meanAmpDict[drg] = {k: [] for k in targetNerveLabels}


normFactor = []
subjectRow = 0
fig_numCh = tools.make_subplots(rows=len(subjectList), cols=len(allDRG), subplot_titles=allDRG*len(allDRG))
fig_meanA = tools.make_subplots(rows=len(subjectList), cols=len(allDRG), subplot_titles=allDRG*len(allDRG))

fig_numChan = tools.make_subplots(rows=1, cols=len(allDRG), subplot_titles=allDRG)
fig_meanAmp = tools.make_subplots(rows=1, cols=len(allDRG), subplot_titles=allDRG)

# for subject in subjectList:
for iDRG in allDRG:
    for subject in subjectList:

        subjectRow = subjectList.index(subject) + 1

        # returns all sessions per iDRG per subject
        res2 = hf.sessionPerDRG(subject, eType)

    # iterate over each iDRG
    # for iDRG in res2.keys():
        subjectNumChanDict = dict.fromkeys(targetNerveLabels, 0)
        subjectMeanAmpDict = {k: [] for k in targetNerveLabels}


        subjectCol = allDRG.index(iDRG) + 1
        if iDRG in res2.keys():
            targetSesh = res2[iDRG] #sorted([value for value in allEtypeSesh if value in res2[iDRG]])

            for sesh in targetSesh:
                threshDict = hf.thresholdPerCuff(subject, sesh, ignoreCuffs, collapseCuffs)
                allActiveChans = sorted(threshDict.keys())

                # if allActiveChans:
                for iChan in allActiveChans:
                    # if threshDict[iChan]:
                    for cuffName in threshDict[iChan].keys():
                        if eType == 'epineural':
                            threshCharge = hf.convertCurrentToCharge(threshDict[iChan][cuffName], subject, sesh)
                        else:
                            threshCharge = threshDict[iChan][cuffName]

                        numChanDict[iDRG][cuffName] += 1
                        meanAmpDict[iDRG][cuffName].append(threshCharge)

                        subjectNumChanDict[cuffName] += 1
                        subjectMeanAmpDict[cuffName].append(threshCharge)

            nodecolor = [np.mean(subjectMeanAmpDict[cuff]) for cuff in targetNerveLabels if subjectMeanAmpDict[cuff]]
            nodeLabel = [cuff for cuff in targetNerveLabels if subjectMeanAmpDict[cuff]]
            figDict_meanAmp = hf.generateInnervationTree(nodeLabel, nodecolor, 10, etype=eType)
            [fig_meanA.append_trace(iData, subjectRow, subjectCol) for iData in figDict_meanAmp['data']]
            fig_meanA['layout']['showlegend'] = False

            nodeSize = [subjectNumChanDict[cuff] for cuff in targetNerveLabels if subjectNumChanDict[cuff] !=0]
            nodeLabel = [cuff for cuff in targetNerveLabels if subjectNumChanDict[cuff] !=0]
            figDict_numChans = hf.generateInnervationTree(nodeLabel, hf.colorOrder[subjectCol-1], nodeSize, etype=eType)
            [fig_numCh.append_trace(iData, subjectRow, subjectCol) for iData in figDict_numChans['data']]
            fig_numCh['layout']['showlegend'] = False

    drgCol = allDRG.index(iDRG)
    nodeColor_meanAmp = [np.mean(meanAmpDict[iDRG][cuff]) for cuff in targetNerveLabels if meanAmpDict[iDRG][cuff]]
    nodeLabel = [cuff for cuff in targetNerveLabels if meanAmpDict[iDRG][cuff]]
    figDict_meanAmp = hf.generateInnervationTree(nodeLabel, nodeColor_meanAmp,etype=eType)
    [fig_meanAmp.append_trace(iData, 1, drgCol + 1) for iData in figDict_meanAmp['data']]
    fig_meanAmp['layout']['showlegend'] = False

    nodeSize_numChan = [numChanDict[iDRG][cuff] for cuff in targetNerveLabels if numChanDict[iDRG][cuff] != 0]
    nodeLabel = [cuff for cuff in targetNerveLabels if numChanDict[iDRG][cuff] != 0]
    figDict_numChan = hf.generateInnervationTree(nodeLabel, hf.colorOrder[drgCol], nodeSize_numChan,etype=eType)
    [fig_numChan.append_trace(iData, 1, drgCol + 1) for iData in figDict_numChan['data']]
    fig_numChan['layout']['showlegend'] = False

if eType == 'epineural':
    fig_numChan['layout'].update(height=400, width=1300)
    fig_meanAmp['layout'].update(height=400, width=3000)
else:
    fig_numChan['layout'].update(height=1000, width=4500)
    fig_meanAmp['layout'].update(height=400, width=3000)

plotly.offline.plot(fig_numChan, filename=eType+'\\perDRG\\numChans_combined.html',auto_open=False)
plotly.plotly.image.save_as(fig_numChan, filename=eType+'\\perDRG\\numChans_combined.pdf')
plotly.plotly.image.save_as(fig_numChan, filename=eType+'\\perDRG\\numChans_combined.png')

plotly.offline.plot(fig_meanAmp, filename=eType+'\\perDRG\\meanAmp_combined.html',auto_open=False)
plotly.plotly.image.save_as(fig_meanAmp, filename=eType+'\\perDRG\\meanAmp_combined.pdf')
plotly.plotly.image.save_as(fig_meanAmp, filename=eType+'\\perDRG\\meanAmp_combined.png')

plotly.offline.plot(fig_numCh, filename=eType+'\\perDRG\\numChans_perSub.html',auto_open=False)
plotly.plotly.image.save_as(fig_numCh, filename=eType+'\\perDRG\\numChans_perSub.pdf')
plotly.plotly.image.save_as(fig_numCh, filename=eType+'\\perDRG\\numChans_perSub.png')

plotly.offline.plot(fig_meanA, filename=eType+'\\perDRG\\meanAmp_perSub.html',auto_open=False)
plotly.plotly.image.save_as(fig_meanA, filename=eType+'\\perDRG\\meanAmp_perSub.pdf')
plotly.plotly.image.save_as(fig_meanA, filename=eType+'\\perDRG\\meanAmp_perSub.png')

print 'finished'


