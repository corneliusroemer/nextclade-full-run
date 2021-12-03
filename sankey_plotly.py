#%%
import pandas as pd
import plotly.graph_objects as go
import pandas as pd
from pysankey import sankey
import matplotlib.pyplot as plt

#%%
df = pd.read_csv('classification.tsv', sep='\t')

#%%
# Count all unique pairs
flows = df.groupby(['lineage', 'clade']).size()
#%%
a = flows.index.get_level_values(0)
b = flows.index.get_level_values(1)
weight = list(flows)
#%%
lineage = set(flows.index.get_level_values('lineage').unique())
clade = set(flows.index.get_level_values('clade').unique())
labels = list(lineage.union(clade))
joint_lookup = {k: v for v, k in enumerate(labels)}


#%%
fig = go.Figure(data=[go.Sankey(
    node = dict(
      pad = 15,
      thickness = 20,
      line = dict(color = "black", width = 0.5),
      label = labels,
      color = "blue"
    ),
    link = dict(
      source = list(map(joint_lookup.get,lineage)), # indices correspond to labels, eg A1, A2, A1, B1, ...
      target = list(map(joint_lookup.get,clade)),
      value = list(flows),
  ))])

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
fig.show()
# %%
# %%
ax = sankey(
      left=a[:300], right=b[:300],
      rightWeight=weight[:300], leftWeight=weight[:300], fontsize=20
)
plt.gcf().set_size_inches(40,40)
plt.savefig('sankey.pdf', bbox_inches='tight',transparent=False) # to save
# %%
