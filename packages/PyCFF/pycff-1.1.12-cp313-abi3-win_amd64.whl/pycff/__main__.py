# -*- coding: utf-8 -*-

import os
import sys

if sys.path[0] in ("", os.getcwd()):
    sys.path.pop(0)
    
if __package__ == "":
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)

def main():
    from pycff.application import run_app as _main
    sys.exit(_main())

if __name__ == "__main__":
    main()
