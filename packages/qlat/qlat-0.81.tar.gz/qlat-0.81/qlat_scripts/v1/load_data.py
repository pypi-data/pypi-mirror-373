import qlat as q

from auto_contractor.eval import *

import os
import numpy as np

from .jobs import *

is_mira_data = False

def get_prop_wsrc(prop_cache, inv_type, t_src, tag_snk_type):
    cache_type_dict = {
            "wsrc_wsnk ; psel_ts": "psel_ts",
            "wsrc ; fsel": "fsel",
            "wsrc ; psel": "psel",
            }
    cache_type = cache_type_dict[tag_snk_type]
    prop_cache_prob = prop_cache["prob"]
    prop_cache_type = prop_cache[cache_type]
    tslice = t_src
    def mk_tag(inv_acc):
        return f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc} ; {tag_snk_type}"
    tag = mk_tag(inv_acc=1)
    tag1 = mk_tag(inv_acc=2)
    prob = prop_cache_prob[f"type={inv_type} ; accuracy=1 ; wsrc ; prob"]
    # level light_accuracy strange_accuracy
    # 0     inv_acc=1      inv_acc=1
    # 3     inv_acc=2      inv_acc=2
    assert prob == 1
    val = prop_cache_type.get(tag)
    if tag1 not in prop_cache_type:
        return val
    source_specification = repr(("wall", t_src,))
    val_list = [ val, prop_cache_type.get(tag1), ]
    rel_acc_list = [ 0, 3, ]
    prob_list = [ 1, prop_cache_prob[f"type={inv_type} ; accuracy=2 ; wsrc ; prob"], ]
    return mk_ama_val(val, source_specification, val_list, rel_acc_list, prob_list)

def get_prop_wsnk_wsrc(prop_cache, inv_type, t_snk, t_src):
    sp_prop = get_prop_wsrc(prop_cache, inv_type, t_src, "wsrc_wsnk ; psel_ts")
    def f(x):
        return x.get_elem_wm(t_snk)
    return ama_apply1(f, sp_prop)

def get_prop_psnk_wsrc_fsel(prop_cache, inv_type, xg_snk, t_src, fsel_pos_dict):
    assert isinstance(xg_snk, tuple) and len(xg_snk) == 4
    idx_snk = fsel_pos_dict[xg_snk]
    def f(x):
        return x.get_elem_wm(idx_snk)
    return ama_apply1(f, get_prop_wsrc(prop_cache, inv_type, t_src, "wsrc ; fsel"))

def get_prop_psnk_wsrc_psel(prop_cache, inv_type, xg_snk, t_src, psel_pos_dict):
    assert isinstance(xg_snk, tuple) and len(xg_snk) == 4
    idx_snk = psel_pos_dict[xg_snk]
    def f(x):
        return x.get_elem_wm(idx_snk)
    return ama_apply1(f, get_prop_wsrc(prop_cache, inv_type, t_src, "wsrc ; psel"))

### -------

def get_prop_psrc(prop_cache, inv_type, xg_src, tag_snk_type):
    cache_type_dict = {
            "psrc_wsnk ; psel_ts": "psel_ts",
            "psrc ; fsel": "fsel",
            "psrc ; psel": "psel",
            }
    cache_type = cache_type_dict[tag_snk_type]
    prop_cache_prob = prop_cache["prob"]
    prop_cache_type = prop_cache[cache_type]
    xg = xg_src
    xg_str = f"({xg[0]},{xg[1]},{xg[2]},{xg[3]})"
    def mk_tag(inv_acc):
        return f"xg={xg_str} ; type={inv_type} ; accuracy={inv_acc} ; {tag_snk_type}"
    tag = mk_tag(inv_acc=0)
    tag1 = mk_tag(inv_acc=1)
    tag2 = mk_tag(inv_acc=2)
    prob = prop_cache_prob[f"type={inv_type} ; accuracy=0 ; psrc ; prob"]
    # level light_accuracy strange_accuracy
    # 0     inv_acc=0      inv_acc=0/zero_prop
    # 1     inv_acc=0      inv_acc=0
    # 2     inv_acc=1      inv_acc=1
    # 3     inv_acc=2      inv_acc=2
    source_specification = repr(("point", tuple(xg_src),))
    if prob == 1.0:
        val = prop_cache_type.get(tag)
        assert val is not None
        if tag1 not in prop_cache_type:
            return val
    else:
        assert prob < 1
        assert inv_type == 1
        val = 0
        if tag not in prop_cache_type:
            return val
    val_list = [
            val,
            prop_cache_type.get(tag),
            prop_cache_type.get(tag1),
            prop_cache_type.get(tag2),
            ]
    rel_acc_list = [ 0, 1, 2, 3, ]
    # Should use the same prob list for strange and light for correct AMA merge!!!
    # It should be the same for accuracy=1,2
    # At present, it is a hack for the accuracy=0 case, where number strange quark props may be less than the number of light quark props.
    prob_list = [
            1.0,
            prop_cache_prob[f"type=1 ; accuracy=0 ; psrc ; prob"],
            prop_cache_prob[f"type=1 ; accuracy=1 ; psrc ; prob"],
            prop_cache_prob[f"type=1 ; accuracy=2 ; psrc ; prob"],
            ]
    return mk_ama_val(val, source_specification, val_list, rel_acc_list, prob_list)

