# plots innervation trees where node size is the number of channels activating the nerve
# returns 2 graphs 1) tree per drg per subject and 2) tree aggregated across subjects

import plotly
from plotly import tools
import helperFcns as hf
import numpy as np

eType = 'epineural'
collapseCuffs = False

cuffParentsDict = hf.getCanonicalInnervation()
cuffDict = cuffParentsDict.keys()
cuffCoord = hf.getInnervationTreeCoords()
allCuffs = hf.allCuffs_mdf.keys()
subjectList = hf.getSubjects(eType)
allDRG = hf.allDRG


numChanDict= dict.fromkeys(allDRG,{})
meanAmpDict = dict.fromkeys(allDRG,{})
for drg in allDRG:
    numChanDict[drg] = dict.fromkeys(allCuffs,0)
    for iCuff in allCuffs:
        meanAmpDict[drg][iCuff] = []


normFactor = []
subjectRow = 0
fig_numCh = tools.make_subplots(rows=len(subjectList), cols=4, subplot_titles=allDRG*4)
fig_meanA = tools.make_subplots(rows=len(subjectList), cols=4, subplot_titles=allDRG*4)

for subject in subjectList:
    seshDict = {}

    subjectRow = subjectList.index(subject) + 1

    # returns all sessions per DRG per subject
    res2 = hf.sessionPerDRG(subject)                       # add arguemnt for penetrating vs epineural
    res3 = hf.sessionPerElectrodeType(subject)

    # iterate over each DRG
    for iDRG in res2['result']:
        subjectNumChanDict = dict.fromkeys(allCuffs, 0)
        subjectMeanAmpDict = {}
        for iCuff in allCuffs:
            subjectMeanAmpDict[iCuff] = []

        if iDRG['DRG'] in allDRG:
            subjectCol = allDRG.index(iDRG['DRG']) + 1
            allEtypeSesh = res3[eType]
            targetSesh = sorted([value for value in allEtypeSesh if value in iDRG['session']])
            # iterate over each session
            for sesh in targetSesh:
                threshDict = hf.thresholdPerCuff(subject, sesh, allCuffs, collapseCuffs)
                allActiveChans = sorted(threshDict.keys())
                numActiveChans = len(allActiveChans)

                if numActiveChans != 0:

                    for iChan in allActiveChans:
                        if bool(threshDict[iChan]):
                            resultCuffs = threshDict[iChan].keys()

                            for cuffName in resultCuffs:
                                numChanDict[iDRG['DRG']][cuffName] += 1
                                meanAmpDict[iDRG['DRG']][cuffName].append(threshDict[iChan][cuffName])
                                subjectNumChanDict[cuffName] += 1
                                subjectMeanAmpDict[cuffName].append(threshDict[iChan][cuffName])

            nodeColor = [np.mean(subjectMeanAmpDict[cuff]) for cuff in cuffDict if cuff]
            figDict_meanAmp = hf.generateInnervationTree(subjectNumChanDict.keys(), nodeColor, 10, showAnnots=False)
            [fig_meanA.append_trace(iData, subjectRow, subjectCol) for iData in figDict_meanAmp['data']]
            fig_meanA['layout']['showlegend'] = False
            for iAnnot in range(len(figDict_meanAmp['layout']['annotations'])):
                figDict_meanAmp['layout']['annotations'][iAnnot]['xref'] = 'x' + str(subjectCol * 4 + subjectRow)
                figDict_meanAmp['layout']['annotations'][iAnnot]['yref'] = 'y' + str(subjectCol * 4 + subjectRow)
            fig_meanA['layout']['annotations'].extend(figDict_meanAmp['layout']['annotations'])
            fig_meanA['layout']['xaxis' + str(subjectCol)].update(figDict_meanAmp['layout']['xaxis'])
            fig_meanA['layout']['yaxis' + str(subjectCol)].update(figDict_meanAmp['layout']['yaxis'])

            nodeSize = [subjectNumChanDict[cuff] for cuff in cuffDict]
            figDict_numChans = hf.generateInnervationTree(subjectNumChanDict.keys(), hf.colorOrder[subjectCol-1], nodeSize, False)
            [fig_numCh.append_trace(iData, subjectRow, subjectCol) for iData in figDict_numChans['data']]
            fig_numCh['layout']['showlegend'] = False
            for iAnnot in range(len(figDict_numChans['layout']['annotations'])):
                figDict_numChans['layout']['annotations'][iAnnot]['xref'] = 'x' + str(subjectCol*4+subjectRow)
                figDict_numChans['layout']['annotations'][iAnnot]['yref'] = 'y' + str(subjectCol*4+subjectRow)
            fig_numCh['layout']['annotations'].extend(figDict_numChans['layout']['annotations'])
            fig_numCh['layout']['xaxis' + str(subjectCol)].update(figDict_numChans['layout']['xaxis'])
            fig_numCh['layout']['yaxis' + str(subjectCol)].update(figDict_numChans['layout']['yaxis'])

