import sys, json; sys.path.insert(0,'scripts')
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.metrics import roc_auc_score
import prep
d=pd.read_excel(prep.P); o=pd.read_pickle('scripts/o.pkl'); Kr=pd.read_pickle('scripts/Kr.pkl')
N=len(o); res={}
def pf(p):
    return '$<$0.001' if p<0.001 else f'{p:.3f}'
def pct(n,t): return f'{n} ({100*n/t:.1f})'
def esc(s): return str(s).replace('&','\\&').replace('%','\\%').replace('_','\\_')
def chi_p(ct):
    ct=np.asarray(ct)
    chi,p,_,e=stats.chi2_contingency(ct,correction=False)
    if ct.shape==(2,2) and (e<5).any(): return stats.fisher_exact(ct)[1],'F'
    return p,'$\\chi^2$'
def wr(name,txt): open(f'tables/{name}.tex','w').write(txt)
# ---------- Table 1
L=[];
def sec(t): L.append(f'\\multicolumn{{3}}{{l}}{{\\textbf{{{t}}}}} \\\\')
def row(lab,n,t=N): L.append(f'\\quad {esc(lab)} & {n} & {100*n/t:.1f} \\\\')
sec('Age (years)'); L.append(f'\\quad Mean $\\pm$ SD & \\multicolumn{{2}}{{c}}{{{o.age.mean():.2f} $\\pm$ {o.age.std():.2f}}} \\\\')
L.append(f'\\quad Median (range) & \\multicolumn{{2}}{{c}}{{{o.age.median():.0f} ({o.age.min()}--{o.age.max()})}} \\\\')
for k,lab in [('18-21','18--21'),('22-23','22--23'),('24+','24 and above')]: row(lab,int((o.age_grp==k).sum()))
sec('Field of study')
for k,lab in [('Medical/Health Sciences/pharmacy/Nursing','Medical / Health sciences / Pharmacy / Nursing'),('Engineering /Technology','Engineering / Technology'),('Arts/Humanities','Arts / Humanities'),('Science','Science'),('Commerce/Business','Commerce / Business'),('Other','Other')]: row(lab,int((o.faculty==k).sum()))
sec('Academic stream (grouped)'); row('Healthcare',int(o.health.sum())); row('Non-healthcare',int((1-o.health).sum()))
sec("Parents' highest education")
pe=o.parent_edu.value_counts()
for k,lab in [('University/Higher education','University / higher education'),('Secondary school','Secondary school'),('Primary school','Primary school'),('No formal education','No formal education'),('Not sure','Not sure')]: row(lab,int(pe.get(k,0)))
L.append(f'\\quad Missing & {int(o.parent_edu.isna().sum())} & -- \\\\')
sec('Prior education/information on STIs')
for k,lab in [('Yes, formal class or curriculum','Yes, formal class or curriculum'),('Yes, through a health campaign','Yes, through a health campaign'),('No','No'),('Not sure','Not sure')]: row(lab,int((o.sti_edu==k).sum()))
sec('Had heard of HPV before the survey'); n=int((o.heard=='Yes').sum()); row('Yes',n); row('No',int((o.heard=='No').sum())); L.append(f'\\quad Missing & {int(o.heard.isna().sum())} & -- \\\\')
sec('Parents/guardians discussed HPV or its vaccine')
for k,lab in [('Yes, in detail','Yes, in detail'),('Briefly','Briefly'),('Never','Never'),('I am not sure what they think','Not sure what they think')]: row(lab,int((o.parent_disc==k).sum()))
sec('Discussing HPV considered taboo in own social context')
for k,lab in [('Yes, very much so','Yes, very much so'),('Somewhat','Somewhat'),('Not really','Not really'),('No','No')]: row(lab,int((o.taboo==k).sum()))
sec('University has provided an HPV vaccination awareness programme')
for k,lab in [('Yes','Yes'),('No','No'),('I am not aware of any','Not aware of any')]: row(lab,int((o.univ_prog==k).sum()))
sec('Self-rated knowledge of HPV and its vaccine')
for k in ['Excellent','Good','Moderate','Poor','None at all']: row(k,int((o.self_rate==k).sum()))
L.append(f'\\quad Missing & {int(o.self_rate.isna().sum())} & -- \\\\')
wr('t1_sociodemographic','\\begin{longtable}{@{}p{9.2cm}rr@{}}\n\\caption{Socio-demographic characteristics and background of the respondents ($N=231$).}\\label{tab:sociodemo}\\\\\n\\toprule\nCharacteristic & $n$ & \\% \\\\\n\\midrule\n\\endfirsthead\n\\caption[]{(continued)}\\\\\n\\toprule\nCharacteristic & $n$ & \\% \\\\\n\\midrule\n\\endhead\n\\midrule\\multicolumn{3}{r}{\\emph{continued on next page}}\\\\\n\\endfoot\n\\bottomrule\n\\endlastfoot\n'+'\n'.join(L)+'\n\\end{longtable}\n')
# ---------- Table 2 acceptance
cats=[('Fully vaccinated (all doses completed)','Fully vaccinated'),('Partially vaccinated','Partially vaccinated'),('Not vaccinated or unsure; "very likely" to accept','Very likely'),('Not vaccinated or unsure; "likely" to accept','Likely'),('Not vaccinated or unsure; "uncertain"','Uncertain'),('Not vaccinated or unsure; "very unlikely"','Very unlikely')]
L=[]; T=229
for lab,k in cats:
    n=int((o.accept_cat==k).sum()); L.append(f'{lab} & {n} & {100*n/T:.1f} \\\\')
