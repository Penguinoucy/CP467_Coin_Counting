# Small progress-report update

This update is compared against the CP467 project ZIP you uploaded. It contains only changed/new
files, apart from omitting the large generated per-photo marked copies. No original dataset photos
are included. Nothing needs to be deleted from your current project.

Included: working code and dependencies, selected settings, 48 converted labels, source VIA exports,
recorded predictions/metrics/timings, CSVs, plots, the eight-image report and its builder.
The report can be rebuilt using your existing photos without re-running the experiments.

## Merge on your Mac

1. Unzip this download into Downloads. Do not replace your entire existing project folder.
2. Save your existing work in Git and start a new branch. See PUSH_TO_GITHUB.md for exact commands.
3. From your existing project root, merge the extracted folder contents:

```bash
rsync -av --exclude='.git/' --exclude='.venv/' ~/Downloads/CP467_Coin_Counting_Changes/ ./
```

This updates matching file paths and preserves unrelated files and photos. Review conflicts if
teammates have edited the same code, manifest or labels. There are no empty label templates in this patch.
If your extracted folder is somewhere else, adjust the source path in the command.

4. The report is reports/Mid_Progress_Report_Draft.pdf (all eight example panels).
5. To verify/rebuild after installing requirements.txt:

```bash
python scripts/verify_inputs.py
python scripts/summarize_results.py --run-root outputs/midprogress
python scripts/build_midprogress_report.py
```

6. Follow PUSH_TO_GITHUB.md to review, commit, push a branch and open a pull request.

PATCH_FILES.csv lists the changed/new paths. No remote files or repository branches were modified here.
