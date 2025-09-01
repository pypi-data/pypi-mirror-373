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
static constexpr auto number_of_datum_variables = 7;
static constexpr auto number_of_floating_point_variables = 18;
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
 
#define nrn_init _nrn_init__capmpr
#define _nrn_initial _nrn_initial__capmpr
#define nrn_cur _nrn_cur__capmpr
#define _nrn_current _nrn_current__capmpr
#define nrn_jacob _nrn_jacob__capmpr
#define nrn_state _nrn_state__capmpr
#define _net_receive _net_receive__capmpr 
#define pmp pmp__capmpr 
 
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
#define pump _ml->template fpfield<0>(_iml)
#define pump_columnindex 0
#define pumpca _ml->template fpfield<1>(_iml)
#define pumpca_columnindex 1
#define Dpump _ml->template fpfield<2>(_iml)
#define Dpump_columnindex 2
#define Dpumpca _ml->template fpfield<3>(_iml)
#define Dpumpca_columnindex 3
#define cai _ml->template fpfield<4>(_iml)
#define cai_columnindex 4
#define Dcai _ml->template fpfield<5>(_iml)
#define Dcai_columnindex 5
#define cao _ml->template fpfield<6>(_iml)
#define cao_columnindex 6
#define ica _ml->template fpfield<7>(_iml)
#define ica_columnindex 7
#define ipump _ml->template fpfield<8>(_iml)
#define ipump_columnindex 8
#define ipump_last _ml->template fpfield<9>(_iml)
#define ipump_last_columnindex 9
#define voli _ml->template fpfield<10>(_iml)
#define voli_columnindex 10
#define area1 _ml->template fpfield<11>(_iml)
#define area1_columnindex 11
#define c1 _ml->template fpfield<12>(_iml)
#define c1_columnindex 12
#define c2 _ml->template fpfield<13>(_iml)
#define c2_columnindex 13
#define c3 _ml->template fpfield<14>(_iml)
#define c3_columnindex 14
#define c4 _ml->template fpfield<15>(_iml)
#define c4_columnindex 15
#define v _ml->template fpfield<16>(_iml)
#define v_columnindex 16
#define _g _ml->template fpfield<17>(_iml)
#define _g_columnindex 17
#define _ion_cao *(_ml->dptr_field<0>(_iml))
#define _p_ion_cao static_cast<neuron::container::data_handle<double>>(_ppvar[0])
#define _ion_cai *(_ml->dptr_field<1>(_iml))
#define _p_ion_cai static_cast<neuron::container::data_handle<double>>(_ppvar[1])
#define _ion_ica *(_ml->dptr_field<2>(_iml))
#define _p_ion_ica static_cast<neuron::container::data_handle<double>>(_ppvar[2])
#define _ion_dicadv *(_ml->dptr_field<3>(_iml))
#define _ion_ca_erev *_ml->dptr_field<4>(_iml)
#define _style_ca	*_ppvar[5].get<int*>()
#define diam	(*(_ml->dptr_field<6>(_iml)))
 /* Thread safe. No static _ml, _iml or _ppvar. */
 static int hoc_nrnpointerindex =  -1;
 static _nrn_mechanism_std_vector<Datum> _extcall_thread;
 static Prop* _extcall_prop;
 /* _prop_id kind of shadows _extcall_prop to allow validity checking. */
 static _nrn_non_owning_id_without_container _prop_id{};
 /* external NEURON variables */
 /* declaration of user functions */
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
 {"setdata_capmpr", _hoc_setdata},
 {0, 0}
};
 
/* Direct Python call wrappers to density mechanism functions.*/
 
static NPyDirectMechFunc npy_direct_func_proc[] = {
 {0, 0}
};
 /* declare global and static user variables */
 #define gind 0
 #define _gth 0
#define car car_capmpr
 double car = 5e-05;
#define k4 k4_capmpr
 double k4 = 5;
#define k3 k3_capmpr
 double k3 = 500;