acc=int(o.accept.sum()); 
body='\n'.join(L[:2])+'\n\\midrule\n'+'\n'.join(L[2:])
wr('t2_acceptance',f'''\\begin{{table}}[!htb]\\centering\\small
\\caption{{Vaccination status and intention to accept the HPV vaccine ($n=229$; two respondents who were unvaccinated did not answer the intention item).}}\\label{{tab:acceptance}}
\\begin{{tabular}}{{@{{}}p{{9.2cm}}rr@{{}}}}\\toprule
Category & $n$ & \\% \\\\\\midrule
{body}
\\midrule
\\textbf{{Accepting}} (vaccinated, or likely/very likely) & \\textbf{{{acc}}} & \\textbf{{{100*acc/T:.1f}}} \\\\
\\textbf{{Not accepting}} (uncertain or very unlikely) & \\textbf{{{T-acc}}} & \\textbf{{{100*(T-acc)/T:.1f}}} \\\\
\\bottomrule\\end{{tabular}}\\end{{table}}
''')
res['accept_n']=acc;res['accept_pct']=100*acc/T
# ---------- Table 3 item-wise knowledge
items=['HPV stands for Human Papillomavirus.','HPV can infect both males and females.','HPV infection often does not require treatment.','HPV can cause genital warts.','HPV can be passed on during sexual intercourse.','HPV infection can lead to cervical cancer.','HPV infection causes menstrual problems in women.\\textsuperscript{$\\dagger$}','Most people infected with HPV show no visible symptoms.','HPV is one of the most common sexually transmitted infections worldwide.','An HPV vaccine is currently available.','The HPV vaccine is most effective when given before sexual activity begins.','The HPV vaccine protects against all strains of HPV.\\textsuperscript{$\\dagger$}','Males can also benefit from the HPV vaccine.','A Pap smear can detect HPV-related abnormal cell changes in the cervix.','Condom use reduces, but does not eliminate, the risk of HPV transmission.']
L=[];kt=[]
for i in range(15):
    k=f'K{i+1}'; a=o[o.health==1][k].sum(); b=o[o.health==0][k].sum(); ct=[[a,95-a],[b,136-b]]; p,t=chi_p(ct)
    L.append(f'K{i+1} & {items[i]} & {o[k].sum()} ({100*o[k].mean():.1f}) & {a} ({100*a/95:.1f}) & {b} ({100*b/136:.1f}) & {pf(p)}{"\\textsuperscript{F}" if t=="F" else ""} \\\\')
    kt.append((i+1,o[k].mean()*100,a/95*100,b/136*100,p))
