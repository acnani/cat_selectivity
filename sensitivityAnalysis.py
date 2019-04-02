import os
import plotly
from plotly import tools
import plotly.graph_objs as go
import math
import pymongo
import yaml
from time import strftime

# constants
mongohost = "192.168.0.246"
mongoport = 15213
collection = 'selectivity'

# instantiate the mongo client
client = pymongo.MongoClient(mongohost, mongoport)
# get handle to database
db = client.acute

# gets global FP/FN/TP/TN rate
TN = db.selectivity.find({'mdf_metadata.is_sig':0, 'mdf_metadata.is_sig_manual':0}).count()
FP = db.selectivity.find({'mdf_metadata.is_sig':1, 'mdf_metadata.is_sig_manual':0}).count()
FN = db.selectivity.find({'mdf_metadata.is_sig':0, 'mdf_metadata.is_sig_manual':1}).count()
TP = db.selectivity.find({'mdf_metadata.is_sig':1, 'mdf_metadata.is_sig_manual':1}).count()

# sensitivity = TP/(TP+FN)      # true positive rate
# specificity = TN/(TN+FP)      # true negative rate
# predictive value positive = TP/(TP+FP)
# predictive value negative = TN/(TN+FN)



# gets global FP/FN/TP/TN rate by subject
# for subject in ['Galactus','Hobgoblin','']
TN = db.selectivity.find({'mdf_metadata.is_sig':0, '$mdf_metadata.is_sig_manual':0}).count()
FP = db.selectivity.find({'mdf_metadata.is_sig':1, '$mdf_metadata.is_sig_manual':0}).count()
FN = db.selectivity.find({'mdf_metadata.is_sig':0, '$mdf_metadata.is_sig_manual':1}).count()
TP = db.selectivity.find({'mdf_metadata.is_sig':1, '$mdf_metadata.is_sig_manual':1}).count()



# gets global FP/FN/TP/TN rate by amp
res3 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'recruitment',
            }},
          {"$group": {
              "_id": {"is_sig":"$mdf_metadata.is_sig", "is_sig_validate":"$mdf_metadata.is_sig_manual", "amp":"$mdf_metadata.amplitude"},
              "count":{"$sum": 1}
          }},
          {"$project": {
              "_id": 1,
              "count": "$count"
          }}]})

# gets global FP/FN/TP/TN rate by cuff
res4 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'recruitment',
            }},
          {"$group": {
              "_id": {"is_sig":"$mdf_metadata.is_sig", "is_sig_validate":"$mdf_metadata.is_sig_manual", "cuff":"$mdf_metadata.location"},
              "count":{"$sum": 1}
          }},
          {"$project": {
              "_id": 1,
              "count": "$count"
          }}]})

# gets global FP/FN/TP/TN rate per subject per amp
res5 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'recruitment',
            }},
          {"$group": {
              "_id": {"is_sig":"$mdf_metadata.is_sig", "is_sig_validate":"$mdf_metadata.is_sig_manual", "subject":"$mdf_metadata.subject", "amp":"$mdf_metadata.amplitude"},
              "count":{"$sum": 1}
          }},
          {"$project": {
              "_id": 1,
              "count": "$count"
          }}]})

# gets global FP/FN/TP/TN rate per subject per cuff
res6 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'recruitment',
            }},
          {"$group": {
              "_id": {"is_sig":"$mdf_metadata.is_sig", "is_sig_validate":"$mdf_metadata.is_sig_manual", "subject":"$mdf_metadata.subject", "cuff":"$mdf_metadata.location"},
              "count":{"$sum": 1}
          }},
          {"$project": {
              "_id": 1,
              "count": "$count"
          }}]})

# gets global FP/FN/TP/TN rate per cuff per amp
res7 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'recruitment',
            }},
          {"$group": {
              "_id": {"is_sig":"$mdf_metadata.is_sig", "is_sig_validate":"$mdf_metadata.is_sig_manual", "cuff":"$mdf_metadata.location", "amp":"$mdf_metadata.amplitude"},
              "count":{"$sum": 1}
          }},
          {"$project": {
              "_id": 1,
              "count": "$count"
          }}]})

# gets global FP/FN/TP/TN rate per subj, per amp, per cuff
res8 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'recruitment',
            }},
          {"$group": {
              "_id": {"is_sig":"$mdf_metadata.is_sig", "is_sig_validate":"$mdf_metadata.is_sig_manual", "subject":"$mdf_metadata.subject", "cuff":"$mdf_metadata.location", "amp":"$mdf_metadata.amplitude"},
              "count":{"$sum": 1}
          }},
          {"$project": {
              "_id": 1,
              "count": "$count"
          }}]})

