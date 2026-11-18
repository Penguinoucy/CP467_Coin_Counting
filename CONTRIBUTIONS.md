# Files each role must complete
Owners remain unassigned until the group chooses them.

| Role | Files or folders | Required contribution |
|---|---|---|
| 1 Photos and labels | data/images/ | Add the 240 actual photos with filenames matching the manifest. |
| 1 | data/manifest.csv | Verify planned conditions, actual paths, layout IDs, and fixed 28/4/8 split. |
| 1 | data/labels/*.json | Fill all 240 templates with centres/radii, dimensions, counts, annotator/reviewer, and honest status. |
| 1 | data/capture_log.json; docs/capture_guide.md | Record the actual setup and collection procedure; coordinate shared work. |
| 1 | data/raw_annotations/ | Add original annotation-tool exports if used; implement a converter if required. |
| 1 | reports/sections/role_1.md | Write actual data progress, procedure, and limitations. |
| 2 Circle method | detectors/hough.py; configs/hough.json | Implement detect(), add and justify settings, then mark implementation_ready true. |
| 2 | references/hough.md; references/clahe.md; reports/sections/role_2.md | Supply full sources, method description, examples, and failures. |
| 3 Background method | detectors/contours.py; configs/contours.json | Implement segmentation, cleanup, filtering, and moment centroids; configure and mark ready. |
| 3 | references/contours.md; references/clahe.md; reports/sections/role_3.md | Supply sources, masks/outlines, method text, and failures. |
| 4 Evaluation | evaluation/matching.py; evaluation/metrics.py; evaluation/plots.py; evaluation/README.md | Implement and check matching/metrics, document fields, and plot four comparable configurations. |
| 4 | reports/sections/role_4.md | Supply real accuracy tables, separate contact results, failure analysis, and sample-size limitations. |
| 5 Integration | run.py; evaluate.py; scripts/run_all.py; README.md | Review supplied orchestration against actual member code, connect components, and check a clean setup. |
| 5 | requirements.txt; docs/hardware.json; docs/experiment_log.md | Freeze tested versions and record actual machine, runs, timings, and commit IDs. |
| 5 | docs/demo_checklist.md; references/tools.md; reports/sections/role_5.md | Prepare the demo, tool citations, integration write-up, and timing results. |
| All; coordinated by 5 | configs/common.json | Agree on common CLAHE settings/placement and shared timing repetitions. |
| All; coordinated by 5 | configs/final_test_approval.json | Confirm frozen settings and test-set isolation truthfully before final testing. |
| All; assembled by 5 | reports/progress_report.md; reports/final_report.md; reports/presentation_outline.md; reports/figures/ | Replace prompts with each member's actual contributions and measured figures. |

## Shared collection duties
Each person contributes eight layouts (six separated and two touching), labels their photos,
and reviews another member's labels. Role 1 coordinates; Role 5 assembles each member's
finished report section. Roles 2 and 3 retain ownership of fixing their detector code.

## Supplied infrastructure
The manifest, 240 empty label templates, runners, shared helpers, setup/data checks,
and mock integration tests are supplied. No real photos, annotations, working detectors,
matching algorithm, accuracy measurements, or report findings are supplied.
Do not replace your own existing requirements.txt with this starter list if it already
records tested versions. Merge the actual dependencies and freeze your environment.
