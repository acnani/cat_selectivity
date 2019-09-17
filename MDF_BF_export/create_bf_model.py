import os
import pymongo
from blackfynn import Blackfynn

mongohost = "192.168.0.246"
mongoport = 15213

DATA_BASE = os.path.join('R:\\', 'DB', 'MDF', 'cat', 'acuteSelectivity')
client = pymongo.MongoClient(mongohost, mongoport)
db = client.acute
collection = db.selectivity


bf = Blackfynn('lumbar_selectivity')
ds1 = bf.get_dataset('N:dataset:1cc6b671-0dea-4aab-ad30-ed3884e17028')


def getNestedKeys(d):
    outList = []
    for k, v in d.iteritems():
        if 'annotation' not in k:
            if isinstance(v, dict):
                tmp = ['%s-%s' % (k, x) for x in getNestedKeys(v)]
                outList.extend(tmp)
            else:
                outList.append(k)
    return outList


def getDictVals(d, key):
    subKeys = key.split('-')
    #     print subKeys
    if len(subKeys) == 1:
        if subKeys[0] in d.keys():
            return d[subKeys[0]]
        else:
            return []
    elif len(subKeys) == 2:
        if subKeys[0] in d.keys() and subKeys[1] in d[subKeys[0]].keys():
            return d[subKeys[0]][subKeys[1]]
        else:
            return []
    else:
        print 'invalid keys'


def getDictValType(d, key):
    subKeys = key.split('-')
    if len(subKeys) == 1:
        val = d[subKeys[0]]
    elif len(subKeys) == 2:
        val = d[subKeys[0]][subKeys[1]]
    else:
        print 'invalid keys'

    if val:
        if isinstance(val, unicode):
            return str
        if isinstance(val, list):
            return str  # type(val[0])
        else:
            return type(val)
    else:
        return str


# collection.find().distinct('mdf_def.mdf_type')
allObjTypes = ['recruitment', 'CV']
trialTemplateDict = {}
fieldType = {}
for iType in allObjTypes:

    fieldType.setdefault(iType, {})
    template = set()
    allObj = collection.find({'mdf_def.mdf_type': iType}, {'mdf_metadata': 1, '_id': 0})

    for iObj in allObj:
        tmpDict = iObj['mdf_metadata']
        keyName = getNestedKeys(tmpDict)
        #         add medataand data fields to template
        template.update(set(keyName))
        #         template.update(set(iObj['mdf_def']['mdf_data']['mdf_fields']))

        #         add metadata field types
        for iKey in keyName:
            fieldType[iType].setdefault(iKey, []).append(getDictValType(tmpDict, iKey))

            #     remove duplicate field types
    for typeKey in fieldType[iType].keys():
        fieldType[iType][typeKey] = list(set(fieldType[iType][typeKey]))

    trialTemplateDict[iType] = list(template)

trialTemplateDict['recruitment'].remove('old_block')
trialTemplateDict['recruitment'].remove('old_session')
trialTemplateDict['recruitment'].remove('old_location')
del fieldType['recruitment']['old_block']
del fieldType['recruitment']['old_session']
del fieldType['recruitment']['old_location']
fieldType['recruitment']['CV'] = [str]
trialTemplateDict['recruitment'].append('CV')


# create BF model
iObj = 'recruitment'
print iObj
# create schema
schemaList= [{'name': 'mdfUUID','data_type':str,'description': 'RNEL MDF object uuid'},
             {'name':'CVfile','data_type':str,'description':'file containing conduction velocity data'},
             {'name':'STAfile','data_type':str,'description': 'file containing stimulus triggered average ENG data'},
             {'name':'CVpackageID','data_type':str,'description':'Blackfynn ID for conduction velocity data package'},
             {'name':'STApackageID','data_type':str,'description':'Blackfynn ID for STA data package'},
             {'name':'PW','data_type':float,'description':'pulse width of stimulation'},
             {'name':'binaryRes','data_type':float,'description':'binary search resolution'}]

fieldDescriptors = {}
fieldDescriptors['CV'] = 'conduction velocity of femoral/sciatic trunk'
fieldDescriptors['DRG'] = 'DRG targeted for stimulation'
fieldDescriptors['amplitude'] = 'stimulation amplitude'
fieldDescriptors['block'] = 'trial number'
fieldDescriptors['fs'] = 'sampling frequency'
fieldDescriptors['is_sig'] = 'automated ENG response detected 1/0'
fieldDescriptors['is_sig_manual'] = 'manual ENG response detection (1/0)'
fieldDescriptors['location'] = 'nerve cuff location (ENG source)'
fieldDescriptors['session'] = 'session counter'
fieldDescriptors['stimChan'] = 'DRG stimulation channel number'
fieldDescriptors['subject'] = 'subject name'

# get model fields and field types
fieldTypes = []
for iFieldName,iFieldType in fieldType[iObj].iteritems():
    desc = fieldDescriptors[iFieldName]

    if len(iFieldType)>1:
        if iFieldType == [int, float]:
            val = float
        if iFieldName in ['is_sig','is_sig_manual']:
            val = int
    else:
        val = iFieldType[0]

    if iFieldName == 'subject':
        schemaList.append({'name':iFieldName,'data_type':val, 'title': True, 'description':desc})
    else:
        schemaList.append({'name': iFieldName,'data_type':val,'description':desc})

# create model
ds1.create_model('%s' %iObj, schema=schemaList)