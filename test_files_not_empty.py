import subprocess
from pathlib import Path

pathlist = Path("/Users/heinrich/PycharmProjects/curlSAMOPapers").rglob('**/*.pdf')
for path in pathlist:
    path_in_str = str(path)
    try:
        subprocess.call(('open', path_in_str))
    except:
        print(path_in_str)