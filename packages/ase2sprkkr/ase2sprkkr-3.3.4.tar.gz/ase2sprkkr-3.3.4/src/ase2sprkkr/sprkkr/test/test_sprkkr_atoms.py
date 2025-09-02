from ase import Atoms
from ase.build import bulk
import numpy as np

if __package__:
   from .init_tests import TestCase, patch_package
else:
   from init_tests import TestCase, patch_package
__package__, __name__ = patch_package(__package__, __name__)

from ..sprkkr_atoms import SPRKKRAtoms  # NOQA: E402


class TestSPRKKRAtoms(TestCase):

 def test_extend(self):
     a = SPRKKRAtoms('NaCl')
     a.set_positions([[0,0,0],[0,1,0]])

     b = SPRKKRAtoms('Na')
     b.set_positions([[1,0,0]])

     id1 = id(a.sites[0].site_type)
     id2 = id(b.sites[0].site_type)
     a.extend(b)
     # Test, that the sites property is retained
     self.assertEqual(id1, id(a.sites[0].site_type))
     self.assertNotEqual(id2, id(a.sites[2].site_type))
     assert id(b.sites[0]) != id(a.sites[2])

     a = Atoms('NaCl')
     a.set_positions([[0,0,0],[0,1,0]])
     a.extend(b)
     SPRKKRAtoms.promote_ase_atoms(a)
     self.assertNotEqual(id2, id(a.sites[2].site_type))

 def test_atoms(self):
     a = Atoms('NaCl')
     a.set_positions([[0,0,0],[0,1,0]])
     a.info['occupancy'] = { 0: {'Na' : 1.0}, 1: {'Cl' : 0.4, 'I' : 0.6 } }
     a.arrays['spacegroup_kinds'] = np.asarray([0,1])
     self.assertEqual(str(a.symbols), 'NaCl')
     SPRKKRAtoms.promote_ase_atoms(a)
     self.assertEqual(len(a.sites), 2)
     self.assertEqual(len(a.sites[0].occupation), 1)
     self.assertEqual(len(a.sites[1].occupation), 2)
     self.assertEqual(a.sites[1].occupation['Cl'], 0.4)
     self.assertEqual(str(a.symbols), 'NaI')
     self.assertEqual(a.sites[0].occupation.as_dict, {'Na' : 1})
     self.assertEqual(a.sites[1].occupation.as_dict, {'Cl' : 0.4, 'I': 0.6})
     self.assertEqual(a.info['occupancy']["1"], {'Cl' : 0.4, 'I': 0.6})
     a.sites[1].site_type = a.sites[0].site_type
     a.compute_sites_symmetry()
     a.sites[1].occupation = 'Cl'
     self.assertEqual(str(a.symbols), 'NaCl')

 def test_symmetry(self):
     atoms=bulk('LiCl', 'rocksalt', a=5.64) * (2, 1, 1)
     SPRKKRAtoms.promote_ase_atoms(atoms)
     self.assertTrue(atoms.sites[1].site_type == atoms.sites[3].site_type)
     assert atoms.sites[1] is not atoms.sites[3]
     atoms.symmetry = False
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)
     assert atoms.sites[1] is not atoms.sites[3]
     atoms.symmetry = True
     self.assertTrue(atoms.sites[1].site_type == atoms.sites[3].site_type)
     atoms.sites[3].site_type = atoms.sites[3].site_type.copy()
     assert atoms.sites[1] is not atoms.sites[3]
     # No effect
     atoms.symmetry = True
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)
     assert atoms.sites[1] is not atoms.sites[3]
     atoms.compute_sites_symmetry()
     self.assertTrue(atoms.sites[1].site_type == atoms.sites[3].site_type)
     assert atoms.sites[1] is not atoms.sites[3]
     atoms.symmetry = False
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)
     assert atoms.sites[1] is not atoms.sites[3]
     atoms.sites[3].site_type = atoms.sites[1].site_type
     # No effect
     atoms.symmetry = False
     self.assertTrue(atoms.sites[1].site_type == atoms.sites[3].site_type)
     assert atoms.sites[1] is not atoms.sites[3]
     atoms.breaks_sites_symmetry()
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)
     assert atoms.sites[1] is not atoms.sites[3]

     atoms=bulk('LiCl', 'rocksalt', a=5.64) * (2, 1, 1)
     SPRKKRAtoms.promote_ase_atoms(atoms, symmetry=False)
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)
     # default None for symmetry do not change the already
     # initialized atoms object
     SPRKKRAtoms.promote_ase_atoms(atoms)
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)
     SPRKKRAtoms.promote_ase_atoms(atoms, symmetry=True)
     self.assertTrue(atoms.sites[1].site_type == atoms.sites[3].site_type)

 def test_occupancy(self):
     atoms=bulk('LiCl', 'rocksalt', a=5.64) * (2, 1, 1)
     SPRKKRAtoms.promote_ase_atoms(atoms)
     self.assertTrue(atoms.sites[1].site_type == atoms.sites[3].site_type)
     atoms.breaks_sites_symmetry()
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)

     atoms=bulk('LiCl', 'rocksalt', a=5.64) * (2, 1, 1)
     atoms.info["occupancy"] = {
         0: { 'Li' : 1 },
         1: { 'Cl' : 1 },
         2: { 'Li' : 1 },
         3: { 'Cl' : 1 },
     }
     atoms.arrays['spacegroup_kinds'] = np.array([0,1,0,1])
     SPRKKRAtoms.promote_ase_atoms(atoms)
     self.assertTrue(atoms.sites[1].site_type == atoms.sites[3].site_type)

     atoms=bulk('LiCl', 'rocksalt', a=5.64) * (2, 1, 1)
     atoms.info["occupancy"] = {
         0: { 'Li' : 1 },
         1: { 'Cl' : 0.5, 'I' :0.5 },
         2: { 'Li' : 1 },
         3: { 'Cl' : 1 },
     }
     atoms.arrays['spacegroup_kinds'] = np.array([0,1,0,2])
     SPRKKRAtoms.promote_ase_atoms(atoms)
     self.assertFalse(atoms.sites[1].site_type == atoms.sites[3].site_type)
     self.assertEqual({ 'Cl' : 0.5, 'I' :0.5 }, atoms.sites[1].occupation.as_dict)
