"""Build comparative CSV/JSON/Markdown and plots from completed experiment outputs."""
import argparse,csv,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from evaluation.plots import create_plots
ROOT=Path(__file__).resolve().parents[1]

def write_csv(path,rows):
    if not rows:return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run-root',type=Path,required=True);a=p.parse_args();a.run_root=(ROOT/a.run_root).resolve()
    out=ROOT/'reports/generated';out.mkdir(parents=True,exist_ok=True)
    summaries=[];conditions=[];per_image=[];contact=[];capture=[];evaluations={}
    for split in ['development','validation']:
        entries=[];expected=None
        for method in ['hough','contours']:
            for clahe in ['off','on']:
                path=a.run_root/split/f'{method}_{clahe}'/'evaluation/metrics.json'
                if not path.exists():continue
                e=json.loads(path.read_text());entries.append(e)
                ids={r['image_id'] for r in e['results']['per_image']}
                if expected is None:expected=ids
                elif ids!=expected:raise ValueError('Configurations do not cover the same photos')
                prefix={'split':split,'method':method,'clahe':clahe,'annotation_review':e['annotation_review']}
                summaries.append({**prefix,**e['results']['summary']})
                for c,v in e['results']['by_background_lighting'].items():conditions.append({**prefix,'condition':c,**v})
                for c,v in e['results']['by_contact'].items():contact.append({**prefix,'contact':c,**v})
                for c,v in e['results']['by_capture_group'].items():capture.append({**prefix,'capture_group':c,**v})
                for row in e['results']['per_image']:
                    per_image.append({**prefix,**{k:v for k,v in row.items() if not isinstance(v,list)}})
        if entries and len(entries)!=4:raise ValueError('Expected all four configurations for each evaluated split')
        if entries:evaluations[split]=entries
    for name,rows in [('summary',summaries),('conditions',conditions),('per_image',per_image),('contact',contact),('capture_groups',capture)]:write_csv(out/(name+'.csv'),rows)
    (out/'results.json').write_text(json.dumps({'evaluations':evaluations,'source_run_root':str(a.run_root.relative_to(ROOT))},indent=2))
    if 'development' in evaluations:create_plots(evaluations['development'],out)
    lines=['# Measured preliminary results','All scores are provisional where independent annotation review is pending.','',
           '| Split | Method | CLAHE | Images | Precision | Recall | F1 | MAE | Exact count | Median ms |',
           '|---|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for r in summaries:lines.append(f"| {r['split']} | {r['method']} | {r['clahe']} | {r['n_images']} | {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} | {r['count_mae']:.3f} | {r['exact_count_accuracy']:.1%} | {r['median_ms']:.1f} |")
    lines+=['','Touching-coin results are not evaluated (zero available touching images), not zero performance.',
            'Development data were used for small parameter exploration; those results are not held-out estimates.',
            'Validation results, if present, are a separate small check after development settings were fixed. No final-test images were run.']
    (out/'RESULTS.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
if __name__=='__main__':main()
