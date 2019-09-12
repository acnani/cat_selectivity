import pymongo
import pandas as pd
import helperFcns as hf

eType = 'epineural'
subjectList = hf.getSubjects(eType)
targetNerveLabels = hf.allCuffs_mdf.keys()
coactivationDF = pd.DataFrame(0,columns=targetNerveLabels, index=targetNerveLabels)


FP = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)
FN = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)
TP = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)
TN = pd.DataFrame(0,columns=subjectList, index=targetNerveLabels)

for iSub in subjectList:
    seshList = sum(hf.sessionPerDRG(iSub, eType).values(),[])
    for iNerve in targetNerveLabels:
        FP.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':1, 'mdf_metadata.is_sig_manual':0,},{"mdf_metadata.location":1}).count()
        FN.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':0, 'mdf_metadata.is_sig_manual':1},{"mdf_metadata.location":1}).count()
        TP.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':1, 'mdf_metadata.is_sig_manual':1},{"mdf_metadata.location":1}).count()
        TN.loc[iNerve, iSub] = hf.db[hf.collection].find({'mdf_metadata.subject':iSub, "mdf_metadata.location": iNerve, "mdf_metadata.session": {'$in':seshList},'mdf_def.mdf_type':'recruitment', 'mdf_metadata.is_sig':0, 'mdf_metadata.is_sig_manual':0},{"mdf_metadata.location":1}).count()


# per subject
sensitivity = (TP)/(TP + FN)*100  # FPR
specificity = (TN)/(TN + FP)*100  # TNR
accuracy = (TP + TN)/(TP + TN + FP + FN)*100  # precision
# accuracy.to_csv('R:\\users\\amn69\\Projects\\cat\\selectivity\\surface paper\\drafts\\accuracy.csv')

FP_rate = FP/(FP+TN)

# net
sensitivity_net = float(TP.values.sum())/(TP.values.sum() + FN.values.sum())*100  # FPR
specificity_net = float(TN.values.sum())/(TN.values.sum() + FP.values.sum())*100  # TNR
accuracy_net = float(TP.values.sum() + TN.values.sum())/(TP.values.sum() + TN.values.sum() + FP.values.sum() + FN.values.sum())*100  # precision