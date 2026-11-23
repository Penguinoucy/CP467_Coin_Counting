"""Regression checks for minimal labels and explicit provisional loading."""
from pathlib import Path
import copy,importlib.util,json,unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('minimal_label_loader',ROOT/'utils/data_io.py')
loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)

class MinimalLabelTests(unittest.TestCase):
    def setUp(self):
        self.label={'image_id':'example','image_width':100,'image_height':100,'coin_count':1,
                    'coins':[{'x':50,'y':50,'radius':10}]}
    def test_minimal_requires_explicit_provisional_mode_and_stays_unchanged(self):
        before=copy.deepcopy(self.label)
        with self.assertRaises(ValueError):loader.validate_label(self.label,'example')
        loader.validate_label(self.label,'example',allow_unreviewed=True)
        self.assertEqual(self.label,before)
    def test_incomplete_status_is_not_bypassed(self):
        for status in [None,'pending','incomplete']:
            with self.subTest(status=status),self.assertRaises(ValueError):
                loader.validate_label({**self.label,'annotation_status':status},'example',allow_unreviewed=True)
    def test_missing_or_invalid_data_remain_rejected(self):
        for key,value in [('image_width',None),('coin_count',None),('coin_count',2),('coins',None)]:
            with self.subTest(key=key,value=value),self.assertRaises(ValueError):
                loader.validate_label({**self.label,key:value},'example',allow_unreviewed=True)
        invalid=copy.deepcopy(self.label);invalid['coins'][0]['radius']=0
        with self.assertRaises(ValueError):loader.validate_label(invalid,'example',allow_unreviewed=True)
    def test_full_reviewed_format_still_works(self):
        reviewed={**self.label,'annotation_status':'complete','review_status':'reviewed',
                  'annotator':'Person A','reviewer':'Person B'}
        loader.validate_label(reviewed,'example')
    def test_supplied_48_minimal_labels_are_structurally_valid(self):
        paths=[p for p in (ROOT/'data/labels').glob('*.json') if isinstance(json.loads(p.read_text()).get('coins'),list)];self.assertEqual(len(paths),48)
        count=0
        for path in paths:
            label=json.loads(path.read_text())
            self.assertFalse({'notes','reviewer','annotator','review_status','annotation_status'}&label.keys())
            loader.validate_label(label,path.stem,allow_unreviewed=True);count+=label['coin_count']
        self.assertEqual(count,420)
if __name__=='__main__':unittest.main()
