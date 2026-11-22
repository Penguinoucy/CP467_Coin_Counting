"""Small declared development-only exploration; never opens validation/test images.
Records every candidate and selects one common setting per method across CLAHE off/on.
Run once before reported measurement runs. It is exploratory resubstitution, not held-out evidence.
"""
from pathlib import Path
import sys,json,copy,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import cv2
from utils.data_io import load_manifest,load_label
from evaluation.metrics import evaluate_records
from detectors import hough,contours
ROOT=Path(__file__).resolve().parents[1]

def main():
    cv2.setNumThreads(1)
    common=json.loads((ROOT/'configs/common.json').read_text())
    rows=[r for r in load_manifest(ROOT) if r['split']=='development' and (ROOT/r['image_path']).is_file()]
    if not rows:raise ValueError('No available development images')
    images={r['image_id']:cv2.imread(str(ROOT/r['image_path'])) for r in rows}
    labels={r['image_id']:load_label(ROOT,r['image_id'],allow_unreviewed=True) for r in rows}
    folder=ROOT/'outputs/development_settings';folder.mkdir(parents=True,exist_ok=False)
    all_results=[]
    for name,module,field,values in [('hough',hough,'accumulator_threshold',[35,45,55,65]),('contours',contours,'min_circularity',[0.50,0.65,0.80])]:
        base=json.loads((ROOT/f'configs/{name}.json').read_text());candidates=[]
        for value in values:
            config=copy.deepcopy(base);config['parameters'][field]=value;config['common']=common
            measurements=[]
            for clahe in [False,True]:
                records=[]
                for row in rows:
                    coins=module.detect(images[row['image_id']],config,clahe)
                    records.append({**row,'coins':coins,'median_ms':0.0})
                summary=evaluate_records(records,labels)['summary']
                measurements.append({'clahe':clahe,'summary':summary})
            score=sum(x['summary']['f1'] for x in measurements)/2
            mae=sum(x['summary']['count_mae'] for x in measurements)/2
            result={'method':name,'parameter':field,'value':value,'mean_f1':score,'mean_mae':mae,'results':measurements}
            candidates.append(result);all_results.append(result)
            print(name,field,value,'mean F1',round(score,4),'mean MAE',round(mae,3),flush=True)
        best=max(candidates,key=lambda x:(x['mean_f1'],-x['mean_mae']))
        base['parameters'][field]=best['value']
        base['selection_notes']=f"Development-only exploration on {len(rows)} supplied development photos; selected {field}={best['value']} by highest mean F1 across CLAHE off/on, lower MAE as tie-break. Same settings retained for both variants. Labels not independently reviewed. Validation/test not opened by this script."
        (ROOT/f'configs/{name}.json').write_text(json.dumps(base,indent=2)+'\n')
    report={'split':'development','annotation_review':'provisional_unreviewed','image_ids':[r['image_id'] for r in rows],
            'selection_rule':'Highest mean detection F1 across off/on, lower mean count MAE as tie-break.',
            'candidates':all_results,'limitations':'Reported development scores reuse these data; no independent generalization claim.'}
    (folder/'search.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
