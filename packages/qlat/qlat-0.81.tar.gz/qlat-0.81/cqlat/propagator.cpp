#include "lib.h"

EXPORT(set_point_src_prop, {
  using namespace qlat;
  PyObject* p_prop = NULL;
  PyObject* p_geo = NULL;
  PyObject* p_xg = NULL;
  ComplexD value = 1.0;
  if (!PyArg_ParseTuple(args, "OOO|D", &p_prop, &p_geo, &p_xg, &value)) {
    return NULL;
  }
  Propagator4d& prop = py_convert_type<Propagator4d>(p_prop);
  const Geometry& geo = py_convert_type<Geometry>(p_geo);
  Coordinate xg;
  py_convert(xg, p_xg);
  set_point_src(prop, geo, xg, value);
  Py_RETURN_NONE;
})

EXPORT(set_wall_src_prop, {
  using namespace qlat;
  PyObject* p_prop = NULL;
  PyObject* p_geo = NULL;
  int tslice = -1;
  PyObject* p_lmom = NULL;
  if (!PyArg_ParseTuple(args, "OOi|O", &p_prop, &p_geo, &tslice, &p_lmom)) {
    return NULL;
  }
  Propagator4d& prop = py_convert_type<Propagator4d>(p_prop);
  const Geometry& geo = py_convert_type<Geometry>(p_geo);
  CoordinateD lmom;
  py_convert(lmom, p_lmom);
  set_wall_src(prop, geo, tslice, lmom);
  Py_RETURN_NONE;
})

EXPORT(set_rand_u1_src_psel, {
  using namespace qlat;
  PyObject* p_prop = NULL;
  PyObject* p_fu1 = NULL;
  PyObject* p_psel = NULL;
  PyObject* p_geo = NULL;
  PyObject* p_rs = NULL;
  if (!PyArg_ParseTuple(args, "OOOOO", &p_prop, &p_fu1, &p_psel, &p_geo, &p_rs)) {
    return NULL;
  }
  Propagator4d& prop = py_convert_type<Propagator4d>(p_prop);
  prop.init();
  FieldM<ComplexD, 1>& fu1 = py_convert_type_field<ComplexD, 1>(p_fu1);
  fu1.init();
  const PointsSelection& psel = py_convert_type<PointsSelection>(p_psel);
  const Geometry& geo = py_convert_type<Geometry>(p_geo);
  const RngState& rs = py_convert_type<RngState>(p_rs);
  set_rand_u1_src_psel(prop, fu1, psel, geo, rs);
  Py_RETURN_NONE;
})

EXPORT(set_rand_u1_sol_psel, {
  using namespace qlat;
  PyObject* p_sp_prop = NULL;
  PyObject* p_prop = NULL;
  PyObject* p_fu1 = NULL;
  PyObject* p_psel = NULL;
  if (!PyArg_ParseTuple(args, "OOOO", &p_sp_prop, &p_prop, &p_fu1, &p_psel)) {
    return NULL;
  }
  SelectedPoints<WilsonMatrix>& sp_prop =
      py_convert_type<SelectedPoints<WilsonMatrix> >(p_sp_prop);
  const Propagator4d& prop = py_convert_type<Propagator4d>(p_prop);
  const FieldM<ComplexD, 1>& fu1 = py_convert_type_field<ComplexD, 1>(p_fu1);
  qassert(fu1.multiplicity == 1);
  const PointsSelection& psel = py_convert_type<PointsSelection>(p_psel);
  set_rand_u1_sol_psel(sp_prop, prop, fu1, psel);
  Py_RETURN_NONE;
})

EXPORT(set_rand_u1_src_fsel, {
  using namespace qlat;
  PyObject* p_prop = NULL;
  PyObject* p_fu1 = NULL;
  PyObject* p_fsel = NULL;
  PyObject* p_rs = NULL;
  if (!PyArg_ParseTuple(args, "OOOO", &p_prop, &p_fu1, &p_fsel, &p_rs)) {
    return NULL;
  }
  Propagator4d& prop = py_convert_type<Propagator4d>(p_prop);
  prop.init();
  FieldM<ComplexD, 1>& fu1 = py_convert_type_field<ComplexD, 1>(p_fu1);
  fu1.init();
  QLAT_PUSH_DIAGNOSTIC_DISABLE_DANGLING_REF;
  const FieldSelection& fsel = py_convert_type<FieldSelection>(p_fsel);
  QLAT_DIAGNOSTIC_POP;
  const RngState& rs = py_convert_type<RngState>(p_rs);
  set_rand_u1_src_fsel(prop, fu1, fsel, rs);
  Py_RETURN_NONE;
})

