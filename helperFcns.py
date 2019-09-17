import pymongo
import matplotlib
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import collections
import plotly.graph_objs as go
import pandas as pd
from igraph import *
import matplotlib.pyplot as plt

plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42

# constants
mongohost = "192.168.0.246"
mongoport = 15213
collection = 'selectivity'

# instantiate the mongo client
client = pymongo.MongoClient(mongohost, mongoport)
# get handle to database
db = client.acute

# expt constants
allDRG = ['DRG - L5','DRG - L6','DRG - L7'] # 'DRG - S1'

TDT_fs = 24414.0

# cuff dbName:label
allCuffs_mdf = collections.OrderedDict([('Sciatic_Proximal','Sci'),
                                        ('Tibial','Tib'),
                                        ('Lat_Gas','LG'),
                                        ('Med_Gas','MG'),
                                        ('Dist_Tib','dTib'),
                                        ('Cmn_Per','CP'),
                                        ('Dist_Cmn_Per','dCP'),
                                        ('Dist_Cmn_Per_2','dCP2'),
                                        ('L_D_Cmn_Per','SP'),
                                        ('M_D_Cmn_Per','DP'),
                                        ('BiFem','BF'),
                                        ('Sural','Sur'),
                                        ('Lat_Cut','LC'),
                                        ('Med_Cut','MC'),
                                        ('Sens_Branch','Sensory'),
                                        ('Femoral_Proximal', 'Fem'),
                                        ('Saph', 'Sph'),
                                        ('VLat', 'VL'),
                                        ('VMed', 'VM'),
                                        ('Sart', 'Srt'),
                                        ])

ENG_graphOrder =['Femoral_Proximal',
                 'Femoral_Distal',
                 'Saph',
                 'Sart',
                 'VLat',
                 'VMed',
                 'Sciatic_Proximal',
                 'Sciatic_Distal',
                 'Tibial',
                 'Med_Gas',
                 'Lat_Gas',
                 'Dist_Tib',
                 'Cmn_Per',
                 'Dist_Cmn_Per',
                 'Sens_Branch']

maxTreeDepth = 4

combineCuffs = {'Sural':'Sens_Branch',
                'Lat_Cut':'Sens_Branch',
                'Med_Cut':'Sens_Branch',
                'Sens_Branch':'Sens_Branch',
                'Dist_Cmn_Per':'Dist_Cmn_Per',
                'Dist_Cmn_Per_2':'Dist_Cmn_Per',
                'L_D_Cmn_Per':'Dist_Cmn_Per',
                'M_D_Cmn_Per':'Dist_Cmn_Per'}

agonists = {'VMed':'VLat',
            'VLat':'VMed',
            'Med_Gas':'Lat_Gas',
            'Lat_Gas':'Med_Gas'}

# usec obtained from MATLAB snippet:
# for i = [6, 7, 10, 12, 14, 16, 20, 23]
#     asd = mdf.load('subject','Hobgoblin','mdf_type','trial','session',i);
#     disp(asd(1).md.location)
#     asd(1).stimChan.stimWform(1).data~=0
# end
PWbySession = {'Electro':{20:204.8, 22:204.8, 26:204.8, 27:204.8, 28:204.8, 32:204.8},
               'Freeze':{55:204.8, 56:204.8, 59:204.8, 60:204.8, 61:204.8, 63:204.8, 68:204.8, 999:204.8},
                'Galactus':{15:204.8, 30:81.92, 40:81.92, 41:81.92, 48:81.92, 57:81.92,
                           91:81.92, 94:81.92, 97:81.92, 98:81.92},
                'Hobgoblin':{6:81.92, 7:81.92, 10:81.92, 12:81.92, 14:81.92, 16:81.92, 20:81.92, 23:81.92,
                             47:81.92, 49:81.92, 52:81.92},
                'HA02':{2:204.8, 3:204.8, 4:204.8},
                'HA04':{2:80, 3:80, 4:80}}

