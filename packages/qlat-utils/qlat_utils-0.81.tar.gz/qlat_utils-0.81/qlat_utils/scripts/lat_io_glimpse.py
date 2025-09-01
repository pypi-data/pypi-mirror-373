import qlat_utils as q
import sys

filenames = sys.argv[1:]

ld = q.LatData()
for fn in filenames:
    ld.load(fn)
    sys.stdout.write(f"# '{fn}'\n")
    sys.stdout.write(ld.show())

exit()
