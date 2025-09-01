import qlat_utils as q
import sys

filenames = sys.argv[1:]

assert len(filenames) == 2

ld1 = q.load_lat_data(filenames[0])
ld2 = q.load_lat_data(filenames[1])

print(f"{q.qnorm(ld1 - ld2)}")
print(f"{q.qnorm(ld1)}")
print(f"{q.qnorm(ld2)}")

exit()
