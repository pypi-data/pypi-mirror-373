#pragma once

/* define to 1 if you want MPI specific features activated */
#define NRNMPI 1

/* define to 1 if you want mpi dynamically loaded instead of linked normally */
#define NRNMPI_DYNAMICLOAD 1

/* define to 1 if you want the MUSIC - MUlti SImulation Coordinator */
/* #undef NRN_MUSIC */

/* define to the dll path if you want to load automatically */
#define DLL_DEFAULT_FNAME "x86_64/libnrnmech.dylib"

/* define if needed */
/* #undef ALWAYS_CALL_MPI_INIT */
