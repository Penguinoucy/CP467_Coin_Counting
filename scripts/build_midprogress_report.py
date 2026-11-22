"""Build figures, editable report text and a measured five-page report + references.
Uses existing predictions and metrics only; does not tune or run an experiment.
"""
from pathlib import Path
import csv,json,sys,math,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from PIL import Image,ImageOps
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape
DATA=ROOT/'reports/generated'
G=ROOT/'reports/generated'
G.mkdir(exist_ok=True)
KEYS=['hough_off','hough_on','contours_off','contours_on']
NAMES=['Hough off','Hough on','Contours off','Contours on']
def read(p):return json.loads(p.read_text())
def rows(name):return list(csv.DictReader((DATA/name).open()))
summary=rows('summary.csv');conditions=rows('conditions.csv')
metrics={k:read(ROOT/f'outputs/midprogress/development/{k}/evaluation/metrics.json')['results']['per_image'] for k in KEYS}
preds={k:read(ROOT/f'outputs/midprogress/development/{k}/predictions.json')['images'] for k in KEYS}
# Both previously shown examples; no new experiments or changed scores.
examples=['layout03_dark_directional','layout10_dark_diffuse']
fig,axes=plt.subplots(2,4,figsize=(7.2,7.0))
fig.subplots_adjust(left=.015,right=.985,bottom=.025,top=.88,wspace=.10,hspace=.49)
for row,example in enumerate(examples):
    label=read(ROOT/f'data/labels/{example}.json')
    original=ImageOps.exif_transpose(Image.open(ROOT/f'data/images/{example}.jpg')).convert('RGB')
    original.thumbnail((1200,1200));sx=original.width/label['image_width'];sy=original.height/label['image_height']
    fig.text(.015,.975 if row==0 else .475,f'{example} | {label["coin_count"]} actual coins',fontsize=12,weight='bold',va='top')
    for key,title,ax in zip(KEYS,NAMES,axes[row]):
        p=next(x for x in preds[key] if x['image_id']==example)
        m=next(x for x in metrics[key] if x['image_id']==example)
        ax.imshow(original)
        matched={a for a,b in m['matches']}
        for i,c in enumerate(p['coins']):
            colour='#00ff66' if i in matched else '#ff3030'
            if 'radius' in c:ax.add_patch(Circle((c['x']*sx,c['y']*sy),c['radius']*(sx+sy)/2,fill=False,color=colour,lw=1.0))
            else:ax.plot(c['x']*sx,c['y']*sy,'+',color=colour,ms=6,mew=1.5)
        for i in m['unmatched_labels']:
            c=label['coins'][i];ax.add_patch(Circle((c['x']*sx,c['y']*sy),c['radius']*(sx+sy)/2,fill=False,color='#00cfff',ls='--',lw=1.2))
        ax.set_title(f'{title}\nTP {m["tp"]} FP {m["fp"]} FN {m["fn"]}',fontsize=12,pad=5)
        ax.axis('off')
fig.savefig(G/'qualitative_comparison.png',dpi=300);plt.close(fig)
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Body12',fontName='Helvetica',fontSize=12,leading=15,spaceAfter=9))
styles.add(ParagraphStyle(name='Heading12',fontName='Helvetica-Bold',fontSize=12,leading=15,spaceAfter=10))
styles.add(ParagraphStyle(name='Title12',fontName='Helvetica-Bold',fontSize=12,leading=16,spaceAfter=12,alignment=TA_CENTER))
styles.add(ParagraphStyle(name='Cell12',fontName='Helvetica',fontSize=12,leading=14))
story=[];md=[]
def p(text,bold=False):
    story.append(Paragraph(text,styles['Heading12' if bold else 'Body12']));md.append(('### ' if bold else '')+text.replace('<b>','').replace('</b>','')+'\n')
