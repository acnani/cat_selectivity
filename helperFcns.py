import pymongo
import matplotlib
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import collections
import plotly.graph_objs as go
from igraph import *

# constants
mongohost = "192.168.0.246"
mongoport = 15213
collection = 'selectivity'

# instantiate the mongo client
client = pymongo.MongoClient(mongohost, mongoport)
# get handle to database
db = client.acute

# expt constants
allDRG = ['DRG - L5','DRG - L6','DRG - L7', 'DRG - S1']
# cuff dbName:label
allCuffs_mdf = collections.OrderedDict([('Femoral_Proximal','Fem'), ('Saph','Sph'), ('VMed','VM'), ('VLat','VL'), ('Sart','Srt'),
                                        ('Sciatic_Proximal','Sci'),('Tibial','Tib'),('Med_Gas','MG'),('Lat_Gas','LG'),('Dist_Tib','dTib'),
                                            ('Cmn_Per','CP'),('Dist_Cmn_Per','dCP'),('Dist_Cmn_Per_2','dCP2'),('L_D_Cmn_Per','SP'),('M_D_Cmn_Per','DP'),
                                            ('BiFem','BF'), ('Sural','Sur'), ('Lat_Cut','LC'), ('Med_Cut','MC'), ('Sens_Branch','Sensory'),])

maxTreeDepth = 4

combineCuffs = {'Sural':'Sens_Branch', 'Lat_Cut':'Sens_Branch', 'Med_Cut':'Sens_Branch', 'Sens_Branch':'Sens_Branch',
                'Dist_Cmn_Per':'Dist_Cmn_Per', 'Dist_Cmn_Per_2':'Dist_Cmn_Per', 'L_D_Cmn_Per':'Dist_Cmn_Per', 'M_D_Cmn_Per':'Dist_Cmn_Per'}

epineuralSessions = {'Galactus':[15, 30, 40, 41, 48, 57],
                     'Hobgoblin':[6, 7, 10, 12, 14, 16, 20, 23],
                     'HA02':[2, 3, 4],
                     'HA04':[2, 3, 4]}

penetratingSessions = {'Electro':[20, 22, 26, 27, 28, 32],
                       'Freeze':[55, 56, 59, 60, 61, 63, 68, 999],
                       'Galactus':[91, 94, 97, 98],
                       'Hobgoblin':[47, 49, 52]}

def getSubjects(eType):
    if eType == 'epineural':
        return ['Galactus','Hobgoblin','HA02','HA04']
    elif eType == 'penetrating':
        return ['Electro','Freeze','Galactus','Hobgoblin']
    else:
        return ['Electro','Freeze','Galactus','Hobgoblin','HA02','HA04']


def thresholdPerCuff(sub, session, targetCuffs, combine):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_def.mdf_type": 'recruitment',
                "mdf_metadata.is_sig": 1,
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": session,
                "mdf_metadata.location":{"$in":targetCuffs}
            }},
            {"$group": {
                "_id": {"cuff": "$mdf_metadata.location",
                        "stimChan": "$mdf_metadata.stimChan"},
                "threshAmp": {"$min": "$mdf_metadata.amplitude"}
            }},
            {"$project": {
                "_id": 0,
                "stimChan": "$_id.stimChan",
                "cuff": "$_id.cuff",
                "threshAmp": "$threshAmp"
            }}]})

    thresholdDict = {}
    if len(result1['result']) != 0:
        for entry in result1['result']:
            thresholdDict.setdefault(entry['stimChan'], {})
            if not(entry['cuff'] in ['Sciatic_Distal', 'Femoral_Distal']):
                if entry['cuff'] in combineCuffs.keys():
                    if combine:
                        combinedKey = combineCuffs[entry['cuff']]
                        thresholdDict[entry['stimChan']].setdefault(combinedKey, [])
                        tmp = [thresholdDict[entry['stimChan']][combinedKey]]
                        tmp.append(entry['threshAmp'])
                        # if tmp[0]:
                        #     print 'chut'
                        thresholdDict[entry['stimChan']][combinedKey] = min(tmp)
                    else:
                        thresholdDict[entry['stimChan']][entry['cuff']] = entry['threshAmp']
                else:
                    thresholdDict[entry['stimChan']][entry['cuff']] = entry['threshAmp']

    return thresholdDict