binarySearchResolutionbySession = {'Electro':{20:1, 22:1, 26:1, 27:1, 28:1, 32:1},
                'Freeze':{55:1, 56:1, 59:1, 60:1, 61:1, 63:1, 68:1, 999:1},
                'Galactus':{15:1, 30:1, 40:1, 41:10, 48:10, 57:10,
                           91:1, 94:1.5, 97:1.5, 98:5},
                'Hobgoblin':{6:5, 7:5, 10:5, 12:5, 14:5, 16:5, 20:5, 23:5,
                             47:3, 49:3, 52:3},
                'HA02':{2:5, 3:5, 4:5},
                'HA04':{2:5, 3:5, 4:5}}

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

# animal:DRG(session):channel(block):amp:cuff:cv
def thresholdPerCuff(sub, session, ignoreCuffList, combine, stimUnits='amplitude'):
    ignoreCuffList.extend(['Sciatic_Distal','Femoral_Distal'])
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_def.mdf_type": 'recruitment',
                # "mdf_metadata.is_sig": 1,
                # "mdf_metadata.is_sig_manual": {"$in":[1, None]},
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": session,
                "mdf_metadata.location":{"$nin":ignoreCuffList}
            }},
            {"$group": {
                "_id": {"cuff": "$mdf_metadata.location",
                        "stimChan": "$mdf_metadata.stimChan",
                        'is_sig':'$mdf_metadata.is_sig',
                        'is_sig_manual':'$mdf_metadata.is_sig_manual'},
                "threshAmp": {"$min": "$mdf_metadata.amplitude"}
            }},
            {"$project": {
                "_id": 0,
                'sig':"$_id.is_sig",
                'sig_manual':"$_id.is_sig_manual",
                "stimChan": "$_id.stimChan",
                "cuff": "$_id.cuff",
                "threshAmp": "$threshAmp",
            }}]})

    thresholdDict = {}
    if len(result1['result']) != 0:
            for entry in result1['result']:
                if ('sig_manual' in entry.keys() and entry['sig_manual'] == 1) or ('sig_manual' not in entry.keys() and entry['sig'] == 1):
                    thresholdDict.setdefault(entry['stimChan'], {})
                    # if not(entry['cuff'] in ['Sciatic_Distal', 'Femoral_Distal']):
                    if stimUnits =='charge':
                        stimVal = convertCurrentToCharge(entry['threshAmp'],sub, session)
                    else:
                        stimVal = entry['threshAmp']

                    if entry['cuff'] in combineCuffs.keys():
                        if combine:
                            combinedKey = combineCuffs[entry['cuff']]
                            thresholdDict[entry['stimChan']].setdefault(combinedKey, 999)
                            tmp = [thresholdDict[entry['stimChan']][combinedKey]]
                            tmp.append(stimVal)
                            thresholdDict[entry['stimChan']][combinedKey] = min(tmp)
                        else:
                            # in case sig_manual is 1 sig is 1 is greater than sig manual =1 and sig =0, the threshold will be overwritten to a higher value
                            thresholdDict[entry['stimChan']].setdefault([entry['cuff']],999)
                            tmp = thresholdDict[entry['stimChan']][entry['cuff']]
                            thresholdDict[entry['stimChan']][entry['cuff']] = min(tmp, stimVal)
                            thresholdDict[entry['stimChan']][entry['cuff']] = stimVal
                    else:
                        thresholdDict[entry['stimChan']].setdefault(entry['cuff'], 999)
                        tmp = thresholdDict[entry['stimChan']][entry['cuff']]
                        thresholdDict[entry['stimChan']][entry['cuff']] = min(tmp, stimVal)
                        # thresholdDict[entry['stimChan']][entry['cuff']] = stimVal

    return thresholdDict

def maxAmplitudePerSession(sub, session):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": session,
                "mdf_def.mdf_type": 'recruitment',
            }},
            {"$group": {
                "_id": {},
                "threshAmp": {"$max": "$mdf_metadata.amplitude"},
            }},
        ]})
    return result1['result'][0]['threshAmp']


def getAllElectrodes():
    return db[collection].find().distinct('mdf_metadata.electrode')