res['k_items']=kt
wr('t3_knowledge_items','''\\begin{table}[!htb]\\centering\\footnotesize
\\caption{Item-wise correct responses on the HPV knowledge statements, overall and by academic stream ($N=231$).}\\label{tab:kitems}
\\begin{tabular}{@{}l p{6.1cm} c c c c@{}}\\toprule
 & Statement & Overall & Healthcare & Non-healthcare & $p$ \\\\
 &  & $n$ (\\%) & $n$ (\\%) & $n$ (\\%) &  \\\\\\midrule
'''+'\n'.join(L)+'''
\\bottomrule\\end{tabular}

\\vspace{2pt}\\raggedright\\scriptsize \\textsuperscript{$\\dagger$}False statement (correct answer ``False''). All other statements are true. ``Not sure'' and missing responses were scored as incorrect. $p$ from Pearson's $\\chi^2$ test, or Fisher's exact test where marked \\textsuperscript{F}.
\\end{table}
''')
# ---------- Table 4 score summary
def ms(x): return f'{x.mean():.2f} $\\pm$ {x.std():.2f}'
def md(x): return f'{x.median():.2f} ({x.quantile(.25):.2f}--{x.quantile(.75):.2f})'
u,p=stats.mannwhitneyu(o[o.health==1].know,o[o.health==0].know); ku=(u,p)
u2,p2=stats.mannwhitneyu(o[o.health==1].att,o[o.health==0].att)
res.update(know_U=u,know_p=p,att_U=u2,att_p=p2)
def cc(v,k,g): return int(((o[v]==k)&(o.health==g)).sum())
kc=[(k,cc('know_cat',k,1),cc('know_cat',k,0)) for k in ['Poor','Moderate','Good']]
ac=[(k,cc('att_cat',k,1),cc('att_cat',k,0)) for k in ['Positive','Neutral','Negative']]
pk=stats.chi2_contingency([[x[1],x[2]] for x in kc])[1]
ta=[[87,117],[8,18],[0,1]]
pa=stats.fisher_exact([[87,117],[8,19]])[1]  # positive vs not positive
pk2=stats.chi2_contingency(np.array([[58,97],[37,39]]))[1]
res.update(kcat_p=pk,acat_p=pa,kpoor_p=pk2)
hk,nk,ha,na=o[o.health==1].know,o[o.health==0].know,o[o.health==1].att,o[o.health==0].att
Lk='\n'.join(f'\\quad {lab} & {a} ({100*a/95:.1f}) & {b} ({100*b/136:.1f}) & {a+b} ({100*(a+b)/231:.1f}) & \\\\' for lab,a,b in [(f'{k} ({r})',a,b) for (k,a,b),r in zip(kc,['0--7','8--11','12--15'])])
La='\n'.join(f'\\quad {lab} & {a} ({100*a/95:.1f}) & {b} ({100*b/136:.1f}) & {a+b} ({100*(a+b)/231:.1f}) & \\\\' for lab,a,b in [(f'{k} ({r})',a,b) for (k,a,b),r in zip(ac,['40--50','30--39','10--29'])])
wr('t4_scores',f'''\\begin{{table}}[!htb]\\centering\\footnotesize\\setlength{{\\tabcolsep}}{{4pt}}
\\caption{{Knowledge and attitude scores of healthcare and non-healthcare students ($N=231$).}}\\label{{tab:scores}}
\\begin{{tabular}}{{@{{}}p{{3.6cm}}cccc@{{}}}}\\toprule
 & Healthcare & Non-healthcare & Overall & $p$ \\\\
 & ($n=95$) & ($n=136$) & ($N=231$) &  \\\\\\midrule
\\textbf{{Knowledge score (0--15)}} &&&& \\\\
\\quad Mean $\\pm$ SD & {ms(hk)} & {ms(nk)} & {ms(o.know)} & {pf(p)}\\textsuperscript{{a}} \\\\
\\quad Median (IQR) & {md(hk)} & {md(nk)} & {md(o.know)} & \\\\
{Lk}
\\midrule
\\textbf{{Attitude score (10--50)}} &&&& \\\\
\\quad Mean $\\pm$ SD & {ms(ha)} & {ms(na)} & {ms(o.att)} & {pf(p2)}\\textsuperscript{{a}} \\\\
\\quad Median (IQR) & {md(ha)} & {md(na)} & {md(o.att)} & \\\\
{La}
\\bottomrule\\end{{tabular}}

\\vspace{{2pt}}\\raggedright\\scriptsize \\textsuperscript{{a}}Mann--Whitney $U$ test (knowledge $U={u:,.1f}$; attitude $U={u2:,.1f}$). Percentages are column percentages. Categories follow Bloom's cut-offs.
\\end{{table}}
''')
# ---------- Table 5 attitudes
lab5=['It is necessary to inform people about HPV infection.','It is necessary to inform people about the HPV vaccine.','It is necessary to inform women about HPV and its complications.','All young women should be vaccinated against HPV.','The HPV vaccine should be mandatory for women before marriage.','I recommend the HPV vaccine to my friends.','I would like to know more about the HPV vaccine.','HPV infection is a serious risk for women.','The high cost and difficulty in accessing the vaccine in Bangladesh are obstacles to vaccination.','A Pap smear test is necessary for HPV screening in women.']
L=[];at=[]
for i in range(10):
    s=o[f'A{i+1}'];v=s.dropna();n=len(v)
    cs=[int((v==k).sum()) for k in [1,2,3,4,5]]
    L.append(f'A{i+1} & {lab5[i]} & '+' & '.join(f'{100*c/n:.1f}' for c in cs)+f' & {v.mean():.2f} $\\pm$ {v.std():.2f} \\\\')
    at.append((i+1,[100*c/n for c in cs],v.mean()))
