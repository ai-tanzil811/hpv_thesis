import sys,json;sys.path.insert(0,'scripts')
import numpy as np,pandas as pd,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.ticker
import prep
d=pd.read_excel(prep.P);o=pd.read_pickle('scripts/o.pkl');R=json.load(open('scripts/results.json'))
BL,OR_,GR='#2a78d6','#eb6834','#8a8a86'; INK='#1a1a1a'; MUT='#52514e'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.edgecolor':'#9a9a96','axes.labelcolor':INK,'text.color':INK,'xtick.color':MUT,'ytick.color':INK,'axes.spines.top':False,'axes.spines.right':False,'axes.titlesize':10,'axes.titleweight':'bold','legend.frameon':False})
def save(f,n):
    f.savefig(f'figures/{n}.pdf',bbox_inches='tight');f.savefig(f'figures/{n}.png',dpi=300,bbox_inches='tight');plt.close(f)
def hb(ax,labels,vals,color,fmt=lambda v:f'{v:.1f}%',xmax=None):
    y=np.arange(len(labels))[::-1];ax.barh(y,vals,color=color,height=.62);ax.set_yticks(y);ax.set_yticklabels(labels)
    for yy,v in zip(y,vals): ax.text(v+(xmax or max(vals))*.012,yy,fmt(v),va='center',fontsize=8,color=INK)
    ax.grid(axis='x',color='#e6e6e2',lw=.6);ax.set_axisbelow(True)
# F1 acceptance composition
cats=['Fully vaccinated','Partially vaccinated','Very likely','Likely','Uncertain','Very unlikely']
n=[int((o.accept_cat==c).sum()) for c in cats];T=229
fig,ax=plt.subplots(figsize=(6.3,3.2))
cols=[BL,BL,BL,BL,OR_,OR_]; alpha=[1,.8,.62,.45,1,.75]
y=np.arange(6)[::-1]
for yy,v,c,a in zip(y,n,cols,alpha): ax.barh(yy,v,color=c,alpha=a,height=.62); ax.text(v+2,yy,f'{v} ({100*v/T:.1f}%)',va='center',fontsize=8)
ax.set_yticks(y);ax.set_yticklabels(['Fully vaccinated','Partially vaccinated','Very likely to accept','Likely to accept','Uncertain','Very unlikely to accept'])
ax.set_xlabel('Number of respondents');ax.set_xlim(0,100);ax.grid(axis='x',color='#e6e6e2',lw=.6);ax.set_axisbelow(True)
ax.set_title(f'Acceptance of HPV vaccination (n = 229)',loc='left')
ax.text(98,4.35,f'Accepting: {R["accept_n"]} ({R["accept_pct"]:.1f}%)',ha='right',color=BL,fontsize=9,fontweight='bold')
ax.text(98,0.85,f'Not accepting: {T-R["accept_n"]} ({100-R["accept_pct"]:.1f}%)',ha='right',color=OR_,fontsize=9,fontweight='bold')
save(fig,'fig_acceptance')
# F2 sources
src=d.iloc[:,30:37].copy();src.columns=['School / university curriculum','Healthcare provider','Family or friends','Social media','Television / radio','Newspaper / magazine','Health awareness campaigns']
s=src[o.heard=='Yes'].sum().sort_values(ascending=False);nn=int((o.heard=='Yes').sum())
fig,ax=plt.subplots(figsize=(6.3,3.0));hb(ax,list(s.index),100*s.values/nn,BL,xmax=60);ax.set_xlim(0,62);ax.set_xlabel(f'Respondents who had heard of HPV (%; n = {nn}; multiple responses allowed)')
ax.set_title('First source of information about HPV',loc='left');save(fig,'fig_sources')
# F3 knowledge items
k=np.array(R['k_items']);short=['HPV = Human Papillomavirus','Infects both males and females','Often needs no treatment','Can cause genital warts','Passed on during sex','Can lead to cervical cancer','Causes menstrual problems (F)','Most infections show no symptoms','Common STI worldwide','A vaccine is available','Vaccine best before sexual activity','Vaccine protects all strains (F)','Males can benefit from vaccine','Pap smear detects cell changes','Condoms reduce, not eliminate, risk']
idx=np.argsort(k[:,1]);fig,ax=plt.subplots(figsize=(6.5,5.2));y=np.arange(15)
ax.hlines(y,k[idx,2],k[idx,3],color='#c8c8c4',lw=1.2,zorder=1)
ax.scatter(k[idx,2],y,color=BL,s=34,zorder=3,label='Healthcare');ax.scatter(k[idx,3],y,color=OR_,s=34,marker='D',zorder=3,label='Non-healthcare')
ax.set_yticks(y);ax.set_yticklabels([f'K{int(k[i,0])}  {short[i]}' for i in idx],fontsize=8);ax.set_xlim(0,100);ax.set_xlabel('Correct responses (%)')
ax.axvline(50,color='#b0b0ac',lw=.8,ls=':');ax.grid(axis='x',color='#e6e6e2',lw=.6);ax.set_axisbelow(True)
ax.legend(loc='lower right');ax.set_title('Item-wise correct knowledge responses by academic stream',loc='left');save(fig,'fig_knowledge_items')
# F4 knowledge distribution + categories
fig,(a1,a2)=plt.subplots(1,2,figsize=(7.0,3.1),gridspec_kw={'width_ratios':[1.5,1],'wspace':.45})
xs=np.arange(16);hh=np.bincount(o[o.health==1].know,minlength=16);nn_=np.bincount(o[o.health==0].know,minlength=16)
a1.bar(xs-.2,hh,.4,color=BL,label='Healthcare');a1.bar(xs+.2,nn_,.4,color=OR_,label='Non-healthcare')
a1.axvline(7.5,color=MUT,lw=.8,ls=':');a1.axvline(11.5,color=MUT,lw=.8,ls=':');a1.set_xlabel('Knowledge score (0–15)');a1.set_ylabel('Respondents');a1.legend(loc='upper right',fontsize=8)
a1.set_xticks(range(0,16,1));a1.tick_params(axis='x',labelsize=7.5);a1.set_title('(a) Score distribution',loc='left',fontsize=9)

