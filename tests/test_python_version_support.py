from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def load_package_info_module():
    package_info_path = Path(__file__).resolve().parents[1] / "setup" / "package_info.py"
    spec = spec_from_file_location("package_info", package_info_path)
    module = module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_python_314_classifier_present():
    package_info = load_package_info_module()
    assert 'Programming Language :: Python :: 3.14' in package_info.CLASSIFIERS
