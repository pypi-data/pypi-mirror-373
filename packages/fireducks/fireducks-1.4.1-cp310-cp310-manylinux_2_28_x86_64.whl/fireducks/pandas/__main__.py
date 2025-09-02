# Copyright (c) 2024 NEC Corporation. All Rights Reserved.

import os.path
from fireducks import imhook, importhook

# ignore this script itself
importhook.ImportHook.ignore_names.append(os.path.abspath(__file__))

if __name__ == "__main__":
    imhook.run_default_action()
