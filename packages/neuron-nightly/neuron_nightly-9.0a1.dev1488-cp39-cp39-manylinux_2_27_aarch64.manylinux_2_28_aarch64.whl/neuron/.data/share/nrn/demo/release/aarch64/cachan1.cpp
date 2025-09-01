/* Created by Language version: 7.7.0 */
/* VECTORIZED */
#define NRN_VECTORIZED 1
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "mech_api.h"
#undef PI
#define nil 0
#define _pval pval
// clang-format off
#include "md1redef.h"
#include "section_fwd.hpp"
#include "nrniv_mf.h"
#include "md2redef.h"
#include "nrnconf.h"
// clang-format on
#include "neuron/cache/mechanism_range.hpp"
static constexpr auto number_of_datum_variables = 4;
static constexpr auto number_of_floating_point_variables = 9;
namespace {
template <typename T>
using _nrn_mechanism_std_vector = std::vector<T>;
using _nrn_model_sorted_token = neuron::model_sorted_token;
using _nrn_mechanism_cache_range = neuron::cache::MechanismRange<number_of_floating_point_variables, number_of_datum_variables>;
using _nrn_mechanism_cache_instance = neuron::cache::MechanismInstance<number_of_floating_point_variables, number_of_datum_variables>;
using _nrn_non_owning_id_without_container = neuron::container::non_owning_identifier_without_container;
template <typename T>
using _nrn_mechanism_field = neuron::mechanism::field<T>;
template <typename... Args>
void _nrn_mechanism_register_data_fields(Args&&... args) {
  neuron::mechanism::register_data_fields(std::forward<Args>(args)...);
}
}
 
#if !NRNGPU
#undef exp
#define exp hoc_Exp
#if NRN_ENABLE_ARCH_INDEP_EXP_POW
#undef pow
#define pow hoc_pow
#endif
#endif
 
#define nrn_init _nrn_init__cachan1
#define _nrn_initial _nrn_initial__cachan1
#define nrn_cur _nrn_cur__cachan1
#define _nrn_current _nrn_current__cachan1
#define nrn_jacob _nrn_jacob__cachan1
#define nrn_state _nrn_state__cachan1
#define _net_receive _net_receive__cachan1 
#define _f_rate _f_rate__cachan1 
#define rate rate__cachan1 
#define states states__cachan1 
 
#define _threadargscomma_ _ml, _iml, _ppvar, _thread, _globals, _nt,
#define _threadargsprotocomma_ Memb_list* _ml, size_t _iml, Datum* _ppvar, Datum* _thread, double* _globals, NrnThread* _nt,
#define _internalthreadargsprotocomma_ _nrn_mechanism_cache_range* _ml, size_t _iml, Datum* _ppvar, Datum* _thread, double* _globals, NrnThread* _nt,
#define _threadargs_ _ml, _iml, _ppvar, _thread, _globals, _nt
#define _threadargsproto_ Memb_list* _ml, size_t _iml, Datum* _ppvar, Datum* _thread, double* _globals, NrnThread* _nt
#define _internalthreadargsproto_ _nrn_mechanism_cache_range* _ml, size_t _iml, Datum* _ppvar, Datum* _thread, double* _globals, NrnThread* _nt
 	/*SUPPRESS 761*/
	/*SUPPRESS 762*/
	/*SUPPRESS 763*/
	/*SUPPRESS 765*/
	 extern double *hoc_getarg(int);
 
