# outputs one innervation tree html file per session per subject for number of channels activating a cuff

import plotly
from plotly import tools
import helperFcns as hf
import pandas as pd
import seaborn as sns
from helperFcns import plt

eType = 'penetrating'
stimunit = 'amplitude'
collapseCuffs = True       # to avoid combining cuffs OR to ignore parent but not child (eg ignore Sensory but not Sural)
ignoreCuffs = ['BiFem']

allDRG = hf.allDRG
subjectList = hf.getSubjects(eType)

allCuffs = hf.allCuffs_mdf.keys()

# hf.thresholdPerCuff('Galactus',41,[],True)
# subDict = {}
for iDRG in allDRG:
    for subject in subjectList:
        res2 = hf.sessionPerDRG(subject, eType)

        # iterate over each DRG
        if iDRG in res2.keys():
            targetSesh = res2[iDRG]

            # iterate over each session
            for sesh in targetSesh:
                hmapDF = pd.DataFrame(['stimChan','threshVal'])

                threshDict = hf.thresholdPerCuff(subject, sesh, ignoreCuffs, collapseCuffs,stimUnits=stimunit)
                allActiveChans = sorted(threshDict.keys())
                numActiveChans = len(allActiveChans)

                # sns.heatmap(pd.DataFrame.from_dict(threshDict))
                # plt.suptitle('%s: %s: session %03d (%s)'%(subject, iDRG, sesh,stimunit))
                # plt.savefig(eType+'\\perSession\\%s_%s_sesh%03d_%s.png'%(subject, iDRG, sesh,stimunit))
                # plt.savefig(eType + '\\perSession\\%s_%s_sesh%03d_%s.pdf' % (subject, iDRG, sesh, stimunit))
                # plt.close()

                if numActiveChans != 0:
                    fig = tools.make_subplots(rows=numActiveChans, cols=1, subplot_titles=allActiveChans)
                    subplotRow = 0

                    # iterate over each stim channel
                    for iChan in allActiveChans:
                        if bool(threshDict[iChan]):
                            subplotRow = subplotRow+1
                            resultCuffs = threshDict[iChan].keys()
                            allAmps = [threshDict[iChan][cuffName] for cuffName in resultCuffs]

                            figDict = hf.generateInnervationTree(resultCuffs, allAmps, 25,stimUnits=stimunit, eType=eType)
                            [fig.append_trace(iData, subplotRow, 1) for iData in figDict['data']]
                            fig['layout']['showlegend'] = False

                    if bool(fig['data']):           # if threshDict[iChan] for all chnnels is empty
                        fig['layout'].update(height = 600*numActiveChans, )
                        plotly.offline.plot(fig, filename=eType+'\\perSession\\%s_%s_sesh%03d_%s.html' %(subject, iDRG, sesh,stimunit),auto_open=False)
