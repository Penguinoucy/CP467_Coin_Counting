"""Reproduce four configurations on the available development subset (validation optional)."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output-root',default='outputs/midprogress')
    p.add_argument('--include-validation',action='store_true',help='Evaluate 02/12 separately after freezing development settings')
    p.add_argument('--allow-unreviewed-labels',action='store_true',help='Explicitly label all scores provisional')
    a=p.parse_args();base=ROOT/a.output_root;base.mkdir(parents=True,exist_ok=False)
    splits=[('development',['01','03','04','09','10','11'])]
    if a.include_validation:splits.append(('validation',['02','12']))
    snapshots=base/'config_snapshot';snapshots.mkdir()
    for name in ['common','hough','contours']:(snapshots/(name+'.json')).write_bytes((ROOT/f'configs/{name}.json').read_bytes())
    for split,layouts in splits:
        for method in ['hough','contours']:
            for clahe in ['off','on']:
                out=base/split/f'{method}_{clahe}'
                subprocess.run([sys.executable,str(ROOT/'run.py'),'--method',method,'--split',split,'--clahe',clahe,
                    '--layouts',*layouts,'--output',str(out)],cwd=ROOT,check=True)
                cmd=[sys.executable,str(ROOT/'evaluate.py'),'--predictions',str(out/'predictions.json'),'--output',str(out/'evaluation')]
                if a.allow_unreviewed_labels:cmd.append('--allow-unreviewed-labels')
                subprocess.run(cmd,cwd=ROOT,check=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/summarize_results.py'),'--run-root',str(base)],cwd=ROOT,check=True)
    print('Reproduction complete; see reports/generated/ and the selected run folder.')
if __name__=='__main__':main()
