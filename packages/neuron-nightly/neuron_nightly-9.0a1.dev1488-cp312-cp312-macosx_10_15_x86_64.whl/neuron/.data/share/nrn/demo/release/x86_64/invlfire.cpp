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
static constexpr auto number_of_datum_variables = 2;
static constexpr auto number_of_floating_point_variables = 7;
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
 
#define nrn_init _nrn_init__IntervalFire
#define _nrn_initial _nrn_initial__IntervalFire
#define nrn_cur _nrn_cur__IntervalFire
#define _nrn_current _nrn_current__IntervalFire
#define nrn_jacob _nrn_jacob__IntervalFire
#define nrn_state _nrn_state__IntervalFire
#define _net_receive _net_receive__IntervalFire 
 
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
#define tau _ml->template fpfield<0>(_iml)
#define tau_columnindex 0
#define invl _ml->template fpfield<1>(_iml)
#define invl_columnindex 1
#define m _ml->template fpfield<2>(_iml)
#define m_columnindex 2
#define minf _ml->template fpfield<3>(_iml)
#define minf_columnindex 3
#define t0 _ml->template fpfield<4>(_iml)
#define t0_columnindex 4
#define v _ml->template fpfield<5>(_iml)
#define v_columnindex 5
#define _tsav _ml->template fpfield<6>(_iml)
#define _tsav_columnindex 6
#define _nd_area *_ml->dptr_field<0>(_iml)
 /* Thread safe. No static _ml, _iml or _ppvar. */
 static int hoc_nrnpointerindex =  -1;
 static _nrn_mechanism_std_vector<Datum> _extcall_thread;
 /* external NEURON variables */
 /* declaration of user functions */
 static double _hoc_M(void*);
 static double _hoc_firetime(void*);
 static int _mechtype;
extern void _nrn_cacheloop_reg(int, int);
extern void hoc_register_limits(int, HocParmLimits*);
extern void hoc_register_units(int, HocParmUnits*);
extern void nrn_promote(Prop*, int, int);
 
#define NMODL_TEXT 1
#if NMODL_TEXT
static void register_nmodl_text_and_filename(int mechtype);
#endif
 extern Prop* nrn_point_prop_;
 static int _pointtype;
 static void* _hoc_create_pnt(Object* _ho) { void* create_point_process(int, Object*);
 return create_point_process(_pointtype, _ho);
}
 static void _hoc_destroy_pnt(void*);
 static double _hoc_loc_pnt(void* _vptr) {double loc_point_process(int, void*);
 return loc_point_process(_pointtype, _vptr);
}
 static double _hoc_has_loc(void* _vptr) {double has_loc_point(void*);
 return has_loc_point(_vptr);
}
 static double _hoc_get_loc_pnt(void* _vptr) {
 double get_loc_point_process(void*); return (get_loc_point_process(_vptr));
}
 static void _hoc_setdata(void*);
 /* connect user functions to hoc names */
 static VoidFunc hoc_intfunc[] = {
 {0, 0}
};
 static Member_func _member_func[] = {
 {"loc", _hoc_loc_pnt},
 {"has_loc", _hoc_has_loc},
 {"get_loc", _hoc_get_loc_pnt},
 {"M", _hoc_M},
 {"firetime", _hoc_firetime},
 {0, 0}
};
#define M M_IntervalFire
#define firetime firetime_IntervalFire
 extern double M( _internalthreadargsproto_ );
 extern double firetime( _internalthreadargsproto_ );
 /* declare global and static user variables */
 #define gind 0
 #define _gth 0
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 {"invl", 1e-09, 1e+09},
 {"tau", 1e-09, 1e+09},
 {0, 0, 0}
};
 static HocParmUnits _hoc_parm_units[] = {
 {"tau", "ms"},
 {"invl", "ms"},
 {0, 0}
};
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 {0, 0}
};
 static DoubVec hoc_vdoub[] = {
 {0, 0, 0}
};
 static double _sav_indep;
 extern void _nrn_setdata_reg(int, void(*)(Prop*));
 static void _setdata(Prop* _prop) {
 }
 static void _hoc_setdata(void* _vptr) { Prop* _prop;
 _prop = ((Point_process*)_vptr)->_prop;
   _setdata(_prop);
 }
 static void nrn_alloc(Prop*);
static void nrn_init(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
static void nrn_state(_nrn_model_sorted_token const&, NrnThread*, Memb_list*, int);
 static void _hoc_destroy_pnt(void* _vptr) {
   destroy_point_process(_vptr);
}
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"IntervalFire",
 "tau",
 "invl",
 0,
 "m",
 0,
 0,
 0};
 
 /* Used by NrnProperty */
 static _nrn_mechanism_std_vector<double> _parm_default{
     5, /* tau */
     10, /* invl */
 }; 
 
 