#define t _nt->_t
#define dt _nt->_dt
#define K _ml->template fpfield<0>(_iml)
#define K_columnindex 0
#define imax _ml->template fpfield<1>(_iml)
#define imax_columnindex 1
#define ica _ml->template fpfield<2>(_iml)
#define ica_columnindex 2
#define S _ml->template fpfield<3>(_iml)
#define S_columnindex 3
#define DS _ml->template fpfield<4>(_iml)
#define DS_columnindex 4
#define cao _ml->template fpfield<5>(_iml)
#define cao_columnindex 5
#define cai _ml->template fpfield<6>(_iml)
#define cai_columnindex 6
#define v _ml->template fpfield<7>(_iml)
#define v_columnindex 7
#define _g _ml->template fpfield<8>(_iml)
#define _g_columnindex 8
#define _ion_cao *(_ml->dptr_field<0>(_iml))
#define _p_ion_cao static_cast<neuron::container::data_handle<double>>(_ppvar[0])
#define _ion_cai *(_ml->dptr_field<1>(_iml))
#define _p_ion_cai static_cast<neuron::container::data_handle<double>>(_ppvar[1])
#define _ion_ica *(_ml->dptr_field<2>(_iml))
#define _p_ion_ica static_cast<neuron::container::data_handle<double>>(_ppvar[2])
#define _ion_dicadv *(_ml->dptr_field<3>(_iml))
 /* Thread safe. No static _ml, _iml or _ppvar. */
 static int hoc_nrnpointerindex =  -1;
 static _nrn_mechanism_std_vector<Datum> _extcall_thread;
 static Prop* _extcall_prop;
 /* _prop_id kind of shadows _extcall_prop to allow validity checking. */
 static _nrn_non_owning_id_without_container _prop_id{};
 /* external NEURON variables */
 extern double celsius;
 /* declaration of user functions */
 static void _hoc_alp(void);
 static void _hoc_bet(void);
 static void _hoc_rate(void);
 static int _mechtype;
extern void _nrn_cacheloop_reg(int, int);
extern void hoc_register_limits(int, HocParmLimits*);
extern void hoc_register_units(int, HocParmUnits*);
extern void nrn_promote(Prop*, int, int);
 
#define NMODL_TEXT 1
#if NMODL_TEXT
static void register_nmodl_text_and_filename(int mechtype);
#endif
 static void _hoc_setdata();
 /* connect user functions to hoc names */
 static VoidFunc hoc_intfunc[] = {
 {"setdata_cachan1", _hoc_setdata},
 {"alp_cachan1", _hoc_alp},
 {"bet_cachan1", _hoc_bet},
 {"rate_cachan1", _hoc_rate},
 {0, 0}
};
 
/* Direct Python call wrappers to density mechanism functions.*/
 static double _npy_alp(Prop*);
 static double _npy_bet(Prop*);
 static double _npy_rate(Prop*);
 
static NPyDirectMechFunc npy_direct_func_proc[] = {
 {"alp", _npy_alp},
 {"bet", _npy_bet},
 {"rate", _npy_rate},
 {0, 0}
};
#define alp alp_cachan1
#define bet bet_cachan1
 extern double alp( _internalthreadargsprotocomma_ double );
 extern double bet( _internalthreadargsprotocomma_ double );
 /* declare global and static user variables */
 #define gind 2
 static int _thread1data_inuse = 0;
static double _thread1data[2];
#define _gth 0
#define inf_cachan1 _thread1data[0]
#define inf _globals[0]
#define rfac rfac_cachan1
 double rfac = 1;
#define tau_cachan1 _thread1data[1]
#define tau _globals[1]
#define usetable usetable_cachan1
 double usetable = 1;
 
static void _check_rate(_internalthreadargsproto_); 
static void _check_table_thread(_threadargsprotocomma_ int _type, _nrn_model_sorted_token const& _sorted_token) {
  if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); } 
  _nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml, _type};
  {
    auto* const _ml = &_lmr;
   _check_rate(_threadargs_);
   }
}
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 {"K_cachan1", 1e-06, 1e+06},
 {"imax_cachan1", 0, 1e+09},
 {"rfac_cachan1", 0.01, 100000},
 {"usetable_cachan1", 0, 1},
 {0, 0, 0}
};
 static HocParmUnits _hoc_parm_units[] = {
 {"rfac_cachan1", ".01"},
 {"tau_cachan1", "ms"},
 {"K_cachan1", "/M"},
 {"imax_cachan1", "mA/cm2"},
 {"ica_cachan1", "mA/cm2"},
 {0, 0}
};
 static double S0 = 0;
 static double delta_t = 0.01;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 {"rfac_cachan1", &rfac_cachan1},
 {"inf_cachan1", &inf_cachan1},
 {"tau_cachan1", &tau_cachan1},
 {"usetable_cachan1", &usetable_cachan1},
 {0, 0}
};
 static DoubVec hoc_vdoub[] = {
 {0, 0, 0}
};
 static double _sav_indep;
 extern void _nrn_setdata_reg(int, void(*)(Prop*));
 static void _setdata(Prop* _prop) {
 _extcall_prop = _prop;
 _prop_id = _nrn_get_prop_id(_prop);
 }
 static void _hoc_setdata() {
 Prop *_prop, *hoc_getdata_range(int);
 _prop = hoc_getdata_range(_mechtype);
   _setdata(_prop);
 hoc_retpushx(1.);
}
 static void nrn_alloc(Prop*);