def getAllDRG():
    return db[collection].find({'mdf_def.mdf_type': 'trial'}).distinct('mdf_metadata.location')

def sessionPerDRG(subject, eType):         # need to filter for selectivity vs threshold session

    if eType == 'penetrating':
        matchDict = {
            "mdf_def.mdf_type": 'trial',
            "mdf_metadata.success": 1,
            "mdf_metadata.memo": {"$regex": 'Selectivity'},
            "mdf_metadata.electrode": {"$regex": 'FMA|Utah'},
            "mdf_metadata.subject": subject,
            "mdf_metadata.location":{"$in":allDRG}
        }
    elif eType == 'epineural':
        matchDict = {
            "mdf_def.mdf_type": 'trial',
            "mdf_metadata.success": 1,
            "mdf_metadata.memo": {"$regex": 'Selectivity'},
            "mdf_metadata.electrode": {"$regex": 'Ripple'},
            "mdf_metadata.subject": subject,
            "mdf_metadata.location":{"$in":allDRG}
        }
    else:
        raise Exception('invalid electrode type')

    if subject == 'HA04':
        outDict =  {'DRG - L5': [2],
                    'DRG - L6': [3],
                    'DRG - L7': [4]}
    else:
        result1 = db.command({
            'aggregate': collection,
            'pipeline': [
                {'$match': matchDict},
                {"$group": {
                    "_id": {"DRG": "$mdf_metadata.location"},
                    "session": {"$addToSet": "$mdf_metadata.session"},
                }},
                {"$project": {
                    "_id": 0,
                    "DRG": "$_id.DRG",
                    "session": "$session"
                }}]})
        outDict = {}
        for iRes in result1['result']:
            outDict[iRes['DRG']] = iRes['session']

    return outDict


def convertCurrentToCharge(amplitude_uA, sub, sesh):
    return np.ceil((amplitude_uA*1e-6*PWbySession[sub][sesh]* 1e-6*1e9)*1000)/1000   # ensure 2 decimal places


def getSurveyAmplitude(subj, sesh):
    if subj == 'HA02':
        sesh = 1
    if subj == 'HA04':
        return 350
    else:
        memoField = db[collection].find({"mdf_def.mdf_type": 'trial', "mdf_metadata.subject": subj, "mdf_metadata.session": sesh,'mdf_metadata.memo':{'$regex':'survey'}},
            {"mdf_metadata.memo": 1})
        if memoField.count():
            return int(memoField[0]['mdf_metadata']['memo'].split()[-2])
        else:
            memoField2 = db[collection].find({"mdf_def.mdf_type": 'recruitment', "mdf_metadata.subject": subj, "mdf_metadata.session": 27},{"_id": 0, "mdf_metadata.amplitude": 1}).distinct("mdf_metadata.amplitude")
            return np.ceil(max(list(memoField2)))



def getBinarySearchParams(subject, eType):
    allSesh = sum(sessionPerDRG(subject, eType).values(),[])

    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_def.mdf_type": 'recruitment',
                "mdf_metadata.subject": subject,
                "mdf_metadata.session":{"$in":allSesh}
            }},
            {"$group": {
                "_id": {"sesh":"$mdf_metadata.session", "chan":"$mdf_metadata.stimChan","DRG":"$mdf_metadata.DRG"},
                "stimAmp": { "$addToSet": "$mdf_metadata.amplitude"},
            }},
            {"$project": {
                "_id": 0,
                "DRG": "$_id.DRG",
                "sesh": "$_id.sesh",
                "chan": "$_id.chan",
                "stimAmp": "$stimAmp"
            }}
            ]})
    resolutionVal = {}
    if eType == 'epineural':
        resolutionVal['totalElecs'] = len(allSesh)*4
    else:
        resolutionVal['totalElecs'] = len(allSesh) *32
    for iRes in result1['result']:
        if len(iRes['stimAmp'])>1:
            resolution_amp_uA = binarySearchResolutionbySession[subject][iRes['sesh']]  #np.min(np.diff(sorted(iRes['stimAmp'])))
            resolutionVal.setdefault(iRes['DRG'],[]).append( convertCurrentToCharge(resolution_amp_uA, subject, iRes['sesh']) )
            resolutionVal[iRes['DRG']] = list(set(resolutionVal[iRes['DRG']]))

            survey_amp_uA = getSurveyAmplitude(subject, iRes['sesh'])
            # print iRes['sesh'], iRes['chan'], survey_amp_uA
            resolutionVal.setdefault('surveyCharge', []).append(convertCurrentToCharge(survey_amp_uA, subject, iRes['sesh']))
            resolutionVal['surveyCharge'] = list(set(resolutionVal['surveyCharge']))


    return resolutionVal