extern Prop* need_memb(Symbol*);
static void nrn_alloc(Prop* _prop) {
  Prop *prop_ion{};
  Datum *_ppvar{};
  if (nrn_point_prop_) {
    _nrn_mechanism_access_alloc_seq(_prop) = _nrn_mechanism_access_alloc_seq(nrn_point_prop_);
    _ppvar = _nrn_mechanism_access_dparam(nrn_point_prop_);
  } else {
   _ppvar = nrn_prop_datum_alloc(_mechtype, 3, _prop);
    _nrn_mechanism_access_dparam(_prop) = _ppvar;
     _nrn_mechanism_cache_instance _ml_real{_prop};
    auto* const _ml = &_ml_real;
    size_t const _iml{};
    assert(_nrn_mechanism_get_num_vars(_prop) == 7);
 	/*initialize range parameters*/
 	tau = _parm_default[0]; /* 5 */
 	invl = _parm_default[1]; /* 10 */
  }
 	 assert(_nrn_mechanism_get_num_vars(_prop) == 7);
 	_nrn_mechanism_access_dparam(_prop) = _ppvar;
 	/*connect ionic variables to this model*/
 
}
 static void _initlists();
 
#define _tqitem &(_ppvar[2])
 static void _net_receive(Point_process*, double*, double);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
