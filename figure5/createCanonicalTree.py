import plotly
import helperFcns as hf

allCuffs = hf.allCuffs_mdf.keys()
fig = hf.generateInnervationTree(allCuffs, [255]*len(allCuffs))
plotly.offline.plot(fig, filename='canonicalInnervation.html',auto_open=False)
# plotly.plotly.image.save_as(fig, filename='canonicalInnervation.png')