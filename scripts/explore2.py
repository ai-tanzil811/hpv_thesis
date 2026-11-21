import sys;sys.path.insert(0,'scripts')
import pandas as pd,numpy as np
from scipy import stats
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif
d=pd.read_excel(__import__('prep').P); o=pd.read_pickle('scripts/o.pkl')
src=d.iloc[:,30:38].copy(); src.columns=['Curriculum','Doctor','Family/friends','Social media','TV/Radio','Newspaper','Campaign','Never']
print(src.sum(), (src.drop(columns='Never').sum(axis=1)==0).sum())
print('heard no & never',pd.crosstab(o.heard,src.Never))
print(src[o.heard=='Yes'].sum())
rs=d.iloc[:,52:60];print(rs.sum(), rs.notna().sum(axis=0).max(), (o.vacc_any==0).sum())
en=d.iloc[:,73:79];print(en.sum())
for cols,nm in [(['age','health','pedu_uni','sti_any','heard_yes','pdisc_any','know'],'A'),(['age','health','pedu_uni','sti_any','heard_yes','pdisc_any','know','att'],'B')]:
    X=o[cols+['accept']].dropna(); y=X.pop('accept'); Xc=sm.add_constant(X.astype(float)); m=sm.Logit(y,Xc).fit(disp=0)
    ci=m.conf_int(); print(nm,len(y),int(y.sum()),'\n',pd.DataFrame({'AOR':np.exp(m.params),'lo':np.exp(ci[0]),'hi':np.exp(ci[1]),'p':m.pvalues}).round(3))
    print('AUC',roc_auc_score(y,m.predict(Xc)),'LLR p',m.llr_pvalue,'McF',m.prsquared,'maxVIF',max(vif(Xc.values,i) for i in range(1,Xc.shape[1])))
    n=len(y);ll0=m.llnull;ll=m.llf;cs=1-np.exp(2*(ll0-ll)/n);print('Nagelkerke',cs/(1-np.exp(2*ll0/n)))
# unadjusted ORs
for v in ['age','health','pedu_uni','sti_any','heard_yes','pdisc_any','taboo_any','prog_yes','know','att']:
    X=o[[v,'accept']].dropna();m=sm.Logit(X.accept,sm.add_constant(X[[v]].astype(float))).fit(disp=0);print(v,np.exp(m.params[v]).round(2),np.exp(m.conf_int().loc[v]).round(2).tolist(),round(m.pvalues[v],4))
# restricted intention among unvaccinated/not sure
u=o[(o.vacc_any==0)&o.intent.notna()];print(len(u),u.accept.mean())
print(pd.crosstab(u.heard,u.accept))
# barriers, item-level
B=o[[f'B{i}' for i in range(1,9)]];print(B.describe().T[['count','mean','std']]);print((B>=4).mean())
print(o.B1.value_counts().sort_index())
print(o.video.value_counts(),o.compulsory.value_counts(),o.school_incl.value_counts(),o.provider_rec.value_counts())
print(o.faculty.value_counts())
print(o.accept_cat.value_counts())