def get_prop_wsnk_psrc(prop_cache, inv_type, t_snk, xg_src):
    assert isinstance(xg_src, tuple) and len(xg_src) == 4
    sp_prop = get_prop_psrc(prop_cache, inv_type, xg_src, "psrc_wsnk ; psel_ts")
    def f(x):
        if isinstance(x, int) and x == 0:
            return 0
        return x.get_elem_wm(t_snk)
    return ama_apply1(f, sp_prop)

def get_prop_psnk_psrc_fsel(prop_cache, inv_type, xg_snk, xg_src, fsel_pos_dict):
    assert isinstance(xg_src, tuple) and len(xg_src) == 4
    assert isinstance(xg_snk, tuple) and len(xg_snk) == 4
    idx_snk = fsel_pos_dict[xg_snk]
    def f(x):
        if isinstance(x, int) and x == 0:
            return 0
        return x.get_elem_wm(idx_snk)
    return ama_apply1(f, get_prop_psrc(prop_cache, inv_type, xg_src, "psrc ; fsel"))

def get_prop_psnk_psrc_psel(prop_cache, inv_type, xg_snk, xg_src, psel_pos_dict):
    assert isinstance(xg_src, tuple) and len(xg_src) == 4
    assert isinstance(xg_snk, tuple) and len(xg_snk) == 4
    idx_snk = psel_pos_dict[xg_snk]
    def f(x):
        if isinstance(x, int) and x == 0:
            return 0
        return x.get_elem_wm(idx_snk)
    return ama_apply1(f, get_prop_psrc(prop_cache, inv_type, xg_src, "psrc ; psel"))

### -------

def get_prop_rand_u1_fsel(prop_cache, inv_type):
    inv_acc = 2
    tag = f"type={inv_type} ; accuracy={inv_acc} ; rand_u1 ; fsel"
    return prop_cache["fsel"].get(tag)

def get_prop_psnk_rand_u1_fsel(prop_cache, inv_type, xg_snk, xg_src, fsel_pos_dict):
    assert xg_snk == xg_src
    if isinstance(xg_snk, tuple) and len(xg_snk) == 4:
        idx_snk = fsel_pos_dict[xg_snk]
    else:
        assert isinstance(xg_snk, int)
        idx_snk = xg_snk
    def f(x):
        return x.get_elem_wm(idx_snk)
    return ama_apply1(f, get_prop_rand_u1_fsel(prop_cache, inv_type))

### -------

dict_flavor_inv_type = dict()
dict_flavor_inv_type["l"] = 0
dict_flavor_inv_type["u"] = 0
dict_flavor_inv_type["d"] = 0
dict_flavor_inv_type["s"] = 1
dict_flavor_inv_type["c"] = 2

def f_get_elem_wm(field, pos_snk):
    if isinstance(field, int):
        assert field == 0
        return 0
    return field.get_elem_wm(pos_snk)

def mk_get_elem_wm(field, pos_dict=None):
    """
    return get function
    get(pos_snk) ==> ama_prop
    """
    if pos_dict is None:
        if not isinstance(field, AmaVal):
            def get(pos_snk):
                return f_get_elem_wm(field, pos_snk)
            return get
        else:
            def get(pos_snk):
                return ama_apply2_l(f_get_elem_wm, field, pos_snk)
            return get
    else:
        if not isinstance(field, AmaVal):
            def get(pos_snk):
                idx_snk = pos_dict[pos_snk]
                return f_get_elem_wm(field, idx_snk)
            return get
        else:
            def get(pos_snk):
                idx_snk = pos_dict[pos_snk]
                return ama_apply2_l(f_get_elem_wm, field, idx_snk)
            return get

def f_get_elem_norm_sqrt(field_norm_sqrt, pos_snk):
    if isinstance(field_norm_sqrt, int):
        assert field_norm_sqrt == 0
        return 0
    return field_norm_sqrt.get_elem(pos_snk).item()

def mk_field_norm_sqrt(field):
    if isinstance(field, int):
        assert field == 0
        return 0
    return q.sqrt_field(q.qnorm_field(field))

def mk_get_elem_norm(field, pos_dict=None):
    """
    return get function
    get(pos_snk) ==> ama_prop_norm_sqrt
    """
    field_norm_sqrt = ama_apply1(mk_field_norm_sqrt, field)
    if pos_dict is None:
        if not isinstance(field_norm_sqrt, AmaVal):
            def get(pos_snk):
                return f_get_elem_norm_sqrt(field_norm_sqrt, pos_snk)
            return get
        else:
            def get(pos_snk):
                return ama_apply2_l(f_get_elem_norm_sqrt, field_norm_sqrt, pos_snk)
            return get
    else:
        if not isinstance(field_norm_sqrt, AmaVal):
            def get(pos_snk):
                idx_snk = pos_dict[pos_snk]
                return f_get_elem_norm_sqrt(field_norm_sqrt, idx_snk)
            return get
        else:
            def get(pos_snk):
                idx_snk = pos_dict[pos_snk]
                return ama_apply2_l(f_get_elem_norm_sqrt, field_norm_sqrt, idx_snk)
            return get

