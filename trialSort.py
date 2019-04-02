import pymongo
import yaml

# constants
mongohost = "192.168.0.246"
mongoport = 15213
subject = 'HA02'
collection = 'selectivity'
client = pymongo.MongoClient(mongohost, mongoport)
db = client.acute

res1 = db.command({
        'aggregate' : collection,
        'pipeline' : [
          {'$match' : {
             "mdf_def.mdf_type":'trial',
             "mdf_metadata.success": 1,
            }},
          {"$group": {
              "_id": {"subject":"$mdf_metadata.subject", "protocol":"$mdf_metadata.protocol", "sesh":"$mdf_metadata.session"},
              "blocks": {"$addToSet": "$mdf_metadata.block"},
              "location":{"$addToSet":"$mdf_metadata.location"}
          }},
          {"$project": {
              "_id": 0,
              "subject": "$_id.subject",
              "protocol":"$_id.protocol",
              "session":"$_id.sesh",
              "blocks": "$blocks",
              "DRG": "$location"
          }}]})

trialDict = {}
for entry in res1['result']:
    trialDict.setdefault(entry['subject'],{})
    trialDict[entry['subject']].setdefault('session',[]).append(entry['session'])
    trialDict[entry['subject']].setdefault('blocks',[]).append(entry['blocks'])
    trialDict[entry['subject']].setdefault('protocol',[]).append(entry['protocol'])
    trialDict[entry['subject']].setdefault('DRG',[]).append(entry['DRG'])


# trialDict[res1['result']]
with open('sortedTrials.yml', 'w') as outfile:
    outfile.write(yaml.safe_dump(trialDict, default_flow_style=False))