static void nrn_init(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
static void nrn_state(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
 static void nrn_cur(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
static void nrn_jacob(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
 
static int _ode_count(int);
static void _ode_map(Prop*, int, neuron::container::data_handle<double>*, neuron::container::data_handle<double>*, double*, int);
static void _ode_spec(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
static void _ode_matsol(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
 
#define _cvode_ieq _ppvar[4].literal_value<int>()
 static void _ode_matsol_instance1(_internalthreadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"cachan1",
 "K_cachan1",
 "imax_cachan1",
 0,
 "ica_cachan1",
 0,
 "S_cachan1",
 0,
 0};
 static Symbol* _ca_sym;
 
 /* Used by NrnProperty */
 static _nrn_mechanism_std_vector<double> _parm_default{
     140, /* K */
     1, /* imax */
 }; 
 
 
extern Prop* need_memb(Symbol*);
static void nrn_alloc(Prop* _prop) {
  Prop *prop_ion{};
  Datum *_ppvar{};
   _ppvar = nrn_prop_datum_alloc(_mechtype, 5, _prop);
    _nrn_mechanism_access_dparam(_prop) = _ppvar;
     _nrn_mechanism_cache_instance _ml_real{_prop};
    auto* const _ml = &_ml_real;
    size_t const _iml{};
    assert(_nrn_mechanism_get_num_vars(_prop) == 9);
 	/*initialize range parameters*/
 	K = _parm_default[0]; /* 140 */
 	imax = _parm_default[1]; /* 1 */
 	 assert(_nrn_mechanism_get_num_vars(_prop) == 9);
 	_nrn_mechanism_access_dparam(_prop) = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_ca_sym);
 nrn_promote(prop_ion, 1, 0);
 	_ppvar[0] = _nrn_mechanism_get_param_handle(prop_ion, 2); /* cao */
 	_ppvar[1] = _nrn_mechanism_get_param_handle(prop_ion, 1); /* cai */
 	_ppvar[2] = _nrn_mechanism_get_param_handle(prop_ion, 3); /* ica */
 	_ppvar[3] = _nrn_mechanism_get_param_handle(prop_ion, 4); /* _ion_dicadv */
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 {0, 0}
};
 static void _thread_mem_init(Datum*);
 static void _thread_cleanup(Datum*);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
void _nrn_thread_table_reg(int, nrn_thread_table_check_t);
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 extern "C" void _cachan1_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("ca", -10000.);
 	_ca_sym = hoc_lookup("ca_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 2);
  _extcall_thread.resize(1);
  _thread_mem_init(_extcall_thread.data());
  _thread1data_inuse = 0;
 _mechtype = nrn_get_mechtype(_mechanism[1]);
 hoc_register_parm_default(_mechtype, &_parm_default);
         hoc_register_npy_direct(_mechtype, npy_direct_func_proc);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 1, _thread_mem_init);
     _nrn_thread_reg(_mechtype, 0, _thread_cleanup);
     _nrn_thread_table_reg(_mechtype, _check_table_thread);
 #if NMODL_TEXT
  register_nmodl_text_and_filename(_mechtype);
#endif
   _nrn_mechanism_register_data_fields(_mechtype,
                                       _nrn_mechanism_field<double>{"K"} /* 0 */,
                                       _nrn_mechanism_field<double>{"imax"} /* 1 */,
                                       _nrn_mechanism_field<double>{"ica"} /* 2 */,
                                       _nrn_mechanism_field<double>{"S"} /* 3 */,
                                       _nrn_mechanism_field<double>{"DS"} /* 4 */,
                                       _nrn_mechanism_field<double>{"cao"} /* 5 */,
                                       _nrn_mechanism_field<double>{"cai"} /* 6 */,
                                       _nrn_mechanism_field<double>{"v"} /* 7 */,
                                       _nrn_mechanism_field<double>{"_g"} /* 8 */,
                                       _nrn_mechanism_field<double*>{"_ion_cao", "ca_ion"} /* 0 */,
                                       _nrn_mechanism_field<double*>{"_ion_cai", "ca_ion"} /* 1 */,
                                       _nrn_mechanism_field<double*>{"_ion_ica", "ca_ion"} /* 2 */,
                                       _nrn_mechanism_field<double*>{"_ion_dicadv", "ca_ion"} /* 3 */,
                                       _nrn_mechanism_field<int>{"_cvode_ieq", "cvodeieq"} /* 4 */);
  hoc_register_prop_size(_mechtype, 9, 5);
  hoc_register_dparam_semantics(_mechtype, 0, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 2, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 3, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 4, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 
    hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 cachan1 /project/build_wheel/share/nrn/demo/release/cachan1.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
 static double k = 0x1.0b0e6d55e647cp-76;
 static double e = 0x1.7a4da290c1653p-63;
 static double *_t_inf;
 static double *_t_tau;
static int _reset;
static const char *modelname = "ca channel";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
static int _f_rate(_internalthreadargsprotocomma_ double);
static int rate(_internalthreadargsprotocomma_ double);
 
static int _ode_spec1(_internalthreadargsproto_);
/*static int _ode_matsol1(_internalthreadargsproto_);*/
 static void _n_rate(_internalthreadargsprotocomma_ double _lv);
 static neuron::container::field_index _slist1[1], _dlist1[1];
 static int states(_internalthreadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (_internalthreadargsproto_) {int _reset = 0; {
   rate ( _threadargscomma_ v ) ;
   DS = ( inf - S ) / tau ;
   }
 return _reset;
}
 static int _ode_matsol1 (_internalthreadargsproto_) {
 rate ( _threadargscomma_ v ) ;
 DS = DS  / (1. - dt*( ( ( ( - 1.0 ) ) ) / tau )) ;
  return 0;
}
 /*END CVODE*/
 static int states (_internalthreadargsproto_) { {
   rate ( _threadargscomma_ v ) ;
    S = S + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / tau)))*(- ( ( ( inf ) ) / tau ) / ( ( ( ( - 1.0 ) ) ) / tau ) - S) ;
   }
  return 0;
}
 
double alp ( _internalthreadargsprotocomma_ double _lv ) {
   double _lalp;
 _lalp = rfac * 1.1 * exp ( .85 * ( .001 ) * e / k / ( 273.0 + celsius ) * _lv ) ;
   
return _lalp;
 }
 
static void _hoc_alp(void) {
  double _r;
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
 
  Prop* _local_prop = _prop_id ? _extcall_prop : nullptr;
  _nrn_mechanism_cache_instance _ml_real{_local_prop};
auto* const _ml = &_ml_real;
size_t const _iml{};
_ppvar = _local_prop ? _nrn_mechanism_access_dparam(_local_prop) : nullptr;
_thread = _extcall_thread.data();
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
_nt = nrn_threads;
 _r =  alp ( _threadargscomma_ *getarg(1) );
 hoc_retpushx(_r);
}
 
static double _npy_alp(Prop* _prop) {
    double _r{0.0};
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
 _nrn_mechanism_cache_instance _ml_real{_prop};
auto* const _ml = &_ml_real;
size_t const _iml{};
_ppvar = _nrn_mechanism_access_dparam(_prop);
_thread = _extcall_thread.data();
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
_nt = nrn_threads;
 _r =  alp ( _threadargscomma_ *getarg(1) );
 return(_r);
}
 
double bet ( _internalthreadargsprotocomma_ double _lv ) {
   double _lbet;
 _lbet = rfac * .168 * exp ( - .38 * ( .001 ) * e / k / ( 273.0 + celsius ) * _lv ) ;
   
return _lbet;
 }
 
static void _hoc_bet(void) {
  double _r;
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
 
  Prop* _local_prop = _prop_id ? _extcall_prop : nullptr;
  _nrn_mechanism_cache_instance _ml_real{_local_prop};
auto* const _ml = &_ml_real;
size_t const _iml{};
_ppvar = _local_prop ? _nrn_mechanism_access_dparam(_local_prop) : nullptr;
_thread = _extcall_thread.data();
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
_nt = nrn_threads;
 _r =  bet ( _threadargscomma_ *getarg(1) );
 hoc_retpushx(_r);
}
 
static double _npy_bet(Prop* _prop) {
    double _r{0.0};
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
 _nrn_mechanism_cache_instance _ml_real{_prop};
auto* const _ml = &_ml_real;
size_t const _iml{};
_ppvar = _nrn_mechanism_access_dparam(_prop);
_thread = _extcall_thread.data();
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
_nt = nrn_threads;
 _r =  bet ( _threadargscomma_ *getarg(1) );
 return(_r);
}
 static double _mfac_rate, _tmin_rate;
  static void _check_rate(_internalthreadargsproto_) {
  static int _maktable=1; int _i, _j, _ix = 0;
  double _xi, _tmax;
  static double _sav_celsius;
  static double _sav_rfac;
  if (!usetable) {return;}
  if (_sav_celsius != celsius) { _maktable = 1;}
  if (_sav_rfac != rfac) { _maktable = 1;}
  if (_maktable) { double _x, _dx; _maktable=0;
   _tmin_rate =  - 100.0 ;
   _tmax =  100.0 ;
   _dx = (_tmax - _tmin_rate)/200.; _mfac_rate = 1./_dx;
   for (_i=0, _x=_tmin_rate; _i < 201; _x += _dx, _i++) {
    _f_rate(_threadargscomma_ _x);
    _t_inf[_i] = inf;
    _t_tau[_i] = tau;
   }
   _sav_celsius = celsius;
   _sav_rfac = rfac;
  }
 }

 static int rate(_internalthreadargsprotocomma_ double _lv) { 
#if 0
_check_rate(_threadargs_);
#endif
 _n_rate(_threadargscomma_ _lv);
 return 0;
 }

 static void _n_rate(_internalthreadargsprotocomma_ double _lv){ int _i, _j;
 double _xi, _theta;
 if (!usetable) {
 _f_rate(_threadargscomma_ _lv); return; 
}
 _xi = _mfac_rate * (_lv - _tmin_rate);
 if (std::isnan(_xi)) {
  inf = _xi;
  tau = _xi;
  return;
 }
 if (_xi <= 0.) {
 inf = _t_inf[0];
 tau = _t_tau[0];
 return; }
 if (_xi >= 200.) {
 inf = _t_inf[200];
 tau = _t_tau[200];
 return; }
 _i = (int) _xi;
 _theta = _xi - (double)_i;
 inf = _t_inf[_i] + _theta*(_t_inf[_i+1] - _t_inf[_i]);
 tau = _t_tau[_i] + _theta*(_t_tau[_i+1] - _t_tau[_i]);
 }

 
static int  _f_rate ( _internalthreadargsprotocomma_ double _lv ) {
   double _la , _lb ;
 _la = alp ( _threadargscomma_ _lv ) ;
   _lb = bet ( _threadargscomma_ _lv ) ;
   tau = 1.0 / ( _la + _lb ) ;
   inf = _la / ( _la + _lb ) ;
    return 0; }
 
static void _hoc_rate(void) {
  double _r;
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
 
  Prop* _local_prop = _prop_id ? _extcall_prop : nullptr;
  _nrn_mechanism_cache_instance _ml_real{_local_prop};
auto* const _ml = &_ml_real;
size_t const _iml{};
_ppvar = _local_prop ? _nrn_mechanism_access_dparam(_local_prop) : nullptr;
_thread = _extcall_thread.data();
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
_nt = nrn_threads;
 
#if 1
 _check_rate(_threadargs_);
#endif
 _r = 1.;
 rate ( _threadargscomma_ *getarg(1) );
 hoc_retpushx(_r);
}
 
static double _npy_rate(Prop* _prop) {
    double _r{0.0};
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
 _nrn_mechanism_cache_instance _ml_real{_prop};
auto* const _ml = &_ml_real;
size_t const _iml{};
_ppvar = _nrn_mechanism_access_dparam(_prop);
_thread = _extcall_thread.data();
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
_nt = nrn_threads;
 
#if 1
 _check_rate(_threadargs_);
#endif
 _r = 1.;
 rate ( _threadargscomma_ *getarg(1) );
 return(_r);
}
 
static int _ode_count(int _type){ return 1;}
 
static void _ode_spec(_nrn_model_sorted_token const& _sorted_token, NrnThread* _nt, Memb_list* _ml_arg, int _type) {
   Datum* _ppvar;
   size_t _iml;   _nrn_mechanism_cache_range* _ml;   Node* _nd{};
  double _v{};
  int _cntml;
  _nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml_arg, _type};
  _ml = &_lmr;
  _cntml = _ml_arg->_nodecount;
  Datum *_thread{_ml_arg->_thread};
  double* _globals = nullptr;
  if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _ppvar = _ml_arg->_pdata[_iml];
    _nd = _ml_arg->_nodelist[_iml];
    v = NODEV(_nd);
  cao = _ion_cao;
  cai = _ion_cai;
     _ode_spec1 (_threadargs_);
  }}
 
static void _ode_map(Prop* _prop, int _ieq, neuron::container::data_handle<double>* _pv, neuron::container::data_handle<double>* _pvdot, double* _atol, int _type) { 
  Datum* _ppvar;
  _ppvar = _nrn_mechanism_access_dparam(_prop);
  _cvode_ieq = _ieq;
  for (int _i=0; _i < 1; ++_i) {
    _pv[_i] = _nrn_mechanism_get_param_handle(_prop, _slist1[_i]);
    _pvdot[_i] = _nrn_mechanism_get_param_handle(_prop, _dlist1[_i]);
    _cvode_abstol(_atollist, _atol, _i);
  }
 }
 
static void _ode_matsol_instance1(_internalthreadargsproto_) {
 _ode_matsol1 (_threadargs_);
 }
 
static void _ode_matsol(_nrn_model_sorted_token const& _sorted_token, NrnThread* _nt, Memb_list* _ml_arg, int _type) {
   Datum* _ppvar;
   size_t _iml;   _nrn_mechanism_cache_range* _ml;   Node* _nd{};
  double _v{};
  int _cntml;
  _nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml_arg, _type};
  _ml = &_lmr;
  _cntml = _ml_arg->_nodecount;
  Datum *_thread{_ml_arg->_thread};
  double* _globals = nullptr;
  if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
  for (_iml = 0; _iml < _cntml; ++_iml) {
    _ppvar = _ml_arg->_pdata[_iml];
    _nd = _ml_arg->_nodelist[_iml];
    v = NODEV(_nd);
  cao = _ion_cao;
  cai = _ion_cai;
 _ode_matsol_instance1(_threadargs_);
 }}
 
static void _thread_mem_init(Datum* _thread) {
 if (_thread1data_inuse) {
  _thread[_gth] = {neuron::container::do_not_search, new double[2]{}};
} else {
  _thread[_gth] = {neuron::container::do_not_search, _thread1data};
  _thread1data_inuse = 1;
}
 }
 
static void _thread_cleanup(Datum* _thread) {
  if (_thread[_gth].get<double*>() == _thread1data) {
   _thread1data_inuse = 0;
  }else{
   delete[] _thread[_gth].get<double*>();
  }
 }

static void initmodel(_internalthreadargsproto_) {
  int _i; double _save;{
  S = S0;
 {
   rate ( _threadargscomma_ v ) ;
   S = inf ;
   }
 
}
}

static void nrn_init(_nrn_model_sorted_token const& _sorted_token, NrnThread* _nt, Memb_list* _ml_arg, int _type){
_nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml_arg, _type};
auto* const _vec_v = _nt->node_voltage_storage();
auto* const _ml = &_lmr;
Datum* _ppvar; Datum* _thread;
Node *_nd; double _v; int* _ni; int _iml, _cntml;
_ni = _ml_arg->_nodeindices;
_cntml = _ml_arg->_nodecount;
_thread = _ml_arg->_thread;
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
for (_iml = 0; _iml < _cntml; ++_iml) {
 _ppvar = _ml_arg->_pdata[_iml];

#if 0
 _check_rate(_threadargs_);
#endif
   _v = _vec_v[_ni[_iml]];
 v = _v;
  cao = _ion_cao;
  cai = _ion_cai;
 initmodel(_threadargs_);
 }
}

