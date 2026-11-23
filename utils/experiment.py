import platform
import subprocess
import sys

def metadata(root):
    def git(*args):
        try:
            return subprocess.check_output(["git","-C",str(root),*args],stderr=subprocess.DEVNULL,text=True).strip()
        except (OSError,subprocess.CalledProcessError):
            return None
    return {"python":sys.version,"platform":platform.platform(),"processor":platform.processor(),
            "git_commit":git("rev-parse","HEAD"),"git_changes":git("status","--porcelain"),
            "note":"Run all four timing comparisons on the same computer; complete docs/hardware.json."}
