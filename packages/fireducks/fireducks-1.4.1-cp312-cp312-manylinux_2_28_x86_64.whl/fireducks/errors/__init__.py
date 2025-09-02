# Copyright (c) 2023 NEC Corporation. All Rights Reserved.


class FallbackWarning(Warning):
    """
    Fallback warning enabled by FIREDUCKS_FLAGS="-Wfallback" or
    fireducks.core.set_fireducks_options("warn-fallback", True)
    """