EXPORT(set_rand_u1_sol_fsel, {
  using namespace qlat;
  PyObject* p_sf_prop = NULL;
  PyObject* p_prop = NULL;
  PyObject* p_fu1 = NULL;
  PyObject* p_fsel = NULL;
  if (!PyArg_ParseTuple(args, "OOOO", &p_sf_prop, &p_prop, &p_fu1, &p_fsel)) {
    return NULL;
  }
  SelectedField<WilsonMatrix>& sf_prop =
      py_convert_type<SelectedField<WilsonMatrix> >(p_sf_prop);
  const Propagator4d& prop = py_convert_type<Propagator4d>(p_prop);
  const FieldM<ComplexD, 1>& fu1 = py_convert_type_field<ComplexD, 1>(p_fu1);
  qassert(fu1.multiplicity == 1);
  QLAT_PUSH_DIAGNOSTIC_DISABLE_DANGLING_REF;
  const FieldSelection& fsel = py_convert_type<FieldSelection>(p_fsel);
  QLAT_DIAGNOSTIC_POP;
  set_rand_u1_sol_fsel(sf_prop, prop, fu1, fsel);
  Py_RETURN_NONE;
})

EXPORT(free_invert_prop, {
  using namespace qlat;
  PyObject* p_prop_sol = NULL;
  PyObject* p_prop_src = NULL;
  double mass = 0.0;
  double m5 = 1.0;
  PyObject* p_momtwist = NULL;
  if (!PyArg_ParseTuple(args, "OOd|dO", &p_prop_sol, &p_prop_src, &mass, &m5,
                        &p_momtwist)) {
    return NULL;
  }
  Propagator4d& prop_sol = py_convert_type<Propagator4d>(p_prop_sol);
  const Propagator4d& prop_src = py_convert_type<Propagator4d>(p_prop_src);
  CoordinateD momtwist;
  py_convert(momtwist, p_momtwist);
  free_invert(prop_sol, prop_src, mass, m5, momtwist);
  Py_RETURN_NONE;
})

EXPORT(convert_wm_from_mspincolor_prop, {
  using namespace qlat;
  PyObject* p_prop_wm = NULL;
  PyObject* p_prop_msc = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_prop_wm, &p_prop_msc)) {
    return NULL;
  }
  Propagator4d& prop_wm = py_convert_type<Propagator4d>(p_prop_wm);
  const Propagator4d& prop_msc = py_convert_type<Propagator4d>(p_prop_msc);
  convert_wm_from_mspincolor(prop_wm, prop_msc);
  Py_RETURN_NONE;
})

EXPORT(convert_mspincolor_from_wm_prop, {
  using namespace qlat;
  PyObject* p_prop_msc = NULL;
  PyObject* p_prop_wm = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_prop_msc, &p_prop_wm)) {
    return NULL;
  }
  Propagator4d& prop_msc = py_convert_type<Propagator4d>(p_prop_msc);
  const Propagator4d& prop_wm = py_convert_type<Propagator4d>(p_prop_wm);
  convert_mspincolor_from_wm(prop_msc, prop_wm);
  Py_RETURN_NONE;
})

EXPORT(convert_wm_from_mspincolor_sp_prop, {
  using namespace qlat;
  PyObject* p_prop_wm = NULL;
  PyObject* p_prop_msc = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_prop_wm, &p_prop_msc)) {
    return NULL;
  }
  SelectedPoints<WilsonMatrix>& prop_wm =
      py_convert_type<SelectedPoints<WilsonMatrix> >(p_prop_wm);
  const SelectedPoints<WilsonMatrix>& prop_msc =
      py_convert_type<SelectedPoints<WilsonMatrix> >(p_prop_msc);
  convert_wm_from_mspincolor(prop_wm, prop_msc);
  Py_RETURN_NONE;
})