#define k2 k2_capmpr
 double k2 = 250000;
#define k1 k1_capmpr
 double k1 = 5e+08;
#define pumpdens pumpdens_capmpr
 double pumpdens = 3e-14;
#define tau tau_capmpr
 double tau = 1e+09;
 /* some parameters have upper and lower limits */
 static HocParmLimits _hoc_parm_limits[] = {
 {0, 0, 0}
};
 static HocParmUnits _hoc_parm_units[] = {
 {"car_capmpr", "mM"},
 {"tau_capmpr", "ms"},
 {"k1_capmpr", "/mM-s"},
 {"k2_capmpr", "/s"},
 {"k3_capmpr", "/s"},
 {"k4_capmpr", "/mM-s"},
 {"pumpdens_capmpr", "mol/cm2"},
 {"pump_capmpr", "mol/cm2"},
 {"pumpca_capmpr", "mol/cm2"},
 {0, 0}
};
 static double cai0 = 0;
 static double delta_t = 0.01;
 static double pumpca0 = 0;
 static double pump0 = 0;
 /* connect global user variables to hoc */
 static DoubScal hoc_scdoub[] = {
 {"car_capmpr", &car_capmpr},
 {"tau_capmpr", &tau_capmpr},
 {"k1_capmpr", &k1_capmpr},
 {"k2_capmpr", &k2_capmpr},
 {"k3_capmpr", &k3_capmpr},
 {"k4_capmpr", &k4_capmpr},
 {"pumpdens_capmpr", &pumpdens_capmpr},
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
 
#define _cvode_ieq _ppvar[7].literal_value<int>()
 static void _ode_matsol_instance1(_internalthreadargsproto_);
 /* connect range variables in _p that hoc is supposed to know about */
 static const char *_mechanism[] = {
 "7.7.0",
"capmpr",
 0,
 0,
 "pump_capmpr",
 "pumpca_capmpr",
 0,
 0};
 static Symbol* _morphology_sym;
 static Symbol* _ca_sym;
 
 /* Used by NrnProperty */
 static _nrn_mechanism_std_vector<double> _parm_default{
 }; 
 
 
extern Prop* need_memb(Symbol*);
static void nrn_alloc(Prop* _prop) {
  Prop *prop_ion{};
  Datum *_ppvar{};
   _ppvar = nrn_prop_datum_alloc(_mechtype, 8, _prop);
    _nrn_mechanism_access_dparam(_prop) = _ppvar;
     _nrn_mechanism_cache_instance _ml_real{_prop};
    auto* const _ml = &_ml_real;
    size_t const _iml{};
    assert(_nrn_mechanism_get_num_vars(_prop) == 18);
 	/*initialize range parameters*/
 	 assert(_nrn_mechanism_get_num_vars(_prop) == 18);
 	_nrn_mechanism_access_dparam(_prop) = _ppvar;
 	/*connect ionic variables to this model*/
 prop_ion = need_memb(_morphology_sym);
 	_ppvar[6] = _nrn_mechanism_get_param_handle(prop_ion, 0); /* diam */
 prop_ion = need_memb(_ca_sym);
 nrn_check_conc_write(_prop, prop_ion, 1);
 nrn_promote(prop_ion, 3, 0);
 	_ppvar[0] = _nrn_mechanism_get_param_handle(prop_ion, 2); /* cao */
 	_ppvar[1] = _nrn_mechanism_get_param_handle(prop_ion, 1); /* cai */
 	_ppvar[2] = _nrn_mechanism_get_param_handle(prop_ion, 3); /* ica */
 	_ppvar[3] = _nrn_mechanism_get_param_handle(prop_ion, 4); /* _ion_dicadv */
 	_ppvar[4] = _nrn_mechanism_get_param_handle(prop_ion, 0); // erev ca
 	_ppvar[5] = {neuron::container::do_not_search, &(_nrn_mechanism_access_dparam(prop_ion)[0].literal_value<int>())}; /* iontype for ca */
 
}
 static void _initlists();
  /* some states have an absolute tolerance */
 static Symbol** _atollist;
 static HocStateTolerance _hoc_state_tol[] = {
 {0, 0}
};
 static void _thread_cleanup(Datum*);
 extern Symbol* hoc_lookup(const char*);
extern void _nrn_thread_reg(int, int, void(*)(Datum*));
void _nrn_thread_table_reg(int, nrn_thread_table_check_t);
extern void hoc_register_tolerance(int, HocStateTolerance*, Symbol***);
extern void _cvode_abstol( Symbol**, double*, int);

 extern "C" void _capmpr_reg() {
	int _vectorized = 1;
  _initlists();
 	ion_reg("ca", -10000.);
 	_morphology_sym = hoc_lookup("morphology");
 	_ca_sym = hoc_lookup("ca_ion");
 	register_mech(_mechanism, nrn_alloc,nrn_cur, nrn_jacob, nrn_state, nrn_init, hoc_nrnpointerindex, 3);
  _extcall_thread.resize(2);
 _mechtype = nrn_get_mechtype(_mechanism[1]);
 hoc_register_parm_default(_mechtype, &_parm_default);
         hoc_register_npy_direct(_mechtype, npy_direct_func_proc);
     _nrn_setdata_reg(_mechtype, _setdata);
     _nrn_thread_reg(_mechtype, 0, _thread_cleanup);
 #if NMODL_TEXT
  register_nmodl_text_and_filename(_mechtype);
#endif
   _nrn_mechanism_register_data_fields(_mechtype,
                                       _nrn_mechanism_field<double>{"pump"} /* 0 */,
                                       _nrn_mechanism_field<double>{"pumpca"} /* 1 */,
                                       _nrn_mechanism_field<double>{"Dpump"} /* 2 */,
                                       _nrn_mechanism_field<double>{"Dpumpca"} /* 3 */,
                                       _nrn_mechanism_field<double>{"cai"} /* 4 */,
                                       _nrn_mechanism_field<double>{"Dcai"} /* 5 */,
                                       _nrn_mechanism_field<double>{"cao"} /* 6 */,
                                       _nrn_mechanism_field<double>{"ica"} /* 7 */,
                                       _nrn_mechanism_field<double>{"ipump"} /* 8 */,
                                       _nrn_mechanism_field<double>{"ipump_last"} /* 9 */,
                                       _nrn_mechanism_field<double>{"voli"} /* 10 */,
                                       _nrn_mechanism_field<double>{"area1"} /* 11 */,
                                       _nrn_mechanism_field<double>{"c1"} /* 12 */,
                                       _nrn_mechanism_field<double>{"c2"} /* 13 */,
                                       _nrn_mechanism_field<double>{"c3"} /* 14 */,
                                       _nrn_mechanism_field<double>{"c4"} /* 15 */,
                                       _nrn_mechanism_field<double>{"v"} /* 16 */,
                                       _nrn_mechanism_field<double>{"_g"} /* 17 */,
                                       _nrn_mechanism_field<double*>{"_ion_cao", "ca_ion"} /* 0 */,
                                       _nrn_mechanism_field<double*>{"_ion_cai", "ca_ion"} /* 1 */,
                                       _nrn_mechanism_field<double*>{"_ion_ica", "ca_ion"} /* 2 */,
                                       _nrn_mechanism_field<double*>{"_ion_dicadv", "ca_ion"} /* 3 */,
                                       _nrn_mechanism_field<double*>{"_ion_ca_erev", "ca_ion"} /* 4 */,
                                       _nrn_mechanism_field<int*>{"_style_ca", "#ca_ion"} /* 5 */,
                                       _nrn_mechanism_field<double*>{"diam", "diam"} /* 6 */,
                                       _nrn_mechanism_field<int>{"_cvode_ieq", "cvodeieq"} /* 7 */);
  hoc_register_prop_size(_mechtype, 18, 8);
  hoc_register_dparam_semantics(_mechtype, 0, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 1, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 2, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 3, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 4, "ca_ion");
  hoc_register_dparam_semantics(_mechtype, 5, "#ca_ion");
  hoc_register_dparam_semantics(_mechtype, 7, "cvodeieq");
  hoc_register_dparam_semantics(_mechtype, 6, "diam");
 	nrn_writes_conc(_mechtype, 0);
 	hoc_register_cvode(_mechtype, _ode_count, _ode_map, _ode_spec, _ode_matsol);
 	hoc_register_tolerance(_mechtype, _hoc_state_tol, &_atollist);
 
    hoc_register_var(hoc_scdoub, hoc_vdoub, hoc_intfunc);
 	ivoc_help("help ?1 capmpr /Users/runner/work/nrn/nrn/build_wheel/share/nrn/demo/release/capmpr.mod\n");
 hoc_register_limits(_mechtype, _hoc_parm_limits);
 hoc_register_units(_mechtype, _hoc_parm_units);
 }
 static double PI = 0x1.921fb54442d18p+1;
 static double FARADAY = 0x1.78e555060882cp+16;
 static double volo = 1;
static int _reset;
static const char *modelname = "";

static int error;
static int _ninits = 0;
static int _match_recurse=1;
static void _modl_cleanup(){ _match_recurse=1;}
 
#define _MATELM1(_row,_col) *(_nrn_thread_getelm(static_cast<SparseObj*>(_so), _row + 1, _col + 1))
 
#define _RHS1(_arg) _rhs[_arg+1]
  
#define _linmat1  0
 static int _spth1 = 1;
 static int _cvspth1 = 0;
 
static int _ode_spec1(_internalthreadargsproto_);
/*static int _ode_matsol1(_internalthreadargsproto_);*/
 static neuron::container::field_index _slist1[3], _dlist1[3]; static double *_temp1;
 static int pmp (void* _so, double* _rhs, _internalthreadargsproto_);
 
static int pmp (void* _so, double* _rhs, _internalthreadargsproto_)
 {int _reset=0;
 {
   double b_flux, f_flux, _term; int _i;
 {int _i; double _dt1 = 1.0/dt;
for(_i=1;_i<3;_i++){
  	_RHS1(_i) = -_dt1*(_ml->data(_iml, _slist1[_i]) - _ml->data(_iml, _dlist1[_i]));
	_MATELM1(_i, _i) = _dt1;
      
}  
_RHS1(1) *= ( voli) ;
_MATELM1(1, 1) *= ( voli); 
_RHS1(2) *= ( ( 1e10 ) * area1) ;
_MATELM1(2, 2) *= ( ( 1e10 ) * area1);  }
 /* COMPARTMENT voli {
     cai }
   */
 /* COMPARTMENT ( 1e10 ) * area1 {
     pump pumpca }
   */
 /* COMPARTMENT volo * ( 1e15 ) {
     }
   */
 /* ~ car <-> cai ( 1.0 / tau , 1.0 / tau )*/
 f_flux =  1.0 / tau * car ;
 b_flux =  1.0 / tau * cai ;
 _RHS1( 1) += (f_flux - b_flux);
 
 _term =  1.0 / tau ;
 _MATELM1( 1 ,1)  += _term;
 /*REACTION*/
  /* ~ cai + pump <-> pumpca ( c1 , c2 )*/
 f_flux =  c1 * pump * cai ;
 b_flux =  c2 * pumpca ;
 _RHS1( 2) -= (f_flux - b_flux);
 _RHS1( 1) -= (f_flux - b_flux);
 
 _term =  c1 * cai ;
 _MATELM1( 2 ,2)  += _term;
 _MATELM1( 1 ,2)  += _term;
 _term =  c1 * pump ;
 _MATELM1( 2 ,1)  += _term;
 _MATELM1( 1 ,1)  += _term;
 _term =  c2 ;
 _MATELM1( 2 ,0)  -= _term;
 _MATELM1( 1 ,0)  -= _term;
 /*REACTION*/
  /* ~ pumpca <-> pump + cao ( c3 , c4 )*/
 f_flux =  c3 * pumpca ;
 b_flux =  c4 * cao * pump ;
 _RHS1( 2) += (f_flux - b_flux);
 
 _term =  c3 ;
 _MATELM1( 2 ,0)  -= _term;
 _term =  c4 * cao ;
 _MATELM1( 2 ,2)  += _term;
 /*REACTION*/
  ipump = ( 1e-4 ) * 2.0 * FARADAY * ( f_flux - b_flux ) / area1 ;
   /* ~ cai < < ( - ( ica - ipump_last ) * area1 / ( 2.0 * FARADAY ) * ( 1e4 ) )*/
 f_flux = b_flux = 0.;
 _RHS1( 1) += (b_flux =   ( - ( ica - ipump_last ) * area1 / ( 2.0 * FARADAY ) * ( 1e4 ) ) );
 /*FLUX*/
   /* pump + pumpca = ( 1e10 ) * area1 * pumpdens */
 _RHS1(0) =  ( 1e10 ) * area1 * pumpdens;
 _MATELM1(0, 0) = 1 * ( ( 1e10 ) * area1);
 _RHS1(0) -= pumpca * ( ( 1e10 ) * area1) ;
 _MATELM1(0, 2) = 1 * ( ( 1e10 ) * area1);
 _RHS1(0) -= pump * ( ( 1e10 ) * area1) ;
 /*CONSERVATION*/
   } return _reset;
 }
 
/*CVODE ode begin*/
 static int _ode_spec1(_internalthreadargsproto_) {
  int _reset=0;
  {
 double b_flux, f_flux, _term; int _i;
 {int _i; for(_i=0;_i<3;_i++) _ml->data(_iml, _dlist1[_i]) = 0.0;}
 /* COMPARTMENT voli {
   cai }
 */
 /* COMPARTMENT ( 1e10 ) * area1 {
   pump pumpca }
 */
 /* COMPARTMENT volo * ( 1e15 ) {
   }
 */
 /* ~ car <-> cai ( 1.0 / tau , 1.0 / tau )*/
 f_flux =  1.0 / tau * car ;
 b_flux =  1.0 / tau * cai ;
 Dcai += (f_flux - b_flux);
 
 /*REACTION*/
  /* ~ cai + pump <-> pumpca ( c1 , c2 )*/
 f_flux =  c1 * pump * cai ;
 b_flux =  c2 * pumpca ;
 Dpump -= (f_flux - b_flux);
 Dcai -= (f_flux - b_flux);
 Dpumpca += (f_flux - b_flux);
 
 /*REACTION*/
  /* ~ pumpca <-> pump + cao ( c3 , c4 )*/
 f_flux =  c3 * pumpca ;
 b_flux =  c4 * cao * pump ;
 Dpumpca -= (f_flux - b_flux);
 Dpump += (f_flux - b_flux);
 
 /*REACTION*/
  ipump = ( 1e-4 ) * 2.0 * FARADAY * ( f_flux - b_flux ) / area1 ;
 /* ~ cai < < ( - ( ica - ipump_last ) * area1 / ( 2.0 * FARADAY ) * ( 1e4 ) )*/
 f_flux = b_flux = 0.;
 Dcai += (b_flux =   ( - ( ica - ipump_last ) * area1 / ( 2.0 * FARADAY ) * ( 1e4 ) ) );
 /*FLUX*/
   /* pump + pumpca = ( 1e10 ) * area1 * pumpdens */
 /*CONSERVATION*/
 _ml->data(_iml, _dlist1[0]) /= ( ( 1e10 ) * area1);
 _ml->data(_iml, _dlist1[1]) /= ( voli);
 _ml->data(_iml, _dlist1[2]) /= ( ( 1e10 ) * area1);
   } return _reset;
 }
 
/*CVODE matsol*/
 static int _ode_matsol1(void* _so, double* _rhs, _internalthreadargsproto_) {int _reset=0;{
 double b_flux, f_flux, _term; int _i;
   b_flux = f_flux = 0.;
 {int _i; double _dt1 = 1.0/dt;
for(_i=0;_i<3;_i++){
  	_RHS1(_i) = _dt1*(_ml->data(_iml, _dlist1[_i]));
	_MATELM1(_i, _i) = _dt1;
      
}  
_RHS1(0) *= ( ( 1e10 ) * area1) ;
_MATELM1(0, 0) *= ( ( 1e10 ) * area1); 
_RHS1(1) *= ( voli) ;
_MATELM1(1, 1) *= ( voli); 
_RHS1(2) *= ( ( 1e10 ) * area1) ;
_MATELM1(2, 2) *= ( ( 1e10 ) * area1);  }
 /* COMPARTMENT voli {
 cai }
 */
 /* COMPARTMENT ( 1e10 ) * area1 {
 pump pumpca }
 */
 /* COMPARTMENT volo * ( 1e15 ) {
 }
 */
 /* ~ car <-> cai ( 1.0 / tau , 1.0 / tau )*/
 _term =  1.0 / tau ;
 _MATELM1( 1 ,1)  += _term;
 /*REACTION*/
  /* ~ cai + pump <-> pumpca ( c1 , c2 )*/
 _term =  c1 * cai ;
 _MATELM1( 2 ,2)  += _term;
 _MATELM1( 1 ,2)  += _term;
 _MATELM1( 0 ,2)  -= _term;
 _term =  c1 * pump ;
 _MATELM1( 2 ,1)  += _term;
 _MATELM1( 1 ,1)  += _term;
 _MATELM1( 0 ,1)  -= _term;
 _term =  c2 ;
 _MATELM1( 2 ,0)  -= _term;
 _MATELM1( 1 ,0)  -= _term;
 _MATELM1( 0 ,0)  += _term;
 /*REACTION*/
  /* ~ pumpca <-> pump + cao ( c3 , c4 )*/
 _term =  c3 ;
 _MATELM1( 0 ,0)  += _term;
 _MATELM1( 2 ,0)  -= _term;
 _term =  c4 * cao ;
 _MATELM1( 0 ,2)  -= _term;
 _MATELM1( 2 ,2)  += _term;
 /* ~ cai < < ( - ( ica - ipump_last ) * area1 / ( 2.0 * FARADAY ) * ( 1e4 ) )*/
 /*FLUX*/
   /* pump + pumpca = ( 1e10 ) * area1 * pumpdens */
 /*CONSERVATION*/
   } return _reset;
 }
 
/*CVODE end*/
 
static int _ode_count(int _type){ return 3;}
 
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
  cai = _ion_cai;
     _ode_spec1 (_threadargs_);
  _ion_cai = cai;
  }}
 
