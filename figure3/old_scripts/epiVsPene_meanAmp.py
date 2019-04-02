# this creates the patch heatmaps and the innervation trees for mean recruited amplitude

# TO DO dort by epineural vs penetrating

import pymongo
import helperFcns as hf
import plotly
import plotly.graph_objs as go
from igraph import *
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

meanAmpDict = dict.fromkeys(subjectList)
for subject in subjectList:
    meanAmpDict[subject] = {}
    for DRG in allDRG:
        meanAmpDict[subject][DRG] = {}
        for cuff in allCuffs:
            meanAmpDict[subject][DRG][cuff] = []



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

                            for cuffName in resultCuffs:
                                meanAmpDict[subject][iDRG['DRG']][cuffName].append(threshDict[iChan][cuffName])

#
# with open ('meanAmpDict_'+eType+'.yml', 'w') as meanDict:
#     yaml.safe_dump(meanAmpDict,meanDict)

# with open ('meanAmpDict_'+eType+'.yml', 'r') as meanDict:
#     meanAmpDict = yaml.load(meanDict)


# create heatmap
hMap = np.zeros((len(subjectList),len(allCuffs),len(allDRG)))
for sub in subjectList:
    for DRG in allDRG:
        for cuffName in meanAmpDict[sub][DRG].keys():
            hMap[subjectList.index(sub), allCuffs.index(cuffName), allDRG.index(DRG)] = mean(meanAmpDict[sub][DRG][cuffName])

## by level
fig = tools.make_subplots(rows=len(allDRG), cols=1, subplot_titles=allDRG)
for iPlot in range(4):
    trace = go.Heatmap(z=hMap[:,:,iPlot], y=subjectList,x=allCuffs)
    fig.append_trace(trace, iPlot+1, 1)

fig['layout'].update(height = 600*3, )
plotly.offline.plot(fig, filename='finalFigs\meanThresholds_hMap_byDRG'+eType+'.html')


## by subject
fig = tools.make_subplots(rows=len(subjectList), cols=1, subplot_titles=subjectList)
for iPlot in range(len(subjectList)):
    trace = go.Heatmap(z=np.transpose(hMap[iPlot,:,:]), y=allDRG,x=allCuffs)
    fig.append_trace(trace, iPlot+1, 1)

fig['layout'].update(height = 600*3, )
plotly.offline.plot(fig, filename='finalFigs\meanThresholds_hMap_bysubject'+eType+'.html')

# # create innervation trees --> this is buggy
fig = tools.make_subplots(rows=len(subjectList), cols=4)

row = 0
for sub in subjectList:
    subjectRow = subjectList.index(sub) + 1
    col = 1
    for DRG in allDRG:
        subjectCol = allDRG.index(DRG) + 1
        nodeColor = [mean(meanAmpDict[sub][DRG][cuff]) for cuff in cuffDict]
        figDict = hf.generateInnervationTree(meanAmpDict[sub][DRG].keys(), 25, nodeColor, False)
        [fig.append_trace(iData, subjectRow, subjectCol) for iData in figDict['data']]
        fig['layout']['showlegend'] = False
        fig['layout']['annotations'].extend(figDict['layout']['annotations'])
        fig['layout']['xaxis' + str(subjectCol)].update(figDict['layout']['xaxis'])
        fig['layout']['yaxis' + str(subjectCol)].update(figDict['layout']['yaxis'])

if bool(fig['data']):  # if threshDict[iChan] for all chnnels is empty
    fig['layout'].update(height=600 * len(subjectList), width=6000)
    plotly.offline.plot(fig, filename='finalFigs\\numChanInnervationTrees' + eType + 'chutya.html')
    # plotly.plotly.image.save_as(fig, filename='finalFigs\\numChanInnervationTrees' + eType + '.png')



