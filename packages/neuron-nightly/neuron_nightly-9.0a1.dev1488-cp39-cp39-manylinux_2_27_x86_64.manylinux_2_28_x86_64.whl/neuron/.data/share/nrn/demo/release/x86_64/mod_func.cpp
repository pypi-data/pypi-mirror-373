#include <stdio.h>
#include "hocdec.h"
extern int nrnmpi_myid;
extern int nrn_nobanner_;

extern "C" void _cabpump_reg(void);
extern "C" void _cachan1_reg(void);
extern "C" void _camchan_reg(void);
extern "C" void _capmpr_reg(void);
extern "C" void _capump_reg(void);
extern "C" void _invlfire_reg(void);
extern "C" void _khhchan_reg(void);
extern "C" void _nacaex_reg(void);
extern "C" void _nachan_reg(void);
extern "C" void _release_reg(void);

extern "C" void modl_reg() {
  if (!nrn_nobanner_) if (nrnmpi_myid < 1) {
    fprintf(stderr, "Additional mechanisms from files\n");
    fprintf(stderr, " \"cabpump.mod\"");
    fprintf(stderr, " \"cachan1.mod\"");
    fprintf(stderr, " \"camchan.mod\"");
    fprintf(stderr, " \"capmpr.mod\"");
    fprintf(stderr, " \"capump.mod\"");
    fprintf(stderr, " \"invlfire.mod\"");
    fprintf(stderr, " \"khhchan.mod\"");
    fprintf(stderr, " \"nacaex.mod\"");
    fprintf(stderr, " \"nachan.mod\"");
    fprintf(stderr, " \"release.mod\"");
    fprintf(stderr, "\n");
  }
  _cabpump_reg();
  _cachan1_reg();
  _camchan_reg();
  _capmpr_reg();
  _capump_reg();
  _invlfire_reg();
  _khhchan_reg();
  _nacaex_reg();
  _nachan_reg();
  _release_reg();
}
