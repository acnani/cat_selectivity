import helperFcns as hf
import seaborn as sns
import numpy as np
import pandas as pd
from helperFcns import plt
sns.set(style="white", color_codes=True)
from itertools import chain
import scipy

eType = 'penetrating'
stimUnits = 'charge'

# f, violinAx = plt.subplots(1, 2, figsize=(14, 5))
cvList = []
i=0
for eType in ['penetrating','epineural']:
    subjectList = hf.getSubjects(eType)
    for nerve in ['Femoral', 'Sciatic']:
        for iSub in subjectList:
            seshPerDRG = hf.sessionPerDRG(iSub, eType)
            allSessions = sum(seshPerDRG.values(),[])

            for iSesh in allSessions:
                res = hf.db.command({
                    'aggregate': hf.collection,
                    'pipeline': [
                        {'$match': {
                            "mdf_metadata.subject": iSub,
                            "mdf_metadata.session": iSesh,
                            "mdf_metadata.location": nerve,
                            "mdf_def.mdf_type": 'CV',
                            "mdf_metadata.is_sig_manual": {"$in": [1, None]},
                        }},
                        {"$group": {
                            "_id": {"stimChan": "$mdf_metadata.stimChan"},
                            "threshAmp": {"$min": "$mdf_metadata.amplitude"},
                        }},
                        {'$project':{
                            '_id':0,
                            'chan':'$_id.stimChan',
                            'thresh':'$threshAmp'
                        }}
                    ]})

                for iChan in res['result']:
                    res2 = hf.db.command({
                        'aggregate': hf.collection,
                        'pipeline': [
                            {'$match': {
                                "mdf_metadata.subject": iSub,
                                "mdf_metadata.session": iSesh,
                                "mdf_metadata.location": nerve,
                                'mdf_metadata.stimChan':iChan['chan'],
                                "mdf_def.mdf_type": 'CV',
                                "mdf_metadata.cv":{'$ne':'999'},
                                "mdf_metadata.is_sig_manual": {"$in": [1, None]},
                            }},
                            {"$group": {
                                "_id": {"amp": "$mdf_metadata.amplitude"},
                                "CV": {"$push": "$mdf_metadata.cv"},
                                "thresh":{'$addToSet':iChan['thresh']}
                            }},
                            {'$project': {
                                '_id': 0,
                                'amp': '$_id.amp',
                                'thresh':'$thresh',
                                'CV': '$CV'
                            }}
                        ]})


                    for iRes in res2['result']:
                        tmp = {}
                        # l = [0, 2, (1, 2), 5, 2, (3, 5)]
                        # list(chain(*(i if isinstance(i, list) else (i,) for i in l)))
                        if isinstance(iRes['CV'][-1], list):
                            allCV = list(chain(*(i if isinstance(i, list) else (i,) for i in iRes['CV']))) #sum(iRes['CV'],[])
                            numCV = len(allCV) #len(sum(iRes['CV'],[]))
                        else:
                            allCV = iRes['CV']
                            numCV = len(iRes['CV'])
                        for iCV in allCV:
                            if iCV != 0:
                                tmp = {}
                                tmp['CV'] = np.ceil(iCV)
                                tmp['CVidx'] = [120, 80, 60, 48, 40, 35, 30].index(np.ceil(iCV))
                                tmp['threshX'] = iRes['amp']/float(iRes['thresh'][0])
                                tmp['stimAmp'] = iRes['amp']
                                tmp['stimCharge'] = hf.convertCurrentToCharge(iRes['amp'],iSub, iSesh)
                                tmp['eType'] = eType
                                tmp['nerve'] = nerve
                                tmp['subject'] = iSub
                                tmp['session'] = iSesh
                                if tmp['threshX'] == 1:
                                    tmp['type'] = 'thresh'
                                else:
                                    tmp['type'] = 'supra'

                                cvList.append(tmp)

CVdf = pd.DataFrame(list(reversed(cvList)))