@q.timer
def populate_prop_idx_cache_wsrc_psel(job_tag, traj, flavor, total_site, psel, fsel):
    prop_cache = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}")
    prop_lookup_cache = q.mk_cache(f"prop_lookup_cache", f"{job_tag}", f"{traj}")
    prop_norm_lookup_cache = q.mk_cache(f"prop_norm_lookup_cache", f"{job_tag}", f"{traj}")
    psel_pos_dict = prop_cache["psel_pos_dict"]
    fsel_pos_dict = prop_cache["fsel_pos_dict"]
    inv_type = dict_flavor_inv_type[flavor]
    type_src = "wall"
    type_snk = "wall"
    for pos_src in range(total_site[3]):
        key = (flavor, pos_src, type_src, type_snk,)
        t_src = pos_src
        f = get_prop_wsrc(prop_cache, inv_type, t_src, "wsrc_wsnk ; psel_ts")
        prop_lookup_cache[key] = mk_get_elem_wm(f)
        prop_norm_lookup_cache[key] = mk_get_elem_norm(f)
    type_snk = "point"
    for pos_src in range(total_site[3]):
        key = (flavor, pos_src, type_src, type_snk,)
        t_src = pos_src
        f = get_prop_wsrc(prop_cache, inv_type, t_src, "wsrc ; psel")
        prop_lookup_cache[key] = mk_get_elem_wm(f, psel_pos_dict)
        prop_norm_lookup_cache[key] = mk_get_elem_norm(f, psel_pos_dict)

@q.timer
def populate_prop_idx_cache_wsrc_fsel(job_tag, traj, flavor, total_site, psel, fsel):
    prop_cache = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}")
    prop_lookup_cache = q.mk_cache(f"prop_lookup_cache", f"{job_tag}", f"{traj}")
    prop_norm_lookup_cache = q.mk_cache(f"prop_norm_lookup_cache", f"{job_tag}", f"{traj}")
    psel_pos_dict = prop_cache["psel_pos_dict"]
    fsel_pos_dict = prop_cache["fsel_pos_dict"]
    inv_type = dict_flavor_inv_type[flavor]
    type_src = "wall"
    type_snk = "point-snk"
    for pos_src in range(total_site[3]):
        key = (flavor, pos_src, type_src, type_snk,)
        t_src = pos_src
        f = get_prop_wsrc(prop_cache, inv_type, t_src, "wsrc ; fsel")
        prop_lookup_cache[key] = mk_get_elem_wm(f, fsel_pos_dict)
        prop_norm_lookup_cache[key] = mk_get_elem_norm(f, fsel_pos_dict)

@q.timer
def populate_prop_idx_cache_psrc_psel(job_tag, traj, flavor, total_site, psel, fsel):
    prop_cache = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}")
    prop_lookup_cache = q.mk_cache(f"prop_lookup_cache", f"{job_tag}", f"{traj}")
    prop_norm_lookup_cache = q.mk_cache(f"prop_norm_lookup_cache", f"{job_tag}", f"{traj}")
    psel_pos_dict = prop_cache["psel_pos_dict"]
    fsel_pos_dict = prop_cache["fsel_pos_dict"]
    inv_type = dict_flavor_inv_type[flavor]
    type_src = "point"
    type_snk = "point"
    for pos_src in psel:
        pos_src = pos_src.to_tuple()
        key = (flavor, pos_src, type_src, type_snk,)
        xg_src = pos_src
        f = get_prop_psrc(prop_cache, inv_type, xg_src, "psrc ; psel")
        prop_lookup_cache[key] = mk_get_elem_wm(f, psel_pos_dict)
        prop_norm_lookup_cache[key] = mk_get_elem_norm(f, psel_pos_dict)

@q.timer
def populate_prop_idx_cache_psrc_fsel(job_tag, traj, flavor, total_site, psel, fsel):
    prop_cache = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}")
    prop_lookup_cache = q.mk_cache(f"prop_lookup_cache", f"{job_tag}", f"{traj}")
    prop_norm_lookup_cache = q.mk_cache(f"prop_norm_lookup_cache", f"{job_tag}", f"{traj}")
    psel_pos_dict = prop_cache["psel_pos_dict"]
    fsel_pos_dict = prop_cache["fsel_pos_dict"]
    inv_type = dict_flavor_inv_type[flavor]
    type_src = "point"
    type_snk = "point-snk"
    for pos_src in psel:
        pos_src = pos_src.to_tuple()
        key = (flavor, pos_src, type_src, type_snk,)
        xg_src = pos_src
        f = get_prop_psrc(prop_cache, inv_type, xg_src, "psrc ; fsel")
        prop_lookup_cache[key] = mk_get_elem_wm(f, fsel_pos_dict)
        prop_norm_lookup_cache[key] = mk_get_elem_norm(f, fsel_pos_dict)

@q.timer
def populate_prop_idx_cache_rand_u1_fsel(job_tag, traj, flavor, total_site, psel, fsel):
    prop_cache = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}")
    prop_lookup_cache = q.mk_cache(f"prop_lookup_cache", f"{job_tag}", f"{traj}")
    prop_norm_lookup_cache = q.mk_cache(f"prop_norm_lookup_cache", f"{job_tag}", f"{traj}")
    psel_pos_dict = prop_cache["psel_pos_dict"]
    fsel_pos_dict = prop_cache["fsel_pos_dict"]
    inv_type = dict_flavor_inv_type[flavor]
    type_src = "point-snk"
    type_snk = "point-snk"
    f = get_prop_rand_u1_fsel(prop_cache, inv_type)
    for pos_src in fsel.to_psel_local():
        pos_src = tuple(pos_src)
        key = (flavor, pos_src, type_src, type_snk,)
        idx = fsel_pos_dict[pos_src]
        d = { pos_src: idx, }
        prop_lookup_cache[key] = mk_get_elem_wm(f, d)
        prop_norm_lookup_cache[key] = mk_get_elem_norm(f, d)

