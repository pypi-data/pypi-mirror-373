#include "lib.h"

namespace qlat
{  //

template <class M>
PyObject* refresh_expanded_field_ctype(PyObject* p_field, PyObject* p_comm_plan)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  if (NULL == p_comm_plan) {
    refresh_expanded(f);
  } else {
    const CommPlan& cp = py_convert_type<CommPlan>(p_comm_plan);
    refresh_expanded(f, cp);
  }
  Py_RETURN_NONE;
}

template <class M>
PyObject* refresh_expanded_1_field_ctype(PyObject* p_field)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  refresh_expanded_1(f);
  Py_RETURN_NONE;
}

template <class M, class N>
PyObject* assign_as_field_ctype(Field<N>& f, PyObject* p_field1)
{
  const Field<M>& f1 = py_convert_type_field<M>(p_field1);
  assign(f, f1);
  Py_RETURN_NONE;
}

template <class M, class N>
PyObject* assign_from_field_ctype(PyObject* p_field, const Field<N>& f1)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  assign(f, f1);
  Py_RETURN_NONE;
}

template <class M>
PyObject* get_elems_field_ctype(PyObject* p_field, const Coordinate& xg)
{
  const Field<M>& f = py_convert_type_field<M>(p_field);
  return py_convert(field_get_elems(f, xg));
}

template <class M>
PyObject* get_elem_field_ctype(PyObject* p_field, const Coordinate& xg, const int m)
{
  const Field<M>& f = py_convert_type_field<M>(p_field);
  if (m >= 0) {
    return py_convert(field_get_elem(f, xg, m));
  } else {
    return py_convert(field_get_elem(f, xg));
  }
}

template <class M>
PyObject* set_elems_field_ctype(PyObject* p_field, const Coordinate& xg,
                                PyObject* p_val)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  const int multiplicity = f.multiplicity;
  qassert((Long)PyBytes_Size(p_val) == (Long)multiplicity * (Long)sizeof(M));
  const Vector<M> val((M*)PyBytes_AsString(p_val), multiplicity);
  field_set_elems(f, xg, val);
  Py_RETURN_NONE;
}

template <class M>
PyObject* set_elem_field_ctype(PyObject* p_field, const Coordinate& xg,
                               const int m, PyObject* p_val)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  qassert(PyBytes_Size(p_val) == sizeof(M));
  const M& val = *(M*)PyBytes_AsString(p_val);
  if (m >= 0) {
    field_set_elem(f, xg, m, val);
  } else {
    field_set_elem(f, xg, val);
  }
  Py_RETURN_NONE;
}

template <class M>
PyObject* get_elems_field_ctype(PyObject* p_field, const Long index)
{
  const Field<M>& f = py_convert_type_field<M>(p_field);
  return py_convert(f.get_elems_const(index));
}

template <class M>
PyObject* get_elem_field_ctype(PyObject* p_field, const Long index, const int m)
{
  const Field<M>& f = py_convert_type_field<M>(p_field);
  if (m >= 0) {
    return py_convert(f.get_elem(index, m));
  } else {
    return py_convert(f.get_elem(index));
  }
}

template <class M>
PyObject* set_elems_field_ctype(PyObject* p_field, const Long index,
                                PyObject* p_val)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  const int multiplicity = f.multiplicity;
  qassert((Long)PyBytes_Size(p_val) == (Long)multiplicity * (Long)sizeof(M));
  const Vector<M> val((M*)PyBytes_AsString(p_val), multiplicity);
  assign(f.get_elems(index), val);
  Py_RETURN_NONE;
}

template <class M>
PyObject* set_elem_field_ctype(PyObject* p_field, const Long index,
                               const int m, PyObject* p_val)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  qassert(PyBytes_Size(p_val) == sizeof(M));
  const M& val = *(M*)PyBytes_AsString(p_val);
  if (m >= 0) {
    f.get_elem(index, m) = val;
  } else {
    f.get_elem(index) = val;
  }
  Py_RETURN_NONE;
}