void _nrn_thread_table_reg(int, nrn_thread_table_check_t);
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 extern "C" void _invlfire_reg() {
	int _vectorized = 1;
  _initlists();
 	_pointtype = point_register_mech(_mechanism,
	 nrn_alloc,nullptr, nullptr, nullptr, nrn_init,
	 hoc_nrnpointerindex, 1,
	 _hoc_create_pnt, _hoc_destroy_pnt, _member_func);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
 hoc_register_parm_default(_mechtype, &_parm_default);
     _nrn_setdata_reg(_mechtype, _setdata);
 #if NMODL_TEXT
  register_nmodl_text_and_filename(_mechtype);
#endif
   _nrn_mechanism_register_data_fields(_mechtype,
                                       _nrn_mechanism_field<double>{"tau"} /* 0 */,
                                       _nrn_mechanism_field<double>{"invl"} /* 1 */,
                                       _nrn_mechanism_field<double>{"m"} /* 2 */,
                                       _nrn_mechanism_field<double>{"minf"} /* 3 */,
                                       _nrn_mechanism_field<double>{"t0"} /* 4 */,
                                       _nrn_mechanism_field<double>{"v"} /* 5 */,
                                       _nrn_mechanism_field<double>{"_tsav"} /* 6 */,
                                       _nrn_mechanism_field<double*>{"_nd_area", "area"} /* 0 */,
                                       _nrn_mechanism_field<Point_process*>{"_pntproc", "pntproc"} /* 1 */,
                                       _nrn_mechanism_field<void*>{"_tqitem", "netsend"} /* 2 */);
  hoc_register_prop_size(_mechtype, 7, 3);
  hoc_register_dparam_semantics(_mechtype, 0, "area");
  hoc_register_dparam_semantics(_mechtype, 1, "pntproc");
  hoc_register_dparam_semantics(_mechtype, 2, "netsend");
 add_nrn_artcell(_mechtype, 2);
 add_nrn_has_net_event(_mechtype);
 pnt_receive[_mechtype] = _net_receive;
 pnt_receive_size[_mechtype] = 1;
 
    hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 IntervalFire /Users/runner/work/1/s/build_wheel/share/nrn/demo/release/invlfire.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
static int _reset;
static const char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
 
double M ( _internalthreadargsproto_ ) {
   double _lM;
 _lM = minf + ( m - minf ) * exp ( - ( t - t0 ) / tau ) ;
   
return _lM;
 }
 
static double _hoc_M(void* _vptr) {
 double _r;
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   auto* const _pnt = static_cast<Point_process*>(_vptr);
  auto* const _p = _pnt->_prop;
  if (!_p) {
    hoc_execerror("POINT_PROCESS data instance not valid", NULL);
  }
   _nrn_mechanism_cache_instance _ml_real{_p};
  auto* const _ml = &_ml_real;
  size_t const _iml{};
  _ppvar = _nrn_mechanism_access_dparam(_p);
  _thread = _extcall_thread.data();
  double* _globals = nullptr;
  if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
  _nt = static_cast<NrnThread*>(_pnt->_vnt);
 _r =  M ( _threadargs_ );
 return(_r);
}
 
static void _net_receive (Point_process* _pnt, double* _args, double _lflag) 
{  Prop* _p; Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   _nrn_mechanism_cache_instance _ml_real{_pnt->_prop};
  auto* const _ml = &_ml_real;
  size_t const _iml{};
   _thread = nullptr; double* _globals = nullptr; _nt = (NrnThread*)_pnt->_vnt;   _ppvar = _nrn_mechanism_access_dparam(_pnt->_prop);
  if (_tsav > t){ hoc_execerror(hoc_object_name(_pnt->ob), ":Event arrived out of order. Must call ParallelContext.set_maxstep AFTER assigning minimum NetCon.delay");}
 _tsav = t;   if (_lflag == 1. ) {*(_tqitem) = nullptr;}
 {
   m = M ( _threadargs_ ) ;
   t0 = t ;
   if ( _lflag  == 0.0 ) {
     m = m + _args[0] ;
     if ( m > 1.0 ) {
       m = 0.0 ;
       net_event ( _pnt, t ) ;
       }
     artcell_net_move ( _tqitem, _pnt, t + firetime ( _threadargs_ ) ) ;
     }
   else {
     net_event ( _pnt, t ) ;
     m = 0.0 ;
     artcell_net_send ( _tqitem, _args, _pnt, t +  firetime ( _threadargs_ ) , 1.0 ) ;
     }
   } }
 
double firetime ( _internalthreadargsproto_ ) {
   double _lfiretime;
 _lfiretime = tau * log ( ( minf - m ) / ( minf - 1.0 ) ) ;
   
return _lfiretime;
 }
 
static double _hoc_firetime(void* _vptr) {
 double _r;
 Datum* _ppvar; Datum* _thread; NrnThread* _nt;
   auto* const _pnt = static_cast<Point_process*>(_vptr);
  auto* const _p = _pnt->_prop;
  if (!_p) {
    hoc_execerror("POINT_PROCESS data instance not valid", NULL);
  }
   _nrn_mechanism_cache_instance _ml_real{_p};
  auto* const _ml = &_ml_real;
  size_t const _iml{};
  _ppvar = _nrn_mechanism_access_dparam(_p);
  _thread = _extcall_thread.data();
  double* _globals = nullptr;
  if (gind != 0 && _thread != nullptr) { _globals = _thread[_gth].get<double*>(); }
  _nt = static_cast<NrnThread*>(_pnt->_vnt);
 _r =  firetime ( _threadargs_ );
 return(_r);
}

static void initmodel(_internalthreadargsproto_) {
  int _i; double _save;{
 {
   minf = 1.0 / ( 1.0 - exp ( - invl / tau ) ) ;
   m = 0.0 ;
   t0 = t ;
   artcell_net_send ( _tqitem, nullptr, _ppvar[1].get<Point_process*>(), t +  firetime ( _threadargs_ ) , 1.0 ) ;
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
 _tsav = -1e20;
 initmodel(_threadargs_);
}
}

static double _nrn_current(_internalthreadargsprotocomma_ double _v) {
double _current=0.; v=_v;
{
} return _current;
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
 v=_v;
{
}}

}

static void terminal(){}

static void _initlists(){
 int _i; static int _first = 1;
  if (!_first) return;
_first = 0;
}

#if NMODL_TEXT
static void register_nmodl_text_and_filename(int mech_type) {
    const char* nmodl_filename = "/Users/runner/work/1/s/build_wheel/share/nrn/demo/release/invlfire.mod";
    const char* nmodl_file_text = 
  ": dm/dt = (minf - m)/tau\n"
  ": input event adds w to m\n"
  ": when m = 1, or event makes m >= 1 cell fires\n"
  ": minf is calculated so that the natural interval between spikes is invl\n"
  "\n"
  "NEURON {\n"
  "	ARTIFICIAL_CELL IntervalFire\n"
  "	RANGE tau, m, invl\n"
  "	: m plays the role of voltage\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "	tau = 5 (ms)   <1e-9,1e9>\n"
  "	invl = 10 (ms) <1e-9,1e9>\n"
  "}\n"
  "\n"
  "ASSIGNED {\n"
  "	m\n"
  "	minf\n"
  "	t0(ms)\n"
  "}\n"
  "\n"
  "INITIAL {\n"
  "	minf = 1/(1 - exp(-invl/tau)) : so natural spike interval is invl\n"
  "	m = 0\n"
  "	t0 = t\n"
  "	net_send(firetime(), 1)\n"
  "}\n"
  "\n"
  "FUNCTION M() {\n"
  "	M = minf + (m - minf)*exp(-(t - t0)/tau)\n"
  "}\n"
  "\n"
  "NET_RECEIVE (w) {\n"
  "	m = M()\n"
  "	t0 = t\n"
  "	if (flag == 0) {\n"
  "		m = m + w\n"
  "		if (m > 1) {\n"
  "			m = 0\n"
  "			net_event(t)\n"
  "		}\n"
  "		net_move(t+firetime())\n"
  "	}else{\n"
  "		net_event(t)\n"
  "		m = 0\n"
  "		net_send(firetime(), 1)\n"
  "	}\n"
  "}\n"
  "\n"
  "FUNCTION firetime()(ms) { : m < 1 and minf > 1\n"
  "	firetime = tau*log((minf-m)/(minf - 1))\n"
  ":	printf(\"firetime=%g\\n\", firetime)\n"
  "}\n"
  "\n"
  ;
    hoc_reg_nmodl_filename(mech_type, nmodl_filename);
    hoc_reg_nmodl_text(mech_type, nmodl_file_text);
}
#endif
