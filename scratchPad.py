import helperFcns as hf
import plotly



# allCuffs = hf.allCuffs_mdf.keys()
# asd = hf.generateInnervationTree(allCuffs, range(len(allCuffs)))
# plotly.offline.plot(asd, filename='canonicalInnervation_helper.html',auto_open=False)

# qwe = hf.thresholdPerCuff_HA04('HA04',[134])
# print qwe


etype = 'penetrating'
for sub in hf.getSubjects(etype):
    # print sub
    # print sorted(hf.sessionPerElectrodeType(sub)[etype])
    hf.getRecruitmentUUIDforValidation(sub, etype)
