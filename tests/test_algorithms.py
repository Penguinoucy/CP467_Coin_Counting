"""Meaningful algorithm/integration checks; synthetic fixtures are not study data."""
from pathlib import Path
import copy,itertools,json,random,subprocess,sys,unittest
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from evaluation.matching import match_coins
from evaluation.metrics import evaluate_records,summarize
from utils.data_io import validate_label,load_manifest
from detectors import contours,hough

class AlgorithmTests(unittest.TestCase):
    def test_greedy_counterexample(self):
        p=[{'x':2,'y':0},{'x':-4,'y':0}];g=[{'x':0,'y':0,'radius':10},{'x':4,'y':0,'radius':10}]
        self.assertEqual(set(match_coins(p,g)),{(0,1),(1,0)})
    def test_minimum_distance_tie_break(self):
        p=[{'x':1,'y':0},{'x':9,'y':0}];g=[{'x':0,'y':0,'radius':50},{'x':10,'y':0,'radius':50}]
        self.assertEqual(set(match_coins(p,g)),{(0,0),(1,1)})
    def test_empty_and_outside(self):
        self.assertEqual(match_coins([],[]),[])
        self.assertEqual(match_coins([{'x':100,'y':100}],[{'x':0,'y':0,'radius':2}]),[])
    def test_threshold_inclusive(self):
        g=[{'x':10,'y':10,'radius':10}]
        self.assertEqual(match_coins([{'x':15,'y':10}],g),[(0,0)])
        self.assertEqual(match_coins([{'x':15.001,'y':10}],g),[])
    def test_matches_equal_small_bruteforce(self):
        rng=random.Random(467)
        for _ in range(35):
            n,m=rng.randint(1,4),rng.randint(1,4)
            p=[{'x':rng.uniform(0,20),'y':0} for i in range(n)]
            g=[{'x':rng.uniform(0,20),'y':0,'radius':rng.uniform(3,20)} for j in range(m)]
            best=(-1,float('inf'))
            for choices in itertools.product(range(-1,m),repeat=n):
                used=[x for x in choices if x>=0]
                if len(set(used))!=len(used):continue
                ds=[abs(p[i]['x']-g[j]['x']) for i,j in enumerate(choices) if j>=0]
                if any(abs(p[i]['x']-g[j]['x'])>g[j]['radius']/2 for i,j in enumerate(choices) if j>=0):continue
                count=len(used);cost=sum(ds)
                if count>best[0] or (count==best[0] and cost<best[1]):best=(count,cost)
            matches=match_coins(p,g)
            self.assertEqual(len(matches),best[0]);self.assertAlmostEqual(sum(abs(p[i]['x']-g[j]['x']) for i,j in matches),best[1])
    def test_count_cancellation_not_hidden(self):
        record={'image_id':'sample','arrangement_id':'01','background':'dark','lighting':'dim','contact':'separated','median_ms':1,
                'coins':[{'x':10,'y':10},{'x':90,'y':90}]}
        result=evaluate_records([record],{'sample':{'coins':[{'x':10,'y':10,'radius':10},{'x':40,'y':40,'radius':10}]}})
        self.assertEqual(result['summary']['count_mae'],0)
        self.assertEqual(result['summary']['f1'],0.5)
        self.assertEqual(result['by_contact']['touching']['status'],'not_evaluated')
        self.assertIsNone(result['by_contact']['touching']['f1'])
    def test_zero_predictions_no_divide_by_zero(self):
        r={'image_id':'x','arrangement_id':'01','background':'dark','lighting':'dim','contact':'separated','median_ms':1,'coins':[]}
        s=evaluate_records([r],{'x':{'coins':[{'x':10,'y':10,'radius':10}]}})['summary']
        self.assertEqual(s['f1'],0);self.assertEqual(s['recall'],0);self.assertEqual(s['count_mae'],1)
    def test_unreviewed_opt_in_never_mutates_label(self):
        label={'image_id':'x','annotation_status':'complete','review_status':'not_reviewed','annotator':None,'reviewer':None,
               'image_width':100,'image_height':100,'coin_count':1,'coins':[{'x':20,'y':20,'radius':10}]}
        before=copy.deepcopy(label)
        with self.assertRaises(ValueError):validate_label(label,'x')
        validate_label(label,'x',allow_unreviewed=True);self.assertEqual(label,before)
    def test_blank_photos(self):
        common=json.loads((ROOT/'configs/common.json').read_text())
        for name,module in [('hough',hough),('contours',contours)]:
            config=json.loads((ROOT/f'configs/{name}.json').read_text());config['common']=common
            for level in [0,255]:
                image=np.full((500,500,3),level,np.uint8)
                self.assertEqual(module.detect(image,config),[])
    def test_contours_both_polarities_and_original_coordinates(self):
        common=json.loads((ROOT/'configs/common.json').read_text());common['max_side']=500
        config=json.loads((ROOT/'configs/contours.json').read_text());config['common']=common
        for bg,fg in [(0,200),(255,40)]:
            image=np.full((1000,1000,3),bg,np.uint8)
            for centre in [(250,250),(750,250),(500,700)]:cv2.circle(image,centre,60,(fg,fg,fg),-1)
            result=contours.detect(image,config)
            self.assertEqual(len(result),3)
            for x,y in [(250,250),(750,250),(500,700)]:
                self.assertLess(min(np.hypot(c['x']-x,c['y']-y) for c in result),3)
    def test_hough_original_coordinates(self):
        config=json.loads((ROOT/'configs/hough.json').read_text());config['common']=json.loads((ROOT/'configs/common.json').read_text());config['common']['max_side']=500
        image=np.zeros((1000,1000,3),np.uint8)
        for centre in [(250,250),(750,250),(500,700)]:cv2.circle(image,centre,60,(220,220,220),-1)
        result=hough.detect(image,config)
        self.assertEqual(len(result),3)
        for x,y in [(250,250),(750,250),(500,700)]:self.assertLess(min(np.hypot(c['x']-x,c['y']-y) for c in result),8)
    def test_validation_layout_cannot_be_requested_as_development(self):
        p=subprocess.run([sys.executable,str(ROOT/'run.py'),'--method','hough','--split','development','--clahe','off','--layouts','02','--output','outputs/should_not_exist'],text=True,capture_output=True)
        self.assertEqual(p.returncode,2);self.assertIn('outside development',p.stderr)

if __name__=='__main__':unittest.main()
