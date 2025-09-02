import os
from ..readers.scf import ScfOutputReader, ScfResult, atomic_types_definition

if __package__:
   from .init_tests import TestCase, patch_package
else:
   from init_tests import TestCase, patch_package
__package__, __name__ = patch_package(__package__, __name__)


class TestOutput(TestCase):

  def test_scf(self):
      atomic_types_definition.parse(
"""  33 E= 0.6083 0.0000          IT=   1  Li_1
         DOS      NOS     P_spin   m_spin    P_orb    m_orb    B_val      B_core
  s    0.4387   0.0296    0.0000   0.0000   0.00000  0.00000    0.00 s      0.00
  p    1.2579   0.0962    0.0000   0.0000   0.00000  0.00000    0.00 ns     0.00
  d    0.6886   0.0926    0.0000   0.0000   0.00000  0.00000    0.00 cor    0.00
  f    0.3427   0.0476    0.0000   0.0000   0.00000  0.00000    0.00
 sum   2.7279   0.2660    0.0000   0.0000   0.00000  0.00000    0.00 v+c    0.00
 E_band         0.11559127 [Ry]
dipole moment   1      0.0000000000000000      0.0000000000000000      0.0000000000000000""")  # NOQA: E122

  def test_output(self):
      path = os.path.join(
              os.path.dirname(__file__),
              '..', 'examples', 'scf.out'
      )

      # read_from_file is both method and class_method
      for reader in ScfOutputReader, ScfOutputReader():

          out = ScfResult(None, None, None)
          reader.read_from_file(path, read_args = [out])

          self.assertEqual(out.iterations[-1]['energy']['EMIN'](), -0.5)
          self.assertEqual(len(out.iterations[-1]['atomic_types']), 2)
          self.assertEqual(out.iterations[0].converged(), False)
          self.assertEqual(out.iterations[-1].converged(), True)