res['a_items']=at
wr('t5_attitude_items','''\\begin{table}[!htb]\\centering\\footnotesize
\\caption{Attitudes towards HPV prevention, screening and vaccination (row percentages; 5-point Likert scale).}\\label{tab:attitudes}
\\begin{tabular}{@{}l p{5.6cm} ccccc c@{}}\\toprule
 & Statement & SD & D & N & A & SA & Mean $\\pm$ SD \\\\\\midrule
'''+'\n'.join(L)+'''
\\bottomrule\\end{tabular}

\\vspace{2pt}\\raggedright\\scriptsize SD = strongly disagree, D = disagree, N = neutral, A = agree, SA = strongly agree. Item-level non-response was at most four respondents ($\\leq$1.7\\%).
\\end{table}
''')
# ---------- Table 6 barriers
bl=['Lack of awareness about HPV and the vaccine','Cost of the vaccine','Fear of side effects','Cultural or religious concerns','Belief that the vaccine is not necessary','Lack of healthcare-provider recommendation','Limited availability in health facilities','Feeling ashamed or judged because of STIs']
bar=[]
for i in range(8):
    s=o[f'B{i+1}'].dropna(); bar.append((bl[i],s.mean(),s.std(),100*(s>=4).mean(),len(s),[100*(s==k).mean() for k in range(1,6)]))
