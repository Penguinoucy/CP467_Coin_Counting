"""Plot only actual evaluated records. No illustrative numbers enter these charts."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

COLORS=['#275D89','#4FA3A5','#D08C3F','#AA536B']

def create_plots(evaluations,output_directory):
    output=Path(output_directory);output.mkdir(parents=True,exist_ok=True)
    names=[('Hough + CLAHE' if e['clahe'] else 'Hough') if e['method']=='hough' else ('Contours + CLAHE' if e['clahe'] else 'Contours') for e in evaluations]
    summaries=[e['results']['summary'] for e in evaluations]
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,3,figsize=(12,4),layout='constrained')
    for ax,key,title in zip(axes,['f1','count_mae','exact_count_accuracy'],['Detection F1','Count MAE (coins/image)','Exact-count accuracy']):
        ax.bar(range(len(names)),[s[key] for s in summaries],color=COLORS)
        ax.set_xticks(range(len(names)),names,rotation=35,ha='right');ax.set_title(title);ax.grid(axis='y',alpha=.2)
        if key!='count_mae':ax.set_ylim(0,1.05)
    fig.suptitle('Preliminary development results | supplied annotations not independently reviewed',fontsize=12)
    fig.savefig(output/'development_overview.png',dpi=180);plt.close(fig)
    conditions=list(evaluations[0]['results']['by_background_lighting'])
    fig,ax=plt.subplots(figsize=(11,4.6),layout='constrained');x=np.arange(len(conditions));width=.2
    for i,e in enumerate(evaluations):
        ax.bar(x+(i-1.5)*width,[e['results']['by_background_lighting'][c]['f1'] for c in conditions],width,label=names[i],color=COLORS[i])
    ax.set_xticks(x,[c.replace('_','\n') for c in conditions]);ax.set_ylim(0,1.05);ax.set_ylabel('Detection F1');ax.legend(ncol=2);ax.grid(axis='y',alpha=.2)
    ax.set_title('Development F1 by background and lighting (six photos per condition)')
    fig.savefig(output/'development_conditions.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.5,3.5),layout='constrained')
    ax.barh(names,[s['median_ms'] for s in summaries],color=COLORS)
    ax.set_xlabel('Median of per-photo median runtimes (ms)');ax.set_title('CPU preprocessing + detection; loading/drawing excluded')
    fig.savefig(output/'development_timing.png',dpi=180);plt.close(fig)
    return [str(output/p) for p in ['development_overview.png','development_conditions.png','development_timing.png']]
