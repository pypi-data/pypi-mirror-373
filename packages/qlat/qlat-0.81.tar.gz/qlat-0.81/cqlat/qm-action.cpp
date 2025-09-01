#include "lib.h"

EXPORT(mk_qm_action, {
  using namespace qlat;
  double alpha = 0.0;
  double beta = 0.0;
  double FV_offset = 0.0;
  double TV_offset = 0.0;
  double barrier_strength = 1.0;
  double L = 1.0;
  double M = 0.0;
  double epsilon = 0.0;
  long t_FV_out = 10;
  long t_FV_mid = 5;
  double dt = 1.0;
  bool measure_offset_L = false;
  bool measure_offset_M = false;
  
  if (!PyArg_ParseTuple(args, "d|d|d|d|d|d|d|d|l|l|d|b|b", &alpha, &beta, &FV_offset, &TV_offset,
      &barrier_strength, &L, &M, &epsilon, &t_FV_out, &t_FV_mid, &dt, 
      &measure_offset_L, &measure_offset_M)) {
    return NULL;
  }
  QMAction* pqma = new QMAction(alpha, beta, FV_offset, TV_offset, barrier_strength, L, M, epsilon, t_FV_out, t_FV_mid, dt, measure_offset_L, measure_offset_M);
  return py_convert((void*)pqma);
})

EXPORT(free_qm_action, {
  using namespace qlat;
  return free_obj<QMAction>(args);
})

EXPORT(set_qm_action, {
  using namespace qlat;
  return set_obj<QMAction>(args);
})

EXPORT(get_alpha_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.alpha);
})

EXPORT(get_beta_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.beta);
})

EXPORT(get_barrier_strength_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.barrier_strength);
})

EXPORT(get_M_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.M);
})

EXPORT(get_L_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.L);
})

EXPORT(get_t_FV_out_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.t_FV_out);
})

EXPORT(get_t_FV_mid_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.t_FV_mid);
})

EXPORT(get_dt_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  if (!PyArg_ParseTuple(args, "O", &p_qma)) {
    return NULL;
  }
  const QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.dt);
})

EXPORT(V_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  double x = 0.0;
  long t = 0;
  if (!PyArg_ParseTuple(args, "O|d|l", &p_qma, &x, &t)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.V(x,t));
})

EXPORT(dV_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  double x = 0.0;
  long t = 0;
  if (!PyArg_ParseTuple(args, "O|d|l", &p_qma, &x, &t)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  return py_convert(qma.dV(x,t));
})

EXPORT(action_node_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  PyObject* p_f = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_qma, &p_f)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  const Field<double>& f = py_convert_type<Field<double>>(p_f);
  const double ret = qma.action_node(f);
  return py_convert(ret);
})

EXPORT(hmc_m_hamilton_node_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  PyObject* p_m = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_qma, &p_m)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  const Field<double>& m = py_convert_type<Field<double>>(p_m);
  const double ret = qma.hmc_m_hamilton_node(m);
  return py_convert(ret);
})

EXPORT(sum_sq_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  PyObject* p_f = NULL;
  if (!PyArg_ParseTuple(args, "OO", &p_qma, &p_f)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  const Field<double>& f = py_convert_type<Field<double>>(p_f);
  const double ret = qma.sum_sq(f);
  return py_convert(ret);
})

EXPORT(hmc_set_force_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  PyObject* p_force = NULL;
  PyObject* p_f = NULL;
  if (!PyArg_ParseTuple(args, "OOO", &p_qma, &p_force, &p_f)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  Field<double>& force = py_convert_type<Field<double>>(p_force);
  const Field<double>& f = py_convert_type<Field<double>>(p_f);
  qma.hmc_set_force(force, f);
  Py_RETURN_NONE;
})

EXPORT(hmc_field_evolve_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  PyObject* p_f = NULL;
  PyObject* p_m = NULL;
  double step_size = 0.0;
  if (!PyArg_ParseTuple(args, "OOOd", &p_qma, &p_f, &p_m, &step_size)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  Field<double>& f = py_convert_type<Field<double>>(p_f);
  const Field<double>& m = py_convert_type<Field<double>>(p_m);
  qma.hmc_field_evolve(f, m, step_size);
  Py_RETURN_NONE;
})

EXPORT(hmc_set_rand_momentum_qm_action, {
  using namespace qlat;
  PyObject* p_qma = NULL;
  PyObject* p_m = NULL;
  PyObject* p_rs = NULL;
  if (!PyArg_ParseTuple(args, "OOO", &p_qma, &p_m, &p_rs)) {
    return NULL;
  }
  QMAction& qma = py_convert_type<QMAction>(p_qma);
  Field<double>& m = py_convert_type<Field<double>>(p_m);
  const RngState& rs = py_convert_type<RngState>(p_rs);
  qma.hmc_set_rand_momentum(m, rs);
  Py_RETURN_NONE;
})
