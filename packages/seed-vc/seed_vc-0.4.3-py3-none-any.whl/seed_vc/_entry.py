import os
import sys
import runpy


def _ensure_local_imports():
    # Add the installed package directory (seed_vc) into sys.path so intra-package
    # absolute imports like `from .modules import ...` continue to work after install.
    pkg_dir = os.path.dirname(__file__)
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)


def app():
    _ensure_local_imports()
    runpy.run_module("seed_vc.app_vc", run_name="__main__")


def app_v2():
    _ensure_local_imports()
    runpy.run_module("seed_vc.app_vc_v2", run_name="__main__")


def app_combined():
    _ensure_local_imports()
    runpy.run_module("seed_vc.app", run_name="__main__")


def infer_v1():
    _ensure_local_imports()
    runpy.run_module("seed_vc.inference", run_name="__main__")


def infer_v2():
    _ensure_local_imports()
    runpy.run_module("seed_vc.inference_v2", run_name="__main__")


def train():
    _ensure_local_imports()
    runpy.run_module("seed_vc.train", run_name="__main__")


def eval():
    _ensure_local_imports()
    runpy.run_module("seed_vc.eval", run_name="__main__")