template <class M>
PyObject* fft_fields_ctype(const std::vector<PyObject*>& p_field_vec,
                           const std::vector<int>& fft_dirs,
                           const std::vector<bool>& fft_is_forwards,
                           int mode_fft = 1)
{
  const Long n_field = p_field_vec.size();
  std::vector<Handle<Field<M> > > vec(n_field);
  for (Long i = 0; i < n_field; ++i) {
    vec[i].init(py_convert_type_field<M>(p_field_vec[i]));
  }
  fft_complex_fields(vec, fft_dirs, fft_is_forwards, mode_fft);
  Py_RETURN_NONE;
}

template <class M>
PyObject* field_shift_field_ctype(PyObject* p_field_new, PyObject* p_field,
                                   const Coordinate& shift)
{
  Field<M>& f_new = py_convert_type_field<M>(p_field_new);
  const Field<M>& f = py_convert_type_field<M>(p_field);
  field_shift(f_new, f, shift);
  Py_RETURN_NONE;
}

template <class M>
PyObject* reflect_field_ctype(PyObject* p_field)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  reflect_field(f);
  Py_RETURN_NONE;
}

template <class M>
PyObject* split_fields_field_ctype(const std::vector<PyObject*>& p_f_vec,
                                   PyObject* p_field)
{
  const std::string ctype = py_get_ctype(p_field);
  const Field<M>& f = py_convert_type_field<M>(p_field);
  const int nf = p_f_vec.size();
  std::vector<Handle<Field<M> > > vec(nf);
  for (int i = 0; i < nf; ++i) {
    qassert(py_get_ctype(p_f_vec[i]) == ctype);
    Field<M>& fi = py_convert_type_field<M>(p_f_vec[i]);
    vec[i].init(fi);
  }
  split_fields(vec, f);
  Py_RETURN_NONE;
}

template <class M>
PyObject* merge_fields_field_ctype(PyObject* p_field,
                                   const std::vector<PyObject*>& p_f_vec)
{
  const std::string ctype = py_get_ctype(p_field);
  Field<M>& f = py_convert_type_field<M>(p_field);
  const int nf = p_f_vec.size();
  std::vector<ConstHandle<Field<M> > > vec(nf);
  for (int i = 0; i < nf; ++i) {
    qassert(py_get_ctype(p_f_vec[i]) == ctype);
    const Field<M>& fi = py_convert_type_field<M>(p_f_vec[i]);
    vec[i].init(fi);
  }
  merge_fields(f, vec);
  Py_RETURN_NONE;
}

template <class M>
PyObject* merge_fields_ms_ctype(PyObject* p_field,
                                const std::vector<PyObject*>& p_f_vec,
                                const std::vector<int>& m_vec)
{
  Field<M>& f = py_convert_type_field<M>(p_field);
  const std::string ctype = py_get_ctype(p_field);
  const int multiplicity = p_f_vec.size();
  std::vector<ConstHandle<Field<M> > > vec(multiplicity);
  for (int m = 0; m < multiplicity; ++m) {
    qassert(py_get_ctype(p_f_vec[m]) == ctype);
    const Field<M>& fm = py_convert_type_field<M>(p_f_vec[m]);
    vec[m].init(fm);
  }
  merge_fields_ms(f, vec, m_vec);
  Py_RETURN_NONE;
}

template <class M>
PyObject* qnorm_field_field_ctype(FieldM<double, 1>& f, PyObject* p_field1)
{
  const Field<M>& f1 = py_convert_type_field<M>(p_field1);
  qnorm_field(f, f1);
  Py_RETURN_NONE;
}

}  // namespace qlat

EXPORT(make_field_expand_comm_plan, {
  using namespace qlat;
  PyObject* p_comm_plan = NULL;
  PyObject* p_comm_marks = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_comm_plan, &p_comm_marks)) {
    return NULL;
  }
  CommPlan& cp = py_convert_type<CommPlan>(p_comm_plan);
  const CommMarks& marks = py_convert_type<CommMarks>(p_comm_marks);
  cp = make_comm_plan(marks);
  Py_RETURN_NONE;
})

