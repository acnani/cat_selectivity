# this creates the patch heatmaps and the innervation trees for number of chans

# TO Do sort by sessions

import helperFcns as hf
import plotly
import plotly.graph_objs as go
from plotly import tools
import numpy as np
import yaml


eType = 'epineural'
collapseCuffs = False

cuffParentsDict = hf.getCanonicalInnervation()
cuffDict = cuffParentsDict.keys()
cuffCoord = hf.getInnervationTreeCoords()
allCuffs = hf.allCuffs_mdf.keys()
subjectList = hf.getSubjects(eType)
allDRG = hf.allDRG

numChanDict = dict.fromkeys(subjectList)
for subject in subjectList:
    numChanDict[subject] = {}
    for DRG in allDRG:
        numChanDict[subject][DRG] = {}
        for cuff in allCuffs:
            numChanDict[subject][DRG][cuff] = 0


for subject in subjectList:
    seshDict = {}

    # returns all sessions per DRG per subject
    res2 = hf.sessionPerDRG(subject)                       # add arguemnt for penetrating vs epineural
    res3 = hf.sessionPerElectrodeType(subject)

    # iterate over each DRG
    for iDRG in res2['result']:
        if iDRG['DRG'] in allDRG:

            allEtypeSesh = res3[eType]
            targetSesh = sorted([value for value in allEtypeSesh if value in iDRG['session']])
            # iterate over each session
            for sesh in targetSesh:
                threshDict = hf.thresholdPerCuff(subject, sesh, allCuffs, False)
                allActiveChans = sorted(threshDict.keys())
                numActiveChans = len(allActiveChans)

                if numActiveChans != 0:

                    for iChan in allActiveChans:
                        if bool(threshDict[iChan]):
                            resultCuffs = threshDict[iChan].keys()
                            allAmps = [threshDict[iChan][cuffName] for cuffName in resultCuffs]
                            recruitmentThresh = min(allAmps)


                            for cuffName in resultCuffs:
                                numChanDict[subject][iDRG['DRG']][cuffName] += 1


# create heatmap
hMap = np.zeros((len(subjectList),len(allCuffs),len(allDRG)))
for sub in subjectList:
    for DRG in allDRG:
        for cuffName in numChanDict[sub][DRG].keys():
            hMap[subjectList.index(sub), allCuffs.index(cuffName), allDRG.index(DRG)] = numChanDict[sub][DRG][cuffName]

## by level
fig = tools.make_subplots(rows=len(allDRG), cols=1, subplot_titles=allDRG)
for iPlot in range(4):
    trace = go.Heatmap(z=hMap[:,:,iPlot], y=subjectList,x=allCuffs)
    fig.append_trace(trace, iPlot+1, 1)

fig['layout'].update(height = 600*3, )
plotly.offline.plot(fig, filename='finalFigs\\numChans_hMap_byDRG'+eType+'.html')


# by subject
fig = tools.make_subplots(rows=len(subjectList), cols=1, subplot_titles=subjectList)
for iPlot in range(len(subjectList)):
    trace = go.Heatmap(z=np.transpose(hMap[iPlot,:,:]), y=allDRG,x=allCuffs)
    fig.append_trace(trace, iPlot+1, 1)

fig['layout'].update(height = 600*3, )
plotly.offline.plot(fig, filename='finalFigs\\numChans_hMap_bysubject'+eType+'.html')




# # create innervation trees --> this is buggy
fig = tools.make_subplots(rows=len(subjectList), cols=4)

row = 0
for sub in subjectList:
    subjectRow = subjectList.index(sub) +1

    for DRG in allDRG:
        graphEdges = []
        subjectCol = allDRG.index(DRG)+1
        nodeSize = [numChanDict[sub][DRG][cuff] for cuff in cuffDict]
        figDict = hf.generateInnervationTree(numChanDict[sub][DRG].keys(), nodeSize, hf.colorOrder[subjectCol - 1], False)
        [fig.append_trace(iData, subjectRow, subjectCol) for iData in figDict['data']]
        fig['layout']['showlegend'] = False
        fig['layout']['annotations'].extend(figDict['layout']['annotations'])
        fig['layout']['xaxis' + str(subjectCol)].update(figDict['layout']['xaxis'])
        fig['layout']['yaxis' + str(subjectCol)].update(figDict['layout']['yaxis'])

if bool(fig['data']):  # if threshDict[iChan] for all chnnels is empty
    fig['layout'].update(height=600 * len(subjectList), width = 6000)
    plotly.offline.plot(fig, filename='finalFigs\\numChanInnervationTrees'+eType+'.html')
    # plotly.plotly.image.save_as(fig, filename='finalFigs\\numChanInnervationTrees' + eType + '.png')


print 'asd'


