#%%
import pandas as pd
#%%
df = pd.read_csv('nextclade_new.tsv', sep='\t')
#%%
meta = pd.read_csv('metadata.tsv.gz', sep='\t', usecols=['strain','date','region','country','Nextstrain_clade','pango_lineage','submitting_lab'])
meta
#%%
meta
# %%
df.set_index('seqName', inplace=True)
df
# %%
meta.set_index('strain', inplace=True)
meta
# %%
merged = df.merge(meta, left_index=True, right_index=True, how='inner')
merged
# %%
medians = merged.groupby('pango_lineage').median().sort_values('qc.overallScore', ascending=False)
# %%
medians
# %%
lineage_counts = merged.groupby('pango_lineage')['totalSubstitutions'].count().rename('count')
# %%
medians.insert(0, 'count', lineage_counts)
#%%
medians.to_csv('medians_pango.tsv', sep='\t')
# %%
lineage_counts['None']
# %%
merged.groupby('pango_lineage').get_group('AY.33.1')['qc.snpClusters.totalSNPs']
# %%
