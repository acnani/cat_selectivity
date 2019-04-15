import numpy as np
import helperFcns as hf
import seaborn as sns
import collections
import pandas as pd
import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype'] = 'none'


for eType in ['epineural', 'penetrating']:
    cuffLabels = hf.allCuffs_mdf.keys()
    cuffNames = hf.allCuffs_mdf.values()

    subjectList = hf.getSubjects(eType)
    cuffPerSub = hf.cuffsPerSubject2(subjectList)

    cuffArray = collections.OrderedDict()
    for iSub in subjectList:
        cuffArray[iSub] = np.double(~(np.isin(cuffLabels, cuffPerSub[iSub])))

    # format dataframe
    cuff_DF = pd.DataFrame.from_dict(cuffArray,'index')
    cuff_DF.columns = cuffNames

    # generate heatmap and edit figure
    plt.figure(figsize=(10, 2))
    hmap = sns.heatmap(cuff_DF,cmap='Greys',cbar=False, linewidths=0.5,linecolor=[0,0,0])
    hmap.set_yticklabels(hmap.get_yticklabels(), rotation=45)
    plt.show()
    plt.savefig('implantedCuffs_'+eType+'.svg')
    plt.savefig('implantedCuffs_'+eType+'.png')
    plt.close()