def getSingleAmplitudeChannels(subject, sesh):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_metadata.subject": subject,
                "mdf_metadata.session": sesh,   #{'$in': [20, 22, 26, 27, 28, 32]},
                "mdf_def.mdf_type": 'recruitment',
            }},
            {"$group": {
                "_id": {"stimChan": "$mdf_metadata.stimChan"},  #, 'sesh': "$mdf_metadata.session"},
                "threshAmp": {"$addToSet": "$mdf_metadata.amplitude"},
            }},
        ]})

    seshChanDict = []
    for i in sorted(result1['result']):
        if len(i['threshAmp']) == 1:
            # seshChanDict.setdefault([i['_id']['sesh']],[]).append(i['_id']['stimChan'])
            seshChanDict.append(i['_id']['stimChan'])

    return seshChanDict


def getAllCuffs(subList):
    return db[collection].find({'mdf_def.mdf_type': 'ENGdata', "mdf_metadata.subject": {"$in": subList}}).distinct(
        'mdf_metadata.location')
    # res1 = db.command({
    #         'aggregate' : collection,
    #         'pipeline' : [
    #           {'$match' : {
    #              "mdf_def.mdf_type":'ENGdata',
    #               "mdf_metadata.subject": {"$in": subList}
    #             }},
    #           {"$group": {
    #               "_id": {"id": "1"},
    #                "nerves":{"$addToSet": "$mdf_metadata.location"}
    #           }}
    #           ]})

    # implantedCuffs = [i['nerve'] for i in res1['result']]
    # return res1['result'][0]['nerves']


def cuffsPerSubject(subList):
    if not isinstance(subList, list):
        subList = [subList]

    res1 = {}
    for iSub in subList:
        res1[iSub] = db[collection].find({"mdf_metadata.subject": iSub, "mdf_def.mdf_type": 'ENGdata'}).distinct(
            'mdf_metadata.location')

    return res1



## Innervation Tree related
def getInnervationParents(): # getCanonicalInnervation
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
    innervationDict[''] = ['Femoral_Proximal', 'Sciatic_Proximal']


    return innervationDict


def getInnervationTreeCoords():
    coords = {}
    coords['Sciatic_Proximal'] = [3.6, 4.0]
    coords['Cmn_Per'] = [7.9, 3.0]
    coords['Tibial'] = [5.4, 3.0]
    coords['BiFem'] = [4.4, 3.0]
    coords['Sural'] = [3.4, 3.0]
    coords['Sens_Branch'] = [2.4, 3.0]
    coords['Med_Cut'] = [1.4, 3.0]
    coords['Lat_Cut'] = [0.4, 3.0]
    coords['Dist_Cmn_Per'] = [8.4, 2.0]
    coords['Dist_Cmn_Per_2'] = [7.4, 2.0]
    coords['L_D_Cmn_Per'] = [8.9, 1.0]
    coords['M_D_Cmn_Per'] = [7.9, 1.0]
    coords['Med_Gas'] = [6.4, 2.0]
    coords['Lat_Gas'] = [5.5, 2.0]
    coords['Dist_Tib'] = [4.4, 2.0]
    coords['Femoral_Proximal'] = [-2.3, 4.0]
    coords['Saph'] = [-0.8, 3.0]
    coords['VMed'] = [-1.8, 3.0]
    coords['VLat'] = [-2.8, 3.0]
    coords['Sart'] = [-3.8, 3.0]

    return coords