plotly.offline.plot(fig_numCh, filename='innervationTrees_perDRG\\numChans_' + eType + '_perSub.html')
plotly.offline.plot(fig_meanA, filename='innervationTrees_perDRG\\meanAmp_' + eType + '_perSub.html')
# plotly.plotly.image.save_as(fig, filename='finalFigs\\numChanInnervationTrees' + eType + '.svg')





fig_numChan = tools.make_subplots(rows=1, cols=4, subplot_titles= allDRG)
fig_meanAmp = tools.make_subplots(rows=1, cols=4, subplot_titles= allDRG)
for DRG in allDRG:
    col = allDRG.index(DRG)
    nodeColor_meanAmp = [np.mean(meanAmpDict[DRG][cuff]) for cuff in cuffDict if cuff]
    figDict_meanAmp = hf.generateInnervationTree(numChanDict[DRG].keys(), nodeColor_meanAmp)
    [fig_meanAmp.append_trace(iData, 1, col + 1) for iData in figDict_meanAmp['data']]
    fig_meanAmp['layout']['showlegend'] = False
    for iAnnot in range(len(nodeColor_meanAmp)):
        figDict_meanAmp['layout']['annotations'][iAnnot]['xref'] = 'x' + str(col + 1)
        figDict_meanAmp['layout']['annotations'][iAnnot]['yref'] = 'y' + str(col + 1)
    fig_meanAmp['layout']['annotations'].extend(figDict_meanAmp['layout']['annotations'])
    fig_meanAmp['layout']['xaxis' + str(col + 1)].update(figDict_meanAmp['layout']['xaxis'])
    fig_meanAmp['layout']['yaxis' + str(col + 1)].update(figDict_meanAmp['layout']['yaxis'])

    nodeSize_numChan = [numChanDict[DRG][cuff] for cuff in cuffDict]
    figDict_numChan = hf.generateInnervationTree(numChanDict[DRG].keys(), hf.colorOrder[col], nodeSize_numChan)
    [fig_numChan.append_trace(iData, 1, col+1) for iData in figDict_numChan['data']]
    fig_numChan['layout']['showlegend'] = False
    for iAnnot in range(len(nodeSize_numChan)):
        figDict_numChan['layout']['annotations'][iAnnot]['xref'] = 'x' + str(col+1)
        figDict_numChan['layout']['annotations'][iAnnot]['yref'] = 'y' + str(col+1)
    fig_numChan['layout']['annotations'].extend(figDict_numChan['layout']['annotations'])
    fig_numChan['layout']['xaxis' + str(col+1)].update(figDict_numChan['layout']['xaxis'])
    fig_numChan['layout']['yaxis' + str(col+1)].update(figDict_numChan['layout']['yaxis'])

fig_numChan['layout'].update(height=1000, width=6000)
fig_meanAmp['layout'].update(height=1000, width=6000)

plotly.offline.plot(fig_numChan, filename='innervationTrees_perDRG\\numChans_'+eType+'_combined.html')
plotly.offline.plot(fig_meanAmp, filename='innervationTrees_perDRG\\meanAmp_'+eType+'_combined.html')
