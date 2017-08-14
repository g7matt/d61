from main import *
from bokeh.io import output_notebook
from bokeh.resources import INLINE
output_notebook(resources=INLINE, hide_banner=True)

dblp = PaperCollection("DBLP1.csv")
scholar = PaperCollection("Scholar.csv")

dataset = Eval("DBLP-Scholar_perfectMapping.csv", dblp.normalised(), scholar.normalised())
