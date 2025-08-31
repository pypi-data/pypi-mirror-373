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
static constexpr auto number_of_floating_point_variables = 8;
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
 
#define nrn_init _nrn_init__cachan
#define _nrn_initial _nrn_initial__cachan
#define nrn_cur _nrn_cur__cachan
#define _nrn_current _nrn_current__cachan
#define nrn_jacob _nrn_jacob__cachan
#define nrn_state _nrn_state__cachan
#define _net_receive _net_receive__cachan 
#define castate castate__cachan 
 
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
#define pcabar _ml->template fpfield<0>(_iml)
#define pcabar_columnindex 0
#define ica _ml->template fpfield<1>(_iml)
#define ica_columnindex 1
#define oca _ml->template fpfield<2>(_iml)
#define oca_columnindex 2
#define cai _ml->template fpfield<3>(_iml)
#define cai_columnindex 3
#define cao _ml->template fpfield<4>(_iml)
#define cao_columnindex 4
#define Doca _ml->template fpfield<5>(_iml)
#define Doca_columnindex 5
#define v _ml->template fpfield<6>(_iml)
#define v_columnindex 6
#define _g _ml->template fpfield<7>(_iml)
#define _g_columnindex 7
#define _ion_cai *(_ml->dptr_field<0>(_iml))
#define _p_ion_cai static_cast<neuron::container::data_handle<double>>(_ppvar[0])
#define _ion_cao *(_ml->dptr_field<1>(_iml))
#define _p_ion_cao static_cast<neuron::container::data_handle<double>>(_ppvar[1])
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
 static void _hoc_efun(void);
 static void _hoc_ghk(void);
 static void _hoc_oca_tau(void);
 static void _hoc_oca_ss(void);
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
 {"setdata_cachan", _hoc_setdata},
 {"efun_cachan", _hoc_efun},
 {"ghk_cachan", _hoc_ghk},
 {"oca_tau_cachan", _hoc_oca_tau},
 {"oca_ss_cachan", _hoc_oca_ss},
 {0, 0}
};
 
/* Direct Python call wrappers to density mechanism functions.*/
 static double _npy_efun(Prop*);
 static double _npy_ghk(Prop*);
 static double _npy_oca_tau(Prop*);
 static double _npy_oca_ss(Prop*);
 
static NPyDirectMechFunc npy_direct_func_proc[] = {
 {"efun", _npy_efun},
 {"ghk", _npy_ghk},
 {"oca_tau", _npy_oca_tau},
 {"oca_ss", _npy_oca_ss},
 {0, 0}
};
#define _f_oca_tau _f_oca_tau_cachan
#define _f_oca_ss _f_oca_ss_cachan
#define efun efun_cachan
#define ghk ghk_cachan
#define oca_tau oca_tau_cachan
#define oca_ss oca_ss_cachan
 extern double _f_oca_tau( _internalthreadargsprotocomma_ double );
 extern double _f_oca_ss( _internalthreadargsprotocomma_ double );
 extern double efun( _internalthreadargsprotocomma_ double );
 extern double ghk( _internalthreadargsprotocomma_ double , double , double );
 extern double oca_tau( _internalthreadargsprotocomma_ double );
 extern double oca_ss( _internalthreadargsprotocomma_ double );
 /* declare global and static user variables */
 #define gind 0
 #define _gth 0
#define taufactor taufactor_cachan
 double taufactor = 2;
#define usetable usetable_cachan
 double usetable = 1;
 
