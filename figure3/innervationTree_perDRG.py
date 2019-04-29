# plots innervation trees where node size is the number of channels activating the nerve
# returns 2 graphs 1) tree per drg per subject and 2) tree aggregated across subjects

import plotly
from plotly import tools
import helperFcns as hf
import numpy as np

eType = 'epineural'
stimunit = 'charge'

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
# fig_numCh = tools.make_subplots(rows=len(subjectList), cols=len(allDRG), subplot_titles=allDRG*len(allDRG))
# fig_meanA = tools.make_subplots(rows=len(subjectList), cols=len(allDRG), subplot_titles=allDRG*len(allDRG))

# fig_numChan = tools.make_subplots(rows=1, cols=len(allDRG), subplot_titles=allDRG)
fig_meanAmp = tools.make_subplots(rows=len(allDRG), cols=1, subplot_titles=allDRG)

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
                threshDict = hf.thresholdPerCuff(subject, sesh, ignoreCuffs, collapseCuffs,stimUnits=stimunit)
                allActiveChans = sorted(threshDict.keys())

                # if allActiveChans:
                for iChan in allActiveChans:
                    # if threshDict[iChan]:
                    # sciThresh = threshDict[iChan].pop("Sciatic_Proximal", None)
                    # meanAmpDict[iDRG]["Sciatic_Proximal"].append(sciThresh)
                    # femThresh = threshDict[iChan].pop("Femoral_Proximal", None)
                    # meanAmpDict[iDRG]["Femoral_Proximal"].append(femThresh)
                    # threshCharge = min(threshDict[iChan].values())
                    recruitedCuffs = threshDict[iChan].keys()#[iKey for iKey in threshDict[iChan].keys() if threshDict[iChan][iKey]<= threshCharge]
                    for cuffName in recruitedCuffs:
                        threshCharge = threshDict[iChan][cuffName]

                        numChanDict[iDRG][cuffName] += 1
                        meanAmpDict[iDRG][cuffName].append(threshCharge)

                        subjectNumChanDict[cuffName] += 1
                        subjectMeanAmpDict[cuffName].append(threshCharge)

            # nodecolor = [np.mean(subjectMeanAmpDict[cuff]) for cuff in targetNerveLabels if subjectMeanAmpDict[cuff]]
            # nodeLabel = [cuff for cuff in targetNerveLabels if subjectMeanAmpDict[cuff]]
            # figDict_meanAmp = hf.generateInnervationTree(nodeLabel, nodecolor, 10, stimUnits=stimunit,eType=eType)
            # [fig_meanA.append_trace(iData, subjectRow, subjectCol) for iData in figDict_meanAmp['data']]
            # fig_meanA['layout']['showlegend'] = False

            # nodeSize = [subjectNumChanDict[cuff]*10 for cuff in targetNerveLabels if subjectNumChanDict[cuff] !=0]
            # nodeLabel = [cuff for cuff in targetNerveLabels if subjectNumChanDict[cuff] !=0]
            # figDict_numChans = hf.generateInnervationTree(nodeLabel, hf.colorOrder[subjectCol-1], nodeSize, stimUnits=stimunit,eType=eType) #
            # [fig_numCh.append_trace(iData, subjectRow, subjectCol) for iData in figDict_numChans['data']]
            # fig_numCh['layout']['showlegend'] = False

    drgCol = allDRG.index(iDRG)
    nodeColor_meanAmp = [np.mean(meanAmpDict[iDRG][cuff]) for cuff in targetNerveLabels if meanAmpDict[iDRG][cuff]]
    nodeLabel = [cuff for cuff in targetNerveLabels if meanAmpDict[iDRG][cuff]]
    figDict_meanAmp = hf.generateInnervationTree(nodeLabel, nodeColor_meanAmp,stimUnits=stimunit,eType=eType)
    [fig_meanAmp.append_trace(iData, drgCol + 1, 1) for iData in figDict_meanAmp['data']]
    for x in ['xaxis','yaxis']:
        fig_meanAmp['layout'][x+str(drgCol + 1)].update(figDict_meanAmp['layout'][x])

    # nodeSize_numChan = [numChanDict[iDRG][cuff] for cuff in targetNerveLabels if numChanDict[iDRG][cuff] != 0]
    # nodeLabel = [cuff for cuff in targetNerveLabels if numChanDict[iDRG][cuff] != 0]
    # figDict_numChan = hf.generateInnervationTree(nodeLabel, hf.colorOrder[drgCol], nodeSize_numChan,stimUnits=stimunit,eType=eType)
    # [fig_numChan.append_trace(iData, 1, drgCol + 1) for iData in figDict_numChan['data']]
    # fig_numChan['layout']['showlegend'] = False

if eType == 'epineural':
    # fig_numChan['layout'].update(height=400, width=1300)
    fig_meanAmp['layout'].update(height=1400, width=1000, showlegend=False,plot_bgcolor='rgb(248,248,248)',margin=dict(l=40, r=40, b=85, t=100))
else:
    # fig_numChan['layout'].update(height=1000, width=4500)
    fig_meanAmp['layout'].update(height=1400, width=1000, showlegend=False,plot_bgcolor='rgb(248,248,248)',margin=dict(l=40, r=40, b=85, t=100))

# plotly.offline.plot(fig_numChan, filename=eType+'\\numChans_combined.html',auto_open=False)
# plotly.plotly.image.save_as(fig_numChan, filename=eType+'\\numChans_combined.pdf')
# plotly.plotly.image.save_as(fig_numChan, filename=eType+'\\numChans_combined.png')

plotly.offline.plot(fig_meanAmp, filename=eType+'\\mean'+stimunit+'_combined.html',auto_open=False)
plotly.plotly.image.save_as(fig_meanAmp, filename=eType+'\\mean'+stimunit+'_combined.pdf')
plotly.plotly.image.save_as(fig_meanAmp, filename=eType+'\\mean'+stimunit+'_combined.png')

# plotly.offline.plot(fig_numCh, filename=eType+'\\perDRG\\numChans_perSub.html',auto_open=False)
# plotly.plotly.image.save_as(fig_numCh, filename=eType+'\\numChans_perSub.pdf')
# plotly.plotly.image.save_as(fig_numCh, filename=eType+'\\numChans_perSub.png')

# plotly.offline.plot(fig_meanA, filename=eType+'\\perDRG\\mean'+stimunit+'_perSub.html',auto_open=False)
# plotly.plotly.image.save_as(fig_meanA, filename=eType+'\\mean'+stimunit+'_perSub.pdf')
# plotly.plotly.image.save_as(fig_meanA, filename=eType+'\\mean'+stimunit+'_perSub.png')

print 'finished'