static double _nrn_current(_internalthreadargsprotocomma_ double _v) {
double _current=0.; v=_v;
{ {
   double _lkca ;
 _lkca = K * cao * exp ( - .08 * ( v + 70.0 ) ) ;
   ica = - imax * pow( S , 5.0 ) * ( _lkca - K * cai ) / ( 1.0 + _lkca ) ;
   }
 _current += ica;

} return _current;
}

static void nrn_cur(_nrn_model_sorted_token const& _sorted_token, NrnThread* _nt, Memb_list* _ml_arg, int _type) {
_nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml_arg, _type};
auto const _vec_rhs = _nt->node_rhs_storage();
auto const _vec_sav_rhs = _nt->node_sav_rhs_storage();
auto const _vec_v = _nt->node_voltage_storage();
auto* const _ml = &_lmr;
Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; double _rhs, _v; int _iml, _cntml;
_ni = _ml_arg->_nodeindices;
_cntml = _ml_arg->_nodecount;
_thread = _ml_arg->_thread;
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
for (_iml = 0; _iml < _cntml; ++_iml) {
 _ppvar = _ml_arg->_pdata[_iml];
   _v = _vec_v[_ni[_iml]];
  cao = _ion_cao;
  cai = _ion_cai;
 auto const _g_local = _nrn_current(_threadargscomma_ _v + .001);
 	{ double _dica;
  _dica = ica;
 _rhs = _nrn_current(_threadargscomma_ _v);
  _ion_dicadv += (_dica - ica)/.001 ;
 	}
 _g = (_g_local - _rhs)/.001;
  _ion_ica += ica ;
	 _vec_rhs[_ni[_iml]] -= _rhs;
 
}
 
}

