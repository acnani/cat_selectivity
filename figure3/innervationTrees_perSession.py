# outputs one innervation tree html file per session per subject for number of channels activating a cuff

import plotly
import os
from plotly import tools
import helperFcns as hf

eType = 'penetrating'
collapseCuffs = True       # to avoid combining cuffs OR to ignore parent but not child (eg ignore Sensory but not Sural)

allDRG = hf.allDRG
subjectList = hf.getSubjects(eType)

allCuffs = hf.allCuffs_mdf.keys()

subDict = {}
for subject in subjectList:
    seshDict = {}

    # returns all sessions per DRG per subject
    res2 = hf.sessionPerDRG(subject)
    res3 = hf.sessionPerElectrodeType(subject)

    # iterate over each DRG
    for iDRG in res2['result']:
        if iDRG['DRG'] in allDRG:
            allEtypeSesh = res3[eType]
            targetSesh = sorted([value for value in allEtypeSesh if value in iDRG['session']])

            # iterate over each session
            for sesh in targetSesh:
                threshDict = hf.thresholdPerCuff(subject, sesh, allCuffs, collapseCuffs)
                allActiveChans = sorted(threshDict.keys())
                numActiveChans = len(allActiveChans)

                if numActiveChans != 0:
                    fig = tools.make_subplots(rows=numActiveChans, cols=1, subplot_titles=allActiveChans)
                    subplotRow = 0

                    # iterate over each stim channel
                    for iChan in allActiveChans:
                        if bool(threshDict[iChan]):

                            subplotRow = subplotRow+1
                            resultCuffs = threshDict[iChan].keys()
                            allAmps = [threshDict[iChan][cuffName] for cuffName in resultCuffs]

                            figDict = hf.generateInnervationTree(resultCuffs, allAmps, 25)

                            [fig.append_trace(iData, subplotRow, 1) for iData in figDict['data']]
                            fig['layout']['showlegend'] = False
                            for iAnnot in range(len(resultCuffs)):
                                figDict['layout']['annotations'][iAnnot]['xref'] = 'x'+str(subplotRow)
                                figDict['layout']['annotations'][iAnnot]['yref'] = 'y'+str(subplotRow)
                            fig['layout']['annotations'].extend(figDict['layout']['annotations'])
                            fig['layout']['xaxis'+str(subplotRow)].update(figDict['layout']['xaxis'])
                            fig['layout']['yaxis'+str(subplotRow)].update(figDict['layout']['yaxis'])

                    if bool(fig['data']):           # if threshDict[iChan] for all chnnels is empty
                        fig['layout'].update(height = 600*numActiveChans, )
                        plotly.offline.plot(fig, filename='innervationTrees_perSession\\%s\\%s_%s_sesh%03d.html' %(eType, subject, iDRG['DRG'], sesh),auto_open=False)