EXPORT(convert_mspincolor_from_wm_sp_prop, {
  using namespace qlat;
  PyObject* p_prop_msc = NULL;
  PyObject* p_prop_wm = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_prop_msc, &p_prop_wm)) {
    return NULL;
  }
  SelectedPoints<WilsonMatrix>& prop_msc =
      py_convert_type<SelectedPoints<WilsonMatrix> >(p_prop_msc);
  const SelectedPoints<WilsonMatrix>& prop_wm =
      py_convert_type<SelectedPoints<WilsonMatrix> >(p_prop_wm);
  convert_mspincolor_from_wm(prop_msc, prop_wm);
  Py_RETURN_NONE;
})

EXPORT(convert_wm_from_mspincolor_s_prop, {
  using namespace qlat;
  PyObject* p_prop_wm = NULL;
  PyObject* p_prop_msc = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_prop_wm, &p_prop_msc)) {
    return NULL;
  }
  SelectedField<WilsonMatrix>& prop_wm =
      py_convert_type<SelectedField<WilsonMatrix> >(p_prop_wm);
  const SelectedField<WilsonMatrix>& prop_msc =
      py_convert_type<SelectedField<WilsonMatrix> >(p_prop_msc);
  convert_wm_from_mspincolor(prop_wm, prop_msc);
  Py_RETURN_NONE;
})

EXPORT(convert_mspincolor_from_wm_s_prop, {
  using namespace qlat;
  PyObject* p_prop_msc = NULL;
  PyObject* p_prop_wm = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_prop_msc, &p_prop_wm)) {
    return NULL;
  }
  SelectedField<WilsonMatrix>& prop_msc =
      py_convert_type<SelectedField<WilsonMatrix> >(p_prop_msc);
  const SelectedField<WilsonMatrix>& prop_wm =
      py_convert_type<SelectedField<WilsonMatrix> >(p_prop_wm);
  convert_mspincolor_from_wm(prop_msc, prop_wm);
  Py_RETURN_NONE;
})

EXPORT(free_scalar_invert_mom_cfield, {
  using namespace qlat;
  PyObject* p_field = NULL;
  double mass = 0.0;
  if (!PyArg_ParseTuple(args, "Od", &p_field, &mass)) {
    return NULL;
  }
  qassert("ComplexD" == py_get_ctype(p_field));
  Field<ComplexD>& f = py_convert_type_field<ComplexD>(p_field);
  const CoordinateD momtwist;
  prop_free_scalar_invert(f, mass, momtwist);
  Py_RETURN_NONE;
})

EXPORT(flip_tpbc_with_tslice_sp_prop, {
  using namespace qlat;
  PyObject* p_sp_prop = NULL;
  int tslice_flip_tpbc = -1;
  if (!PyArg_ParseTuple(args, "Oi", &p_sp_prop, &tslice_flip_tpbc)) {
    return NULL;
  }
  SelectedPoints<WilsonMatrix>& sp_prop =
      py_convert_type_spoints<WilsonMatrix>(p_sp_prop);
  QLAT_PUSH_DIAGNOSTIC_DISABLE_DANGLING_REF;
  const PointsSelection& psel =
      py_convert_type<PointsSelection>(p_sp_prop, "psel");
  const Geometry& geo = py_convert_type<Geometry>(p_sp_prop, "psel", "geo");
  QLAT_DIAGNOSTIC_POP;
  const int t_size = geo.total_site()[3];
  flip_tpbc_with_tslice(sp_prop, psel, tslice_flip_tpbc, t_size);
  Py_RETURN_NONE;
})

EXPORT(flip_tpbc_with_tslice_s_prop, {
  using namespace qlat;
  PyObject* p_s_prop = NULL;
  int tslice_flip_tpbc = -1;
  if (!PyArg_ParseTuple(args, "Oi", &p_s_prop, &tslice_flip_tpbc)) {
    return NULL;
  }
  SelectedField<WilsonMatrix>& s_prop =
      py_convert_type_sfield<WilsonMatrix>(p_s_prop);
  QLAT_PUSH_DIAGNOSTIC_DISABLE_DANGLING_REF;
  const FieldSelection& fsel =
      py_convert_type<FieldSelection>(p_s_prop, "fsel");
  QLAT_DIAGNOSTIC_POP;
  flip_tpbc_with_tslice(s_prop, fsel, tslice_flip_tpbc);
  Py_RETURN_NONE;
})