static void nrn_jacob(_nrn_model_sorted_token const& _sorted_token, NrnThread* _nt, Memb_list* _ml_arg, int _type) {
_nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml_arg, _type};
auto const _vec_d = _nt->node_d_storage();
auto const _vec_sav_d = _nt->node_sav_d_storage();
auto* const _ml = &_lmr;
Datum* _ppvar; Datum* _thread;
Node *_nd; int* _ni; int _iml, _cntml;
_ni = _ml_arg->_nodeindices;
_cntml = _ml_arg->_nodecount;
_thread = _ml_arg->_thread;
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
for (_iml = 0; _iml < _cntml; ++_iml) {
  _vec_d[_ni[_iml]] += _g;
 
}
 
}

static void nrn_state(_nrn_model_sorted_token const& _sorted_token, NrnThread* _nt, Memb_list* _ml_arg, int _type) {
_nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml_arg, _type};
auto* const _vec_v = _nt->node_voltage_storage();
auto* const _ml = &_lmr;
Datum* _ppvar; Datum* _thread;
Node *_nd; double _v = 0.0; int* _ni;
_ni = _ml_arg->_nodeindices;
size_t _cntml = _ml_arg->_nodecount;
_thread = _ml_arg->_thread;
double* _globals = nullptr;
if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
for (size_t _iml = 0; _iml < _cntml; ++_iml) {
 _ppvar = _ml_arg->_pdata[_iml];
 _nd = _ml_arg->_nodelist[_iml];
   _v = _vec_v[_ni[_iml]];
 v=_v;
{
  cao = _ion_cao;
  cai = _ion_cai;
 {   states(_threadargs_);
  } }}

}

