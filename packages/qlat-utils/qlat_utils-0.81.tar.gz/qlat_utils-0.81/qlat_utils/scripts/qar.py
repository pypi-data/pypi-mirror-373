# Author: Luchang Jin 2024

import qlat_utils as q
import sys

def remove_trailing_slashes(path):
    while True:
        if path == "":
            return ""
        if path[-1] == "/":
            path = path[:-1]
        else:
            break
    return path

def show_list_qar(path_qar, idx=0, is_recursive=True, drop_prefix=""):
    assert path_qar[-4:] == ".qar"
    fns = q.list_qar(path_qar)
    for i, fn in enumerate(fns):
        pfn_full = path_qar[:-4] + "/" + fn
        assert pfn_full.startswith(drop_prefix)
        pfn = pfn_full[len(drop_prefix):]
        q.displayln_info(f"{idx:8} '{path_qar}' {i:8} '{pfn}'")
        idx += 1
        if is_recursive and fn[-4:] == ".qar":
            idx = show_list_qar(pfn_full, idx, is_recursive=is_recursive, drop_prefix=drop_prefix)
    return idx

def build_index_qar(path_qar, is_recursive=True):
    assert path_qar[-4:] == ".qar"
    q.qar_build_index_info(path_qar)
    if not is_recursive:
        return
    fns = q.list_qar(path_qar)
    for fn in fns:
        if fn[-4:] == ".qar":
            pfn_full = path_qar[:-4] + "/" + fn
            build_index_qar(pfn_full, is_recursive=is_recursive)

if len(sys.argv) < 2:
    q.displayln_info("Usage: qar list path.qar")
    q.displayln_info("Usage: qar build-idx path.qar")
    q.displayln_info("Usage: qar create path.qar path")
    q.displayln_info("Usage: qar extract path.qar path")
    q.displayln_info("Usage: qar cp path_src path_dst")
    q.displayln_info("Usage: qar cat path1 path2 ...")
    q.displayln_info("Usage: qar l path1.qar path2.qar ...")
    q.displayln_info("Usage: qar lr path1.qar path2.qar ...")
    q.displayln_info("Usage: qar b path1.qar path2.qar ...")
    q.displayln_info("Usage: qar br path1.qar path2.qar ...")
    q.displayln_info("Usage: qar c path1 path2 ...")
    q.displayln_info("Usage: qar x path1.qar path2.qar ...")
    q.displayln_info("Usage: qar cr path1 path2 ...")
    q.displayln_info("       Remove folders after qar files created")
    q.displayln_info("Usage: qar xr path1.qar path2.qar ...")
    q.displayln_info("       Remove qar files after folder extracted")
    exit(1)

assert len(sys.argv) >= 2

action = sys.argv[1]

if action == "list":
    assert len(sys.argv) == 3
    path_qar = sys.argv[2]
    show_list_qar(path_qar, 0, is_recursive=False)
elif action == "build-idx":
    assert len(sys.argv) == 3
    path_qar = sys.argv[2]
    build_index_qar(path_qar, is_recursive=False)
elif action == "create":
    assert len(sys.argv) == 4
    path_qar = sys.argv[2]
    path = sys.argv[3]
    assert not q.does_file_exist(path_qar)
    assert q.is_directory(path)
    q.qar_create_info(path_qar, path)
elif action == "extract":
    assert len(sys.argv) == 4
    path_qar = sys.argv[2]
    path = sys.argv[3]
    assert q.does_file_exist_qar(path_qar)
    assert not q.does_file_exist(path)
    q.qar_extract_info(path_qar, path)
elif action == "cp":
    assert len(sys.argv) == 4
    path_src = sys.argv[2]
    path_dst = sys.argv[3]
    assert q.does_file_exist_qar(path_src)
    assert not q.does_file_exist(path_dst)
    q.qcopy_file_info(path_src, path_dst)
elif action == "cat":
    assert len(sys.argv) >= 2
    for path in sys.argv[2:]:
        assert q.does_file_exist_qar(path)
        content = q.qcat_bytes(path)
        sys.stdout.buffer.write(content)
elif action == "l":
    idx = 0
    for path_qar in sys.argv[2:]:
        idx = show_list_qar(path_qar, idx, is_recursive=False)
elif action == "lr":
    idx = 0
    for path_qar in sys.argv[2:]:
        idx = show_list_qar(path_qar, idx, is_recursive=True)
elif action == "b":
    for path_qar in sys.argv[2:]:
        build_index_qar(path_qar, is_recursive=False)
elif action == "br":
    for path_qar in sys.argv[2:]:
        build_index_qar(path_qar, is_recursive=True)
elif action in [ "c", "cr" ]:
    path_list = sys.argv[2:]
    for path in path_list:
        path = remove_trailing_slashes(path)
        path_qar = path + ".qar"
        assert not q.does_file_exist(path_qar)
        assert q.is_directory(path)
    for path in path_list:
        path = remove_trailing_slashes(path)
        path_qar = path + ".qar"
        if action == "c":
            q.qar_create_info(path_qar, path)
        elif action == "cr":
            q.qar_create_info(path_qar, path, is_remove_folder_after=True)
elif action in [ "x", "xr" ]:
    path_qar_list = sys.argv[2:]
    for path_qar in path_qar_list:
        assert path_qar[-4:] == ".qar"
        path = path_qar[:-4]
        assert path != ""
        assert q.does_file_exist_qar(path_qar)
        assert not q.does_file_exist(path)
    for path_qar in path_qar_list:
        path = path_qar[:-4]
        if action == "x":
            q.qar_extract_info(path_qar, path)
        elif action == "xr":
            q.qar_extract_info(path_qar, path, is_remove_qar_after=True)
else:
    assert False

q.clear_all_caches()

exit()