bar.sort(key=lambda x:-x[1]); res['barriers']=bar
L=[f'{i+1} & {b[0]} & {b[4]} & {b[1]:.2f} $\\pm$ {b[2]:.2f} & {b[3]:.1f} \\\\' for i,b in enumerate(bar)]
wr('t6_barriers','''\\begin{table}[!htb]\\centering\\small
\\caption{Perceived barriers to HPV vaccination, ranked by mean rating (1--5 scale; higher = greater barrier).}\\label{tab:barriers}
\\begin{tabular}{@{}c p{7.0cm} c c c@{}}\\toprule
Rank & Barrier & $n$ & Mean $\\pm$ SD & Rated 4--5 (\\%) \\\\\\midrule
'''+'\n'.join(L)+'''
\\bottomrule\\end{tabular}\\end{table}
''')
# ---------- Table 7 bivariate
def biv(v,labels,title,test='chi'):
    out=[];ct=pd.crosstab(o[v],o.accept);p,t=chi_p(ct.loc[[k for k,_ in labels]].values)
    first=True
    for k,lab in labels:
        a=int(ct.loc[k,1]);b=int(ct.loc[k,0]);tot=a+b
        out.append(f'\\quad {lab} & {tot} & {a} ({100*a/tot:.1f}) & {b} ({100*b/tot:.1f}) & '+((pf(p)+('\\textsuperscript{F}' if t=='F' else '')) if first else '')+' \\\\'); first=False
    return [f'\\multicolumn{{5}}{{l}}{{\\textbf{{{title}}}}} \\\\']+out
L=[]
L+=biv('age_grp',[('18-21','18--21'),('22-23','22--23'),('24+','24 and above')],'Age (years)')
L+=biv('grp',[('Healthcare','Healthcare'),('Non-healthcare','Non-healthcare')],'Academic stream')
L+=biv('pedu_uni',[(1.0,'University / higher'),(0.0,'Below university or unsure')],"Parents' education")
L+=biv('sti_any',[(1,'Yes'),(0,'No / not sure')],'Prior STI education')
L+=biv('heard_yes',[(1.0,'Yes'),(0.0,'No')],'Had heard of HPV before the survey')
L+=biv('pdisc_any',[(1,'Yes (brief or detailed)'),(0,'Never / unsure')],'Parental discussion of HPV')
L+=biv('taboo_any',[(1.0,'Taboo (very much / somewhat)'),(0.0,'Not taboo')],'Discussing HPV is taboo')
L+=biv('prog_yes',[(1,'Yes'),(0,'No / not aware')],'University awareness programme')
L+=biv('know_cat',[('Poor','Poor (0--7)'),('Moderate','Moderate (8--11)'),('Good','Good (12--15)')],'Knowledge level')
# attitude: positive vs not
o['att_bin']=np.where(o.att>=40,'Positive','Not positive'); 
L+=biv('att_bin',[('Positive','Positive ($\\geq$40)'),('Not positive','Neutral/negative ($<$40)')],'Attitude level')
rows=[]
for v,l in [('know','Knowledge score'),('att','Attitude score'),('age','Age (years)')]:
    x=o[o.accept==1][v];y=o[o.accept==0][v];U,p=stats.mannwhitneyu(x,y)
    rows.append(f'\\quad {l}, mean $\\pm$ SD & -- & {x.mean():.2f} $\\pm$ {x.std():.2f} & {y.mean():.2f} $\\pm$ {y.std():.2f} & {pf(p)}\\textsuperscript{{M}} \\\\'); res[f'acc_{v}']=(x.mean(),y.mean(),U,p)