@q.timer
def get_prop_lookup_snk_src(prop_lookup_cache, flavor, p_snk, p_src):
    """
    p_snk and p_src should be.
    e.g. p_src = ("point", xg,)
    e.g. p_snk = ("point-snk", xg,)
    e.g. p_src = ("wall", t,)
    xg should be tuple of 4 int.
    """
    assert isinstance(p_snk, tuple) and isinstance(p_src, tuple)
    type_snk, pos_snk = p_snk
    type_src, pos_src = p_src
    #
    key = (flavor, pos_src, type_src, type_snk,)
    get = prop_lookup_cache.get(key)
    if get is not None:
        return get(pos_snk)
    else:
        # use g5_herm
        key = (flavor, pos_snk, type_snk, type_src,)
        get = prop_lookup_cache.get(key)
        if get is not None:
            return ("g5_herm", get(pos_src),)
        else:
            q.displayln_info(f"get_prop_lookup_snk_src {flavor} {p_snk} {p_src}")
            assert False
            return None

@q.timer
def get_prop_norm_lookup_snk_src(prop_norm_lookup_cache, flavor, p_snk, p_src):
    """
    return norm_sqrt
    p_snk and p_src should be.
    e.g. p_src = ("point", xg,)
    e.g. p_snk = ("point-snk", xg,)
    e.g. p_src = ("wall", t,)
    xg should be tuple of 4 int.
    """
    assert isinstance(p_snk, tuple) and isinstance(p_src, tuple)
    type_snk, pos_snk = p_snk
    type_src, pos_src = p_src
    #
    key = (flavor, pos_src, type_src, type_snk,)
    get = prop_norm_lookup_cache.get(key)
    if get is not None:
        return get(pos_snk)
    else:
        # use g5_herm
        key = (flavor, pos_snk, type_snk, type_src,)
        get = prop_norm_lookup_cache.get(key)
        if get is not None:
            return get(pos_src)
        else:
            q.displayln_info(f"get_prop_norm_lookup_snk_src {flavor} {p_snk} {p_src}")
            assert False
            return None

### -------

def check_cache_assign(cache, key, val):
    if key in cache:
        assert cache[key] == val
    cache[key] = val

@q.timer
def load_prop_wsrc_psel(job_tag, traj, flavor, *, psel, fsel, gt):
    """
    cache_psel[f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc} ; wsrc ; psel"]
    cache_psel_ts[f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc} ; wsrc_wsnk ; psel_ts"]
    cache_prob[f"type={inv_type} ; accuracy={inv_acc} ; wsrc ; prob"]
    """
    cache_psel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel")
    cache_psel_ts = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel_ts")
    cache_prob = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"prob")
    total_site = q.Coordinate(get_param(job_tag, "total_site"))
    psel_ts = q.get_psel_tslice(total_site)
    if flavor in [ "l", "u", "d", ]:
        flavor_inv_type = 0
        flavor_tag = "light"
    elif flavor in [ "s", ]:
        flavor_inv_type = 1
        flavor_tag = "strange"
    else:
        assert False
    path_sp = f"{job_tag}/psel-prop-wsrc-{flavor_tag}/traj-{traj}"
    if get_load_path(f"{path_sp}.qar", f"{path_sp}/checkpoint.txt") is None:
        return None
    gt_inv = gt.inv()
    count = { 1: 0, 2: 0, }
    inv_type = flavor_inv_type
    wi_list = []
    for inv_acc in [ 2, 1, 0, ]:
        for tslice in range(total_site[3]):
            wi = (tslice, inv_acc,)
            wi_list.append(wi)
    idx = 0
    for tslice, inv_acc in wi_list:
        tag = f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc}"
        if get_load_path(f"{path_sp}/{tag}.lat") is None:
            continue
        q.displayln_info(0, f"load_prop_wsrc_psel: idx={idx} ; tslice={tslice} ; inv_type={inv_type} ; path_sp='{path_sp}'")
        idx += 1
        # load psel psnk prop
        fn_sp = os.path.join(path_sp, f"{tag}.lat")
        sp_prop = q.PselProp(psel)
        sp_prop.load(get_load_path(fn_sp))
        sp_prop = gt_inv * sp_prop
        cache_psel[f"{tag} ; wsrc ; psel"] = sp_prop
        # load wsnk prop
        fn_spw = os.path.join(path_sp, f"{tag} ; wsnk.lat")
        spw_prop = q.PselProp(psel_ts)
        spw_prop.load(get_load_path(fn_spw))
        cache_psel_ts[f"{tag} ; wsrc_wsnk ; psel_ts"] = spw_prop
        # ADJUST ME
        if job_tag == "48I" and flavor == "s" and is_mira_data:
            # 48I strange quark wsrc boundary condition is anti-periodic, different from other 48I props
            # only need this for the MIRA data set (new summit data set have consistent boundary condition).
            q.displayln_info(f"flip_tpbc_with_tslice {job_tag} {flavor} {tag} ; wsrc ; psel")
            q.flip_tpbc_with_tslice(cache_psel[f"{tag} ; wsrc ; psel"], tslice)
            q.displayln_info(f"flip_tpbc_with_tslice {job_tag} {flavor} {tag} ; wsrc_wsnk ; psel_ts")
            q.flip_tpbc_with_tslice(cache_psel_ts[f"{tag} ; wsrc_wsnk ; psel_ts"], tslice)
        #
        # increase count
        count[inv_acc] += 1
    assert count[1] == total_site[3]
    check_cache_assign(cache_prob, f"type={inv_type} ; accuracy=1 ; wsrc ; prob", 1)
    check_cache_assign(cache_prob, f"type={inv_type} ; accuracy=2 ; wsrc ; prob", get_prob_exact_wsrc(job_tag))
    populate_prop_idx_cache_wsrc_psel(job_tag, traj, flavor, total_site, psel, fsel)
    return True

