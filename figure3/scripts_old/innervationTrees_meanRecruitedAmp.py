# this creates the patch heatmaps and the innervation trees for mean recruited amplitude

# TO DO dort by epineural vs penetrating

import pymongo
from helperFcns import thresholdPerCuff, getInnervationTreeCoords, getCanonicalInnervation, sessionPerDRG, sessionPerElectrodeType
import plotly
import plotly.graph_objs as go
from igraph import *
from plotly import tools
import numpy as np
import yaml

# constants
mongohost = "192.168.0.246"
mongoport = 15213
collection = 'selectivity'

# instantiate the mongo client
client = pymongo.MongoClient(mongohost, mongoport)
# get handle to database
db = client.acute


cuffParentsDict = getCanonicalInnervation()
cuffCoord = getInnervationTreeCoords()
allCuffs = ['Femoral_Proximal','Saph','VMed','VLat','Sart','Lat_Fem','Med_Fem','Mid_Fem',
             'Sciatic_Proximal','Cmn_Per','Dist_Cmn_Per','Dist_Cmn_Per_2','L_D_Cmn_Per','M_D_Cmn_Per',
                       'Tibial','Med_Gas','Lat_Gas','Dist_Tib',
                       'BiFem', 'Sural', 'Lat_Cut', 'Med_Cut', 'Sens_Branch',]

subjectList = ['Electro','Freeze','Galactus','Hobgoblin','HA02','HA04']
allDRG = ['DRG - L5','DRG - L6','DRG - L7', 'DRG - S1']

# meanAmpDict = dict.fromkeys(subjectList)
# for subject in subjectList:
#     meanAmpDict[subject] = {}
#     for DRG in allDRG:
#         meanAmpDict[subject][DRG] = {}
#         for cuff in allCuffs:
#             meanAmpDict[subject][DRG][cuff] = []
#
#
# for subject in subjectList:
#     seshDict = {}
#
#     # returns all sessions per DRG per subject
#     res2 = sessionPerDRG(subject)                       # add arguemnt for penetrating vs epineural
#
#     # iterate over each DRG
#     for iDRG in res2['result']:
#         if iDRG['DRG'] in allDRG:
#
#             # iterate over each session
#             for sesh in sorted(iDRG['session']):
#                 threshDict = thresholdPerCuff(subject, sesh)
#                 allActiveChans = sorted(threshDict.keys())
#                 numActiveChans = len(allActiveChans)
#
#                 if numActiveChans != 0:
#
#                     for iChan in allActiveChans:
#                         if bool(threshDict[iChan]):
#                             resultCuffs = threshDict[iChan].keys()
#                             allAmps = [threshDict[iChan][cuffName] for cuffName in resultCuffs]
#                             recruitmentThresh = min(allAmps)
#
#                             if [recruitmentThresh] == list(set(allAmps)):
#                                 print 'same threshold: possibly high amp survey'
#                             else:
#                                 for cuffName in resultCuffs:
#                                     meanAmpDict[subject][iDRG['DRG']][cuffName].append(threshDict[iChan][cuffName])
#
#
# with open ('meanAmpDict.yml', 'w') as meanDict:
#     yaml.safe_dump(meanAmpDict,meanDict)

with open ('meanAmpDict.yml', 'r') as meanDict:
    meanAmpDict = yaml.load(meanDict)


# create heatmap
hMap = np.zeros((len(subjectList),len(allCuffs),len(allDRG)))
for sub in subjectList:
    for DRG in allDRG:
        for cuffName in meanAmpDict[sub][DRG].keys():
            hMap[subjectList.index(sub), allCuffs.index(cuffName), allDRG.index(DRG)] = mean(meanAmpDict[sub][DRG][cuffName])

## by level
fig = tools.make_subplots(rows=len(allDRG), cols=1, subplot_titles=allDRG)
for iPlot in range(4):
    trace = go.Heatmap(z=hMap[:,:,iPlot], y=subjectList,x=allCuffs,showscale=False)
    fig.append_trace(trace, iPlot+1, 1)