def sessionPerDRG(subject):         # need to filter for selectivity vs threshold session
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_def.mdf_type": 'recruitment',
                # "mdf_metadata.success": 1,
                "mdf_metadata.subject": subject
            }},
            {"$group": {
                "_id": {"DRG": "$mdf_metadata.DRG"},
                "session": {"$addToSet": "$mdf_metadata.session"},
            }},
            {"$project": {
                "_id": 0,
                "DRG": "$_id.DRG",
                "session": "$session"
            }}]})
    return result1


def sessionPerElectrodeType(subject):
    seshByElec = {}
    if subject == 'HA04':                           # import did not include electrode type.
        seshByElec['epineural'] = [2,3,4]
        return seshByElec
    else:
        res2 = db.command({
                'aggregate' : collection,
                'pipeline' : [
                  {'$match' : {
                      "mdf_def.mdf_type":'trial',
                      "mdf_metadata.success":1,
                      "mdf_metadata.subject": subject,
                    }},
                  {"$group": {
                      "_id": {"subject":"$mdf_metadata.subject", "electrodeType":"$mdf_metadata.electrode"},
                      "sessions": { "$push": "$mdf_metadata.session"},
                      "memo": {"$push": "$mdf_metadata.memo"}
                  }},
                  {"$project": {
                      "_id": 0,
                      "subject": "$_id.subject",
                      "electrodeType": "$_id.electrodeType",
                      "sessions": "$sessions",
                      "memo": "$memo"
                  }}]})

        # this is filthy...i should use unwind and regex in the aggregation pipeline
        for entry in res2['result']:
            if 'electrodeType' in entry.keys():
                if 'Utah' in entry['electrodeType'] or 'FMA' in entry['electrodeType']:
                    for memoidx in range(len(entry['memo'])):
                        memoLine = entry['memo'][memoidx]
                        if 'Selectivity' in memoLine:
                            seshByElec.setdefault('penetrating',[]).append(entry['sessions'][memoidx])
                    seshByElec['penetrating'] = list(set(seshByElec['penetrating']))

                elif 'Ripple' in entry['electrodeType']:
                    for memoidx in range(len(entry['memo'])):
                        memoLine = entry['memo'][memoidx]
                        if 'Selectivity' in memoLine:
                            seshByElec.setdefault('epineural',[]).append(entry['sessions'][memoidx])
                    seshByElec['epineural'] = list(set(seshByElec['epineural']))

        return seshByElec


def getAllCuffs(subList):
    res1 = db.command({
            'aggregate' : collection,
            'pipeline' : [
              {'$match' : {
                 "mdf_def.mdf_type":'ENGdata',
                  "mdf_metadata.subject": {"$in": subList}
                }},
              {"$group": {
                  "_id": {"id": "1"},
                   "nerves":{"$addToSet": "$mdf_metadata.location"}
              }},
            {"$project": {
                "_id": 0,
                "nerve": "$nerves",
                # "count": "$count"
            }}
              ]})

    # implantedCuffs = [i['nerve'] for i in res1['result']]
    return res1['result'][0]['nerve']


def cuffsPerSubject(subList):
    if not isinstance(subList, list):
        subList = [subList]

    res1 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'ENGdata',
              "mdf_metadata.subject": {"$in": subList}
            }},
          {"$group": {
              "_id": {"sub": "$mdf_metadata.subject"},
              "nerves":{"$addToSet": "$mdf_metadata.location"}
          }},
          {"$project": {
              "_id": 0,
              "subject": "$_id.sub",
              "nerve": "$nerves",
              # "count": "$count"
          }}]})

    # implantedCuffs = [i['nerve'] for i in res1['result']]
    return res1['result']





