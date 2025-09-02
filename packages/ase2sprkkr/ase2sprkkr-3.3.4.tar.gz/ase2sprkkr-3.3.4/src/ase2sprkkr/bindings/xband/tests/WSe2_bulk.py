from ase.build import bulk
import ase2sprkkr
import ase
from ase.visualize import view
from ase2sprkkr.sprkkr.calculator import SPRKKR
from ase.spacegroup import crystal
from ase2sprkkr.sprkkr.sprkkr_atoms import SPRKKRAtoms
from ase import Atoms

def xtest():
  print("ASE version", ase.__version__)
  print("ase2sprkkr version", ase2sprkkr.__version__)

  a = 3.282
  c = 12.96

  wse2 = crystal('WSe',  [[1/3,2/3,1/4],  [1/3,2/3,0.6211]], cellpar=[a,a,c,90.,90.,120.], spacegroup=194, pbc=True)
  from ase2sprkkr.bindings.xband import symmetry as sym
  print(wse2.positions)

  wse2_bulk = SPRKKRAtoms.promote_ase_atoms(wse2)

  # Empty sphere algorithm complains if symmetry is on
  # wse2_bulk.symmetry = False

  # Options for input file:
  opts = {
      'CONTROL.KRMT':4,
      'CONTROL.KRWS':1,
      'SITES.NL':4,
      'MODE.LLOYD':True,
      'TAU.BZINT':'POINTS',
      'TAU.NKTAB':1000,
      'SCF.VXC':'VWN',
      'SCF.NITER':200,
      'SCF.MIX':0.1,
      'SCF.TOL':1E-5,
      'SCF.ISTBRY':1,
  }


  calculator=SPRKKR(atoms=wse2_bulk,options=opts)

  calculator.save_input(input_file='WSe2.inp', directory=False, potential_file='WSe2.pot',empty_spheres={'min_radius':0.9, 'max_radius':3.5, 'mesh': 64, 'verbose':True})

  es = wse2_bulk[6:]
  es.wrap()
  wse2_bulk.positions[6:] = es.positions
  view(wse2_bulk)
  breakpoint()

if __name__ == '__main__':
    xtest()
