# Author: Luchang Jin 2022

import qlat_utils as q
import sys

def show_list_qar(path_qar, idx = 0, is_recursive = True, drop_prefix = ""):
    assert path_qar[-4:] == ".qar"
    fns = q.list_qar(path_qar)
    for i, fn in enumerate(fns):
        pfn_full = path_qar[:-4] + "/" + fn
        assert pfn_full.startswith(drop_prefix)
        pfn = pfn_full[len(drop_prefix):]
        q.displayln_info(f"{idx:8} '{path_qar}' {i:8} '{pfn}'")
        idx += 1
        if is_recursive and fn[-4:] == ".qar":
            idx = show_list_qar(pfn_full, idx, is_recursive = is_recursive, drop_prefix = drop_prefix)
    return idx

if len(sys.argv) < 2:
    q.displayln_info("Usage: qar-glimpse path1.qar path2.qar ... path1 path2 ...")
    exit(1)

assert len(sys.argv) >= 2

idx = 0
for path in sys.argv[1:]:
    if path[-4:] == ".qar":
        idx = show_list_qar(path, idx, is_recursive = True, drop_prefix = path[:-4] + "/")
    else:
        assert q.does_file_exist_qar(path)
        content = q.qcat_bytes(path)
        sys.stdout.buffer.write(content)

q.clear_all_caches()

exit()
