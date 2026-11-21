import sys, json; sys.path.insert(0,'scripts')
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from prep import load
d,o,Kr=load()
A=o[[f'A{i}' for i in range(1,11)]]
o['att']=A.apply(lambda r:r.fillna(r.mean()),axis=1).sum(axis=1)
o['att_pos']=(o.att>=40).astype(int)
o['att_cat']=pd.cut(o.att,[0,29.99,39.99,50],labels=['Negative','Neutral','Positive'])
o.loc[o.accept_cat=='Missing','accept']=np.nan
o['grp']=np.where(o.health==1,'Healthcare','Non-healthcare')
o['age_grp']=pd.cut(o.age,[0,21,23,99],labels=['18-21','22-23','24+'])
o['pedu_uni']=np.where(o.parent_edu.isna(),np.nan,(o.parent_edu=='University/Higher education').astype(float))
o['sti_any']=o.sti_edu.str.startswith('Yes').astype(int)
o['pdisc_any']=o.parent_disc.isin(['Briefly','Yes, in detail']).astype(int)
o['taboo_any']=o.taboo.isin(['Yes, very much so','Somewhat']).astype(float); o.loc[o.taboo.isna(),'taboo_any']=np.nan
o['prog_yes']=(o.univ_prog=='Yes').astype(int)
o['heard_yes']=np.where(o.heard.isna(),np.nan,(o.heard=='Yes').astype(float))
o['bar_mean']=o[[f'B{i}' for i in range(1,9)]].mean(axis=1)
o.to_pickle('scripts/o.pkl'); Kr.to_pickle('scripts/Kr.pkl')
def mwu(x,y):
    x,y=x.dropna(),y.dropna(); u,p=stats.mannwhitneyu(x,y,alternative='two-sided'); return u,p
R={}
# knowledge / attitude by group
for v in ['know','att','age']:
    h=o[o.health==1][v];n=o[o.health==0][v]; u,p=mwu(h,n)
    R[v]=dict(all=(o[v].mean(),o[v].std(),o[v].median(),o[v].quantile(.25),o[v].quantile(.75)),h=(h.mean(),h.std()),n=(n.mean(),n.std()),U=u,p=p)
    print(v,R[v])
for v in ['know_cat','att_cat']:
    ct=pd.crosstab(o.grp,o[v]);print(ct, stats.chi2_contingency(ct)[:2]); print(o[v].value_counts())
rho=stats.spearmanr(o.know,o.att);print('spearman know-att',rho)
print('rho know-barmean',stats.spearmanr(o.know,o.bar_mean))
print('accept by group'); print(pd.crosstab(o.grp,o.accept,margins=True), stats.chi2_contingency(pd.crosstab(o.grp,o.accept))[:2])
print(o.accept.value_counts(dropna=True), o.accept.mean())
# bivariate
rows=[]
cats=['age_grp','grp','pedu_uni','sti_any','heard_yes','pdisc_any','taboo_any','prog_yes','know_cat','att_cat','self_rate','provider_rec']
for v in cats:
    ct=pd.crosstab(o[v],o.accept)
    chi,p,_,e=stats.chi2_contingency(ct)
    if (e<5).mean()>0.2 and ct.shape==(2,2): p=stats.fisher_exact(ct)[1]
    print('\n',v,round(p,4));print(pd.concat([ct,(ct[1]/ct.sum(axis=1)*100).round(1)],axis=1))
for v in ['age','know','att','bar_mean']:
    u,p=mwu(o[o.accept==1][v],o[o.accept==0][v]);print(v,o[o.accept==1][v].mean(),o[o.accept==0][v].mean(),u,p)
# logistic
def fit(cols):
    X=o[cols+['accept']].dropna(); y=X.pop('accept'); X=sm.add_constant(X.astype(float)); m=sm.Logit(y,X).fit(disp=0)
    ci=m.conf_int(); out=pd.DataFrame({'AOR':np.exp(m.params),'lo':np.exp(ci[0]),'hi':np.exp(ci[1]),'p':m.pvalues}); 
    return m,out,len(y)
m1c=['age','health','pedu_uni','sti_any','pdisc_any','taboo_any','know']
m1,t1,n1=fit(m1c);print(n1,t1.round(3), m1.prsquared, 'AUC')
from sklearn.metrics import roc_auc_score