## Innervation Tree related
def getCanonicalInnervation():
    innervationDict  = {}
    innervationDict['Sciatic_Proximal']= ''
    innervationDict['Cmn_Per']= 'Sciatic_Proximal'
    innervationDict['Tibial'] = 'Sciatic_Proximal'
    innervationDict['BiFem'] = 'Sciatic_Proximal'
    innervationDict['Sural']= 'Sciatic_Proximal'
    innervationDict['Lat_Cut'] = 'Sciatic_Proximal'
    innervationDict['Med_Cut']= 'Sciatic_Proximal'
    innervationDict['Sens_Branch']= 'Sciatic_Proximal'
    innervationDict['Dist_Cmn_Per'] = 'Cmn_Per'
    innervationDict['Dist_Cmn_Per_2']= 'Cmn_Per'
    innervationDict['L_D_Cmn_Per']= 'Dist_Cmn_Per'
    innervationDict['M_D_Cmn_Per']= 'Dist_Cmn_Per'
    innervationDict['Med_Gas']= 'Tibial'
    innervationDict['Lat_Gas']= 'Tibial'
    innervationDict['Dist_Tib']= 'Tibial'
    innervationDict['Femoral_Proximal'] = ''
    innervationDict['Saph']= 'Femoral_Proximal'
    innervationDict['VMed']= 'Femoral_Proximal'
    innervationDict['VLat']= 'Femoral_Proximal'
    innervationDict['Sart'] = 'Femoral_Proximal'
    # innervationDict['Lat_Fem']= ''
    # innervationDict['Med_Fem']= ''
    # innervationDict['Mid_Fem']= ''

    return innervationDict


def getInnervationChildren():
    innervationDict  = {}
    innervationDict['Sciatic_Proximal']= ['Cmn_Per', 'Tibial', 'BiFem','Sural','Lat_Cut','Med_Cut','Sens_Branch']
    innervationDict['Cmn_Per'] = ['Dist_Cmn_Per', 'Dist_Cmn_Per_2']
    innervationDict['Dist_Cmn_Per'] = ['L_D_Cmn_Per', 'M_D_Cmn_Per']
    innervationDict['Tibial']= ['Med_Gas', 'Lat_Gas', 'Dist_Tib']
    innervationDict['Femoral_Proximal'] = ['Saph', 'VMed', 'VLat', 'Sart']


    return innervationDict


def getInnervationTreeCoords():
    coords = {}
    coords['Sciatic_Proximal'] = [3.6, 4.0]
    coords['Cmn_Per'] = [7.9, 3.0]
    coords['Tibial'] = [5.4, 3.0]
    coords['BiFem'] = [4.4, 3.0]
    coords['Sural'] = [3.4, 3.0]
    coords['Lat_Cut'] = [2.4, 3.0]
    coords['Med_Cut'] = [1.4, 3.0]
    coords['Sens_Branch'] = [0.4, 3.0]
    coords['Dist_Cmn_Per'] = [8.4, 2.0]
    coords['Dist_Cmn_Per_2'] = [7.4, 2.0]
    coords['L_D_Cmn_Per'] = [8.9, 1.0]
    coords['M_D_Cmn_Per'] = [7.9, 1.0]
    coords['Med_Gas'] = [6.4, 2.0]
    coords['Lat_Gas'] = [5.4, 2.0]
    coords['Dist_Tib'] = [4.4, 2.0]
    coords['Femoral_Proximal'] = [-2.3, 4.0]
    coords['Saph'] = [-0.8, 3.0]
    coords['VMed'] = [-1.8, 3.0]
    coords['VLat'] = [-2.8, 3.0]
    coords['Sart'] = [-3.8, 3.0]

    return coords