def generateInnervationTree(resultCuffs, nodeColor, nodeSize=40, stimUnits='amplitude', eType='epineural'):

    cuffParentsDict = getInnervationParents()
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

    if isinstance(nodeColor, list):
        hoverText = ['%s, c%0.1f' % (allCuffs_mdf[x], y) for x,y in zip(resultCuffs,nodeColor)]
    elif isinstance(nodeSize, list):
        hoverText = ['%s, c%0.1f' % (allCuffs_mdf[x], y) for x,y in zip(resultCuffs,nodeSize)]
    else:
        hoverText = []

    if stimUnits == 'charge':
        if eType == 'epineural':
            colorMap = [9,26]
        else:
            colorMap = [1,6] #[6, 1]
    else:                               # current
        if eType == 'epineural':
            colorMap = [300, 0]
        else:
            colorMap = [40, 0]

    lines = go.Scatter(x=Xe,
                       y=Ye,
                       mode='lines',
                       line=dict(color='rgb(210,210,210)', width=1),
                       hoverinfo='none'
                       )
    dots = go.Scatter(x=Xn,
                      y=Yn,
                      mode='markers',
                      marker=dict(size=nodeSize,
                                  color=nodeColor,  # '#DB4551',
                                  cmin=colorMap[0], cmax=colorMap[1],
                                  line=dict(color='rgb(50,50,50)', width=1),
                                  colorscale=magma,
                                  # colorscale=[[0, 'rgb(49,54,149)'],  # 0
                                  #               [0.0005, 'rgb(69,117,180)'],  # 10
                                  #               [0.005, 'rgb(116,173,209)'],  # 100
                                  #               [0.05, 'rgb(171,217,233)'],  # 1000
                                  #               [0.5, 'rgb(224,243,248)'],
                                  #               [0.75, 'rgb(215,48,39)'],# 10000
                                  #               [1.0, 'rgb(165,0,38)'],  # 100000
                                  #               ],
                                  colorbar=dict(thickness=20)
                                  ),
                      text=hoverText,
                      hoverinfo='text',
                      opacity=1
                      )

    layout = dict(title='Innervation tree',
                  font=dict(size=12),
                  showlegend=False,
                  xaxis=dict(range=[-5, 10], showline=False, zeroline=True, showgrid=False, showticklabels=False, ),
                  yaxis=dict(range=[1.5, 4.5], showline=False, zeroline=True, showgrid=True, showticklabels=False, ),
                  margin=dict(l=40, r=40, b=85, t=100),
                  hovermode='closest',
                  plot_bgcolor='rgb(248,248,248)'
                  )

    data = [lines, dots]
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

def createMagmaCMAP():
    magma_cmap = matplotlib.cm.get_cmap('magma')
    magma_rgb = []
    norm = matplotlib.colors.Normalize(vmin=0, vmax=255)

    for i in range(0, 255):
        k = matplotlib.colors.colorConverter.to_rgb(magma_cmap(norm(i)))
        magma_rgb.append(k)

    h = 1.0 / (255 - 1)
    pl_colorscale = []

    for k in range(255):
        C = map(np.uint8, np.array(magma_cmap(k * h)[:3]) * 255)
        pl_colorscale.append([k * h, 'rgb' + str((C[0], C[1], C[2]))])

    return pl_colorscale
magma = createMagmaCMAP()


## needed to get sessions and uuid per subject per eType for validation
def getRecruitmentUUIDforValidation(subject, etype):
    tmp = sessionPerDRG(subject, etype) #sessionPerElectrodeType(subject)
    seshByEtype = sum(list(tmp.values()), [])

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


