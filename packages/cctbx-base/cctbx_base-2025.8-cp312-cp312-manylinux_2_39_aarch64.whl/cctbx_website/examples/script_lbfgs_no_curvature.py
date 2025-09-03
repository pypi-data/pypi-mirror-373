from __future__ import absolute_import, division, print_function
#********************************************************************
# This script is automatically generated when running libtbx.refresh (or bootstrap.py)
# It is not part of the GitHub repository
# So if this script is manually changed, the changes will be lost when updating
#********************************************************************
from __future__ import division, print_function
from scitbx.array_family import flex
from libtbx import adopt_init_args
import scitbx.lbfgs
from scitbx import lbfgsb

class rosenbrock(object):
  def __init__(self, a, b, x):
    adopt_init_args(self, locals())
    assert self.x.size() == 2

  def update(self, x):
    self.x = x
    assert self.x.size() == 2

  def target(self):
    return (self.a-self.x[0])**2+self.b*(self.x[1]-self.x[0]**2)**2

  def gradients(self):
    g1 = 2*(self.x[0]-self.a) + 4*self.b*(self.x[0]**3-self.x[0]*self.x[1])
    g2 = 2*self.b*(self.x[1]-self.x[0]**2)
    return flex.double([g1,g2])

def lbfgs_run(target_evaluator, use_bounds, lower_bound, upper_bound):
  minimizer = lbfgsb.minimizer(
    n   = target_evaluator.n,
    l   = lower_bound, # lower bound
    u   = upper_bound, # upper bound
    nbd = flex.int(target_evaluator.n, use_bounds)) # flag to apply both bounds
  minimizer.error = None
  try:
    icall = 0
    while 1:
      icall += 1
      x, f, g = target_evaluator()
      have_request = minimizer.process(x, f, g)
      if(have_request):
        requests_f_and_g = minimizer.requests_f_and_g()
        continue
      assert not minimizer.requests_f_and_g()
      if(minimizer.is_terminated()): break
  except RuntimeError as e:
    minimizer.error = str(e)
  minimizer.n_calls = icall
  return minimizer

class minimizer_bound(object):

  def __init__(self,
               calculator,
               use_bounds,
               lower_bound,
               upper_bound,
               initial_values):
    adopt_init_args(self, locals())
    self.x = initial_values
    self.n = self.x.size()

  def run(self):
    self.minimizer = lbfgs_run(
      target_evaluator=self,
      use_bounds=self.use_bounds,
      lower_bound = self.lower_bound,
      upper_bound = self.upper_bound)
    self()
    return self

  def __call__(self):
    self.calculator.update(x = self.x)
    self.f = self.calculator.target()
    self.g = self.calculator.gradients()
    return self.x, self.f, self.g

class minimizer_unbound(object):
  #
  def __init__(self, max_iterations, calculator):
    adopt_init_args(self, locals())
    self.x = self.calculator.x
    self.minimizer = scitbx.lbfgs.run(
      target_evaluator=self,
      termination_params=scitbx.lbfgs.termination_parameters(
        max_iterations=max_iterations))

  def compute_functional_and_gradients(self):
    self.calculator.update(x = self.x)
    t = self.calculator.target()
    g = self.calculator.gradients()
    return t,g

def run():
  # Instantiate rosenbrock class
  calculator = rosenbrock(a = 20, b = 10, x = flex.double([0,0]))
  #
  print('Run L-BFGS (no boundaries)')
  m_unbound = minimizer_unbound(max_iterations=100, calculator=calculator)
  print('\tMinimum: ', list(m_unbound.x))
  print()
  print('Run L-BFGS-B with boundaries')
  m_bound = minimizer_bound(
    calculator     = calculator,
    use_bounds     = 2,
    lower_bound    = flex.double([-10000,-10000]),
    upper_bound    = flex.double([10000,10000]),
    initial_values = flex.double([0,0])).run()
  print('\tMinimum: ', list(m_bound.x))

if (__name__ == "__main__"):
  run()