g=['Healthcare','Non-healthcare'];tot=[95,136];cc=[[58,26,11],[97,29,10]]
labs=['Poor','Moderate','Good'];left=np.zeros(2);sh=np.array([[100*c/t for c in r] for r,t in zip(cc,tot)])
for j,l in enumerate(labs):
    a2.barh([1,0],sh[:,j],left=left,color=['#cfdff3','#7fb0e8',BL][j],height=.55,label=l,edgecolor='white',linewidth=1.5)
    for yy,(v,lf) in enumerate(zip(sh[:,j],left)):
        if v>=13: a2.text(lf+v/2,[1,0][yy],f'{v:.0f}%',ha='center',va='center',fontsize=8,color=INK if j<2 else 'white')
    left+=sh[:,j]
a2.set_yticks([1,0]);a2.set_yticklabels(g,fontsize=8);a2.set_xlim(0,100);a2.set_xlabel('Respondents (%)')
a2.legend(ncol=3,loc='upper center',bbox_to_anchor=(.5,-.28),fontsize=7.5,handlelength=1,columnspacing=1);a2.set_title('(b) Knowledge level',loc='left',fontsize=9)
save(fig,'fig_knowledge_dist')
# F5 attitude diverging
a=R['a_items'];sh_=['Inform: HPV infection','Inform: HPV vaccine','Inform women of complications','All young women vaccinated','Mandatory before marriage','Recommend to friends','Want to know more','HPV is a serious risk','Cost / access are obstacles','Pap smear is necessary']
P=np.array([x[1] for x in a]);fig,ax=plt.subplots(figsize=(6.6,3.9))
cs=['#e2603a','#f3b49c','#d8d8d4','#9cc2ee',BL];names=['Strongly disagree','Disagree','Neutral','Agree','Strongly agree']
y=np.arange(10)[::-1]
neg=P[:,0]+P[:,1];left=-(neg+P[:,2]/2)
for j in range(5):
    w=P[:,j];ax.barh(y,w,left=left,color=cs[j],height=.62,edgecolor='white',linewidth=.8,label=names[j]);
    for yy,l,ww in zip(y,left,w):
        if ww>=7: ax.text(l+ww/2,yy,f'{ww:.0f}',ha='center',va='center',fontsize=7,color='white' if j in(0,4) else INK)
    left=left+w
ax.axvline(0,color=MUT,lw=.8);ax.set_yticks(y);ax.set_yticklabels([f'A{i+1}  {s}' for i,s in enumerate(sh_)],fontsize=8)
ax.set_xlim(-40,100);ax.set_xticks([-20,0,20,40,60,80,100]);ax.set_xticklabels(['20','0','20','40','60','80','100']);ax.set_xlabel('Respondents (%) — disagree to the left, agree to the right')
ax.legend(ncol=5,loc='upper center',bbox_to_anchor=(.45,1.14),fontsize=7,handlelength=1,columnspacing=1)
save(fig,'fig_attitudes')
# F6 barriers
b=R['barriers'];fig,ax=plt.subplots(figsize=(6.4,3.2));hb(ax,[x[0] for x in b],[x[1] for x in b],BL,fmt=lambda v:f'{v:.2f}',xmax=5)
ax.set_xlim(0,5);ax.set_xlabel('Mean rating (1–5; higher = greater perceived barrier)');ax.set_title('Perceived barriers to HPV vaccination',loc='left');save(fig,'fig_barriers')
# F7 acceptance by factor
fac=[('Had heard of HPV','heard_yes',[(1.0,'Yes'),(0.0,'No')]),('Knowledge level','know_cat',[('Poor','Poor'),('Moderate','Moderate'),('Good','Good')]),('Attitude level','att_bin',[('Positive','Positive'),('Not positive','Neutral/negative')]),('Academic stream','grp',[('Healthcare','Healthcare'),('Non-healthcare','Non-healthcare')]),('Parental discussion','pdisc_any',[(1,'Discussed'),(0,'Never/unsure')])]
o['att_bin']=np.where(o.att>=40,'Positive','Not positive')
rows=[]
for t,v,cl in fac:
    for k,l in cl:
        s=o[o[v]==k].accept.dropna();rows.append((t,l,100*s.mean(),len(s),s.sum()))
