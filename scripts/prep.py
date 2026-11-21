import pandas as pd, numpy as np, re
P="/mnt/user-data/attachments/3c374fb7-7657-57c2-9adf-784be8374b3c/239f9086-Knowledge_Attitudes_and_Acceptance_of_HPV_Vaccination_Among_Female_Students_-_all_versions_-_labels_-_2026-10-29-18-22-44.xlsx"
def load():
    d=pd.read_excel(P); c=list(d.columns)
    o=pd.DataFrame(index=d.index)
    S=lambda i:d.iloc[:,i].astype('string').str.strip().str.replace('\xa0','',regex=False).str.strip()
    o['age']=d.iloc[:,5]
    f=S(7); o['faculty']=f
    o['health']=(f.str.startswith('Medical')).astype(int)
    o['parent_edu']=S(10)
    o['sti_edu']=S(11)
    o['heard']=S(28)
    o['self_rate']=S(38)
    # knowledge
    ans=[S(i) for i in range(13,28)]
    keys=['True']*15; keys[6]='False'; keys[11]='False'
    K=pd.DataFrame({f'K{i+1}':(ans[i]==keys[i]).fillna(False).astype(int) for i in range(15)})
    Kr=pd.DataFrame({f'K{i+1}':ans[i] for i in range(15)})
    o=pd.concat([o,K],axis=1)
    o['know']=K.sum(axis=1)
    o['know_cat']=pd.cut(o.know,[-1,7,11,15],labels=['Poor','Moderate','Good'])
    # attitude
    mp={'Strongly disagree':1,'Disagree':2,'Neutral':3,'Agree':4,'Strongly Agree':5}
    A=pd.DataFrame({f'A{i-39}':S(i).str.title().map({k.title():v for k,v in mp.items()}) for i in range(40,50)})
    o=pd.concat([o,A],axis=1)
    o['att']=A.sum(axis=1,min_count=1)
    o['att_n']=A.notna().sum(axis=1)
    o['att_pos']=(o.att>=40).astype(int)
    o['vacc']=S(50)
    o['intent']=S(60)
    o['provider_rec']=S(61)
    o['taboo']=S(79); o['parent_disc']=S(80); o['field_improved']=S(81); o['univ_prog']=S(82)
    o['video']=S(83); o['compulsory']=S(84); o['school_incl']=S(71)
    # barriers
    B=d.iloc[:,63:71].copy(); B.columns=[f'B{i}' for i in range(1,9)]
    o=pd.concat([o,B],axis=1)
    # outcome
    vacc_any=o.vacc.str.startswith('Yes').fillna(False)
    intent_pos=o.intent.isin(['Likely','Very likely']).fillna(False)
    o['vacc_any']=vacc_any.astype(int)
    o['accept']=(vacc_any|intent_pos).astype(int)
    o['accept_cat']=np.select([(o.vacc=='Yes, all doses completed').fillna(False).to_numpy(bool),(o.vacc=='Yes, partially vaccinated').fillna(False).to_numpy(bool),(o.intent=='Very likely').fillna(False).to_numpy(bool),(o.intent=='Likely').fillna(False).to_numpy(bool),(o.intent=='Uncertain').fillna(False).to_numpy(bool),(o.intent=='Very unlikely').fillna(False).to_numpy(bool)],
        ['Fully vaccinated','Partially vaccinated','Very likely','Likely','Uncertain','Very unlikely'],'Missing')
    return d,o,Kr
if __name__=='__main__':
    d,o,Kr=load()
    print(o.accept_cat.value_counts()); print(o.accept.value_counts())
    print(o.know.describe(), o.att.describe(), o.att_n.value_counts())
    print(o.know_cat.value_counts(), o.att_pos.mean())
    print(o[[f'K{i}' for i in range(1,16)]].mean().round(3).to_string())
    print(o[o.accept_cat=='Missing'][['vacc','intent']].value_counts())
    print(Kr.apply(lambda s:s.value_counts()).T)
    print(pd.crosstab(o.health,o.accept,margins=True))