@q.timer
def load_prop_wsrc_fsel(job_tag, traj, flavor, *, psel, fsel, gt):
    """
    need to load psel first
    cache_fsel[f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc} ; wsrc ; fsel"]
    cache_psel[f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc} ; wsrc ; psel"]
    cache_psel_ts[f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc} ; wsrc_wsnk ; psel_ts"]
    cache_prob[f"type={inv_type} ; accuracy={inv_acc} ; wsrc ; prob"]
    """
    cache_fsel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"fsel")
    cache_psel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel")
    cache_psel_ts = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel_ts")
    cache_prob = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"prob")
    total_site = q.Coordinate(get_param(job_tag, "total_site"))
    psel_ts = q.get_psel_tslice(total_site)
    if flavor in [ "l", "u", "d", ]:
        flavor_inv_type = 0
        flavor_tag = "light"
    elif flavor in [ "s", ]:
        flavor_inv_type = 1
        flavor_tag = "strange"
    else:
        assert False
    path_s = f"{job_tag}/prop-wsrc-{flavor_tag}/traj-{traj}"
    if get_load_path(f"{path_s}.qar", f"{path_s}/geon-info.txt") is None:
        return None
    sfr = q.open_fields(get_load_path(path_s + "/geon-info.txt"), "r")
    gt_inv = gt.inv()
    count = { 1: 0, 2: 0, }
    inv_type = flavor_inv_type
    wi_list = []
    for inv_acc in [ 2, 1, 0, ]:
        for tslice in range(total_site[3]):
            wi = (tslice, inv_acc,)
            wi_list.append(wi)
    idx = 0
    for tslice, inv_acc in wi_list:
        tag = f"tslice={tslice} ; type={inv_type} ; accuracy={inv_acc}"
        if tag not in sfr:
            continue
        q.displayln_info(0, f"load_prop_wsrc_fsel: idx={idx} ; tslice={tslice} ; inv_type={inv_type} ; path_s='{path_s}'")
        # load fsel psnk prop
        sc_prop = q.SelProp(fsel)
        sc_prop.load_double_from_float(sfr, tag)
        sc_prop = gt_inv * sc_prop
        cache_fsel[f"{tag} ; wsrc ; fsel"] = sc_prop
        # ADJUST ME
        if job_tag == "48I" and flavor == "s" and is_mira_data:
            # 48I strange quark wsrc boundary condition is anti-periodic, different from other 48I props
            q.displayln_info(f"flip_tpbc_with_tslice {job_tag} {flavor} {tag} ; wsrc ; fsel")
            q.flip_tpbc_with_tslice(cache_fsel[f"{tag} ; wsrc ; fsel"], tslice)
        #
        # check psel psnk prop
        if f"{tag} ; wsrc ; psel" in cache_psel:
            psel_common = psel.intersect(fsel)
            sp_prop_fsel = q.PselProp(psel_common)
            sp_prop_fsel @= sc_prop
            sp_prop_psel = q.PselProp(psel_common)
            sp_prop_psel @= cache_psel[f"{tag} ; wsrc ; psel"]
            sp_prop_psel -= sp_prop_fsel
            assert sp_prop_psel.qnorm() <= 1e-14 * sp_prop_fsel.qnorm()
        # increase count
        count[inv_acc] += 1
    sfr.close()
    assert count[1] == total_site[3]
    check_cache_assign(cache_prob, f"type={inv_type} ; accuracy=1 ; wsrc ; prob", 1)
    check_cache_assign(cache_prob, f"type={inv_type} ; accuracy=2 ; wsrc ; prob", get_prob_exact_wsrc(job_tag))
    populate_prop_idx_cache_wsrc_fsel(job_tag, traj, flavor, total_site, psel, fsel)
    return True

