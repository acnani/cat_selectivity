from blackfynn import Blackfynn
import os
import sys
if sys.platform == 'win32':
    rootPath = 'R:\\'
else:
    rootPath = os.path.join('//', 'media', 'rnelshare')

sys.path.append(os.path.join(rootPath,'users','amn69','Projects','cat','selectivity','surface paper','v2018'))
import helperFcns as hf

bf = Blackfynn('lumbar_selectivity')
catDS = bf.get_dataset('N:dataset:1cc6b671-0dea-4aab-ad30-ed3884e17028')

db = hf.db
collection = db.selectivity
collection2 = db.blackfynnUpload

allSubjects = ['Electro','Freeze','Galactus','Hobgoblin','HA02'] # ['HA04']#,

PWbySession = hf.PWbySession
binarySearchResolutionbySession = hf.binarySearchResolutionbySession

def getDictVals(d,key):
    subKeys = key.split('-')
#     print subKeys
    if len(subKeys) == 1:
        if subKeys[0] in d.keys():
            if isinstance(d[subKeys[0]],list):
                return ', '.join(str(e) for e in d[subKeys[0]])
            else:
                return d[subKeys[0]]
        else:
            return []
    elif len(subKeys) == 2:
        if subKeys[0] in d.keys() and subKeys[1] in d[subKeys[0]].keys():
            if isinstance(d[subKeys[0]][subKeys[1]],list):
                return ', '.join(str(e) for e in  d[subKeys[0]][subKeys[1]])
            else:
                return d[subKeys[0]][subKeys[1]]
        else:
            return []
    else:
        print 'invalid keys'

globalidx = 0
for iSub in allSubjects:
    print iSub
    targetSessions = sorted(hf.PWbySession[iSub].keys())
    trialObj = list(collection.find({'mdf_def.mdf_type': 'recruitment', 'mdf_metadata.subject': iSub,
                                     'mdf_metadata.session': {'$in': targetSessions}}))

    for i, iObj in enumerate(trialObj):
        if globalidx % 1000 == 0:
            print iSub, i, globalidx

        globalidx += 1
        seshNum = iObj['mdf_metadata']['session']
        uid = iObj['mdf_def']['mdf_uuid']
        pw = PWbySession[iSub][seshNum]
        binRes = binarySearchResolutionbySession[iSub][seshNum]

        # trial
        trialModel = catDS.get_model('recruitment')
        modelKeys = trialModel.schema.keys()

        recordDict = {}
        recordDictmongo = {'type':'BFuploadFinal','subject': iSub, 'subjectIdx':i,'globalIdx':globalidx}
        for iKey in modelKeys:
            if iKey == 'mdfUUID':
                recordDict[iKey] = uid
            elif iKey == 'PW':
                recordDict[iKey] = pw
            elif iKey == 'binaryRes':
                recordDict[iKey] = binRes
            elif iKey == 'CV':
                cvFile = []
                if 'Femoral' in iObj['mdf_metadata']['location'] or 'Sciatic' in iObj['mdf_metadata']['location']:

                    cvObj = list(collection.find({'mdf_def.mdf_type': 'CV',
                                                  'mdf_metadata.subject': iObj['mdf_metadata']['subject'],
                                                  'mdf_metadata.session': iObj['mdf_metadata']['session'],
                                                  'mdf_metadata.block': iObj['mdf_metadata']['block'],
                                                  'mdf_metadata.stimChan': iObj['mdf_metadata']['stimChan'],
                                                  'mdf_metadata.amplitude': iObj['mdf_metadata']['amplitude'],
                                                  'mdf_metadata.location': iObj['mdf_metadata']['location'].split('_')[0],
                                                  'mdf_metadata.DRG': iObj['mdf_metadata']['DRG'],
                                                  },{'mdf_metadata.cv': 1, 'mdf_def.mdf_files.mdf_data': 1}))

                    #                     print cvObj, iObj['mdf_metadata']['is_sig']
                    if cvObj:
                        cvFile = cvObj[0]['mdf_def']['mdf_files']['mdf_data'].split('\\')[-1][:-4]
                        # cvFile = '%s_ssn%03d_blk%03d_ch%03d_a%0.1f_%s.data' %( iObj['mdf_metadata']['subject'], iObj['mdf_metadata']['session'],
                        #                                                        iObj['mdf_metadata']['block'], iObj['mdf_metadata']['stimChan'], iObj['mdf_metadata']['amplitude'], iObj['mdf_metadata']['location'].split('_')[0])
                        if isinstance(cvObj[0]['mdf_metadata']['cv'], list):
                            recordDict[iKey] = ', '.join(str(e) for e in cvObj[0]['mdf_metadata']['cv'])
                        else:
                            recordDict[iKey] = str(cvObj[0]['mdf_metadata']['cv'])

            else:
                val = getDictVals(iObj['mdf_metadata'], iKey)
                if iKey == 'amplitude':
                    val = float(val)
                elif iKey in ['is_sig', 'is_sig_manual']:
                    if val == 1:
                        val = 1
                    elif val == 0:
                        val = 0
                    else:
                        val = 999

                recordDict[iKey] = val

        # trialRecord = trialModel.create_record(recordDict)

        # STAfilename = '%s_ssn%03d_blk%03d_ch%03d_a%0.1f_%s.data' %(iObj['mdf_metadata']['subject'],iObj['mdf_metadata']['session'],iObj['mdf_metadata']['block'],iObj['mdf_metadata']['stimChan'],iObj['mdf_metadata']['amplitude'],iObj['mdf_metadata']['location'])
        STAfilename = iObj['mdf_def']['mdf_files']['mdf_data'].split('\\')[-1][:-4]
        resDict = list(collection2.find({'subject': iSub, 'type':'STA','STAfile': STAfilename}))[0]
        # BFdatafile = bf.get(resDict['bf_id']) #seshFolder.get_items_by_name(STAfilename)[0]
        # BFdatafile.relate_to(trialRecord)

        recordDict['STAfile'] = STAfilename
        recordDict['STApackageID'] = resDict['bf_id']
        recordDictmongo['STAfile'] = STAfilename
        recordDictmongo['STApackageID'] = resDict['bf_id']


        if cvFile:
            resDict2 = list(collection2.find({'subject': iSub, 'type':'CV','CVfile': cvFile}))[0]
            # BF_CVdatafile = bf.get(resDict2['bf_id']) #seshFolder.get_items_by_name(cvFile)[0]
            # BF_CVdatafile.relate_to(trialRecord)
            recordDict['CVfile'] = cvFile
            recordDict['CVpackageID'] = resDict2['bf_id']
            recordDictmongo['CVfile'] = cvFile
            recordDictmongo['CVpackageID'] = resDict2['bf_id']

        trialRecord = trialModel.create_record(recordDict)
        recordDictmongo['recordID'] = trialRecord.id
        collection2.insert_one(recordDictmongo)

    print '    finished'