static void _ode_map(Prop* _prop, int _ieq, neuron::container::data_handle<double>* _pv, neuron::container::data_handle<double>* _pvdot, double* _atol, int _type) { 
  Datum* _ppvar;
  _ppvar = _nrn_mechanism_access_dparam(_prop);
  _cvode_ieq = _ieq;
  for (int _i=0; _i < 3; ++_i) {
    _pv[_i] = _nrn_mechanism_get_param_handle(_prop, _slist1[_i]);
    _pvdot[_i] = _nrn_mechanism_get_param_handle(_prop, _dlist1[_i]);
    _cvode_abstol(_atollist, _atol, _i);
  }
 	_pv[1] = _p_ion_cai;
 }
 
static void _ode_matsol_instance1(_internalthreadargsproto_) {
 _cvode_sparse_thread(&(_thread[_cvspth1].literal_value<void*>()), 3, _dlist1, neuron::scopmath::row_view{_ml, _iml}, _ode_matsol1, _threadargs_);
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
  cai = _ion_cai;
 _ode_matsol_instance1(_threadargs_);
 }}
 
static void _thread_cleanup(Datum* _thread) {
   _nrn_destroy_sparseobj_thread(static_cast<SparseObj*>(_thread[_cvspth1].get<void*>()));
   _nrn_destroy_sparseobj_thread(static_cast<SparseObj*>(_thread[_spth1].get<void*>()));
 }

