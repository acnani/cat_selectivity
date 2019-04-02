import helperFcns as hf
import plotly
import plotly.graph_objs as go
import numpy as np
from plotly import tools

eType = 'epineural'
collapseCuffs = True       # to avoid combining cuffs OR to ignore parent but not child (eg ignore Sensory but not Sural)
ignoreCuffs = ['BiFem']

cuffChildrenDict = hf.getInnervationChildren()
cuffParentsDict = hf.getCanonicalInnervation()
cuffCoord = hf.getInnervationTreeCoords()
colorList = hf.colorOrder
allDRG = hf.allDRG

subjectList = hf.getSubjects(eType)
etypeCuffs = hf.getAllCuffs(subjectList)
allCuffs = [i for i in hf.allCuffs_mdf if i in etypeCuffs]       # remove distal contact
targetCuffs = [x for x in allCuffs if x not in ignoreCuffs]      # remove ignore cuffs. keep collapse cuff since we want to request these thresholds

if collapseCuffs:
    ignoreCuffs.extend([x for x in hf.combineCuffs.keys() if x != hf.combineCuffs[x]])

validCuffs = [i for i in targetCuffs if i not in ignoreCuffs]    # cuff names after combining


selectiveBarCount = np.zeros((len(validCuffs),1))
nonSelectiveBarCount = np.zeros((len(validCuffs),1))

data_selec = []
data_nonSelec = []
allLevels_data_selec = np.zeros((len(validCuffs), 1))
allLevels_data_nonselec = np.zeros((len(validCuffs), 1))
coactivationMat = np.zeros((len(validCuffs), len(validCuffs)))

fig = tools.make_subplots(rows=2, cols=1, subplot_titles=['selective counts per DRG','total selective counts'])
fig2 = tools.make_subplots(rows=2, cols=1, subplot_titles=['non-selective counts per DRG','total non-selective counts'])

for iDRG in allDRG:
    selectiveBarCount = np.zeros((len(validCuffs), 1))
    nonSelectiveBarCount = np.zeros((len(validCuffs), 1))

    coactivationMat_perDRG = np.zeros((len(validCuffs), len(validCuffs)))

    for subject in subjectList:
        # returns all sessions per DRG per subject
        res2 = hf.sessionPerDRG(subject)  # add arguemnt for penetrating vs epineural
        res3 = hf.sessionPerElectrodeType(subject)
        DRGidx = [res2['result'].index(val) for val in res2['result'] if iDRG == val['DRG']]

        if len(DRGidx) != 0:
            if eType in res3.keys():
                allEtypeSesh = res3[eType]
                targetSesh = sorted([value for value in allEtypeSesh if value in res2['result'][DRGidx[0]]['session']])
                # iterate over each session
                for sesh in targetSesh:
                    threshDict = hf.thresholdPerCuff(subject, sesh, targetCuffs, collapseCuffs)
                    allActiveChans = sorted(threshDict.keys())
                    numActiveChans = len(allActiveChans)

                    for iStimChan in allActiveChans:
                        stimChanDict = threshDict[iStimChan]
                        allRecruitedCuffs = stimChanDict.keys()
                        for iActiveCuff in allRecruitedCuffs:
                            activeChanIdx = validCuffs.index(iActiveCuff)         # row
                            activeChanAmp = stimChanDict[iActiveCuff]

                            coactivatedCuffIdx = [validCuffs.index(val) for val in allRecruitedCuffs if stimChanDict[val] <= activeChanAmp]   # allow counting iActiveCuff so that diagonal is unity
                            coactivationMat[activeChanIdx, coactivatedCuffIdx] += 1
                            coactivationMat_perDRG[activeChanIdx, coactivatedCuffIdx] += 1

                            coactivatedCuffs = [val for val in allRecruitedCuffs if stimChanDict[val] <= activeChanAmp and val !=iActiveCuff]

                            # check if parent nerve of active nerve is coactivated
                            cuffParent = [cuffParentsDict[iActiveCuff]]                 # list of all parents of the active cuff up to the trunk
                            if cuffParent[0] != '':
                                cuffParent.append(cuffParentsDict[cuffParent[0]])
                            notParentCoactive = [value for value in coactivatedCuffs if value not in cuffParent]        # non-parent nerves that are coactivated with the active cuff

                            # check if active nerve has a child and whether it is coactivated
                            if iActiveCuff in cuffChildrenDict.keys():
                                cuffChild = cuffChildrenDict[iActiveCuff]
                                notChild = [value for value in notParentCoactive if value not in cuffChild]
                                notParentCoactive = notChild

                            if len(notParentCoactive)==0:
                                selectiveBarCount[activeChanIdx] += 1

                            else:
                                nonSelectiveBarCount[activeChanIdx] += 1

    trace1 = go.Bar(y=np.ndarray.tolist(np.transpose(selectiveBarCount))[0], x=validCuffs, name=iDRG, legendgroup = iDRG, marker={'color':colorList[allDRG.index(iDRG)]})
    trace2 = go.Bar(y=np.ndarray.tolist(np.transpose(nonSelectiveBarCount))[0], x=validCuffs, name=iDRG, legendgroup = iDRG, marker={'color':colorList[allDRG.index(iDRG)]})
    fig.append_trace(trace1, 1, 1)
    fig2.append_trace(trace2, 1, 1)

    allLevels_data_selec += selectiveBarCount
    allLevels_data_nonselec += nonSelectiveBarCount

    normVal2 = np.transpose(np.tile(np.max(coactivationMat_perDRG, 0), (len(validCuffs), 1)))
    hMapMat2 = np.flipud(np.divide(coactivationMat_perDRG, 1) * 100)
    data2 = [go.Heatmap(z=hMapMat2, y=list(reversed(validCuffs)), x=validCuffs, colorscale=hf.parula)]
    plotly.offline.plot({'data':data2, 'layout':go.Layout(title=eType + ' ' + iDRG + ' coactivation matrix')}, filename=eType + '_' + iDRG +'_coactivationMat_.html', auto_open=True)

layout = go.Layout(barmode='group')

fig.append_trace(go.Bar(y=np.ndarray.tolist(np.transpose(allLevels_data_selec))[0], x=validCuffs, name='selec', showlegend = False), 2, 1)
fig2.append_trace(go.Bar(y=np.ndarray.tolist(np.transpose(allLevels_data_nonselec))[0], x=validCuffs, name='nonselec', showlegend = False), 2, 1)

plotly.offline.plot(fig, layout, filename= eType +'_selective_counts_.html')
plotly.offline.plot(fig2, layout, filename= eType +'_nonselective_counts_.html')


normVal = np.transpose(np.tile(np.max(coactivationMat,0),(len(validCuffs),1)))
hMapMat = np.flipud(np.divide(coactivationMat,normVal)*100)

data = [go.Heatmap(z=hMapMat, y=list(reversed(validCuffs)),x=validCuffs,colorscale=hf.parula)]
plotly.offline.plot({'data':data, 'layout':go.Layout(title=eType+' coactivation matrix')},filename=eType+'_combo_coactivationMat.html',auto_open=True)