EXPORT(set_marks_field_all, {
  using namespace qlat;
  PyObject* p_comm_marks = NULL;
  PyObject* p_geo = NULL;
  int multiplicity = 0;
  PyObject* p_tag = NULL;
  if (!PyArg_ParseTuple(args, "OOiO", &p_comm_marks, &p_geo, &multiplicity, &p_tag)) {
    return NULL;
  }
  CommMarks& marks = py_convert_type<CommMarks>(p_comm_marks);
  const Geometry& geo = py_convert_type<Geometry>(p_geo);
  std::string tag = py_convert_data<std::string>(p_tag);
  set_marks_field_all(marks, geo, multiplicity, tag);
  Py_RETURN_NONE;
})

EXPORT(refresh_expanded_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_comm_plan = NULL;
  if (!PyArg_ParseTuple(args, "O|O", &p_field, &p_comm_plan)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, refresh_expanded_field_ctype, ctype, p_field, p_comm_plan);
  return p_ret;
})

EXPORT(refresh_expanded_1_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_field)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, refresh_expanded_1_field_ctype, ctype, p_field);
  return p_ret;
})

EXPORT(set_phase_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_lmom = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field, &p_lmom)) {
    return NULL;
  }
  const CoordinateD lmom = py_convert_data<CoordinateD>(p_lmom);
  FieldM<ComplexD, 1>& f = py_convert_type_field<ComplexD, 1>(p_field);
  set_phase_field(f, lmom);
  Py_RETURN_NONE;
})

EXPORT(assign_as_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_field1 = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field, &p_field1)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  const std::string ctype1 = py_get_ctype(p_field1);
  PyObject* p_ret = NULL;
  if (ctype == "ComplexD") {
    Field<ComplexD>& f = py_convert_type_field<ComplexD>(p_field);
    FIELD_DISPATCH(p_ret, assign_as_field_ctype, ctype1, f, p_field1);
  } else if (ctype == "RealD") {
    Field<double>& f = py_convert_type_field<double>(p_field);
    FIELD_DISPATCH(p_ret, assign_as_field_ctype, ctype1, f, p_field1);
  } else if (ctype == "ComplexF") {
    Field<ComplexF>& f = py_convert_type_field<ComplexF>(p_field);
    FIELD_DISPATCH(p_ret, assign_as_field_ctype, ctype1, f, p_field1);
  } else if (ctype == "RealF") {
    Field<float>& f = py_convert_type_field<float>(p_field);
    FIELD_DISPATCH(p_ret, assign_as_field_ctype, ctype1, f, p_field1);
  } else if (ctype == "Char") {
    Field<char>& f = py_convert_type_field<char>(p_field);
    FIELD_DISPATCH(p_ret, assign_as_field_ctype, ctype1, f, p_field1);
  } else {
    displayln("assign_as_field: " + ctype + " " + ctype1);
    qassert(false);
  }
  return p_ret;
})

EXPORT(assign_from_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_field1 = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field, &p_field1)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  const std::string ctype1 = py_get_ctype(p_field1);
  PyObject* p_ret = NULL;
  if (ctype1 == "ComplexD") {
    const Field<ComplexD>& f1 = py_convert_type_field<ComplexD>(p_field1);
    FIELD_DISPATCH(p_ret, assign_from_field_ctype, ctype, p_field, f1);
  } else if (ctype1 == "RealD") {
    const Field<double>& f1 = py_convert_type_field<double>(p_field1);
    FIELD_DISPATCH(p_ret, assign_from_field_ctype, ctype, p_field, f1);
  } else if (ctype1 == "ComplexF") {
    const Field<ComplexF>& f1 = py_convert_type_field<ComplexF>(p_field1);
    FIELD_DISPATCH(p_ret, assign_from_field_ctype, ctype, p_field, f1);
  } else if (ctype1 == "RealF") {
    const Field<float>& f1 = py_convert_type_field<float>(p_field1);
    FIELD_DISPATCH(p_ret, assign_from_field_ctype, ctype, p_field, f1);
  } else if (ctype1 == "Char") {
    const Field<char>& f1 = py_convert_type_field<char>(p_field1);
    FIELD_DISPATCH(p_ret, assign_from_field_ctype, ctype, p_field, f1);
  } else {
    displayln("assign_from_field: " + ctype + " " + ctype1);
    qassert(false);
  }
  return p_ret;
})