static void terminal(){}

static void _initlists(){
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = {S_columnindex, 0};  _dlist1[0] = {DS_columnindex, 0};
   _t_inf = makevector(201*sizeof(double));
   _t_tau = makevector(201*sizeof(double));
_first = 0;
}

#if NMODL_TEXT
static void register_nmodl_text_and_filename(int mech_type) {
    const char* nmodl_filename = "/project/build_wheel/share/nrn/demo/release/cachan1.mod";
    const char* nmodl_file_text = 
  "TITLE ca channel\n"
  ": Ca channel used  by Augustine (1990) J. Physiol. 431\n"
  ":  341-364   should use at celsius = 16\n"
  "\n"
  "NEURON {\n"
  "	SUFFIX cachan1\n"
  "	USEION ca READ cao,cai WRITE ica\n"
  "	RANGE K, ica, imax\n"
  "	GLOBAL inf, tau, rfac\n"
  "	THREADSAFE\n"
  "}\n"
  "\n"
  "UNITS {\n"
  "	(mA) = (milliamp)\n"
  "	(mV) = (millivolt)\n"
  "	(M) = (1/liter)\n"
  "	(mM) = (milliM)\n"
  "	k = (k) (joule/degC)\n"
  "	e = (e) (coulombs)\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "	rfac = 1	<.01, 1e5>\n"
  "	K = 140 (/M)	<1e-6, 1e6>\n"
  "	imax = 1 (mA/cm2) <0, 1e9>\n"
  "}\n"
  "\n"
  "STATE {\n"
  "	S\n"
  "}\n"
  "\n"
  "ASSIGNED {\n"
  "	v (mV)\n"
  "	cao (mM)\n"
  "	cai (mM)\n"
  "	celsius (degC) : 16\n"
  "	ica (mA/cm2)\n"
  "	inf\n"
  "	tau (ms)\n"
  "}\n"
  "\n"
  "\n"
  "INITIAL {\n"
  "	rate(v)\n"
  "	S = inf\n"
  "}\n"
  "\n"
  "BREAKPOINT {LOCAL kca\n"
  "	SOLVE states METHOD cnexp\n"
  "	kca = K*cao*exp(-.08(/mV)*(v+70))\n"
  "	ica = -imax * S^5 * (kca - K*cai)/(1 + kca)\n"
  "}\n"
  "\n"
  "DERIVATIVE states {	: exact when v held constant\n"
  "	rate(v)\n"
  "	S' = (inf - S)/tau\n"
  "}\n"
  "\n"
  "FUNCTION alp(v(mV))(/ms) {\n"
  "	alp = rfac * 1.1(/ms)*exp(.85*(.001)*e/k/(273+celsius)*v)\n"
  "}\n"
  "\n"
  "FUNCTION bet(v(mV))(/ms) {\n"
  "		bet = rfac * .168(/ms)*exp(-.38*(.001)*e/k/(273+celsius)*v)\n"
  "}\n"
  "\n"
  "PROCEDURE rate(v(mV)) {LOCAL a, b\n"
  "	TABLE inf, tau DEPEND celsius, rfac FROM -100 TO 100 WITH 200\n"
  "		a = alp(v)  b=bet(v)\n"
  "		tau = 1/(a + b)\n"
  "		inf = a/(a + b)\n"
  "}\n"
  ;
    hoc_reg_nmodl_filename(mech_type, nmodl_filename);
    hoc_reg_nmodl_text(mech_type, nmodl_file_text);
}
#endif