fig['layout'].update(height = 600*3)
plotly.offline.plot(fig, filename='finalFigs\meanThresholds_hMap_byDRG.html')


## by subject
fig = tools.make_subplots(rows=len(subjectList), cols=1, subplot_titles=subjectList)
for iPlot in range(len(subjectList)):
    trace = go.Heatmap(z=np.transpose(hMap[iPlot,:,:]), y=allDRG,x=allCuffs,showscale=False)
    fig.append_trace(trace, iPlot+1, 1)

fig['layout'].update(height = 600*3)
plotly.offline.plot(fig, filename='finalFigs\meanThresholds_hMap_bysubject.html')

# # create innervation trees --> this is buggy
fig = tools.make_subplots(rows=len(subjectList), cols=4)

row = 0
for sub in subjectList:
    row = row + 1
    col = 1
    for DRG in allDRG:
        graphEdges = []

        for cuffName in meanAmpDict[sub][DRG].keys():
            allCuffs = cuffParentsDict.keys()
            if cuffName in cuffParentsDict.keys():
                parent = cuffParentsDict[cuffName]
                if parent != '':
                    graphEdges.append([allCuffs.index(parent), allCuffs.index(cuffName)])


        G = Graph()
        allChildCuffs = cuffParentsDict.keys()
        G.add_vertices(len(allCuffs))
        G.add_edges(graphEdges)
        print G

        lay = [cuffCoord[iCuff] for iCuff in allCuffs]
        nr_vertices = len(allCuffs)
        v_label = allCuffs

        position = {k: lay[k] for k in range(nr_vertices)}
        Y = [lay[k][1] for k in range(nr_vertices)]
        M = max(Y)

        es = EdgeSeq(G) # sequence of edges
        E = [e.tuple for e in G.es] # list of edges

        L = len(position)
        Xn = [position[k][0] for k in range(L)]
        Yn = [2*M-position[k][1] for k in range(L)]
        Xe = []
        Ye = []
        for edge in E:
            Xe+=[position[edge[0]][0],position[edge[1]][0], None]
            Ye+=[2*M-position[edge[0]][1],2*M-position[edge[1]][1], None]

        labels = v_label

        lines = go.Scatter(x=Xe,
                           y=Ye,
                           mode='lines',
                           line=dict(color='rgb(210,210,210)', width=1),
                           hoverinfo='none'
                           )
        dots = go.Scatter(x=Xn,
                          y=Yn,
                          mode='markers',
                          # name='',
                          marker=dict(symbol='dot',
                                        size=30,
                                        color=[],    #'#DB4551',
                                        line=dict(color='rgb(50,50,50)', width=1),
                                        colorscale='RdBu',
                                        ),
                          text=labels,
                          hoverinfo='text',
                          opacity=1
                          )
        cuffDict = cuffParentsDict.keys()
        for cuff in cuffDict:
            dots['marker']['color'].append(str(mean(meanAmpDict[sub][DRG][cuff])))
            node_info = '%0.1f' % ( mean(meanAmpDict[sub][DRG][cuff]))
            dots['text'][cuffDict.index(cuff)] = str(node_info)

        print row, col
        fig.append_trace(lines, row, col)
        fig.append_trace(dots, row, col)
        fig['layout']['showlegend'] = False
        fig['layout']['xaxis' + str(row)].update(showgrid=False, showticklabels=False, range=[-10, 7])
        fig['layout']['yaxis' + str(col)].update(showticklabels=False, range=[2, 8])
        col =  col+1




if bool(fig['data']):  # if threshDict[iChan] for all chnnels is empty
    fig['layout'].update(height=600 * len(subjectList), width = 3000)
    plotly.offline.plot(fig, filename='finalFigs\meanAmpInnervationTrees.html')


print 'asd'