EXPORT(get_elems_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_index = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field, &p_index)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  PyObject* p_ret = NULL;
  if (PyLong_Check(p_index)) {
    const Long index = py_convert_data<Long>(p_index);
    FIELD_DISPATCH(p_ret, get_elems_field_ctype, ctype, p_field, index);
  } else {
    const Coordinate xg = py_convert_data<Coordinate>(p_index);
    FIELD_DISPATCH(p_ret, get_elems_field_ctype, ctype, p_field, xg);
  }
  return p_ret;
})

EXPORT(get_elem_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_index = NULL;
  Long m = -1;
  if (!PyArg_ParseTuple(args, "OO|l", &p_field, &p_index, &m)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  PyObject* p_ret = NULL;
  if (PyLong_Check(p_index)) {
    const Long index = py_convert_data<Long>(p_index);
    FIELD_DISPATCH(p_ret, get_elem_field_ctype, ctype, p_field, index, m);
  } else {
    const Coordinate xg = py_convert_data<Coordinate>(p_index);
    FIELD_DISPATCH(p_ret, get_elem_field_ctype, ctype, p_field, xg, m);
  }
  return p_ret;
})

EXPORT(set_elems_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_index = NULL;
  PyObject* p_val = NULL;
  if (!PyArg_ParseTuple(args, "OOO", &p_field, &p_index, &p_val)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  PyObject* p_ret = NULL;
  if (PyLong_Check(p_index)) {
    const Long index = py_convert_data<Long>(p_index);
    FIELD_DISPATCH(p_ret, set_elems_field_ctype, ctype, p_field, index, p_val);
  } else {
    const Coordinate xg = py_convert_data<Coordinate>(p_index);
    FIELD_DISPATCH(p_ret, set_elems_field_ctype, ctype, p_field, xg, p_val);
  }
  return p_ret;
})

EXPORT(set_elem_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_index = NULL;
  Long m = -1;
  PyObject* p_val = NULL;
  if (!PyArg_ParseTuple(args, "OOlO", &p_field, &p_index, &m, &p_val)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  PyObject* p_ret = NULL;
  if (PyLong_Check(p_index)) {
    const Long index = py_convert_data<Long>(p_index);
    FIELD_DISPATCH(p_ret, set_elem_field_ctype, ctype, p_field, index, m, p_val);
  } else {
    const Coordinate xg = py_convert_data<Coordinate>(p_index);
    FIELD_DISPATCH(p_ret, set_elem_field_ctype, ctype, p_field, xg, m, p_val);
  }
  return p_ret;
})

EXPORT(fft_fields, {
  // forward compute
  // field(k) <- \sum_{x} exp( - ii * 2 pi * k * x ) field(x)
  // backwards compute
  // field(x) <- \sum_{k} exp( + ii * 2 pi * k * x ) field(k)
  using namespace qlat;
  PyObject* p_field_vec = NULL;
  PyObject* p_fft_dirs = NULL;
  PyObject* p_fft_is_forwards = NULL;
  int mode_fft = 1;
  if (!PyArg_ParseTuple(args, "OOO|i", &p_field_vec, &p_fft_dirs,
                        &p_fft_is_forwards, &mode_fft)) {
    return NULL;
  }
  const std::vector<PyObject*> p_f_vec =
      py_convert_data<std::vector<PyObject*> >(p_field_vec);
  qassert(p_f_vec.size() >= 1);
  const std::string ctype = py_get_ctype(p_f_vec[0]);
  for (Long i = 0; i < (Long)p_f_vec.size(); ++i) {
    qassert(ctype == py_get_ctype(p_f_vec[i]));
  }
  const std::vector<int> fft_dirs =
      py_convert_data<std::vector<int> >(p_fft_dirs);
  const std::vector<bool> fft_is_forwards =
      py_convert_data<std::vector<bool> >(p_fft_is_forwards);
  qassert(fft_dirs.size() == fft_is_forwards.size());
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, fft_fields_ctype, ctype, p_f_vec, fft_dirs,
                 fft_is_forwards, mode_fft);
  return p_ret;
})

