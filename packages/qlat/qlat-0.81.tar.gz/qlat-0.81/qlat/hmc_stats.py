from qlat.hmc import *

import qlat.c as c

def get_gm_force_magnitudes(gm_force, n_elems):
    return c.get_gm_force_magnitudes(gm_force, n_elems)

def display_gm_force_magnitudes(gm_force, n_elems):
    c.display_gm_force_magnitudes(gm_force, n_elems)

def save_gm_force_magnitudes_list(fn):
    mk_file_dirs_info(fn)
    c.save_gm_force_magnitudes_list(fn)

def display_gauge_field_info_table_with_wilson_flow(
        fn_gf_info, fn_wilson_flow_energy, gf, flow_time, flow_steps, steps, c1 = 0.0):
    c.display_gauge_field_info_table_with_wilson_flow(
            fn_gf_info, fn_wilson_flow_energy, gf, flow_time, flow_steps, steps, c1)

