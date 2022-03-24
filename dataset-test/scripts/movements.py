#%%
# import typer
import pandas as pd


#%%
# old = "dataset-test/nextclade_old.tsv"
# new = "dataset-test/nextclade_new.tsv"
old = "nextclade_old.tsv"
new = "nextclade_new.tsv"
df_old = pd.read_csv(old, sep='\t').set_index('seqName')
df_new = pd.read_csv(new, sep='\t').set_index('seqName')
df_old
#%%
df = df_old.join(df_new, how='inner',lsuffix='_old', rsuffix='_new')
# df.sort_values(by=['clade_old','clade_new'],inplace=True,ascending=True)
df
#%%
for key in ['clade','Nextclade_pango','qc.overallStatus']:
      #%%
      # key = 'Nextclade_pango'
      key_old = key + '_old'
      key_new = key + '_new'
      # Count all unique pairs
      flows = pd.DataFrame(df.groupby([key_old, key_new]).size(),columns=['count'])
      flows.reset_index(inplace=True)
      flows
      #%%
      old_count = df_old[key].value_counts()
      new_count = df_new[key].value_counts()
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
      flows[flows[key_old] != flows[key_new]].to_csv('results/' + key + '_changes.tsv', sep='\t',float_format='%.2g', index=False)
#%%
