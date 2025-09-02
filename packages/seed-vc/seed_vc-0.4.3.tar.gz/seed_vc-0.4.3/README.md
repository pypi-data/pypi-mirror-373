# Publish Python package seed-vc with the Python Package Index

## Prepare:
Initializing and updating submodules

git submodule update --init --recursive

## Clean:
Clean the dist/ directory

rm -rf dist

## Build:
Build sdist and wheel for seed_vc only

python3 -m pip install -U build twine

python3 -m build

This creates:

dist/seed_vc-0.4.3-py3-none-any.whl

dist/seed_vc-0.4.3.tar.gz

## Test install: 
python -m venv .venv && .venv/bin/pip install dist/seed_vc-0.4.3-*.whl

## Upload:
Upload only your package files (not all files in dist)

python3 -m twine upload dist/seed_vc-0.4.3*

Tip: For a dry run against TestPyPI first:

python3 -m twine upload --repository testpypi dist/seed_vc-0.4.3*

## Usage:
After pip install seed-vc, users get these commands:

seed-vc-app — runs seed_vc/app_vc.py
seed-vc-app-v2 — runs seed_vc/app_vc_v2.py
seed-vc-app-combined — runs seed_vc/app.py
seed-vc-infer-v1 — runs seed_vc/inference.py
seed-vc-infer-v2 — runs seed_vc/inference_v2.py
seed-vc-train — runs seed_vc/train.py
seed-vc-eval — runs seed_vc/eval.py