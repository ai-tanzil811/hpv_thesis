import json
R=json.load(open('scripts/results.json'))
sd=R['sens']['df']
lab={'age':'Age (per year)','health':'Healthcare stream (vs non-healthcare)','pedu_uni':'Parent with university education','sti_any':'Prior STI education','heard_yes':'Had heard of HPV','pdisc_any':'Parents discussed HPV','know':'Knowledge score (per point)','att':'Attitude score (per point)'}
pf=lambda p:'$<$0.001' if p<.001 else f'{p:.3f}'
rows='\n'.join(f"{lab[k]} & {sd['OR'][k]:.2f} ({sd['lo'][k]:.2f}--{sd['hi'][k]:.2f}) & {pf(sd['p'][k])} \\\\" for k in lab)
q=[]
def sec(t): q.append(f'\\subsection*{{{t}}}')
def item(t,opts=None):
    s=f'\\item {t}'
    if opts: s+='\\\\\\hspace*{1em}\\textit{'+' / '.join(opts)+'}'
    q.append(s)
def begin(): q.append('\\begin{enumerate}[leftmargin=*,itemsep=3pt]')
def end(): q.append('\\end{enumerate}')
LK=['Strongly disagree','Disagree','Neutral','Agree','Strongly agree']
q.append(r'''\chapter{Appendix A: Survey Questionnaire}
\setstretch{1.1}\small
\textbf{Title of survey:} Knowledge, Attitudes, and Acceptance of HPV Vaccination Among Female Students.

\textbf{Consent statement.} This survey is part of an academic research study on knowledge, attitudes, and acceptance of HPV vaccination among students. Participation is completely voluntary and responses are anonymous and confidential. By continuing, the respondent agrees to take part. \textit{(Response: ``I agree to participate'')}

\textbf{Supervision.} The study is carried out under the supervision of Hasnat M.\ Alamgir, PhD, Director of IRT, Department of Pharmacy, Southeast University.
''')
sec('Section A: Socio-demographic information');begin()
item('Name of university',['free text']);item('Age',['years']);item('What is your current level of education?',['free text'])
item('Faculty / field of study',['Medical/Health Sciences/Pharmacy/Nursing','Engineering/Technology','Science','Arts/Humanities','Commerce/Business','Other'])
item('Where do you live?',['free text']);item('Home district',['free text'])
item("What is your parent's highest level of education?",['No formal education','Primary school','Secondary school','University/Higher education','Not sure'])
item('Have you previously received any formal education or information about sexually transmitted infections (STIs)?',['Yes, formal class or curriculum','Yes, through a health campaign','No','Not sure'])
end()
sec('Section B: Knowledge of HPV (True / False / Not sure)');begin()
for t in ['HPV stands for Human Papillomavirus.','HPV can infect both males and females.','HPV infection often does not require treatment.','HPV can cause genital warts.','HPV can be passed on during sexual intercourse.','HPV infection can lead to cervical cancer.','HPV infection causes menstrual problems in women.','The majority of people infected with HPV do not show visible symptoms.','HPV is one of the most common sexually transmitted infections worldwide.','An HPV vaccine is currently available.','The HPV vaccine is most effective when given before sexual activity begins.','The HPV vaccine protects against all strains of HPV.','Males can also benefit from receiving the HPV vaccine.','A Pap smear / cervical screening test can detect HPV-related abnormal cell changes in the cervix.','Condom use significantly reduces, but does not fully eliminate, the risk of HPV transmission.']: item(t)
end()
sec('Section C: Awareness of HPV');begin()
item('Have you ever heard about HPV (Human Papillomavirus) before this survey?',['Yes','No'])
item('Where did you first learn about HPV? (select all that apply)',['School / university curriculum','Healthcare provider / doctor','Family or friends','Social media (e.g., Facebook, Instagram, TikTok)','Television / radio','Newspaper / magazine','Health awareness campaigns','Never heard about it before'])
item('How would you rate your current knowledge about HPV and its vaccine?',['None at all','Poor','Moderate','Good','Excellent'])
end()
sec('Section D: Attitudes (5-point Likert scale: strongly disagree to strongly agree)');begin()
for t in ['It is necessary to inform people about ``HPV infection''.','It is necessary to inform people about ``HPV vaccine''.','It is necessary to inform women about HPV and its complications.','All young women should be vaccinated against the HPV virus.','HPV vaccine should be mandatory for women before marriage.','I recommend HPV vaccine to my friends.','I would like to know more about HPV vaccine.','HPV infection is a serious risk for women.','The high cost and difficulty in accessing the HPV vaccine in Bangladesh are obstacles to vaccination.','Pap smear test is necessary for HPV screening in women.']: item(t)
end()
sec('Section E: Vaccination status and intention');begin()
item('Have you ever received the HPV vaccine?',['No','Yes, partially vaccinated','Yes, all doses completed','Not sure'])
item('If you have NOT been vaccinated, what are the main reasons? (select all that apply)',['I did not know about the vaccine','I was concerned about safety or side effects','I thought the vaccine was only for females','The vaccine was not available or affordable','I did not think I was at risk','My family or religion was against it','My doctor never recommended it','Other'])
item('If you are not yet vaccinated, how likely are you to receive the HPV vaccine in the future?',['Very unlikely','Uncertain','Likely','Very likely'])
item('Would a recommendation from a healthcare provider increase your likelihood of getting vaccinated?',['Definitely yes','Probably yes','Not sure','Probably not','Definitely not'])
end()
sec('Section F: Perceived barriers (rated 1--5)');begin()
for t in ['Lack of awareness about HPV and the vaccine','Cost of the vaccine','Fear of side effects','Cultural or religious concerns','Belief that the vaccine is not necessary','Lack of healthcare provider recommendation','Limited availability in health facilities','Feeling ashamed or judged because of sexually transmitted infections (STIs)']: item(t)
end()
sec('Section G: Institutional and social context');begin()
item('Do you think HPV vaccination should be included in school / college / university health programmes?',LK)
item('Which of the following would most encourage you to get vaccinated? (select all that apply)',['Free or subsidised vaccine',"Doctor's recommendation",'Educational campaign at university','Support from family / friends','Knowing someone affected by HPV-related disease','Vaccine available at health centre'])
item('In your cultural or social context, is discussing HPV (a sexually transmitted infection) considered taboo?',['No','Not really','Somewhat','Yes, very much so'])
item('Did your parents or guardians ever discuss HPV or HPV vaccination with you?',['Never','Briefly','Yes, in detail','I am not sure what they think'])
item('Do you believe your field of study has improved your awareness of HPV?',LK)
item('Has your school / college / university provided any formal education or awareness programme about HPV vaccination?',['Yes','No','I am not aware of any'])
item('Would a short educational video or workshop about HPV significantly improve your vaccination intentions?',['Definitely yes','Probably yes','Not sure','Probably not','No'])
item('In your opinion, should HPV education be made compulsory in the academic curriculum?',LK)
item('What specific actions do you think the government should take to improve HPV vaccination rates among young people?',['open-ended'])
end()
q.append('\\vspace{6pt}\\textit{Thank you for your participation!}\n\\normalsize')
app='\n'.join(q)+r'''
\clearpage\setstretch{1.5}\normalsize
\chapter{Appendix B: Ethical Approval}
\fillin{Ethical approval letter to be added here: name of the approving committee, reference number and date of approval. Insert the scanned letter with \texttt{\textbackslash includegraphics} or \texttt{\textbackslash includepdf} from the \texttt{pdfpages} package.}

\clearpage
\chapter{Appendix C: Sensitivity Analysis}
\setstretch{1.2}
Table~\ref{tab:sens} repeats the multivariable model with attitude score (Model 2) among respondents who were unvaccinated or unsure of their status and who answered the intention question ($n=187$ with complete data, of whom 143 were likely or very likely to be vaccinated).

\begin{table}[!htb]\centering\small
\caption{Sensitivity analysis: logistic regression of intention to be vaccinated among unvaccinated or unsure students.}\label{tab:sens}
\begin{tabular}{@{}p{6.5cm}cc@{}}\toprule
Variable & AOR (95\% CI) & $p$ \\\midrule
'''+rows+r'''
\bottomrule\end{tabular}\end{table}
'''
open('chapters/appendices.tex','w').write(app)
