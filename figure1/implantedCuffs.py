import numpy as np
import helperFcns as hf
import seaborn as sns
import collections
import pandas as pd
from helperFcns import plt


for eType in ['epineural', 'penetrating']:
    cuffLabels = hf.allCuffs_mdf.keys()
    cuffNames = hf.allCuffs_mdf.values()

    subjectList = hf.getSubjects(eType)
    cuffPerSub = hf.cuffsPerSubject(subjectList)

    cuffArray = collections.OrderedDict()
    for iSub in subjectList:
        cuffArray[iSub] = np.double(~(np.isin(cuffLabels, cuffPerSub[iSub])))

    # format dataframe
    cuff_DF = pd.DataFrame.from_dict(cuffArray,'index')
    cuff_DF.columns = cuffNames
    cuff_DF = cuff_DF.loc[:, (cuff_DF != 1).any(axis=0)]

    zm = np.ma.masked_less(cuff_DF.values, 1)
    x = np.arange(len(cuff_DF.columns) + 1)
    y = np.arange(len(cuff_DF.index) + 1)

    # generate heatmap and edit figure
    plt.figure(figsize=(10, 2.5))
    hmap = sns.heatmap(cuff_DF,cmap='Greys',cbar=False, linewidths=0.5,linecolor=[0,0,0], vmin=3, vmax=5)
    hmap.set_yticklabels(hmap.get_yticklabels(), rotation=45)
    hmap.set_xticklabels(hmap.get_xticklabels(), rotation=90)
    plt.pcolor(x, y, zm, hatch='//', alpha=0.)
    # plt.show()
    plt.savefig('implantedCuffs_'+eType+'.png')
    plt.savefig('implantedCuffs_'+eType+'.pdf')
    plt.close()