fig,ax=plt.subplots(figsize=(6.4,3.9));y=[];yl=[];yy=0;prev=None;ticks=[]
cmap={'Had heard of HPV':BL,'Knowledge level':BL,'Attitude level':BL,'Academic stream':GR,'Parental discussion':GR}
pos=[];
for t,l,p,nn_,aa in rows:
    if prev is not None and t!=prev: yy-=.7
    ax.barh(yy,p,color=cmap[t],height=.62);ax.text(p+1,yy,f'{p:.1f}%  (n={nn_})',va='center',fontsize=7.5,bbox=dict(fc='white',ec='none',pad=1.2));ticks.append((yy,f'{t}: {l}'));prev=t;yy-=1
ax.set_yticks([t[0] for t in ticks]);ax.set_yticklabels([t[1] for t in ticks],fontsize=8);ax.set_xlim(0,115);ax.set_xlabel('Respondents accepting HPV vaccination (%)');ax.grid(axis='x',color='#e6e6e2',lw=.6);ax.set_axisbelow(True)
ax.axvline(R['accept_pct'],color=OR_,lw=1,ls='--');ax.text(R['accept_pct']+.8,.55,'Overall 80.3%',color=OR_,fontsize=7.5,va='bottom')
ax.set_title('Acceptance by selected characteristics',loc='left');save(fig,'fig_acceptance_factors')
# F8 forest
dB=pd.DataFrame(R['B']['df']);dB=dB.drop('const');lab={'age':'Age (per year)','health':'Healthcare stream','pedu_uni':'Parent with university education','sti_any':'Prior STI education','heard_yes':'Had heard of HPV','pdisc_any':'Parents discussed HPV','know':'Knowledge score (per point)','att':'Attitude score (per point)'}
fig,ax=plt.subplots(figsize=(6.4,3.4));y=np.arange(len(dB))[::-1]
for yy,(i,r) in zip(y,dB.iterrows()):
    c=BL if r.p<.05 else GR;ax.plot([r.lo,r.hi],[yy,yy],color=c,lw=1.6);ax.scatter(r.OR,yy,color=c,s=34,zorder=3)
    ax.text(10.5,yy,f'{r.OR:.2f} ({r.lo:.2f}–{r.hi:.2f})',va='center',fontsize=7.5,ha='left')
ax.axvline(1,color=MUT,lw=.9,ls='--');ax.set_xscale('log');ax.set_xlim(.15,9);ax.set_xticks([.25,.5,1,2,4,8]);ax.set_xticklabels(['0.25','0.5','1','2','4','8'])
ax.set_yticks(y);ax.set_yticklabels([lab[i] for i in dB.index]);ax.set_xlabel('Adjusted odds ratio (log scale), Model 2')
ax.text(10.5,len(dB)-.4,'AOR (95% CI)',fontsize=7.5,fontweight='bold');ax.set_title('Factors associated with acceptance of HPV vaccination',loc='left')
ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator());ax.spines['bottom'].set_visible(True);save(fig,'fig_forest')
# F9 reasons + motivators
rs=d.iloc[:,52:60].copy();rs.columns=['Did not know about the vaccine','Concerned about safety/side effects','Thought the vaccine was only for females','Not available or affordable','Did not think I was at risk','Family or religion against it',"Doctor never recommended it",'Other']
rcount=rs.sum().sort_values(ascending=False);nr=int(d.iloc[:,52:60].notna().any(axis=1).sum())
en=d.iloc[:,73:79].copy();en.columns=['Free or subsidised vaccine',"Doctor's recommendation",'Educational campaign at university','Support from family/friends','Knowing someone affected by HPV disease','Vaccine available at campus health centre']
ec=en.sum().sort_values(ascending=False)
fig,(a1,a2)=plt.subplots(2,1,figsize=(6.4,6.0));hb(a1,list(rcount.index),100*rcount.values/nr,OR_,xmax=60);a1.set_xlim(0,62);a1.set_xlabel(f'Respondents not vaccinated (%; n = {nr})');a1.set_title('(a) Reasons for not being vaccinated',loc='left',fontsize=9.5)
hb(a2,list(ec.index),100*ec.values/231,BL,xmax=60);a2.set_xlim(0,62);a2.set_xlabel('All respondents (%; n = 231)');a2.set_title('(b) Factors that would encourage vaccination',loc='left',fontsize=9.5)
fig.tight_layout(h_pad=2);save(fig,'fig_reasons_motivators')
print(nr,rcount.to_dict(),ec.to_dict())