f, violinAx = plt.subplots(2,2,figsize=(14, 10))
sns.boxplot(data=CVdf[(CVdf['eType']=='epineural') & (CVdf['nerve']=='Femoral')], x='stimCharge', y='CV',orient='h',hue='type',order=[120, 80, 60, 48, 40, 35, 30],linewidth=1,ax=violinAx[0][0])
sns.boxplot(data=CVdf[(CVdf['eType']=='epineural') & (CVdf['nerve']=='Sciatic')], x='stimCharge', y='CV',orient='h',hue='type',order=[120, 80, 60, 48, 40, 35, 30],linewidth=1,ax=violinAx[0][1])
violinAx[0][0].set_xlim([-2, 70])
violinAx[0][1].set_xlim([-2, 70])
sns.boxplot(data=CVdf[(CVdf['eType']=='penetrating') & (CVdf['nerve']=='Femoral')], x='stimCharge', y='CV',orient='h',hue='type',order=[120, 80, 60, 48, 40, 35, 30],linewidth=1,ax=violinAx[1][0])
sns.boxplot(data=CVdf[(CVdf['eType']=='penetrating') & (CVdf['nerve']=='Sciatic')], x='stimCharge', y='CV',orient='h',hue='type', order=[120, 80, 60, 48, 40, 35, 30],linewidth=1,ax=violinAx[1][1])
violinAx[1][0].set_xlim([-0.5, 10])
violinAx[1][1].set_xlim([-0.5, 10])

# sns.swarmplot(data=CVdf[(CVdf['eType']=='epineural') & (CVdf['nerve']=='Femoral')], x='stimCharge', y='CV',orient='h',order=[120, 80, 60, 48, 40, 35, 30],linewidth=0,size=2,ax=violinAx[0][0],color='k')
# sns.swarmplot(data=CVdf[(CVdf['eType']=='epineural') & (CVdf['nerve']=='Sciatic')], x='stimCharge', y='CV',orient='h',order=[120, 80, 60, 48, 40, 35, 30],linewidth=0,size=2,ax=violinAx[0][1],color='k')
# sns.swarmplot(data=CVdf[(CVdf['eType']=='penetrating') & (CVdf['nerve']=='Femoral') & (CVdf['threshX']!=1)], x='stimCharge', y='CV',orient='h',order=[120, 80, 60, 48, 40, 35, 30],linewidth=0,size=2,ax=violinAx[1][0],color='k')
# sns.swarmplot(data=CVdf[(CVdf['eType']=='penetrating') & (CVdf['nerve']=='Sciatic') & (CVdf['threshX']!=1)], x='stimCharge', y='CV',orient='h',order=[120, 80, 60, 48, 40, 35, 30],linewidth=0,size=2,ax=violinAx[1][1],color='k')


f.savefig("CV_violinPlot.png")
f.savefig("CV_violinPlot.svg")

CVdf.to_csv('conductionVelDF.csv')

tmp = CVdf[(CVdf['eType']=='epineural') & (CVdf['type']=='thresh') &( (CVdf['nerve']=='Femoral'))]
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(tmp['stimCharge'],tmp['CV'])
print slope, r_value**2, p_value

tmp = CVdf[(CVdf['eType']=='epineural') & (CVdf['type']=='thresh') &( (CVdf['nerve']=='Sciatic'))]
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(tmp['stimCharge'],tmp['CV'])
print slope, r_value**2, p_value


tmp = CVdf[(CVdf['eType']=='penetrating') & (CVdf['type']=='thresh') &( (CVdf['nerve']=='Femoral'))]
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(tmp['stimCharge'],tmp['CV'])
print slope, r_value**2, p_value

tmp = CVdf[(CVdf['eType']=='penetrating') & (CVdf['type']=='thresh') &( (CVdf['nerve']=='Sciatic'))]
slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(tmp['stimCharge'],tmp['CV'])
print slope, r_value**2, p_value
