#%%
import pandas as pd
import pandas as pd

#%%
df = pd.read_csv('pango-benchmark/classification.tsv', header=0 ,sep='\t', names=['truth', 'pred'])

#%%
# Count all unique pairs
flows = pd.DataFrame(df.groupby(['truth', 'pred']).size(),columns=['count'])
flows.reset_index(inplace=True)
#%%
old_count = df.truth.value_counts()
new_count = df.pred.value_counts()
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
# flows[flows['clade_old'] != flows['clade_new']].to_csv('clade_changes.tsv', sep='\t',float_format='%.2g')
flows[flows.truth == flows.pred].sort_values(by='count',ascending=False).to_csv('correct_clades.tsv', sep='\t',float_format='%.2g',index=False)
flows[flows.truth != flows.pred].sort_values(by='count',ascending=False).to_csv('wrong_clades.tsv', sep='\t',float_format='%.2g',index=False)
