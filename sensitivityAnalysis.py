import pymongo
import pandas as pd
import helperFcns as hf

eType = 'epineural'
subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()
coactivationDF = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)


ENG_FP = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)
ENG_FN = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)
ENG_TP = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)
ENG_TN = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)

for iSub in subjectList:
    seshList = sum(hf.sessionPerDRG(iSub, eType).values(),[])
    for iNerve in targetNerveLabels:
        ENG_FP.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':1, 'mdf_metadata.is_sig_manual':0,},{"mdf_metadata.location":1}).count()
        ENG_FN.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':0, 'mdf_metadata.is_sig_manual':1},{"mdf_metadata.location":1}).count()
        ENG_TP.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':1, 'mdf_metadata.is_sig_manual':1},{"mdf_metadata.location":1}).count()
        ENG_TN.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':0, 'mdf_metadata.is_sig_manual':0},{"mdf_metadata.location":1}).count()


# per subject
sensitivity = (ENG_TP)/(ENG_TP + ENG_FN)*100  # FPR
specificity = (ENG_TN)/(ENG_TN + ENG_FP)*100  # TNR
accuracy = (ENG_TP + ENG_TN)/(ENG_TP + ENG_TN + ENG_FP + ENG_FN)*100  # precision
accuracy.to_csv('R:\\users\\amn69\\Projects\\cat\\selectivity\\surface paper\\drafts\\accuracy.csv')

# net
sensitivity_net = float(ENG_TP.values.sum())/(ENG_TP.values.sum() + ENG_FN.values.sum())*100  # FPR
specificity_net = float(ENG_TN.values.sum())/(ENG_TN.values.sum() + ENG_FP.values.sum())*100  # TNR
accuracy_net = float(ENG_TP.values.sum() + ENG_TN.values.sum())/(ENG_TP.values.sum() + ENG_TN.values.sum() + ENG_FP.values.sum() + ENG_FN.values.sum())*100  # precision