L+=['\\multicolumn{5}{l}{\\textbf{Continuous variables}} \\\\']+rows
wr('t7_bivariate','''\\begin{table}[!htb]\\centering\\footnotesize
\\caption{Association of respondent characteristics with acceptance of HPV vaccination ($n=229$).}\\label{tab:bivariate}
\\begin{tabular}{@{}p{5.2cm} c c c c@{}}\\toprule
Variable & Total & Accepting & Not accepting & $p$ \\\\
 & $n$ & $n$ (row \\%) & $n$ (row \\%) &  \\\\\\midrule
'''+'\n'.join(L)+'''
\\bottomrule\\end{tabular}

\\vspace{2pt}\\raggedright\\scriptsize $p$ from Pearson's $\\chi^2$ test (Fisher's exact test where marked \\textsuperscript{F}; Mann--Whitney $U$ test where marked \\textsuperscript{M}). Totals vary slightly because of missing responses.
\\end{table}
''')
# ---------- Table 8 logistic
def fit(cols):
    X=o[cols+['accept']].dropna(); y=X.pop('accept'); Xc=sm.add_constant(X.astype(float)); m=sm.Logit(y,Xc).fit(disp=0)
    ci=m.conf_int(); df=pd.DataFrame({'OR':np.exp(m.params),'lo':np.exp(ci[0]),'hi':np.exp(ci[1]),'p':m.pvalues})
    n=len(y);ll0=m.llnull;cs=1-np.exp(2*(ll0-m.llf)/n)
    return m,df,dict(n=n,ev=int(y.sum()),auc=roc_auc_score(y,m.predict(Xc)),nag=cs/(1-np.exp(2*ll0/n)),llr=m.llr_pvalue)
colsA=['age','health','pedu_uni','sti_any','heard_yes','pdisc_any','know']; colsB=colsA+['att']
mA,dA,sA=fit(colsA); mB,dB,sB=fit(colsB)
lab={'age':'Age (per year)','health':'Healthcare stream (vs non-healthcare)','pedu_uni':"Parent with university education (vs not)",'sti_any':'Prior STI education (vs none/unsure)','heard_yes':'Had heard of HPV (vs not)','pdisc_any':'Parents discussed HPV (vs never/unsure)','know':'Knowledge score (per point)','att':'Attitude score (per point)'}
un={}
for v in colsB:
    X=o[[v,'accept']].dropna();m=sm.Logit(X.accept,sm.add_constant(X[[v]].astype(float))).fit(disp=0);ci=np.exp(m.conf_int().loc[v]);un[v]=(np.exp(m.params[v]),ci[0],ci[1],m.pvalues[v])
def f3(t): return f'{t[0]:.2f} ({t[1]:.2f}--{t[2]:.2f})'
L=[]
for v in colsB:
    a=dA.loc[v] if v in dA.index else None; b=dB.loc[v]
    L.append(f'{lab[v]} & {f3(un[v])} & {pf(un[v][3])} & '+(f'{a.OR:.2f} ({a.lo:.2f}--{a.hi:.2f}) & {pf(a.p)}' if a is not None else '-- & --')+f' & {b.OR:.2f} ({b.lo:.2f}--{b.hi:.2f}) & {pf(b.p)} \\\\')
