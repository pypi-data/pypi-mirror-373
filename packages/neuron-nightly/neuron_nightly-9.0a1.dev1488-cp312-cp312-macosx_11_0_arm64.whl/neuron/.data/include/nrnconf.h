#pragma once

/* Define to one if want to debug using sha1 hashes of data */
#define NRN_ENABLE_DIGEST 0

/* Define to one if want to allow selection of architecture independent */
/* 53 bit double precision of exp and pow from mpfr */
#define NRN_ENABLE_ARCH_INDEP_EXP_POW 0

/* Define if building universal (internal helper macro) */
/* #undef AC_APPLE_UNIVERSAL_BUILD */

/* if mac os x */
#define DARWIN 1

/* Define to 1 if you have the <dlfcn.h> header file. */
#define HAVE_DLFCN_H 1

/* Define to 1 if you have the <execinfo.h> header file. */
#define HAVE_EXECINFO_H 1

/* Define to 1 if you have the `index' function. */
/* #undef HAVE_INDEX */

/* Define to 1 if you have the `isatty' function. */
#define HAVE_ISATTY 1

/* define if using InterViews */
#define HAVE_IV 1

/* Define to 1 if you have the `mallinfo' function. */
/* #undef HAVE_MALLINFO */

/* Define to 1 if you have the `mallinfo2' function. */
/* #undef HAVE_MALLINFO2 */

/* Define to 1 if you have the <malloc.h> header file. */
/* #undef HAVE_MALLOC_H */

/* Define to 1 if you have the `mkstemp' function. */
#define HAVE_MKSTEMP 1

/* Define to 1 if you have the `posix_memalign' function. */
#define HAVE_POSIX_MEMALIGN 1

/* Define to 1 if you have the `setenv' function. */
#define HAVE_SETENV 1

/* Define to 1 if you have the `setitimer' function. */
#define HAVE_SETITIMER 1

/* Define to 1 if you have the `sigaction' function. */
#define HAVE_SIGACTION 1

/* Define to 1 if you have the `sigprocmask' function. */
#define HAVE_SIGPROCMASK 1

/* (Define if this signal exists) */
#define HAVE_SIGBUS 1

/* Define to 1 if you have the <sys/types.h> header file. */
#define HAVE_SYS_TYPES_H 1

/* Define to 1 if you have the <unistd.h> header file. */
#define HAVE_UNISTD_H 1

/* define if using mingw */
/* #undef MINGW */

/* where the lib hoc is */
#define NEURON_DATA_DIR "/var/folders/y6/nj790rtn62lfktb1sh__79hc0000gn/T/tmp2ckogx27/wheel/platlib/share/nrn"

/* host triplet */
#define NRNHOST "arm64-Darwin"

/* if 1 then dlopen nrnmech instead of special */
#define NRNMECH_DLL_STYLE 1

/* if nrnoc can use X11 */
#define NRNOC_X11 1

/* location of NEURON libraries */
#define NRN_LIBDIR "/var/folders/y6/nj790rtn62lfktb1sh__79hc0000gn/T/tmp2ckogx27/wheel/platlib/lib"

/* Name of package */
#define PACKAGE "nrn"

/* Define to the version of this package. */
#define PACKAGE_VERSION "9.0.0a0.post1488"

/* Define SUNDIALS data type 'realtype' as 'long double' */
#define SUNDIALS_DOUBLE_PRECISION 1

/* Use generic math functions */
#define SUNDIALS_USE_GENERIC_MATH 1

/* Version number of package */
#define VERSION "9.0.0a0.post1488"

/* Define WORDS_BIGENDIAN to 1 if your processor stores words with the most
   significant byte first (like Motorola and SPARC, unlike Intel). */
#if defined AC_APPLE_UNIVERSAL_BUILD
# if defined __BIG_ENDIAN__
#  define WORDS_BIGENDIAN 1
# endif
#else
# ifndef WORDS_BIGENDIAN
/* #undef WORDS_BIGENDIAN */
# endif
#endif

/* Define to 1 if `lex' declares `yytext' as a `char *' by default, not a
   `char[]'. */
#define YYTEXT_POINTER 1

/* Define to `int' if <sys/types.h> does not define. */
/* #undef pid_t */

/* __cplusplus guard still needed because this header is included from C code in
 * mesch (and maybe others)
 */
#if defined(__cplusplus)
#include <array>
#include <string_view>
namespace neuron::config {
#ifdef USE_PYTHON
   constexpr std::string_view default_python_executable{R"(/private/var/folders/y6/nj790rtn62lfktb1sh__79hc0000gn/T/build-env-e3k1nual/bin/python)"};
   constexpr std::array<std::string_view, 1> supported_python_versions{"3.12"};
#endif
   constexpr std::string_view shared_library_prefix{"lib"};
   constexpr std::string_view shared_library_suffix{".dylib"};
   constexpr std::string_view system_processor{"arm64"};
}
#endif

#ifdef MINGW
#define WIN32 1
#endif
