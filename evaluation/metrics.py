from statistics import median
from evaluation.matching import match_coins
IMPLEMENTATION_READY=True

def summarize(rows):
    if not rows:
        return {'status':'not_evaluated','n_images':0,'n_arrangements':0,'precision':None,'recall':None,'f1':None,'count_mae':None,'exact_count_accuracy':None,'median_ms':None}
    tp,fp,fn=(sum(r[k] for r in rows) for k in ['tp','fp','fn'])
    return {'status':'evaluated','n_images':len(rows),'n_arrangements':len({r['arrangement_id'] for r in rows}),
        'true_coins':sum(r['true_count'] for r in rows),'predicted_coins':sum(r['predicted_count'] for r in rows),
        'tp':tp,'fp':fp,'fn':fn,'precision':tp/(tp+fp) if tp+fp else 0.0,'recall':tp/(tp+fn) if tp+fn else 0.0,
        'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0.0,
        'count_mae':sum(r['absolute_count_error'] for r in rows)/len(rows),
        'exact_count_accuracy':sum(r['exact_count'] for r in rows)/len(rows),'median_ms':median(r['median_ms'] for r in rows)}

def evaluate_records(prediction_records,labels_by_image_id):
    rows=[]
    for record in prediction_records:
        label=labels_by_image_id[record['image_id']];matches=match_coins(record['coins'],label['coins'])
        tp=len(matches);n=len(record['coins']);actual=len(label['coins']);pm={i for i,j in matches};gm={j for i,j in matches}
        rows.append({**{k:record[k] for k in ['image_id','arrangement_id','background','lighting','contact']},
            'tp':tp,'fp':n-tp,'fn':actual-tp,'predicted_count':n,'true_count':actual,'absolute_count_error':abs(n-actual),
            'exact_count':n==actual,'median_ms':record['median_ms'],'matches':[list(x) for x in matches],
            'unmatched_predictions':[i for i in range(n) if i not in pm],'unmatched_labels':[i for i in range(actual) if i not in gm]})
    return {'per_image':rows,'summary':summarize(rows),
        'by_contact':{c:summarize([r for r in rows if r['contact']==c]) for c in ['separated','touching']},
        'by_background_lighting':{f'{b}_{l}':summarize([r for r in rows if r['background']==b and r['lighting']==l]) for b in ['dark','light'] for l in ['diffuse','dim','directional']},
        'by_layout':{a:summarize([r for r in rows if r['arrangement_id']==a]) for a in sorted({r['arrangement_id'] for r in rows})},
        'by_capture_group':{g:summarize([r for r in rows if (int(r['arrangement_id'])<=4)==(g=='layouts01-04')]) for g in ['layouts01-04','layouts09-12']},
        'metric_notes':'Micro detection scores use summed TP/FP/FN. Undefined ratios in evaluated groups are 0. Absent groups are null/not_evaluated. Exact count can hide cancelling detection errors.'}
