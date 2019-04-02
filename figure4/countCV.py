import pymongo
import plotly
from plotly import tools
import plotly.graph_objs as go
import math
from helperFcns import uniqueCVs
from scipy import stats
import numpy as np

# with open ('meanAmpDict_'+eType+'.yml', 'r') as meanDict:
#     meanAmpDict = yaml.load(meanDict)

subj = 'Galactus'
CVbyAmp = uniqueCVs(subj)

print 'chut'