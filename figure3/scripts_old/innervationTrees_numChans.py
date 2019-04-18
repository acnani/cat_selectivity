import plotly
import plotly.graph_objs as go
from plotly import tools
import numpy as np
import helperFcns as hf


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

normFactor = []
for subject in subjectList:
    seshDict = {}

    # returns all sessions per DRG per subject
    res2 = hf.sessionPerDRG(subject)                       # add arguemnt for penetrating vs epineural

    # iterate over each DRG
    for iDRG in res2['result']:
        if iDRG['DRG'] in allDRG:

            # iterate over each session
            for sesh in sorted(iDRG['session']):
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

                    normFactor.append(max([numChanDict[iDRG['DRG']][cuff] for cuff in cuffDict]))


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
plotly.offline.plot(fig, filename='finalFigs\\numChans_hMap_byDRG.html')


# by subject
fig = tools.make_subplots(rows=len(subjectList), cols=1, subplot_titles=subjectList)
for iPlot in range(len(subjectList)):
    trace = go.Heatmap(z=np.transpose(hMap[iPlot,:,:]), y=allDRG,x=allCuffs)
    fig.append_trace(trace, iPlot+1, 1)

fig['layout'].update(height = 600*3, )
plotly.offline.plot(fig, filename='finalFigs\\numChans_hMap_bysubject.html')




# # create innervation trees --> this is buggy
fig = tools.make_subplots(rows=len(subjectList), cols=4)

row = 0
div = float(max(normFactor))
for sub in subjectList:
    row = row + 1
    col = 1
    for DRG in allDRG:
        graphEdges = []

        if div == 0:
            nodeSize = [0 for cuff in cuffDict]
        else:
            nodeSize = [numChanDict[sub][DRG][cuff]/div*100 for cuff in cuffDict]

        figDict = hf.generateInnervationTree(numChanDict[sub][DRG].keys(), nodeSize, hf.colorOrder[col])

        # for cuffName in numChanDict[sub][DRG].keys():
        #     allCuffs = cuffParentsDict.keys()
        #     if cuffName in cuffParentsDict.keys():
        #         parent = cuffParentsDict[cuffName]
        #         if parent != '':
        #             graphEdges.append([allCuffs.index(parent), allCuffs.index(cuffName)])
        #
        #
        # G = Graph()
        # allChildCuffs = cuffParentsDict.keys()
        # G.add_vertices(len(allCuffs))
        # G.add_edges(graphEdges)
        # print G
        #
        # lay = [cuffCoord[iCuff] for iCuff in allCuffs]
        # nr_vertices = len(allCuffs)
        # v_label = allCuffs
        #
        # position = {k: lay[k] for k in range(nr_vertices)}
        # Y = [lay[k][1] for k in range(nr_vertices)]
        # M = max(Y)
        #
        # es = EdgeSeq(G) # sequence of edges
        # E = [e.tuple for e in G.es] # list of edges
        #
        # L = len(position)
        # Xn = [position[k][0] for k in range(L)]
        # Yn = [2*M-position[k][1] for k in range(L)]
        # Xe = []
        # Ye = []
        # for edge in E:
        #     Xe+=[position[edge[0]][0],position[edge[1]][0], None]
        #     Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]
        #
        # labels = v_label
        #
        # lines = go.Scatter(x=Xe,
        #                    y=Ye,
        #                    mode='lines',
        #                    line=dict(color='rgb(210,210,210)', width=10),
        #                    hoverinfo='none'
        #                    )

        # dots = go.Scatter(x=Xn,
        #                   y=Yn,
        #                   mode='markers',
        #                   # name='',
        #                   marker=dict(symbol='dot',
        #                                 size=markSize,
        #                                 color=[],    #'#DB4551',
        #                                 line=dict(color='rgb(50,50,50)', width=1),
        #                                 colorscale='RdBu',
        #                                 ),
        #                   text=labels,
        #                   hoverinfo='text',
        #                   opacity=1
        #                   )
        #
        #
        # for cuff in cuffDict:
        #     node_info = '%0.1f' % ( numChanDict[sub][DRG][cuff])
        #     dots['text'][cuffDict.index(cuff)] = str(node_info)

        [fig.append_trace(iData, 1, col + 1) for iData in figDict['data']]
        fig['layout']['showlegend'] = False
        for iAnnot in range(len(nodeSize)):
            figDict['layout']['annotations'][iAnnot]['xref'] = 'x' + str(col + 1)
            figDict['layout']['annotations'][iAnnot]['yref'] = 'y' + str(col + 1)
        fig['layout']['annotations'].extend(figDict['layout']['annotations'])
        fig['layout']['xaxis' + str(col + 1)].update(figDict['layout']['xaxis'])
        fig['layout']['yaxis' + str(col + 1)].update(figDict['layout']['yaxis'])
        col = col + 1




if bool(fig['data']):  # if threshDict[iChan] for all chnnels is empty
    fig['layout'].update(height=600 * len(subjectList), width = 6000)
    plotly.offline.plot(fig, filename='finalFigs\\numChanInnervationTrees.html')


print 'asd'


