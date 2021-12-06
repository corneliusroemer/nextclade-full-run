#%%
import pandas as pd
import pandas as pd
from pysankey2.utils import setColorConf
from pysankey2 import Sankey
import matplotlib.pyplot as plt


#%%
old = "nextclade_old_clades.tsv"
new = "nextclade_new_clades.tsv"
df_old = pd.read_csv(old, sep='\t').set_index('seqName')
df_new = pd.read_csv(new, sep='\t').set_index('seqName')
df_old
#%%
df = df_old.join(df_new, how='inner',lsuffix='_old', rsuffix='_new')
# df.sort_values(by=['clade_old','clade_new'],inplace=True,ascending=True)
df
#%%
# Count all unique pairs
flows = pd.DataFrame(df.groupby(['clade_old', 'clade_new']).size(),columns=['count'])
flows.reset_index(inplace=True)

#%%
old_count = df_old.value_counts()
new_count = df_new.value_counts()
count_all = old_count.sum()
#%% 
share_old = []
share_new = []
share_all = []
for index,data in flows.iterrows():
      share_old.append(data[2]/old_count[data[0]])
      share_new.append(data[2]/new_count[data[1]])
      share_all.append(data[2]/count_all)
#%%
flows.loc[:,'share_old']=share_old
flows.loc[:,'share_new']=share_new
flows.loc[:,'share_all']=share_all
#%%
flows[flows['clade_old'] != flows['clade_new']].to_csv('clade_changes.tsv', sep='\t',float_format='%.2g')
#%%
df_old.value_counts()
#%%
#%%
sky = Sankey(df)
fig,ax = sky.plot()
plt.gcf().set_size_inches(10,10)
plt.savefig('sankey.pdf', bbox_inches='tight',transparent=False) # to save
