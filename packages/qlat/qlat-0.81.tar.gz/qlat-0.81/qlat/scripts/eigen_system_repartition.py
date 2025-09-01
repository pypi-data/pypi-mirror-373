# Author: Luchang Jin 2022

import qlat as q
import sys

if len(sys.argv) not in [ 3, 4, ]:
    q.displayln_info("Usage: eigen-system-repartition 1.1.1.8 path [path_new]")
    q.displayln_info("Default path_new is the same as the old path.")
    exit()

q.begin_with_mpi()

new_size_node = q.Coordinate([ int(x) for x in sys.argv[1].split(".") ])
path = sys.argv[2]
if len(sys.argv) == 4:
    path_new = sys.argv[3]
else:
    path_new = path

q.eigen_system_repartition(new_size_node, path, path_new)

q.timer_display()

q.end_with_mpi()

exit()