@q.timer
def load_prop_psrc_psel(job_tag, traj, flavor, *, psel, fsel):
    """
    cache_fsel[f"xg=({xg[0]},{xg[1]},{xg[2]},{xg[3]}) ; type={inv_type} ; accuracy={inv_acc} ; psrc ; fsel"]
    cache_psel[f"xg=({xg[0]},{xg[1]},{xg[2]},{xg[3]}) ; type={inv_type} ; accuracy={inv_acc} ; psrc ; psel"]
    cache_psel_ts[f"xg=({xg[0]},{xg[1]},{xg[2]},{xg[3]}) ; type={inv_type} ; accuracy={inv_acc} ; psrc_wsnk ; psel_ts"]
    cache_prob[f"type={inv_type} ; accuracy={inv_acc} ; psrc ; prob"]
    """
    cache_fsel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"fsel")
    cache_psel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel")
    cache_psel_ts = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel_ts")
    cache_prob = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"prob")
    total_site = q.Coordinate(get_param(job_tag, "total_site"))
    psel_ts = q.get_psel_tslice(total_site)
    if flavor in [ "l", "u", "d", ]:
        flavor_inv_type = 0
        flavor_tag = "light"
    elif flavor in [ "s", ]:
        flavor_inv_type = 1
        flavor_tag = "strange"
    else:
        assert False
    path_sp = f"{job_tag}/psel-prop-psrc-{flavor_tag}/traj-{traj}"
    if get_load_path(f"{path_sp}.qar", f"{path_sp}/checkpoint.txt") is None:
        return None
    count = { 0: 0, 1: 0, 2: 0, }
    inv_type = flavor_inv_type
    idx = 0
    for xg, inv_acc in [ (xg, inv_acc) for xg in psel for inv_acc in (0, 1, 2,) ]:
        xg_str = f"({xg[0]},{xg[1]},{xg[2]},{xg[3]})"
        tag = f"xg={xg_str} ; type={inv_type} ; accuracy={inv_acc}"
        fn_sp = os.path.join(path_sp, f"{tag}.lat")
        fn_sp_load = get_load_path(fn_sp)
        if fn_sp_load is None:
            continue
        q.displayln_info(0, f"load_prop_psrc_psel: idx={idx} ; {tag} ; path_sp={path_sp}")
        idx += 1
        # load psel psnk prop
        sp_prop = q.PselProp(psel)
        sp_prop.load(fn_sp_load)
        cache_psel[f"{tag} ; psrc ; psel"] = sp_prop
        # load wsnk prop
        fn_spw = os.path.join(path_sp, f"{tag} ; wsnk.lat")
        fn_spw_load = get_load_path(fn_spw)
        if fn_spw_load is not None:
            spw_prop = q.PselProp(psel_ts)
            spw_prop.load(fn_spw_load)
            cache_psel_ts[f"{tag} ; psrc_wsnk ; psel_ts"] = spw_prop
        count[inv_acc] += 1
    check_cache_assign(cache_prob, f"type={flavor_inv_type} ; accuracy=0 ; psrc ; prob", count[0] / len(psel))
    check_cache_assign(cache_prob, f"type={flavor_inv_type} ; accuracy=1 ; psrc ; prob", rup.dict_params[job_tag]["prob_acc_1_psrc"])
    check_cache_assign(cache_prob, f"type={flavor_inv_type} ; accuracy=2 ; psrc ; prob", rup.dict_params[job_tag]["prob_acc_2_psrc"])
    populate_prop_idx_cache_psrc_psel(job_tag, traj, flavor, total_site, psel, fsel)
    return True

@q.timer
def load_prop_psrc_fsel(job_tag, traj, flavor, *, psel, fsel):
    """
    need to load psel first
    cache_fsel[f"xg=({xg[0]},{xg[1]},{xg[2]},{xg[3]}) ; type={inv_type} ; accuracy={inv_acc} ; psrc ; fsel"]
    cache_psel[f"xg=({xg[0]},{xg[1]},{xg[2]},{xg[3]}) ; type={inv_type} ; accuracy={inv_acc} ; psrc ; psel"]
    cache_psel_ts[f"xg=({xg[0]},{xg[1]},{xg[2]},{xg[3]}) ; type={inv_type} ; accuracy={inv_acc} ; psrc_wsnk ; psel_ts"]
    cache_prob[f"type={inv_type} ; accuracy={inv_acc} ; psrc ; prob"]
    """
    cache_fsel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"fsel")
    cache_psel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel")
    cache_psel_ts = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"psel_ts")
    cache_prob = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"prob")
    total_site = q.Coordinate(get_param(job_tag, "total_site"))
    psel_ts = q.get_psel_tslice(total_site)
    if flavor in [ "l", "u", "d", ]:
        flavor_inv_type = 0
        flavor_tag = "light"
    elif flavor in [ "s", ]:
        flavor_inv_type = 1
        flavor_tag = "strange"
    else:
        assert False
    path_s = f"{job_tag}/prop-psrc-{flavor_tag}/traj-{traj}"
    if get_load_path(f"{path_s}.qar", f"{path_s}/geon-info.txt") is None:
        return None
    sfr = q.open_fields(get_load_path(path_s + "/geon-info.txt"), "r")
    count = { 0: 0, 1: 0, 2: 0, }
    inv_type = flavor_inv_type
    idx = 0
    for xg, inv_acc in [ (xg, inv_acc) for xg in psel for inv_acc in (0, 1, 2,) ]:
        xg_str = f"({xg[0]},{xg[1]},{xg[2]},{xg[3]})"
        tag = f"xg={xg_str} ; type={inv_type} ; accuracy={inv_acc}"
        if tag not in sfr:
            continue
        q.displayln_info(0, f"load_prop_psrc_fsel: idx={idx} ; {tag} ; path_s={path_s}")
        idx += 1
        # load fsel psnk prop
        sc_prop = q.SelProp(fsel)
        sc_prop.load_double_from_float(sfr, tag)
        cache_fsel[f"{tag} ; psrc ; fsel"] = sc_prop
        # check psel psnk prop
        if f"{tag} ; psrc ; psel" in cache_psel:
            psel_common = psel.intersect(fsel)
            sp_prop_fsel = q.PselProp(psel_common)
            sp_prop_fsel @= sc_prop
            sp_prop_psel = q.PselProp(psel_common)
            sp_prop_psel @= cache_psel[f"{tag} ; psrc ; psel"]
            sp_prop_psel -= sp_prop_fsel
            assert sp_prop_psel.qnorm() <= 1e-14 * sp_prop_fsel.qnorm()
        count[inv_acc] += 1
    sfr.close()
    check_cache_assign(cache_prob, f"type={flavor_inv_type} ; accuracy=0 ; psrc ; prob", count[0] / len(psel))
    check_cache_assign(cache_prob, f"type={flavor_inv_type} ; accuracy=1 ; psrc ; prob", rup.dict_params[job_tag]["prob_acc_1_psrc"])
    check_cache_assign(cache_prob, f"type={flavor_inv_type} ; accuracy=2 ; psrc ; prob", rup.dict_params[job_tag]["prob_acc_2_psrc"])
    populate_prop_idx_cache_psrc_fsel(job_tag, traj, flavor, total_site, psel, fsel)
    return True