wr('t8_logistic',f'''\\begin{{table}}[!htb]\\centering\\footnotesize
\\caption{{Logistic regression of factors associated with acceptance of HPV vaccination.}}\\label{{tab:logistic}}
\\setlength{{\\tabcolsep}}{{3.5pt}}
\\begin{{tabular}}{{@{{}}p{{3.9cm}} cc cc cc@{{}}}}\\toprule
 & \\multicolumn{{2}}{{c}}{{Unadjusted}} & \\multicolumn{{2}}{{c}}{{Model 1}} & \\multicolumn{{2}}{{c}}{{Model 2}} \\\\
\\cmidrule(lr){{2-3}}\\cmidrule(lr){{4-5}}\\cmidrule(lr){{6-7}}
Variable & OR (95\\% CI) & $p$ & AOR (95\\% CI) & $p$ & AOR (95\\% CI) & $p$ \\\\\\midrule
'''+'\n'.join(L)+f'''
\\midrule
$n$ analysed (accepting) & \\multicolumn{{2}}{{c}}{{--}} & \\multicolumn{{2}}{{c}}{{{sA['n']} ({sA['ev']})}} & \\multicolumn{{2}}{{c}}{{{sB['n']} ({sB['ev']})}} \\\\
Nagelkerke $R^2$ & \\multicolumn{{2}}{{c}}{{--}} & \\multicolumn{{2}}{{c}}{{{sA['nag']:.3f}}} & \\multicolumn{{2}}{{c}}{{{sB['nag']:.3f}}} \\\\
AUC & \\multicolumn{{2}}{{c}}{{--}} & \\multicolumn{{2}}{{c}}{{{sA['auc']:.3f}}} & \\multicolumn{{2}}{{c}}{{{sB['auc']:.3f}}} \\\\
\\bottomrule\\end{{tabular}}

\\vspace{{2pt}}\\raggedright\\scriptsize OR = odds ratio; AOR = adjusted odds ratio; CI = confidence interval. Outcome: accepting (1) vs not accepting (0). Model 1 includes socio-demographic variables, prior awareness and knowledge score; Model 2 additionally adjusts for attitude score. Respondents with missing data on any model variable were excluded.
\\end{{table}}
''')
res['A']=dict(df=dA.round(4).to_dict(),**sA); res['B']=dict(df=dB.round(4).to_dict(),**sB); res['un']={k:list(map(float,v)) for k,v in un.items()}
# sensitivity restricted to not-vaccinated
u=o[(o.vacc_any==0)&o.intent.notna()]
Xs=u[colsB+['accept']].dropna(); ys=Xs.pop('accept'); ms_=sm.Logit(ys,sm.add_constant(Xs.astype(float))).fit(disp=0); ci=np.exp(ms_.conf_int())
res['sens']=dict(n=len(ys),ev=int(ys.sum()),df=pd.DataFrame({'OR':np.exp(ms_.params),'lo':ci[0],'hi':ci[1],'p':ms_.pvalues}).round(4).to_dict())
# ---------- Table 9 support
def dist(v,order,labs):
    s=o[v].dropna(); return [int((s==k).sum()) for k in order], len(s)
L=[]
for v,title,order in [('provider_rec','A recommendation from a healthcare provider would increase my likelihood of vaccination',['Definitely yes','Probably yes','Not sure','Probably not','Definitely not']),
 ('video','A short educational video or workshop would improve my vaccination intention',['Definitely yes','Probably yes','Not sure','Probably not','No']),
 ('school_incl','HPV vaccination should be part of school/college/university health programmes',['Strongly agree','Agree','Neutral','Disagree','Strongly disagree']),
 ('compulsory','HPV education should be compulsory in the academic curriculum',['Strongly agree','Agree','Neutral','Disagree','Strongly disagree'])]:
    c,n=dist(v,order,None); L.append(f'{title} & {n} & '+' & '.join(f'{x} ({100*x/n:.1f})' for x in c)+' \\\\')
    res[f'sup_{v}']=(c,n)
wr('t9_support','''\\begin{table}[!htb]\\centering\\scriptsize
\\caption{Views on provider recommendation, educational interventions and institutional policy, $n$ (\\%).}\\label{tab:support}
\\setlength{\\tabcolsep}{3pt}
\\begin{tabular}{@{}p{4.9cm} c c c c c c@{}}\\toprule
Statement & $n$ & \\shortstack{Definitely yes /\\\\strongly agree} & \\shortstack{Probably yes /\\\\agree} & Not sure / neutral & \\shortstack{Probably not /\\\\disagree} & \\shortstack{Definitely not /\\\\strongly disagree} \\\\\\midrule
'''+'\n'.join(L)+'''
\\bottomrule\\end{tabular}\\end{table}
''')
json.dump(res,open('scripts/results.json','w'),default=lambda x:float(x) if isinstance(x,(np.floating,np.integer)) else str(x),indent=1)
print(json.dumps({k:res[k] for k in ['know_U','know_p','att_U','att_p','kcat_p','acat_p','kpoor_p','acc_know','acc_att','acc_age','sens']},default=float)[:1500])
print(dA.round(3));print(dB.round(3));print(sA,sB)
