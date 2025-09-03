#!/usr/bin/env python3

import os
exec(open(os.path.join(os.getcwd(), "src", "gridmarthe", "__version__.py")).read())
print(__version__)
