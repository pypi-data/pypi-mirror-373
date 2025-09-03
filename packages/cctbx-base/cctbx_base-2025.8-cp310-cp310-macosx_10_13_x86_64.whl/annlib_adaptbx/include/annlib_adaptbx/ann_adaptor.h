#ifndef ANNLIB_ANN_AD_H
#define ANNLIB_ANN_AD_H
#include <boost/shared_ptr.hpp>
#include <scitbx/array_family/flex_types.h>
#include <scitbx/array_family/shared.h>
#include <ANN/ANN.h>
#include <ANNSELF_INCLUDE/ANN.h>

namespace af = scitbx::af;

namespace annlib_adaptbx {

class AnnAdaptor {
  typedef boost::shared_ptr<ANNkd_tree> annptr;
 protected:
  annptr kdTree;
  int dimension;
  int k;//number of near neighbors
  double eps;//error bound
  af::shared<ANNcoord> persist_data;
  af::shared<ANNcoord*> persist_ptr;
  void constructor_core(af::shared<ANNcoord>,int);

 public:
  af::flex_int nn;//nearest neighbors
  af::flex_double distances;//nearest distances

 public:
  inline AnnAdaptor(){}
  AnnAdaptor(af::shared<ANNcoord>,int);//coordinates & space dimension
  AnnAdaptor(af::shared<ANNcoord>,int,int);//coordinates, space dimension
                                           //and number of neighbors requested
  ~AnnAdaptor();
  void query(af::shared<ANNcoord>);//query coordinates
};

class AnnAdaptorSelfInclude {
  typedef boost::shared_ptr<annself_include::ANNkd_tree> annptr;
 protected:
  annptr kdTree;
  int dimension;
  int k;//number of near neighbors
  double eps;//error bound
  af::shared<annself_include::ANNcoord> persist_data;
  af::shared<annself_include::ANNcoord*> persist_ptr;
  void constructor_core(af::shared<annself_include::ANNcoord>,int);

 public:
  af::flex_int nn;//nearest neighbors
  af::flex_double distances;//nearest distances

 public:
  inline AnnAdaptorSelfInclude(){}
  AnnAdaptorSelfInclude(af::shared<annself_include::ANNcoord>,int);//coordinates & space dimension
  AnnAdaptorSelfInclude(af::shared<annself_include::ANNcoord>,int,int);//coordinates, space dimension
                                           //and number of neighbors requested
  ~AnnAdaptorSelfInclude();
  void query(af::shared<annself_include::ANNcoord>);//query coordinates
};

}

#endif// ANNLIB_ANN_AD_H
