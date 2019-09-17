from blackfynn import Blackfynn
import glob
import os
import time
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
collection = db.blackfynnUpload

for iSub in ['HA04']: #['Electro','Freeze','HA02','HA04','Galactus','Hobgoblin']:
    print iSub
    if collection.find({'subject': iSub}).count() == 0:
        subjFolder = catDS.create_collection(iSub)
    else:
        subjFolder = catDS.get_items_by_name(iSub)[0]


    targetSessions = sorted(hf.PWbySession[iSub].keys())
    for iSesh in targetSessions:
        print iSesh
        seshFolder = subjFolder.create_collection('session_%d' %iSesh)
        STAfolder = seshFolder.create_collection('STA_recruitment')
        allSTAFiles = sorted(glob.glob(os.path.join(rootPath, 'DB', 'MDF', 'cat', 'acuteSelectivity', 'analysis', 'recruitment','HA04_renamed','*ssn%03d*.mat' %iSesh)))
        for iFile in allSTAFiles:
            if collection.find({'subject': iSub, 'type':'STA','STAfile': iFile.split(os.sep)[-1][:-4]}).count() == 0:
                success = 0
                while success == 0:
                    try:
                        packageInfo = STAfolder.upload(iFile)
                        success = 1
                    except:
                        print 'unable to upload trying again'
                        success = 0
                        time.sleep(5)
                collection.insert_one({'subject': iSub, 'type': 'STA',
                                   'STAfile': iFile.split(os.sep)[-1][:-4],
                                   'bf_id':packageInfo[0][0]['package']['content']['id']})

        CVfolder = seshFolder.create_collection('conductionVelocity')
        allCVFiles = sorted(glob.glob(os.path.join(rootPath, 'DB', 'MDF', 'cat', 'acuteSelectivity', 'analysis', 'CV','HA04_renamed','*ssn%03d*.mat' %iSesh)))
        for iFile in allCVFiles:
            if collection.find({'subject': iSub, 'type': 'CV', 'CVfile': iFile.split(os.sep)[-1][:-4]}).count() == 0:
                success = 0
                while success == 0:
                    try:
                        packageInfo = CVfolder.upload(iFile)
                        success = 1
                    except:
                        print 'unable to upload trying again'
                        success = 0
                        time.sleep(5)
                collection.insert_one({'subject': iSub, 'type': 'CV',
                                   'CVfile': iFile.split(os.sep)[-1][:-4],
                                   'bf_id': packageInfo[0][0]['package']['content']['id']})