static void _check_oca_ss(_internalthreadargsproto_); 
static void _check_oca_tau(_internalthreadargsproto_); 
static void _check_table_thread(_threadargsprotocomma_ int _type, _nrn_model_sorted_token const& _sorted_token) {
  if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); } 
  _nrn_mechanism_cache_range _lmr{_sorted_token, *_nt, *_ml, _type};
  {
    auto* const _ml = &_lmr;
   _check_oca_ss(_threadargs_);
   _check_oca_tau(_threadargs_);
   }
}
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 {"pcabar_cachan", 0, 1e+09},
 {"taufactor_cachan", 1e-06, 1e+06},
 {"usetable_cachan", 0, 1},
 {0, 0, 0}
};
 static HocParmUnits _hoc_parm_units[] = {
 {"taufactor_cachan", "1e-6"},
 {"pcabar_cachan", "cm/s"},
 {"ica_cachan", "mA/cm2"},
 {0, 0}
};
 static double delta_t = 0.01;
 static double oca0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 {"taufactor_cachan", &taufactor_cachan},
 {"usetable_cachan", &usetable_cachan},
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
"cachan",
 "pcabar_cachan",
 0,
 "ica_cachan",
 0,
 "oca_cachan",
 0,
 0};
 static Symbol* _ca_sym;
 
 /* Used by NrnProperty */
 static _nrn_mechanism_std_vector<double> _parm_default{
     2e-08, /* pcabar */
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
    assert(_nrn_mechanism_get_num_vars(_prop) == 8);
 	/*initialize range parameters*/
 	pcabar = _parm_default[0]; /* 2e-08 */
 	 assert(_nrn_mechanism_get_num_vars(_prop) == 8);
 	_nrn_mechanism_access_dparam(_prop) = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_ca_sym);
 nrn_promote(prop_ion, 1, 0);
 	_ppvar[0] = _nrn_mechanism_get_param_handle(prop_ion, 1); /* cai */
 	_ppvar[1] = _nrn_mechanism_get_param_handle(prop_ion, 2); /* cao */
 	_ppvar[2] = _nrn_mechanism_get_param_handle(prop_ion, 3); /* ica */
 	_ppvar[3] = _nrn_mechanism_get_param_handle(prop_ion, 4); /* _ion_dicadv */
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 {0, 0}
};
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
void _nrn_thread_table_reg(int, nrn_thread_table_check_t);
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 extern "C" void _camchan_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("ca", -10000.);
 	_ca_sym = hoc_lookup("ca_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 1);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
 hoc_register_parm_default(_mechtype, &_parm_default);
         hoc_register_npy_direct(_mechtype, npy_direct_func_proc);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_table_reg(_mechtype, _check_table_thread);
 #if NMODL_TEXT
  register_nmodl_text_and_filename(_mechtype);
#endif
   _nrn_mechanism_register_data_fields(_mechtype,
                                       _nrn_mechanism_field<double>{"pcabar"} /* 0 */,
                                       _nrn_mechanism_field<double>{"ica"} /* 1 */,
                                       _nrn_mechanism_field<double>{"oca"} /* 2 */,
                                       _nrn_mechanism_field<double>{"cai"} /* 3 */,
                                       _nrn_mechanism_field<double>{"cao"} /* 4 */,
                                       _nrn_mechanism_field<double>{"Doca"} /* 5 */,
                                       _nrn_mechanism_field<double>{"v"} /* 6 */,
                                       _nrn_mechanism_field<double>{"_g"} /* 7 */,
                                       _nrn_mechanism_field<double*>{"_ion_cai", "ca_ion"} /* 0 */,
                                       _nrn_mechanism_field<double*>{"_ion_cao", "ca_ion"} /* 1 */,
                                       _nrn_mechanism_field<double*>{"_ion_ica", "ca_ion"} /* 2 */,
                                       _nrn_mechanism_field<double*>{"_ion_dicadv", "ca_ion"} /* 3 */,
                                       _nrn_mechanism_field<int>{"_cvode_ieq", "cvodeieq"} /* 4 */);
  hoc_register_prop_size(_mechtype, 8, 5);
  hoc_register_dparam_semantics(_mechtype, 0, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 2, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 3, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 4, "cvodeieq");
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 
    hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 cachan /project/build_wheel/share/nrn/demo/release/camchan.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
 static double FARADAY = 0x1.78e555060882cp+16;
 static double R = 0x1.0a1013e8990bep+3;
 static double *_t_oca_ss;
 static double *_t_oca_tau;
static int _reset;
static const char *modelname = "CaChan";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
 
static int _ode_spec1(_internalthreadargsproto_);
/*static int _ode_matsol1(_internalthreadargsproto_);*/
 static double _n_oca_tau(_internalthreadargsprotocomma_ double _lv);
 static double _n_oca_ss(_internalthreadargsprotocomma_ double _lv);
 static neuron::container::field_index _slist1[1], _dlist1[1];
 static int castate(_internalthreadargsproto_);
 
/*CVODE*/
 static int _ode_spec1 (_internalthreadargsproto_) {int _reset = 0; {
   double _linf , _ltau ;
 _linf = oca_ss ( _threadargscomma_ v ) ;
   _ltau = oca_tau ( _threadargscomma_ v ) ;
   Doca = ( _linf - oca ) / _ltau ;
   }
 return _reset;
}
 static int _ode_matsol1 (_internalthreadargsproto_) {
 double _linf , _ltau ;
 _linf = oca_ss ( _threadargscomma_ v ) ;
 _ltau = oca_tau ( _threadargscomma_ v ) ;
 Doca = Doca  / (1. - dt*( ( ( ( - 1.0 ) ) ) / _ltau )) ;
  return 0;
}
 /*END CVODE*/
 static int castate (_internalthreadargsproto_) { {
   double _linf , _ltau ;
 _linf = oca_ss ( _threadargscomma_ v ) ;
   _ltau = oca_tau ( _threadargscomma_ v ) ;
    oca = oca + (1. - exp(dt*(( ( ( - 1.0 ) ) ) / _ltau)))*(- ( ( ( _linf ) ) / _ltau ) / ( ( ( ( - 1.0 ) ) ) / _ltau ) - oca) ;
   }
  return 0;
}
 
double ghk ( _internalthreadargsprotocomma_ double _lv , double _lci , double _lco ) {
   double _lghk;
 double _lz , _leci , _leco ;
 _lz = ( 1e-3 ) * 2.0 * FARADAY * _lv / ( R * ( celsius + 273.15 ) ) ;
   _leco = _lco * efun ( _threadargscomma_ _lz ) ;
   _leci = _lci * efun ( _threadargscomma_ - _lz ) ;
   _lghk = ( .001 ) * 2.0 * FARADAY * ( _leci - _leco ) ;
   
return _lghk;
 }
 
static void _hoc_ghk(void) {
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
 _r =  ghk ( _threadargscomma_ *getarg(1) , *getarg(2) , *getarg(3) );
 hoc_retpushx(_r);
}
 
static double _npy_ghk(Prop* _prop) {
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
 _r =  ghk ( _threadargscomma_ *getarg(1) , *getarg(2) , *getarg(3) );
 return(_r);
}
 
double efun ( _internalthreadargsprotocomma_ double _lz ) {
   double _lefun;
 if ( fabs ( _lz ) < 1e-4 ) {
     _lefun = 1.0 - _lz / 2.0 ;
     }
   else {
     _lefun = _lz / ( exp ( _lz ) - 1.0 ) ;
     }
   
return _lefun;
 }
 
static void _hoc_efun(void) {
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
 _r =  efun ( _threadargscomma_ *getarg(1) );
 hoc_retpushx(_r);
}
 
static double _npy_efun(Prop* _prop) {
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
 _r =  efun ( _threadargscomma_ *getarg(1) );
 return(_r);
}
 static double _mfac_oca_ss, _tmin_oca_ss;
  static void _check_oca_ss(_internalthreadargsproto_) {
  static int _maktable=1; int _i, _j, _ix = 0;
  double _xi, _tmax;
  if (!usetable) {return;}
  if (_maktable) { double _x, _dx; _maktable=0;
   _tmin_oca_ss =  - 150.0 ;
   _tmax =  150.0 ;
   _dx = (_tmax - _tmin_oca_ss)/200.; _mfac_oca_ss = 1./_dx;
   for (_i=0, _x=_tmin_oca_ss; _i < 201; _x += _dx, _i++) {
    _t_oca_ss[_i] = _f_oca_ss(_threadargscomma_ _x);
   }
  }
 }

 double oca_ss(_internalthreadargsprotocomma_ double _lv) { 
#if 0
_check_oca_ss(_threadargs_);
#endif
 return _n_oca_ss(_threadargscomma_ _lv);
 }

 static double _n_oca_ss(_internalthreadargsprotocomma_ double _lv){ int _i, _j;
 double _xi, _theta;
 if (!usetable) {
 return _f_oca_ss(_threadargscomma_ _lv); 
}
 _xi = _mfac_oca_ss * (_lv - _tmin_oca_ss);
 if (std::isnan(_xi)) {
  return _xi; }
 if (_xi <= 0.) {
 return _t_oca_ss[0];
 }
 if (_xi >= 200.) {
 return _t_oca_ss[200];
 }
 _i = (int) _xi;
 return _t_oca_ss[_i] + (_xi - (double)_i)*(_t_oca_ss[_i+1] - _t_oca_ss[_i]);
 }

 
double _f_oca_ss ( _internalthreadargsprotocomma_ double _lv ) {
   double _loca_ss;
 double _la , _lb ;
 _lv = _lv + 65.0 ;
   _la = 1.0 * efun ( _threadargscomma_ .1 * ( 25.0 - _lv ) ) ;
   _lb = 4.0 * exp ( - _lv / 18.0 ) ;
   _loca_ss = _la / ( _la + _lb ) ;
   
return _loca_ss;
 }
 
static void _hoc_oca_ss(void) {
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
 _check_oca_ss(_threadargs_);
#endif
 _r =  oca_ss ( _threadargscomma_ *getarg(1) );
 hoc_retpushx(_r);
}
 
static double _npy_oca_ss(Prop* _prop) {
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
 _check_oca_ss(_threadargs_);
#endif
 _r =  oca_ss ( _threadargscomma_ *getarg(1) );
 return(_r);
}
 static double _mfac_oca_tau, _tmin_oca_tau;
  static void _check_oca_tau(_internalthreadargsproto_) {
  static int _maktable=1; int _i, _j, _ix = 0;
  double _xi, _tmax;
  static double _sav_celsius;
  static double _sav_taufactor;
  if (!usetable) {return;}
  if (_sav_celsius != celsius) { _maktable = 1;}
  if (_sav_taufactor != taufactor) { _maktable = 1;}
  if (_maktable) { double _x, _dx; _maktable=0;
   _tmin_oca_tau =  - 150.0 ;
   _tmax =  150.0 ;
   _dx = (_tmax - _tmin_oca_tau)/200.; _mfac_oca_tau = 1./_dx;
   for (_i=0, _x=_tmin_oca_tau; _i < 201; _x += _dx, _i++) {
    _t_oca_tau[_i] = _f_oca_tau(_threadargscomma_ _x);
   }
   _sav_celsius = celsius;
   _sav_taufactor = taufactor;
  }
 }

 double oca_tau(_internalthreadargsprotocomma_ double _lv) { 
#if 0
_check_oca_tau(_threadargs_);
#endif
 return _n_oca_tau(_threadargscomma_ _lv);
 }

 static double _n_oca_tau(_internalthreadargsprotocomma_ double _lv){ int _i, _j;
 double _xi, _theta;
 if (!usetable) {
 return _f_oca_tau(_threadargscomma_ _lv); 
}
 _xi = _mfac_oca_tau * (_lv - _tmin_oca_tau);
 if (std::isnan(_xi)) {
  return _xi; }
 if (_xi <= 0.) {
 return _t_oca_tau[0];
 }
 if (_xi >= 200.) {
 return _t_oca_tau[200];
 }
 _i = (int) _xi;
 return _t_oca_tau[_i] + (_xi - (double)_i)*(_t_oca_tau[_i+1] - _t_oca_tau[_i]);
 }

 
double _f_oca_tau ( _internalthreadargsprotocomma_ double _lv ) {
   double _loca_tau;
 double _la , _lb , _lq ;
 _lq = pow( 3.0 , ( ( celsius - 6.3 ) / 10.0 ) ) ;
   _lv = _lv + 65.0 ;
   _la = 1.0 * efun ( _threadargscomma_ .1 * ( 25.0 - _lv ) ) ;
   _lb = 4.0 * exp ( - _lv / 18.0 ) ;
   _loca_tau = taufactor / ( _la + _lb ) ;
   
return _loca_tau;
 }
 
static void _hoc_oca_tau(void) {
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
 _check_oca_tau(_threadargs_);
#endif
 _r =  oca_tau ( _threadargscomma_ *getarg(1) );
 hoc_retpushx(_r);
}
 
static double _npy_oca_tau(Prop* _prop) {
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
 _check_oca_tau(_threadargs_);
#endif
 _r =  oca_tau ( _threadargscomma_ *getarg(1) );
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
  cai = _ion_cai;
  cao = _ion_cao;
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
  cai = _ion_cai;
  cao = _ion_cao;
 _ode_matsol_instance1(_threadargs_);
 }}

