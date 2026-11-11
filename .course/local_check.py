import argparse
from pathlib import Path
import subprocess
from history_rules import check

ALLOWED = {'CMakeLists.txt','cpp/src/fastops.cpp','hybridml/native.py','hybridml/data.py','hybridml/train.py','config/train.toml'}
def git(*args):
 return subprocess.check_output(['git',*args],text=True).strip()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['preflight','protected','hygiene','native','history']);args=parser.parse_args()
 if args.mode=='preflight':
  for name in ['upstream/base','upstream/native-validation','upstream/training-logging','upstream/dataset-loader','upstream/cpu-parallelism']:
   git('rev-parse',name)
 elif args.mode=='protected':
  for name in Path('.course/protected_paths.txt').read_text().splitlines():
   expected=subprocess.check_output(['git','show','upstream/base:'+name])
   if Path(name).read_bytes()!=expected:raise SystemExit('Restore supplied file: '+name)
 elif args.mode=='hygiene':
  changed=set(git('diff','--name-only','upstream/base','HEAD').splitlines())
  if changed-ALLOWED:raise SystemExit('Unexpected changed files: '+str(sorted(changed-ALLOWED)))
  for name in git('ls-files').splitlines():
   if name.startswith('artifacts/') and name!='artifacts/.gitkeep':raise SystemExit('Do not commit generated models: '+name)
 elif args.mode=='native':
  cmake=Path('CMakeLists.txt').read_text();cpp=Path('cpp/src/fastops.cpp').read_text()
  if 'Eigen3::Eigen' not in cmake or 'FASTOPS_ENABLE_DIAGNOSTICS=1' not in cmake or '!std::isfinite(epsilon)' not in cpp:raise SystemExit('Native integration checks failed.')
 elif args.mode=='history':check()
 print(args.mode+' passed')
if __name__=='__main__':main()