@q.timer
def load_prop_rand_u1_fsel(job_tag, traj, flavor, *, psel, fsel):
    """
    cache_fsel[f"type={inv_type} ; accuracy={inv_acc} ; rand_u1 ; fsel"]
    """
    cache_fsel = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"fsel")
    total_site = q.Coordinate(get_param(job_tag, "total_site"))
    quark_flavor_list = get_param(job_tag, "quark_flavor_list", default=[ "light", "strange", "charm", ])
    if flavor in [ "l", "u", "d", ]:
        flavor_inv_type = 0
        flavor_tag = quark_flavor_list[flavor_inv_type]
    elif flavor in [ "s", ]:
        flavor_inv_type = 1
        flavor_tag = quark_flavor_list[flavor_inv_type]
    elif flavor in [ "c", ]:
        flavor_inv_type = 2
        flavor_tag = quark_flavor_list[flavor_inv_type]
    else:
        assert False
    inv_type = flavor_inv_type
    s_prop_avg = q.SelProp(fsel)
    q.set_zero(s_prop_avg)
    path_s = f"{job_tag}/prop-rand-u1-{flavor_tag}/traj-{traj}"
    if get_load_path(f"{path_s}.qar", f"{path_s}/geon-info.txt") is None:
        return None
    sfr = q.open_fields(get_load_path(path_s + "/geon-info.txt"), "r")
    tags = sfr.list()
    prob1 = rup.dict_params[job_tag]["prob_acc_1_rand_u1"]
    prob2 = rup.dict_params[job_tag]["prob_acc_2_rand_u1"]
    n_rand_u1_fsel = rup.dict_params[job_tag]["n_rand_u1_fsel"]
    def load(idx_rand_u1, inv_acc):
        tag = f"idx_rand_u1={idx_rand_u1} ; type={inv_type} ; accuracy={inv_acc}"
        if tag not in tags:
            return None
        s_prop = q.SelProp(fsel)
        total_bytes = s_prop.load_double_from_float(sfr, tag)
        assert total_bytes > 0
        return s_prop
    for idx_rand_u1 in range(n_rand_u1_fsel):
        sp0 = load(idx_rand_u1, inv_acc=0)
        assert sp0 is not None
        sp1 = load(idx_rand_u1, inv_acc=1)
        sp2 = load(idx_rand_u1, inv_acc=2)
        if sp2 is not None:
            assert sp1 is not None
            sp2 -= sp1
            sp2 *= 1 / prob2
        if sp1 is not None:
            sp1 -= sp0
            sp1 *= 1 / prob1
        if sp1 is not None:
            sp0 += sp1
        if sp2 is not None:
            sp0 += sp2
        s_prop_avg += sp0
    s_prop_avg *= 1 / n_rand_u1_fsel
    inv_acc = 2
    cache_fsel[f"type={inv_type} ; accuracy={inv_acc} ; rand_u1 ; fsel"] = s_prop_avg
    populate_prop_idx_cache_rand_u1_fsel(job_tag, traj, flavor, total_site, psel, fsel)
    return True

### -------

@q.timer
def load_gauge_hyp(job_tag, traj, *, gf_hyp):
    """
    """
    if gf_hyp is None:
        return None
    gf = gf_hyp
    gauge_cache = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}", f"gauge")
    geo = q.geo_resize(gf.geo)
    gf_dagger = q.GaugeField(geo)
    gf_dagger @= gf
    gf_dagger[:] = gf_dagger[:].transpose((0, 1, 3, 2,)).conj()
    # gf_dagger.show_info()
    expansion_left = q.Coordinate([ 2, 2, 2, 2, ])
    expansion_right = q.Coordinate([ 1, 1, 1, 1, ])
    gf_expand = q.field_expanded(gf, expansion_left, expansion_right)
    gf_expand.show_info()
    gf_dagger_expand = q.field_expanded(gf_dagger, expansion_left, expansion_right)
    gf_dagger_expand.show_info()
    gauge_cache["gauge_hyp"] = gf_expand
    gauge_cache["gauge_hyp-dagger"] = gf_dagger_expand
    return True

@q.timer
def get_gauge_link_lookup_p_mu(prop_cache, tag, p, mu):
    """
    tag can be "gauge_hyp", "gauge_hyp-dagger"
    p should be tuple of 4 int.
    """
    gf = prop_cache["gauge"][tag]
    assert isinstance(p, tuple)
    assert isinstance(mu, int)
    p_tag, p_xg = p
    assert p_tag.startswith("point")
    assert isinstance(p_xg, tuple)
    geo_pos_dict = prop_cache["geo_pos_dict"]
    cm = q.ColorMatrix()
    if mu >= 0:
        assert mu < 4
        idx = geo_pos_dict[p_xg]
        cm[:] = gf[idx, mu]
    else:
        total_site = gf.total_site
        assert mu >= -4
        mu = -mu - 1
        xg_shift = q.Coordinate()
        xg_shift[mu] = -1
        idx = geo_pos_dict[((q.Coordinate(p_xg) + xg_shift) % total_site).to_tuple()]
        cm[:] = gf[idx, mu].T.conj()
    return cm

