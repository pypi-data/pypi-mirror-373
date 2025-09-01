from pyinstrument import Profiler

profiler = Profiler(interval=0.00001)

profiler.start()

import typically as t  # noqa

profiler.stop()

profiler.print()