static void initmodel(_internalthreadargsproto_) {
  int _i; double _save;{
  pumpca = pumpca0;
  pump = pump0;
 {
   voli = PI * pow( ( diam / 2.0 ) , 2.0 ) * 1.0 ;
   area1 = 2.0 * PI * ( diam / 2.0 ) * 1.0 ;
   c1 = ( 1e7 ) * area1 * k1 ;
   c2 = ( 1e7 ) * area1 * k2 ;
   c3 = ( 1e7 ) * area1 * k3 ;
   c4 = ( 1e7 ) * area1 * k4 ;
    _ss_sparse_thread(&(_thread[_spth1].literal_value<void*>()), 3, _slist1, _dlist1, neuron::scopmath::row_view{_ml, _iml}, &t, dt, pmp, _linmat1, _threadargs_);
     if (secondorder) {
    int _i;
    for (_i = 0; _i < 3; ++_i) {
      _ml->data(_iml, _slist1[_i]) += dt*_ml->data(_iml, _dlist1[_i]);
    }}
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
   _v = _vec_v[_ni[_iml]];
 v = _v;
  cao = _ion_cao;
  cai = _ion_cai;
  cai = _ion_cai;
 initmodel(_threadargs_);
  _ion_cai = cai;
   nrn_wrote_conc(_ca_sym, _ion_ca_erev, _ion_cai, _ion_cao, _style_ca);
}
}

static double _nrn_current(_internalthreadargsprotocomma_ double _v) {
double _current=0.; v=_v;
{ {
   ipump_last = ipump ;
   ica = ipump ;
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
  cai = _ion_cai;
 auto const _g_local = _nrn_current(_threadargscomma_ _v + .001);
 	{ double _dica;
  _dica = ica;
 _rhs = _nrn_current(_threadargscomma_ _v);
  _ion_dicadv += (_dica - ica)/.001 ;
 	}
 _g = (_g_local - _rhs)/.001;
  _ion_cai = cai;
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
double _dtsav = dt;
if (secondorder) { dt *= 0.5; }
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
  cai = _ion_cai;
 {  sparse_thread(&(_thread[_spth1].literal_value<void*>()), 3, _slist1, _dlist1, neuron::scopmath::row_view{_ml, _iml}, &t, dt, pmp, _linmat1, _threadargs_);
     if (secondorder) {
    int _i;
    for (_i = 0; _i < 3; ++_i) {
      _ml->data(_iml, _slist1[_i]) += dt*_ml->data(_iml, _dlist1[_i]);
    }}
 }  _ion_cai = cai;
 }}
 dt = _dtsav;
}

static void terminal(){}

static void _initlists(){
 int _i; static int _first = 1;
  if (!_first) return;
 _slist1[0] = {pumpca_columnindex, 0};  _dlist1[0] = {Dpumpca_columnindex, 0};
 _slist1[1] = {cai_columnindex, 0};  _dlist1[1] = {Dcai_columnindex, 0};
 _slist1[2] = {pump_columnindex, 0};  _dlist1[2] = {Dpump_columnindex, 0};
_first = 0;
}

#if NMODL_TEXT
static void register_nmodl_text_and_filename(int mech_type) {
    const char* nmodl_filename = "/Users/runner/work/nrn/nrn/build_wheel/share/nrn/demo/release/capmpr.mod";
    const char* nmodl_file_text = 
  ":  capump.mod plus a \"reservoir\" used to initialize cai to desired concentrations\n"
  "\n"
  "UNITS {\n"
  "	(mM) = (milli/liter)\n"
  "	(mA) = (milliamp)\n"
  "	(um) = (micron)\n"
  "	(mol) = (1)\n"
  "	PI = (pi) (1)\n"
  "	FARADAY = (faraday) (coulomb)\n"
  "}\n"
  "\n"
  "NEURON {\n"
  "	SUFFIX capmpr\n"
  "	USEION ca READ cao, cai WRITE cai, ica\n"
  "	GLOBAL k1, k2, k3, k4\n"
  "	GLOBAL car, tau\n"
  "}\n"
  "\n"
  "STATE {\n"
  "	pump	(mol/cm2)\n"
  "	pumpca	(mol/cm2)\n"
  "	cai	(mM)\n"
  "}\n"
  "\n"
  "PARAMETER {\n"
  "	car = 5e-5 (mM) : ca in reservoir, used to initialize cai to desired concentrations\n"
  "	tau = 1e9 (ms) : rate of equilibration between cai and car\n"
  "\n"
  "	k1 = 5e8	(/mM-s)\n"
  "	k2 = .25e6	(/s)\n"
  "	k3 = .5e3	(/s)\n"
  "	k4 = 5e0	(/mM-s)\n"
  "\n"
  "	pumpdens = 3e-14 (mol/cm2)\n"
  "}\n"
  "\n"
  "CONSTANT {\n"
  "	volo = 1 (liter)\n"
  "}\n"
  "\n"
  "ASSIGNED {\n"
  "	diam	(um)\n"
  "	cao	(mM)\n"
  "\n"
  "	ica (mA/cm2)\n"
  "	ipump (mA/cm2)\n"
  "	ipump_last (mA/cm2)\n"
  "	voli	(um3)\n"
  "	area1	(um2)\n"
  "	c1	(1+8 um5/ms)\n"
  "	c2	(1-10 um2/ms)\n"
  "	c3	(1-10 um2/ms)\n"
  "	c4	(1+8 um5/ms)\n"
  "}\n"
  "\n"
  "BREAKPOINT {\n"
  "	SOLVE pmp METHOD sparse\n"
  "	ipump_last = ipump\n"
  "	ica = ipump\n"
  "}\n"
  "\n"
  "KINETIC pmp {\n"
  "	COMPARTMENT voli {cai}\n"
  "	COMPARTMENT (1e10)*area1 {pump pumpca}\n"
  "	COMPARTMENT volo*(1e15) {cao car}\n"
  "\n"
  "	~ car <-> cai		(1(um3)/tau,1(um3)/tau)\n"
  "	~ cai + pump <-> pumpca		(c1,c2)\n"
  "	~ pumpca     <-> pump + cao	(c3,c4)\n"
  "\n"
  "	: note that forward flux here is the outward flux\n"
  "	ipump = (1e-4)*2*FARADAY*(f_flux - b_flux)/area1\n"
  "\n"
  "        : ipump_last vs ipump needed because of STEADYSTATE calculation\n"
  "        ~ cai << (-(ica - ipump_last)*area1/(2*FARADAY)*(1e4))\n"
  "\n"
  "	CONSERVE pump + pumpca = (1e10)*area1*pumpdens\n"
  "}\n"
  "\n"
  "INITIAL {\n"
  "	:cylindrical coordinates; actually vol and area1/unit length\n"
  "	voli = PI*(diam/2)^2 * 1(um)\n"
  "	area1 = 2*PI*(diam/2) * 1(um)\n"
  "	c1 = (1e7)*area1 * k1\n"
  "	c2 = (1e7)*area1 * k2\n"
  "	c3 = (1e7)*area1 * k3\n"
  "	c4 = (1e7)*area1 * k4\n"
  "\n"
  "	SOLVE pmp STEADYSTATE sparse\n"
  "}\n"
  ;
    hoc_reg_nmodl_filename(mech_type, nmodl_filename);
    hoc_reg_nmodl_text(mech_type, nmodl_file_text);
}
#endif
