#include <fem.hpp> // Fortran EMulation library of fable module

namespace scitbx {
namespace lbfgs_fem {

using namespace fem::major_types;

struct common_lb3
{
  int mp;
  int lp;
  double gtol;
  double stpmin;
  double stpmax;

  common_lb3() :
    mp(fem::int0),
    lp(fem::int0),
    gtol(fem::double0),
    stpmin(fem::double0),
    stpmax(fem::double0)
  {}
};

struct common :
  fem::common,
  common_lb3
{
  fem::cmn_sve mcsrch_sve;
  fem::cmn_sve lbfgs_sve;
  fem::cmn_sve blockdata_lb2_sve;

  common(
    int argc,
    char const* argv[])
  :
    fem::common(argc, argv)
  {}
};

void
lbfgs(
  common& cmn,
  int const& n,
  int const& m,
  arr_ref<double> x,
  double const& f,
  arr_cref<double> g,
  int const& diagco,
  arr_ref<double> diag,
  arr_cref<int> iprint,
  double const& eps,
  double const& xtol,
  arr_ref<double> w,
  int& iflag);

void
blockdata_lb2(
  common& cmn);

}} // namespace scitbx::lbfgs_fem