### -------

@q.timer_verbose
def run_get_prop(job_tag, traj, *,
                 get_gf=None,
                 get_gf_hyp=None,
                 get_gt=None,
                 get_psel,
                 get_fsel,
                 get_psel_smear=None,
                 prop_types=None):
    if get_gf is None:
        get_gf = lambda: None
    if get_gt is None:
        get_gt = lambda: None
    if get_gf_hyp is None:
        get_gf_hyp = lambda: None
    if get_psel_smear is None:
        get_psel_smear = lambda: None
    if prop_types is None:
        # load psel data before fsel data if possible
        # load strange quark before light quark if possible
        prop_types = [
                "wsrc psel s",
                "wsrc psel l",
                "wsrc fsel s",
                "wsrc fsel l",
                "psrc psel s",
                "psrc psel l",
                "psrc fsel s",
                "psrc fsel l",
                "rand_u1 fsel c",
                "rand_u1 fsel s",
                "rand_u1 fsel l",
                "gf hyp",
                ]
    @q.lazy_call
    @q.timer_verbose
    def mk_get_prop():
        with q.TimerFork():
            total_site = q.Coordinate(get_param(job_tag, "total_site"))
            geo = q.Geometry(total_site)
            gf = get_gf()
            gf_hyp = get_gf_hyp()
            gt = get_gt()
            psel = get_psel()
            psel_smear = get_psel_smear()
            fsel = get_fsel()
            #
            prop_cache = q.mk_cache(f"prop_cache", f"{job_tag}", f"{traj}")
            prop_cache["psel_pos_dict"] = dict([ (pos.to_tuple(), i,) for i, pos in enumerate(psel) ])
            psel_local = fsel.to_psel_local()
            prop_cache["fsel_pos_dict"] = dict([ (pos.to_tuple(), i,) for i, pos in enumerate(psel_local) ])
            if "gf hyp" in prop_types:
                prop_cache["geo_pos_dict"] = dict([ (tuple(pos), i,) for i, pos in enumerate(geo.xg_arr()) ])
            #
            prop_load_dict = dict()
            prop_load_dict["wsrc psel s"] = lambda: load_prop_wsrc_psel(job_tag, traj, "s", psel=psel, fsel=fsel, gt=gt)
            prop_load_dict["wsrc psel l"] = lambda: load_prop_wsrc_psel(job_tag, traj, "l", psel=psel, fsel=fsel, gt=gt)
            prop_load_dict["wsrc fsel s"] = lambda: load_prop_wsrc_fsel(job_tag, traj, "s", psel=psel, fsel=fsel, gt=gt)
            prop_load_dict["wsrc fsel l"] = lambda: load_prop_wsrc_fsel(job_tag, traj, "l", psel=psel, fsel=fsel, gt=gt)
            prop_load_dict["psrc psel s"] = lambda: load_prop_psrc_psel(job_tag, traj, "s", psel=psel, fsel=fsel)
            prop_load_dict["psrc psel l"] = lambda: load_prop_psrc_psel(job_tag, traj, "l", psel=psel, fsel=fsel)
            prop_load_dict["psrc fsel s"] = lambda: load_prop_psrc_fsel(job_tag, traj, "s", psel=psel, fsel=fsel)
            prop_load_dict["psrc fsel l"] = lambda: load_prop_psrc_fsel(job_tag, traj, "l", psel=psel, fsel=fsel)
            prop_load_dict["rand_u1 fsel c"] = lambda: load_prop_rand_u1_fsel(job_tag, traj, "c", psel=psel, fsel=fsel)
            prop_load_dict["rand_u1 fsel s"] = lambda: load_prop_rand_u1_fsel(job_tag, traj, "s", psel=psel, fsel=fsel)
            prop_load_dict["rand_u1 fsel l"] = lambda: load_prop_rand_u1_fsel(job_tag, traj, "l", psel=psel, fsel=fsel)
            prop_load_dict["gf hyp"] = lambda: load_gauge_hyp(job_tag, traj, gf_hyp=gf_hyp)
            for pt in prop_types:
                v = prop_load_dict[pt]()
                if v is None:
                    q.displayln_info(f"mk_get_prop: {pt} not available. return None.")
                    return None
            #
            # prop_lookup_cache[(pos_src, type_src, type_snk,)] ==> get_prop_pos_snk
            # where get_prop_pos_snk(pos_snk) ==> ama_prop
            prop_lookup_cache = q.mk_cache(f"prop_lookup_cache", f"{job_tag}", f"{traj}")
            prop_norm_lookup_cache = q.mk_cache(f"prop_norm_lookup_cache", f"{job_tag}", f"{traj}")
        def get_prop(flavor, *args, is_norm_sqrt=False):
            if is_norm_sqrt:
                p_snk, p_src, = args
                return get_prop_norm_lookup_snk_src(prop_norm_lookup_cache, flavor, p_snk, p_src)
            elif flavor == "U":
                tag, p, mu, = args
                return get_gauge_link_lookup_p_mu(prop_cache, tag, p, mu)
            else:
                p_snk, p_src, = args
                return get_prop_lookup_snk_src(prop_lookup_cache, flavor, p_snk, p_src)
        return get_prop
    return mk_get_prop
