""" SAC exec bindings package. """

from os import environ
from pyutils.dep import check_mod_pkg, check_prog_deps
from pyutils.txt_color import col, Color, print_frame
import traceback
import sys

try:
    binary_deps = []
    binary_helps = []
    if not 'DONT_NEED_SAC' in environ or environ['DONT_NEED_SAC'] == '0':
        binary_deps += ['sac']
        binary_helps += ["""You need sac. To get it you may check https://ds.iris.edu/ds/nodes/dmc/software/downloads/sac/.
The SAC archive contains a README helping for installation.
Anyway this script waits sac binary path to be found in SACBIN or PATH environment variables."""]

    if("SACBIN" in environ.keys()):
        check_prog_deps(binary_deps, environ["SACBIN"], info_msgs=binary_helps)
    else:
        check_prog_deps(binary_deps, info_msgs=binary_helps)
except Exception as e:
    traceback.print_exc(file=sys.stdout)
    msg = str(e)
    if(not msg.lower().startswith("error")):
        msg = "Error: " + msg
    print_frame(msg, Color.RED, centering=False)
    exit()