def generateInnervationTree(resultCuffs, nodeColor, nodeSize=40, showAnnots=True):

    cuffParentsDict = getCanonicalInnervation()
    graphEdges = []
    for cuffName in resultCuffs:
        if cuffName in cuffParentsDict.keys():
            parent = cuffParentsDict[cuffName]
            if parent != '':
                if parent in resultCuffs:
                    graphEdges.append([resultCuffs.index(parent), resultCuffs.index(cuffName)])

    cuffCoord = getInnervationTreeCoords()
    lay = [cuffCoord[iCuff] for iCuff in resultCuffs]

    G = Graph()
    G.add_vertices(len(resultCuffs))
    G.add_edges(graphEdges)
    E = [e.tuple for e in G.es]  # list of edges
    L = len(lay)
    Xn = [lay[k][0] for k in range(L)]
    Yn = [lay[k][1] for k in range(L)]
    Xe = []
    Ye = []
    for edge in E:
        Xe += [lay[edge[0]][0], lay[edge[1]][0], None]
        Ye += [lay[edge[0]][1], lay[edge[1]][1], None]

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
                                  size=nodeSize,
                                  color=nodeColor,  # '#DB4551',
                                  line=dict(color='rgb(50,50,50)', width=1),
                                  colorscale='RdBu',
                                  ),
                      text=[allCuffs_mdf[x] for x in resultCuffs],
                      hoverinfo='text',
                      opacity=1
                      )

    for node in range(len(resultCuffs)):
        node_info = '%s' %dots['text'][node]

        if isinstance(nodeColor, list):
            node_info += ', c%0.1f' % nodeColor[node]

        if isinstance(nodeSize, list):
            node_info += ', s%0.1f' % nodeSize[node]

        dots['text'][node] = str(node_info)



    annotations = go.Annotations()             # text within circle
    if showAnnots:
        for k in range(L):
            annotations.append(
                go.Annotation(
                    text=allCuffs_mdf[resultCuffs[k]],
                    x=lay[k][0],
                    y=lay[k][1],
                    font=dict(color='rgb(250,250,250)', size=10),
                    showarrow=False))

    layout = dict(title='Innervation tree',
                  annotations=annotations,
                  font=dict(size=12),
                  showlegend=False,
                  xaxis=go.XAxis(dict(showline=False,zeroline=True,showgrid=False,showticklabels=False, range=[-5,10])),
                  yaxis=go.YAxis(dict(showline=False,zeroline=True,showgrid=True,showticklabels=False, range=[0.5,5])),
                  margin=dict(l=40, r=40, b=85, t=100),
                  hovermode='closest',
                  plot_bgcolor='rgb(248,248,248)'
                  )

    data = go.Data([lines, dots])
    fig = dict(data=data, layout=layout)

    return fig