EXPORT(field_shift_field, {
  using namespace qlat;
  PyObject* p_field_new = NULL;
  PyObject* p_field = NULL;
  PyObject* p_shift = NULL;
  if (!PyArg_ParseTuple(args, "OOO", &p_field_new, &p_field, &p_shift)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  qassert(py_get_ctype(p_field_new) == py_get_ctype(p_field));
  const Coordinate shift = py_convert_data<Coordinate>(p_shift);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, field_shift_field_ctype, ctype, p_field_new, p_field,
                 shift);
  return p_ret;
})

EXPORT(reflect_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_field)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, reflect_field_ctype, ctype, p_field);
  return p_ret;
})

EXPORT(split_fields_field, {
  using namespace qlat;
  PyObject* p_field_vec = NULL;
  PyObject* p_field = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field_vec, &p_field)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  const std::vector<PyObject*> p_f_vec =
      py_convert_data<std::vector<PyObject*> >(p_field_vec);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, split_fields_field_ctype, ctype, p_f_vec, p_field);
  return p_ret;
})

EXPORT(merge_fields_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_field_vec = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field, &p_field_vec)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  const std::vector<PyObject*> p_f_vec =
      py_convert_data<std::vector<PyObject*> >(p_field_vec);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, merge_fields_field_ctype, ctype, p_field, p_f_vec);
  return p_ret;
})

EXPORT(merge_fields_ms_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_field_vec = NULL;
  PyObject* p_m_vec = NULL;
  if (!PyArg_ParseTuple(args, "OOO", &p_field, &p_field_vec, &p_m_vec)) {
    return NULL;
  }
  const std::string ctype = py_get_ctype(p_field);
  const std::vector<PyObject*> p_f_vec =
      py_convert_data<std::vector<PyObject*> >(p_field_vec);
  const std::vector<int> m_vec = py_convert_data<std::vector<int> >(p_m_vec);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, merge_fields_ms_ctype, ctype, p_field, p_f_vec,
                 m_vec);
  return p_ret;
})

EXPORT(qnorm_field_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_field1 = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field, &p_field1)) {
    return NULL;
  }
  FieldM<double, 1>& f = py_convert_type_field<double, 1>(p_field);
  const std::string ctype = py_get_ctype(p_field1);
  PyObject* p_ret = NULL;
  FIELD_DISPATCH(p_ret, qnorm_field_field_ctype, ctype, f, p_field1);
  return p_ret;
})

EXPORT(set_sqrt_field, {
  using namespace qlat;
  PyObject* p_field = NULL;
  PyObject* p_field1 = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_field, &p_field1)) {
    return NULL;
  }
  Field<double>& f = py_convert_type_field<double>(p_field);
  const Field<double>& f1 = py_convert_type_field<double>(p_field1);
  const Geometry geo = geo_resize(f1.geo());
  qassert(geo.is_only_local);
  f.init();
  f.init(geo, f1.multiplicity);
  qacc_for(index, geo.local_volume(), {
    const Coordinate xl = geo.coordinate_from_index(index);
    const Vector<double> f1v = f1.get_elems_const(xl);
    Vector<double> fv = f.get_elems(xl);
    for (int m = 0; m < f1.multiplicity; ++m) {
      fv[m] = std::sqrt(f1v[m]);
    }
  });
  Py_RETURN_NONE;
})
