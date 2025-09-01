import qlat_utils as q
import sys
import pprint

filenames = sys.argv[1:]

for fn in filenames:
    obj = q.load_pickle_obj(fn)
    sys.stdout.write(f"# '{fn}'\n")
    sys.stdout.write(pprint.pformat(obj))
    sys.stdout.write("\n")

exit()
