import subprocess
import sys
import os
import shutil
from pathlib import Path
from aws_cdk.core import ILocalBundling, BundlingOptions
import jsii

def get_parent_dir() -> str:
    return str(Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute())

def get_lambda_code_dir() -> str:
    return os.path.join(get_parent_dir(), "lambda")

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

@jsii.implements(ILocalBundling)
class LocalBundler():
    """This allows packaging lambda functions without the use of Docker"""

    def try_bundle(self, output_dir: str, options: BundlingOptions) -> bool:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "--version"])
        except:
            return False

        copytree(get_lambda_code_dir(), output_dir)

        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip",
            "install",
            "-r", 
            os.path.join(get_lambda_code_dir(), "requirements.txt"),
            "-t",
            output_dir
        ])
        return True