## create heatmap colormap
def createParulaCMAP():
    cm_data = [[0.2081, 0.1663, 0.5292], [0.2116238095, 0.1897809524, 0.5776761905],
               [0.212252381, 0.2137714286, 0.6269714286], [0.2081, 0.2386, 0.6770857143],
               [0.1959047619, 0.2644571429, 0.7279], [0.1707285714, 0.2919380952,
                                                      0.779247619], [0.1252714286, 0.3242428571, 0.8302714286],
               [0.0591333333, 0.3598333333, 0.8683333333], [0.0116952381, 0.3875095238,
                                                            0.8819571429], [0.0059571429, 0.4086142857, 0.8828428571],
               [0.0165142857, 0.4266, 0.8786333333], [0.032852381, 0.4430428571,
                                                      0.8719571429], [0.0498142857, 0.4585714286, 0.8640571429],
               [0.0629333333, 0.4736904762, 0.8554380952], [0.0722666667, 0.4886666667,
                                                            0.8467], [0.0779428571, 0.5039857143, 0.8383714286],
               [0.079347619, 0.5200238095, 0.8311809524], [0.0749428571, 0.5375428571,
                                                           0.8262714286], [0.0640571429, 0.5569857143, 0.8239571429],
               [0.0487714286, 0.5772238095, 0.8228285714], [0.0343428571, 0.5965809524,
                                                            0.819852381], [0.0265, 0.6137, 0.8135],
               [0.0238904762, 0.6286619048,
                0.8037619048], [0.0230904762, 0.6417857143, 0.7912666667],
               [0.0227714286, 0.6534857143, 0.7767571429], [0.0266619048, 0.6641952381,
                                                            0.7607190476], [0.0383714286, 0.6742714286, 0.743552381],
               [0.0589714286, 0.6837571429, 0.7253857143],
               [0.0843, 0.6928333333, 0.7061666667], [0.1132952381, 0.7015, 0.6858571429],
               [0.1452714286, 0.7097571429, 0.6646285714], [0.1801333333, 0.7176571429,
                                                            0.6424333333], [0.2178285714, 0.7250428571, 0.6192619048],
               [0.2586428571, 0.7317142857, 0.5954285714], [0.3021714286, 0.7376047619,
                                                            0.5711857143], [0.3481666667, 0.7424333333, 0.5472666667],
               [0.3952571429, 0.7459, 0.5244428571], [0.4420095238, 0.7480809524,
                                                      0.5033142857], [0.4871238095, 0.7490619048, 0.4839761905],
               [0.5300285714, 0.7491142857, 0.4661142857], [0.5708571429, 0.7485190476,
                                                            0.4493904762], [0.609852381, 0.7473142857, 0.4336857143],
               [0.6473, 0.7456, 0.4188], [0.6834190476, 0.7434761905, 0.4044333333],
               [0.7184095238, 0.7411333333, 0.3904761905],
               [0.7524857143, 0.7384, 0.3768142857], [0.7858428571, 0.7355666667,
                                                      0.3632714286], [0.8185047619, 0.7327333333, 0.3497904762],
               [0.8506571429, 0.7299, 0.3360285714], [0.8824333333, 0.7274333333, 0.3217],
               [0.9139333333, 0.7257857143, 0.3062761905], [0.9449571429, 0.7261142857,
                                                            0.2886428571], [0.9738952381, 0.7313952381, 0.266647619],
               [0.9937714286, 0.7454571429, 0.240347619], [0.9990428571, 0.7653142857,
                                                           0.2164142857], [0.9955333333, 0.7860571429, 0.196652381],
               [0.988, 0.8066, 0.1793666667], [0.9788571429, 0.8271428571, 0.1633142857],
               [0.9697, 0.8481380952, 0.147452381], [0.9625857143, 0.8705142857, 0.1309],
               [0.9588714286, 0.8949, 0.1132428571], [0.9598238095, 0.9218333333,
                                                      0.0948380952], [0.9661, 0.9514428571, 0.0755333333],
               [0.9763, 0.9831, 0.0538]]
    parula_map = LinearSegmentedColormap.from_list('parula', cm_data)
    parula_rgb = []
    norm = matplotlib.colors.Normalize(vmin=0, vmax=255)
    for i in range(0, 255):
        k = matplotlib.colors.colorConverter.to_rgb(parula_map(norm(i)))
        parula_rgb.append(k)

    h = 1.0/(255-1)
    pl_colorscale = []

    for k in range(255):
        C = map(np.uint8, np.array(parula_map(k*h)[:3])*255)
        pl_colorscale.append([k*h, 'rgb'+str((C[0], C[1], C[2]))])

    return pl_colorscale
parula = createParulaCMAP()
colorOrder = ['rgba(31,119,180,1)', 'rgba(255,127,14,1)', 'rgba(44,160,44,1)', 'rgba(214,30,30,1)']


## needed to get sessions and uuid per subject per eType for validation
def getRecruitmentUUIDforValidation(subject, etype):
    seshByEtype = sessionPerElectrodeType(subject)
    res2 = db.command({
            'aggregate' : collection,
            'pipeline' : [
              {'$match' : {
                  "mdf_def.mdf_type":'recruitment',
                  "mdf_metadata.subject": subject,
                  "mdf_metadata.session":{'$in': seshByEtype[etype]},
                  "mdf_metadata.is_sig_manual": {'$exists': 0}
                }},
              {"$group": {
                  "_id": {"subject":"$mdf_metadata.subject"},
                  "stimAmp": { "$push": "$mdf_metadata.amplitude"},
                  "recruitObj":{ "$push": "$mdf_def.mdf_uuid"}
              }},
              {"$project": {
                  "_id": 0,
                  "stimAmp": "$stimAmp",
                  "objUUID": "$recruitObj",
              }}]})
    if len(res2['result']):
        print '%s has %d recruitment objects that need validation for %s electrodes'  %(subject, len(res2['result'][0]['stimAmp']),etype)
    else:
        print 'all subjects validated'