def page():story.append(PageBreak());md.append('\n---\n')
def table(data,widths):
    t=Table([[Paragraph(escape(str(c)),styles['Cell12']) for c in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5edf4')),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,0),.6,colors.grey),('LINEBELOW',(0,1),(-1,-1),.25,colors.lightgrey)]))
    story.append(t);story.append(Spacer(1,10))
    md.append('\n'.join('| '+' | '.join(str(c) for c in row)+' |' for row in [data[0],['---']*len(data[0])]+data[1:])+'\n')
def fig(name,w,h):story.append(RLImage(str(G/name),width=w,height=h));md.append(f'![{name}](generated/{name})\n')
story.append(Paragraph('CP467 Group 3 - Mid-Progress Report (Draft)',styles['Title12']))
p('November 22, 2026. Kevin Zavitz; Haseeb Siddiqi; Andrew Lin; Sinthujan Jayaranjan; Camilo Castro-Espinel. Member-specific contributions require group confirmation.')
p('1. Project topic',True)
p('Coin Detection and Counting Across Lighting and Background Conditions. The goal is to locate visible coins and count them, comparing classical image-processing methods across controlled capture conditions. Denomination and monetary-value recognition are outside this implementation.')
p('2. Proposal recap',True)
p('We compare gradient Hough Circle Detection [1] with Otsu thresholding, morphological cleanup and external-contour detection [2-6]. Each method runs with CLAHE disabled and enabled [7], producing four configurations. The planned dataset has 40 arrangements photographed under two backgrounds and three lighting conditions (240 photographs). Touching and separated coins will be reported separately.')
p('3. Progress so far',True)
p('Working detectors, label conversion, split-aware runners, one-to-one matching, count/detection metrics, timing, CSV summaries, plots and a report builder are implemented. Twenty software tests passed, including exhaustive checks of small matching problems and synthetic detector/coordinate checks. These are implementation checks, not additional photo evidence. Raw VIA exports [9] are retained, including the three supplied replacements.')
p('4. Dataset available now',True)
p('Layouts 01-04 and 09-12 supply 48 readable photographs and 420 annotated coin instances: 20% of the planned photographs, representing only eight distinct arrangements. Development uses layouts 01, 03, 04, 09, 10 and 11 (36 photos, 306 instances). Validation uses layouts 02 and 12 (12 photos, 114 instances). All available arrangements contain separated coins.')
p('All six photos from an arrangement remain in one split. The full manifest reserves 28/4/8 arrangements for development/validation/test (168/24/48 photos). Independent human review and annotator identities are pending for all 48 supplied labels; all reported scores are provisional. No final-test or touching-coin images were evaluated.')
page()
p('5. Preliminary results: numeric evaluation',True)
p('A match requires a detected centre within half the labelled coin radius. The assignment maximizes the number of valid one-to-one matches, then minimizes total pixel distance [8]. Precision, recall and F1 aggregate coin detections. MAE is mean absolute count error per photo; Exact is the percentage of photos with the correct count. Coin identification can fail even when total counts agree.')
for split,title in [('development','Development: 36 photos / 6 arrangements'),('validation','Validation: 12 photos / 2 arrangements')]:
    p(title,True)
    data=[['Method / CLAHE','P','R','F1','MAE','Exact','ms']]
    for key,name in zip(KEYS,NAMES):
        method,on=key.split('_');r=next(r for r in summary if r['split']==split and r['method']==method and r['clahe']==on)
        data.append([name]+[f'{float(r[v]):.3f}' for v in ['precision','recall','f1','count_mae']]+[f'{100*float(r["exact_count_accuracy"]):.1f}%',f'{float(r["median_ms"]):.1f}'])
    table(data,[112,58,58,58,58,60,56])
p('A development-only search tried Hough accumulator thresholds 35, 45, 55 and 65, and contour circularity cutoffs 0.50, 0.65 and 0.80. Highest mean F1 across CLAHE off/on selected 65 and 0.50. These settings were then fixed for both variants and the validation run. Development scores reuse search images and are optimistic exploratory measurements.')
p('Hough without CLAHE has the highest validation F1 (0.969). Hough with CLAHE gives slightly higher recall, but 21 false positives versus 1 without CLAHE. Contours miss more coins. CLAHE improves development contour F1 but does not improve validation contour F1; two validation arrangements are insufficient for a general conclusion.')
p('Timing: one OpenCV thread, three warm-ups and ten timed repeats per image; table shows the median of per-image medians. Resize/preprocessing/detection are timed; disk I/O, drawing and evaluation are excluded. Max image side is 1200; predictions are restored to original coordinates. Timings were measured on Linux, AMD EPYC 9V74, Python 3.12.14 / OpenCV 5.1.0, not on a group member\'s Mac.')
page()
p('5. Preliminary results: conditions and capture groups',True)
p('Development F1 by background and lighting. Each row contains six photographs of six arrangements (51 coin instances). These photographs are correlated across conditions, so they must not be treated as 36 independent arrangements.')
data=[['Condition','Hough off','Hough on','Contours off','Contours on']]
for c in ['dark_diffuse','dark_dim','dark_directional','light_diffuse','light_dim','light_directional']:
    rr=[next(r for r in conditions if r['split']=='development' and r['condition']==c and r['method']==key.split('_')[0] and r['clahe']==key.split('_')[1]) for key in KEYS]
    data.append([c.replace('_',' / ')]+[f'{float(r["f1"]):.3f}' for r in rr])
table(data,[130,82,82,82,84])
p('The largest Hough+CLAHE failure occurs on dark/diffuse development photos: F1 is 0.546, with 82 false positives and one missed coin. This is consistent with enhanced background/detail edges generating extra circle candidates; the comparison image on the next page documents an example. This is an observed association, not an isolated causal test of surface texture.')
p('Capture groups differ in framing, relative coin size and dark-surface appearance. On development photos, Hough-off F1 is 0.964 for layouts 01-04 and 0.985 for layouts 09-12; contour-off F1 is 0.784 and 0.704, respectively. Both groups are usable for a preliminary comparison, but they are not interchangeable capture setups. Capture-group CSVs retain this distinction.')
p('6. Challenges and limitations',True)
p('Only eight arrangements are available, with no touching cases. Even the complete planned dataset contains only 40 arrangements rather than 240 independent scenes. Global segmentation is vulnerable to shadows, glare and uneven foreground contrast. Some dark-background images have strong texture. Circle labels need independent review, and approximate radii affect matching tolerance. No confidence intervals or claims of final generalization are made from these small, correlated samples.')
p('Saved evidence includes all per-image predictions/matches, condition and capture-group tables, timing records, diagnostic masks and configuration snapshots. Touching groups are marked not evaluated with null scores, rather than being reported as zero accuracy.')
page()
p('5. Preliminary results: qualitative comparison',True)
p('Both examples are shown below: layout 03 from layouts 01-04, and layout 10 from layouts 09-12. Columns compare the same four configurations. Off/on refers to CLAHE.')
fig('qualitative_comparison.png',518,504)
p('Green: matched detection. Red: false detection. Dashed cyan: missed coin. TP/FP/FN: correct/false/missed detections. Hough draws circles; contours mark centres (+). Each photo was selected for the most Hough+CLAHE false positives in its development capture group, so these illustrate failures rather than typical performance.')
page()
p('7. Changes from the proposal',True)
p('The comparison remains four configurations. The manifest uses the recommended 70:10:20 arrangement split, and related photographs stay together. Preliminary experiments use only the eight available arrangements; full-dataset and touching-coin conclusions are deferred. Complete method references and separate contact/capture-condition outputs are now included. Detection still counts coins without classifying denomination.')
p('8. Remaining work and proposed timeline',True)
table([['Target','Work and completion evidence'],['Nov 23-25','Finish 32 remaining layouts (192 photos), prioritizing touching cases. Verify filenames, conditions, capture notes and counts. Record annotators; have another member review each completed label.'],['Nov 25-27','Review both detector implementations and failure examples. Use development data for further changes; document decisions. Treat the validation photos already examined as known development history.'],['Nov 28-29','Freeze shared settings, preserve final-test isolation and record group approval. Run the full experiment; report touching/separated results and errors by condition.'],['Nov 30-Dec 2','Confirm reproducibility on a group computer, prepare the live demo, finalize report figures and actual member contributions, verify repository access, and complete final submission.']],[92,428])
p('Targets are a proposed working schedule and require the group to confirm availability and the course deadline. Group members still need to supply actual capture details, label review, responsibility assignments, interpretation and report sign-off. Software implementation and supplied measurements do not establish which member completed a course responsibility.')
p('Before submission',True)
p('Verify the numerical tables against reports/generated/summary.csv; read the failure cases; confirm the fixed split and pending review status. Merge reviewed code and outputs into the group repository, then verify that the instructor and TA can access it. This package is a local implementation and draft report; no remote changes or invitations have been made.')
p('Reproduction and artifact map',True)
p('README.md contains clean-environment commands. scripts/run_midprogress.py reproduces the pilot into a new output folder; scripts/build_midprogress_report.py rebuilds this PDF from saved measurements. reports/generated/ contains editable CSVs/plots; outputs/midprogress/ contains full predictions and matching records. Original photos are reused from the group dataset and are omitted from the delivery archive.')
page()
p('9. References',True)
refs=(ROOT/'references/REFERENCES.md').read_text()
# Full citation text stays in the editable source too; URL breaks avoid overflowing margins.
for block in re.split(r'\n(?=\d+\. )',refs):
    if block and block[0].isdigit():
        text=' '.join(s.strip() for s in block.split('\n\n# Project repository')[0].splitlines())
        text=text.replace('https://',' https://')
        story.append(Paragraph(re.sub(r'\*([^*]+)\*',r'<i>\1</i>',escape(text)),styles['Body12']))
p('Web documentation accessed November 22, 2026. Documentation describes the methods and APIs; exact installed versions are recorded with this experiment.')
p('10. Links',True)
p('Project repository: <link href="https://github.com/Penguinoucy/CP467_Coin_Counting" color="blue">https://github.com/Penguinoucy/CP467_Coin_Counting</link>')
p('The repository is private. Instructor and TA collaborator access must be verified by the group. This draft and measured outputs are supplied locally; their presence on GitHub has not been verified.')
md.append('\n'+refs)
(ROOT/'reports/progress_report.md').write_text('\n'.join(md))
def footer(canvas,doc):
    canvas.setFont('Helvetica',10);canvas.drawString(46,25,'CP467 Group 3 | Provisional results; label review pending');canvas.drawRightString(566,25,str(doc.page))
path=ROOT/'reports/Mid_Progress_Report_Draft.pdf'
SimpleDocTemplate(str(path),pagesize=(612,792),rightMargin=46,leftMargin=46,topMargin=40,bottomMargin=42,title='CP467 Coin Counting Mid-Progress Report Draft',author='CP467 Group 3').build(story,onFirstPage=footer,onLaterPages=footer)
print(f'Saved {path}; examples {examples}')