def getCVperAmp(sub, session, nerve, stimunit):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": {'$in':session},
                "mdf_metadata.location": nerve,
                "mdf_def.mdf_type": 'CV',
                "mdf_metadata.is_sig_manual": {"$in":[1, None]},
            }},
            {"$group": {
                "_id": {"amp": "$mdf_metadata.amplitude","sesh":"$mdf_metadata.session"},
                "cv": {"$push":"$mdf_metadata.cv"},
                "drg": {"$addToSet": "$mdf_metadata.DRG"},          # since im requesting per DRG, i dont have to worry about push vs add to set. this will always be the same drg
                # "sesh": {"$push": "$mdf_metadata.session"},
            }},
            {"$project": {
                "_id": 0,
                "AMP": "$_id.amp",
                "CV": "$cv",
                "DRG": "$drg",
                "sesh":"$_id.sesh"
            }}]})

    tmpDict = {'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[]}
    for iRes in result1['result']:
        if stimunit == 'charge':
            stimVal = convertCurrentToCharge(iRes['AMP'],sub,iRes['sesh'])
        else:
            stimVal = iRes['AMP']
        tmp = iRes['CV']
        if tmp and not ('999' in tmp):
            if type(tmp) == list:
                CVlist = list(set(flatten(tmp))) # [max(set(flatten(tmp)))] #
            else:
                CVlist = list(set(tmp))
            # outDict.setdefault(iRes['AMP'], []).extend(CVlist)
            numCV=len(CVlist)
            tmpDict['Conduction Velocity'].extend(CVlist)
            tmpDict['Stimulation Amplitude'].extend([stimVal]*numCV)
            tmpDict['Subject'].extend([sub] * numCV)
            tmpDict['DRG'].extend(iRes['DRG']*numCV)
            tmpDict['Threshold'] = 'all'
            tmpDict['session'] = iRes['sesh']

    outDF = pd.DataFrame.from_dict(tmpDict)
    return outDF


def getCVatThresh(sub, session, nerve,stimunit):
    result1 = db.command({
        'aggregate': collection,
        'pipeline': [
            {'$match': {
                "mdf_metadata.subject": sub,
                "mdf_metadata.session": {'$in':session},
                # "mdf_metadata.DRG": DRG,
                "mdf_metadata.location": nerve,
                "mdf_def.mdf_type": 'CV',
                "mdf_metadata.is_sig_manual": {"$in":[1, None]},
            }},
            {"$group": {
                "_id": {"stimChan": "$mdf_metadata.stimChan",'sesh':"$mdf_metadata.session"},
                "threshAmp": {"$min": "$mdf_metadata.amplitude"},
                "drg": {"$addToSet": "$mdf_metadata.DRG"},
            }},
    ]})

    outDict = {'Stimulation Amplitude':[], 'Conduction Velocity':[],'Subject':[],'DRG':[]}
    for iVal in result1['result']:
        tmp = db[collection].distinct("mdf_metadata.cv", {"mdf_metadata.subject": sub,
                                    "mdf_metadata.session": iVal['_id']['sesh'],
                                    # "mdf_metadata.DRG": DRG,
                                    "mdf_metadata.location": nerve,
                                    "mdf_def.mdf_type": 'CV',
                                    "mdf_metadata.is_sig_manual": {"$in":[1, None]},
                                    "mdf_metadata.stimChan":iVal['_id']['stimChan'],
                                    "mdf_metadata.amplitude": {"$lte":iVal['threshAmp'] + 1, "$gte": iVal['threshAmp'] - 1},
                                                          })
        if tmp and not('999' in tmp):

            if stimunit == 'charge':
                stimVal = convertCurrentToCharge(iVal['threshAmp'], sub, iVal['_id']['sesh'])
            else:
                stimVal = iVal['threshAmp']

            if type(tmp) == list:
                # CVlist = [max(set(flatten(tmp)))]
                CVlist = list(set(flatten(tmp)))
            else:
                CVlist = list(set(tmp))

            numCV = len(CVlist)

            outDict['Conduction Velocity'].extend(CVlist)
            outDict['Stimulation Amplitude'].extend([stimVal]*numCV)
            outDict['Subject'].extend([sub] * numCV)
            outDict['DRG'].extend(iVal['drg'] * numCV)
            outDict['Threshold'] = 'thresh'
            outDict['session'] = iVal['_id']['sesh']

    outDF = pd.DataFrame.from_dict(outDict)
    return outDF
