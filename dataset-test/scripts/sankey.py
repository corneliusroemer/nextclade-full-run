#%%
import pandas as pd
import pandas as pd
from pysankey import sankey
import matplotlib.pyplot as plt

#%%
old = "nextclade_old_clades.tsv"
new = "nextclade_new_clades.tsv"
df_old = pd.read_csv(old, sep='\t').set_index('seqName')
df_new = pd.read_csv(new, sep='\t').set_index('seqName')
df_old
#%%
df = df_old.join(df_new, how='inner',lsuffix='_old', rsuffix='_new')
df
#%%
# Count all unique pairs
flows = df.groupby(['clade_old', 'clade_new']).size()
flows
#%%
a = flows.index.get_level_values(0)
b = flows.index.get_level_values(1)
weight = list(flows)
# %%
ax = sankey(
      left=a[:300], right=b[:300],
      rightWeight=weight[:300], leftWeight=weight[:300], fontsize=20
)
plt.gcf().set_size_inches(40,40)
plt.savefig('sankey.pdf', bbox_inches='tight',transparent=False) # to save
# %%
