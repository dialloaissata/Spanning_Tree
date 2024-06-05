#!/usr/bin/env python3

import unittest
import sys
from control.bpdu import ConfigBPDU, Identifier


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: {} part".format(sys.argv[0]))
        sys.exit(1)
    part = sys.argv[1]

    if part in ('compare', 'all'):
        from control.tests.compare import *
    if part in ('handle', 'all'):
        from control.tests.handle import *
    if part in ('emit', 'all'):
        from control.tests.emit import *
    if part in ('root_broadcast', 'all'):
        from control.tests.root_broadcast import *
    if part in ('hello_timer', 'all'):
        from control.tests.hello_timer import *
    if part in ('hold_timer', 'all'):
        from control.tests.hello_timer import *
    if part in ('message_age', 'all'):
        from control.tests.message_age import *
    if part in ('forward_delay', 'all'):
        from control.tests.forward_delay import *

    unittest.main(argv=[sys.argv[0]])