static void initmodel(_internalthreadargsproto_) {
  int _i; double _save;{
  oca = oca0;
 {
   oca = oca_ss ( _threadargscomma_ v ) ;
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
 _check_oca_ss(_threadargs_);
 _check_oca_tau(_threadargs_);
#endif
   _v = _vec_v[_ni[_iml]];
 v = _v;
  cai = _ion_cai;
  cao = _ion_cao;
 initmodel(_threadargs_);
 }
}

static double _nrn_current(_internalthreadargsprotocomma_ double _v) {
double _current=0.; v=_v;
{ {
   ica = pcabar * oca * oca * ghk ( _threadargscomma_ v , cai , cao ) ;
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
  cai = _ion_cai;
  cao = _ion_cao;
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
  cai = _ion_cai;
  cao = _ion_cao;
 {   castate(_threadargs_);
  } }}

}

static void terminal(){}

static void _initlists(){
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = {oca_columnindex, 0};  _dlist1[0] = {Doca_columnindex, 0};
   _t_oca_ss = makevector(201*sizeof(double));
   _t_oca_tau = makevector(201*sizeof(double));
_first = 0;
}

#if NMODL_TEXT
static void register_nmodl_text_and_filename(int mech_type) {
    const char* nmodl_filename = "/project/build_wheel/share/nrn/demo/release/camchan.mod";
    const char* nmodl_file_text = 
  "TITLE CaChan\n"
  ": Calcium Channel with Goldman- Hodgkin-Katz permeability\n"
  ": The fraction of open calcium channels has the same kinetics as\n"
  ":   the HH m process but is slower by taufactor\n"
  "\n"
  "UNITS {\n"
  "	(molar) = (1/liter)\n"
  "}\n"
  "\n"
  "UNITS {\n"
  "	(mV) =	(millivolt)\n"
  "	(mA) =	(milliamp)\n"
  "	(mM) =	(millimolar)\n"
  "}\n"
  "\n"
  "NEURON {\n"
  "	SUFFIX cachan\n"
  "	USEION ca READ cai, cao WRITE ica\n"
  "	RANGE pcabar, ica\n"
  "}\n"
  "\n"
  "UNITS {\n"
  "	:FARADAY = 96520 (coul)\n"
  "	:R = 8.3134 (joule/degC)\n"
  "	FARADAY = (faraday) (coulomb)\n"
  "	R = (k-mole) (joule/degC)\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "	taufactor=2	<1e-6, 1e6>: Time constant factor relative to standard HH\n"
  "	pcabar=.2e-7	(cm/s)	<0, 1e9>: Maximum Permeability\n"
  "}\n"
  "\n"
  "ASSIGNED {\n"
  "	celsius		(degC)\n"
  "	v		(mV)\n"
  "	cai		(mM)\n"
  "	cao		(mM)\n"
  "	ica		(mA/cm2)\n"
  "}\n"
  "\n"
  "STATE {	oca }		: fraction of open channels\n"
  "\n"
  "INITIAL {\n"
  "	oca = oca_ss(v)\n"
  "}\n"
  "\n"
  "BREAKPOINT {\n"
  "	SOLVE castate METHOD cnexp\n"
  "	ica = pcabar*oca*oca*ghk(v, cai, cao)\n"
  "}\n"
  "\n"
  "DERIVATIVE castate {\n"
  "	LOCAL inf, tau\n"
  "	inf = oca_ss(v)  tau = oca_tau(v)\n"
  "	oca' = (inf - oca)/tau\n"
  "}\n"
  "\n"
  "FUNCTION ghk(v(mV), ci(mM), co(mM)) (.001 coul/cm3) {\n"
  "	LOCAL z, eci, eco\n"
  "	z = (1e-3)*2*FARADAY*v/(R*(celsius+273.15))\n"
  "	eco = co*efun(z)\n"
  "	eci = ci*efun(-z)\n"
  "	:high cao charge moves inward\n"
  "	:negative potential charge moves inward\n"
  "	ghk = (.001)*2*FARADAY*(eci - eco)\n"
  "}\n"
  "\n"
  "FUNCTION efun(z) {\n"
  "	if (fabs(z) < 1e-4) {\n"
  "		efun = 1 - z/2\n"
  "	}else{\n"
  "		efun = z/(exp(z) - 1)\n"
  "	}\n"
  "}\n"
  "\n"
  "FUNCTION oca_ss(v(mV)) {\n"
  "	LOCAL a, b\n"
  "	TABLE FROM -150 TO 150 WITH 200\n"
  "	\n"
  "	v = v+65\n"
  "	a = 1(1/ms)*efun(.1(1/mV)*(25-v))\n"
  "	b = 4(1/ms)*exp(-v/18(mV))\n"
  "	oca_ss = a/(a + b)\n"
  "}\n"
  "\n"
  "FUNCTION oca_tau(v(mV)) (ms) {\n"
  "	LOCAL a, b, q\n"
  "	TABLE DEPEND celsius, taufactor FROM -150 TO 150 WITH 200\n"
  "\n"
  "	q = 3^((celsius - 6.3)/10 (degC))\n"
  "	v = v+65\n"
  "	a = 1(1/ms)*efun(.1(1/mV)*(25-v))\n"
  "	b = 4(1/ms)*exp(-v/18(mV))\n"
  "	oca_tau = taufactor/(a + b)\n"
  "}\n"
  "\n"
  "COMMENT\n"
  "This model is related to the passive model in that it also describes\n"
  "a membrane channel. However it involves two new concepts in that the\n"
  "channel is ion selective and the conductance of the channel is\n"
  "described by a state variable.\n"
  "\n"
  "Since many membrane mechanisms involve specific ions whose concentration\n"
  "governs a channel current (either directly or via a Nernst potential) and since\n"
  "the sum of the ionic currents of these mechanisms in turn may govern\n"
  "the concentration, it is necessary that NEURON be explicitly told which\n"
  "ionic variables are being used by this model and which are being computed.\n"
  "This is done by the USEION statement.  This statement uses the indicated\n"
  "base name for an ion (call it `base') and ensures the existance of\n"
  "four range variables that can be used by any mechanism that requests them\n"
  "via the USEION statement. I.e. these variables are shared by the different\n"
  "mechanisms.  The four variables are the current, ibase; the\n"
  "equilibrium potential, ebase; the internal concentration, basei; and the\n"
  "external concentration, baseo. (Note that Ca and ca would be distinct\n"
  "ion species).  The READ part of the statement lists the subset of these\n"
  "four variables which are needed as input to the this model's computations.\n"
  "Any changes to those variables within this mechanism will be lost on exit.\n"
  "The WRITE part of the statement lists the subset which are computed by\n"
  "the present mechanism.  If the current is computed, then it's value\n"
  "on exit will be added to the neuron wide value of ibase and will also\n"
  "be added to the total membrane current that is used to calculate the\n"
  "membrane potential.\n"
  "\n"
  "When this model is `insert'ed, fcurrent() executes all the statements\n"
  "of the EQUATION block EXCEPT the SOLVE statement. I.e. the states are\n"
  "NOT integrated in time.  The fadvance() function executes the entire\n"
  "EQUATION block including the SOLVE statement; thus the states are integrated\n"
  "over the interval t to t+dt.\n"
  "\n"
  "Notice that several mechanisms can WRITE to ibase; but it is an error\n"
  "if several mechanisms (in the same section) WRITE to ebase, baseo, or basei.\n"
  "\n"
  "This model makes use of several variables known specially to NEURON. They are\n"
  "celsius, v, and t.  It implicitly makes use of dt.\n"
  "\n"
  "TABLE refers to a special type of FUNCTION in which the value of the\n"
  "function is computed by table lookup with linear interpolation of\n"
  "the table entries.  TABLE's are recomputed automatically whenever a\n"
  "variable that the table depends on (Through the DEPEND list; not needed\n"
  "in these tables) is changed.\n"
  "The TABLE statement indicates the minimum and maximum values of the argument\n"
  "and the number of table entries.  From NEURON, the function oca_ss_cachan(v)\n"
  "returns the proper value in the table. When the variable \"usetable_cachan\"\n"
  "is set to 0, oca_ss_cachan(v)returns the true function value.\n"
  "Thus the table error can be easily plotted.\n"
  "ENDCOMMENT\n"
  ;
    hoc_reg_nmodl_filename(mech_type, nmodl_filename);
    hoc_reg_nmodl_text(mech_type, nmodl_file_text);
}
#endif