# animal:DRG(session):channel(block):amp:cuff:cv
def CVPerAmplitude(sub, session):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_def.mdf_type": 'CV',
                # "mdf_metadata.is_sig": 1,
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": session
            }},
            {"$group": {
                "_id": {"cuff": "$mdf_metadata.location",
                        "stimChan": "$mdf_metadata.stimChan"},
                "threshAmp": {"$push": "$mdf_metadata.amplitude"},
                "CV": {"$push": "$mdf_metadata.cv"}
            }},
            {"$project": {
                "_id": 0,
                "stimChan": "$_id.stimChan",
                "cuff": "$_id.cuff",
                "threshAmp": "$threshAmp",
                "CV": "$CV"
            }}]})

    thresholdDict = {}      # thresholdDict[23]['Sciatic'][amps]
                            #                             [CVs]
                            #                  ['Distal']

    if len(result1['result']) != 0:
        for entry in result1['result']:
            thresholdDict.setdefault(entry['stimChan'], {})

            amplitudes = []
            condVels = []
            for (amp, CV) in zip(entry['threshAmp'], entry['CV']):
                if type(CV) == list:
                    amplitudes.extend([amp] * len(CV))
                    condVels.extend(CV)
                else:
                    amplitudes.extend([amp])
                    condVels.append(CV)
            thresholdDict[entry['stimChan']].setdefault(entry['cuff'], {'amps': [], 'CV': []})
            thresholdDict[entry['stimChan']][entry['cuff']]['amps'].append(amplitudes)
            thresholdDict[entry['stimChan']][entry['cuff']]['CV'].append(condVels)

    return thresholdDict


def flatten(l):
    flatList = []
    for elem in l:
        # if an element of a list is a list
        # iterate over this list and add elements to flatList
        if type(elem) == list:
            for e in elem:
                if e != '999' and e!=0:
                    flatList.append(np.ceil(e))
        else:
            if elem != '999' and elem!=0:
                flatList.append(np.ceil(elem))
    return flatList


def getCVperAmp(sub, session, nerve,DRG):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": {'$in':session},
                "mdf_metadata.DRG": DRG,
                "mdf_metadata.location": nerve,
                "mdf_def.mdf_type": 'CV',
                "mdf_metadata.is_sig_manual": 1,
            }},
            {"$group": {
                "_id": {"amp": "$mdf_metadata.amplitude"},
                "cv": {"$push":{"$max":"$mdf_metadata.cv"}},
                # "cv": {"$push": "$mdf_metadata.cv"},
            }},
            {"$project": {
                "_id": 0,
                "AMP": "$_id.amp",
                "CV": "$cv"
            }}]})

    outDict = {}
    for iRes in result1['result']:
        tmp = iRes['CV']
        if type(tmp) == list:
            CVlist = flatten(tmp)
        else:
            CVlist = tmp
        outDict.setdefault(iRes['AMP'], []).extend(CVlist)

    return outDict


def getCVatThresh(sub, session, nerve,DRG):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": {'$in':session},
                "mdf_metadata.DRG": DRG,
                "mdf_metadata.location": nerve,
                "mdf_def.mdf_type": 'CV',
                "mdf_metadata.is_sig_manual": 1,
            }},
            {"$group": {
                "_id": {"stimChan": "$mdf_metadata.stimChan"},
                "threshAmp": {"$min": "$mdf_metadata.amplitude"}
            }},
    ]})

    outDict = {}
    for iVal in result1['result']:
        tmp = db[collection].distinct("mdf_metadata.cv", {"mdf_metadata.subject": sub,
                                    "mdf_metadata.session": {'$in':session},
                                    "mdf_metadata.DRG": DRG,
                                    "mdf_metadata.location": nerve,
                                    "mdf_def.mdf_type": 'CV',
                                    "mdf_metadata.is_sig_manual": 1,
                                    "mdf_metadata.stimChan":iVal['_id']['stimChan'],
                                    "mdf_metadata.amplitude": {"$lt":iVal['threshAmp'] + 0.01},
                                    "mdf_metadata.amplitude": {"$gt":iVal['threshAmp'] - 0.01},
                                  })
        if tmp and not('999' in tmp):
            if type(tmp) == list:
                CVlist = [max(flatten(tmp))]
            else:
                CVlist = tmp
            outDict.setdefault(iVal['threshAmp'], []).extend(CVlist)

    return outDict