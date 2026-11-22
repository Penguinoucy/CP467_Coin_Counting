"""Infrastructure checks only. Fake image functions are never experimental evidence."""
import csv
import importlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from utils.data_io import load_manifest, load_label


class InfrastructureTests(unittest.TestCase):
    def setUp(self):
        # A sibling avoids recursive copying if /tmp is unavailable and Python
        # otherwise chooses the current project directory as its fallback.
        self.temp = tempfile.TemporaryDirectory(prefix='cp467_test_', dir=ROOT.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('__pycache__', '.venv', '*.jpg', '*.jpeg', '*.png'))

    def run_command(self, *args, env=None):
        return subprocess.run([sys.executable, *args], cwd=self.root, env=env,
                              text=True, capture_output=True)

    def edit_manifest(self, change):
        path = self.root / 'data/manifest.csv'
        with path.open(newline='') as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            rows = list(reader)
        change(rows)
        with path.open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_manifest_counts_and_no_layout_leakage(self):
        rows = load_manifest(self.root)
        self.assertEqual(len(rows), 240)
        self.assertEqual(len({r['arrangement_id'] for r in rows}), 40)
        counts = {split: sum(r['split'] == split for r in rows)
                  for split in ['development', 'validation', 'test']}
        self.assertEqual(counts, {'development': 168, 'validation': 24, 'test': 48})

    def test_duplicate_photo_is_rejected(self):
        self.edit_manifest(lambda rows: rows[1].update(image_id=rows[0]['image_id']))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            load_manifest(self.root)

    def test_layout_crossing_splits_is_rejected(self):
        self.edit_manifest(lambda rows: rows[0].update(split='test' if rows[0]['split'] != 'test' else 'development'))
        with self.assertRaisesRegex(ValueError, 'crosses'):
            load_manifest(self.root)

    def test_unfinished_labels_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            load_label(self.root, 'layout01_light_diffuse')

    def test_setup_check_needs_no_image_packages(self):
        result = self.run_command('run.py', '--check-setup')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Photos still needed: 240', result.stdout)
        self.assertIn('reviewed labels ready: 0/240', result.stdout)

    def test_unfinished_detector_is_not_treated_as_zero_coins(self):
        path = self.root / 'configs/hough.json'
        config = json.loads(path.read_text()); config['implementation_ready'] = False
        path.write_text(json.dumps(config))
        result = self.run_command('run.py', '--method', 'hough', '--split', 'development',
                                  '--clahe', 'off', '--output', 'outputs/test')
        self.assertEqual(result.returncode, 2)
        self.assertIn('complete detectors/hough.py', result.stderr)
        self.assertFalse((self.root / 'outputs/test/predictions.json').exists())

    def test_final_test_requires_group_checklist(self):
        result = self.run_command('run.py', '--method', 'hough', '--split', 'test',
                                  '--clahe', 'off', '--output', 'outputs/test')
        self.assertEqual(result.returncode, 2)
        self.assertIn('final_test_approval', result.stderr)

    def test_mocked_pilot_and_evaluation_handoff(self):
        # These replacements exist only in the disposable test copy, never the real project.
        mock = Path(self.temp.name) / 'mock_packages'
        mock.mkdir()
        (mock / 'cv2.py').write_text('''
class FakeImage:
    shape = (100, 100, 3)
    def copy(self): return FakeImage()
FONT_HERSHEY_SIMPLEX = 0
def imread(path): return FakeImage()
def circle(*args): pass
def putText(*args): pass
def imwrite(path, image):
    from pathlib import Path
    Path(path).write_text('MOCK IMAGE OUTPUT - NOT A PHOTOGRAPH')
    return True
''')
        (self.root / 'detectors/hough.py').write_text(
            'def detect(image, config, use_clahe=False):\n'
            '    return [{"x":20.0,"y":20.0,"radius":10.0}]\n')
        config_path = self.root / 'configs/hough.json'
        config = json.loads(config_path.read_text())
        config['implementation_ready'] = True
        config_path.write_text(json.dumps(config))
        row = next(r for r in load_manifest(self.root) if r['split'] == 'development')
        (self.root / row['image_path']).write_text('MOCK INPUT - NOT A PHOTOGRAPH')
        env = dict(os.environ, PYTHONPATH=str(mock))
        result = self.run_command('run.py', '--method', 'hough', '--split', 'development',
                                  '--clahe', 'off', '--limit', '1', '--output', 'outputs/mock', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        prediction_path = self.root / 'outputs/mock/predictions.json'
        run = json.loads(prediction_path.read_text())
        self.assertTrue(run['pilot_run'])
        self.assertEqual(run['images'][0]['count'], 1)
        self.assertEqual(len(run['images'][0]['timings_ms']), 10)
        self.assertTrue((self.root / 'outputs/mock/marked_images' / (row['image_id'] + '.jpg')).exists())

        # A deliberately fake evaluator tests the call contract, not any metric algorithm.
        (self.root / 'evaluation/metrics.py').write_text('''
IMPLEMENTATION_READY = True
def evaluate_records(records, labels):
    return {"per_image":[{"image_id":r["image_id"]} for r in records],
            "summary":{"mock_only":True},"by_contact":{},"by_background_lighting":{}}
''')
        missing = self.run_command('evaluate.py', '--predictions', 'outputs/mock/predictions.json',
                                   '--output', 'outputs/mock/evaluation')
        self.assertEqual(missing.returncode, 2)
        self.assertIn('incomplete', missing.stderr)
        label_path = self.root / 'data/labels' / (row['image_id'] + '.json')
        label = json.loads(label_path.read_text())
        label.update(annotation_status='complete', review_status='reviewed', annotator='Member A',
                     reviewer='Member B', image_width=100, image_height=100, coin_count=1,
                     coins=[{'x':20,'y':20,'radius':10}])
        label_path.write_text(json.dumps(label))
        result = self.run_command('evaluate.py', '--predictions', 'outputs/mock/predictions.json',
                                  '--output', 'outputs/mock/evaluation')
        self.assertEqual(result.returncode, 0, result.stderr)
        evaluation = json.loads((self.root / 'outputs/mock/evaluation/metrics.json').read_text())
        self.assertTrue(evaluation['pilot_run'])
        self.assertTrue(evaluation['results']['summary']['mock_only'])


if __name__ == '__main__':
    unittest.main()
