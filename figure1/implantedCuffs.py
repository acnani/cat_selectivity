import plotly
import plotly.graph_objs as go
import pymongo
import yaml
import numpy as np
import helperFcns as hf
import plotly.io as pio

eType = 'epineural'
subjectList = hf.getSubjects(eType)
cuffPerSub = hf.cuffsPerSubject(subjectList)
cuffLabels = hf.allCuffs_mdf.keys()
cuffNames = [hf.allCuffs_mdf[iKey] for iKey in hf.allCuffs_mdf.keys()]

hMap = np.ones((len(subjectList),len(cuffLabels)))
for sub in cuffPerSub:
    rowIdx = subjectList.index(sub['subject'])
    subNerveList = sub['nerve']
    hMap[rowIdx, [i for i, x in enumerate(cuffLabels) if x in subNerveList]] = 0

hMap[:,cuffLabels.index('Sciatic_Proximal')] = 0
hMap[:,cuffLabels.index('Femoral_Proximal')] = 0

colIdx = sum(hMap) != len(cuffPerSub)
cuffList = [cuffNames[i] for i in np.where(colIdx)[0]]
hMap = hMap[:,colIdx]

trace = go.Heatmap(z=hMap, y=subjectList,x=cuffList,colorscale='Greys')
data=[trace]
fig = go.Figure()
fig.add_heatmap(z=hMap, y=subjectList,x=cuffList,colorscale='Greys')
# plotly.offline.plot(data, filename='implantedCuffs_'+eType+'.html',auto_open=True)
pio.write_image(fig, 'implantedCuffs_'+eType+'.svg')