print 'chu'







# trialDict = {}
# for entry in res1['result']:
#     trialDict.setdefault(entry['subject'],{})
#     trialDict[entry['subject']].setdefault('session',[]).append(entry['session'])
#     trialDict[entry['subject']].setdefault('blocks',[]).append(entry['blocks'])
#     trialDict[entry['subject']].setdefault('protocol',[]).append(entry['protocol'])
#     trialDict[entry['subject']].setdefault('DRG',[]).append(entry['DRG'])
#
#
# # trialDict[res1['result']]
# with open('sortedTrials.yml', 'w') as outfile:
#     outfile.write(yaml.safe_dump(trialDict, default_flow_style=False))


# amps = []
# numcounts = []
# elec = []
# for ix in res1['result']:
#     # elecDict['%03d', int(ix['_id']['elec'])] = {}
#     amps.extend([float(ix['_id']['amp'])])
#     numcounts.extend([int(ix['count'])])
#     elec.extend([int(ix['_id']['elec'])])
#     # print '%03d, %03f, %03d' % (ix['count'], float(ix['_id']['amp']), int(ix['_id']['elec']))
#
# chans = list(set(elec)) # [4,5,6,7,8,51,53,54,55,56,101,119,123]  #
# fig = tools.make_subplots(rows=int(math.ceil(len(chans)/8.0)), cols=8, subplot_titles=chans)
#
# for chanNum in chans:
#     chanAmps = [amps[i] for i, val in enumerate(elec) if val == chanNum]
#     ampCounts = [numcounts[i] for i, val in enumerate(elec) if val == chanNum]
#     trace = go.Bar(x=chanAmps, y = ampCounts,showlegend=False) #go.Histogram(x=chanAmps)
#     # layout = go.Layout(showlegend=False)
#
#     fig.append_trace(trace, chans.index(chanNum)/8+1, chans.index(chanNum)%8+1)
#
# fig['layout'].update(height=300*int(math.ceil(len(chans)/8.0)),title='Stim amplitudes tested per unique electrode')
# plotly.offline.plot(fig,filename=os.path.join('R:', 'data_generated', 'human', 'sensory_stim', subject, 'report', strftime("%d_%m_%y"), 'allElecSummary.html'))
#
#
#
#
# res2 = db.command({
#         'aggregate' :collection,
#         'pipeline' : [
#           {'$match' : {
#              "mdf_metadata.subject":subject,
#              "mdf_def.mdf_type":"trial"}},
#           {"$group": {
#                     "_id": {"elec": "$mdf_metadata.elecNum", "type": "$mdf_metadata.trialType"},
#                     "count": {"$sum": 1}
#                 }},
#           {"$project": {
#                    "_id": 1,
#                    "count": "$count"
#                 }}]})
#
# trialType = []
# numcounts = []
# elec = []
# for ix in res2['result']:
#     if ix['_id']['type'] != 'SurfaceStim':
#         trialType.extend([(ix['_id']['type'])])
#         numcounts.extend([int(ix['count'])])
#         elec.extend([int(ix['_id']['elec'])])
#         # print '%03d, %03f, %03d' % (ix['count'], float(ix['_id']['amp']), int(ix['_id']['elec']))
#
# chans = list(set(elec)) # [4,5,6,7,8,51,53,54,55,56,101,119,123]  #
# fig = tools.make_subplots(rows=int(math.ceil(len(chans)/8.0)), cols=8, subplot_titles=chans)
#
# for chanNum in chans:
#     chanTrials = [trialType[i] for i, val in enumerate(elec) if val == chanNum]
#     ampCounts = [numcounts[i] for i, val in enumerate(elec) if val == chanNum]
#     trace = go.Bar(x=sorted(chanTrials), y = [ ampCounts[chanTrials.index(x)] for x in sorted(chanTrials)],showlegend=False) #go.Histogram(x=chanAmps)
#     # layout = go.Layout(showlegend=False)
#
#     fig.append_trace(trace, chans.index(chanNum)/8+1, chans.index(chanNum)%8+1)
#
# fig['layout'].update(height=300*int(math.ceil(len(chans)/8.0)),title='Trial Types per unique electrode')
# plotly.offline.plot(fig,filename=os.path.join('R:', 'data_generated', 'human', 'sensory_stim', subject, 'report', strftime("%d_%m_%y"), 'numTrialsPerElec.html'))