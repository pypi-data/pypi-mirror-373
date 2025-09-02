from ...potential_definitions import PotSectionDefinition, \
                                   PotValueDefinition
from ...potential_sections import PotentialSection

from ....common.grammar_types import Array, Table
from ....sprkkr.sprkkr_atoms import SPRKKRAtoms
import numpy as np


class SitesSection(PotentialSection):
  """ This section retrieves the atomic positions and
      it creates (during reading) the ASE Atoms object """

  def _depends_on(self):
      return ['LATTICE']

  def _set_from_atoms(self, atoms, write_io_data):
      self['SCALED_ATOMIC_POSITIONS'].set(
          atoms.positions[write_io_data['sites_order']] / ( write_io_data['lattice.alat'] * self['BASSCALE']())
      )

  def _update_atoms(self, atoms, read_io_data):
      positions = self['SCALED_ATOMIC_POSITIONS']() * \
            (read_io_data['lattice.alat'] * self['BASSCALE']())
      try:
         if atoms:
            atoms.set_positions(positions)
            return
      except ValueError:
         pass
      atoms = SPRKKRAtoms(positions = positions, potential = self._container)
      read_io_data.update_atoms(atoms)
      return atoms


class SitesSectionDefinition(PotSectionDefinition):

  def __init__(self, name='SITES', **kwargs):
      V = PotValueDefinition
      members = [
          V('CARTESIAN', bool, fixed_value=True),
          # V('BASSCALE', Array(float, length=3), fixed_value=[1.,1.,1.]),
          V('BASSCALE', default_value=[1.,1.,1.], type=Array(float, length=3,
                  after_convert = lambda s,v: np.ones((3)) if np.all(v==0.) else v,
                  condition = lambda v: True if np.all(v!=0.) else "BASSCALE values should not be zero (with the exception that [0,0,0] is considered as valid and replaced by [1,1,1]"
          )),
          V('SCALED_ATOMIC_POSITIONS', Table({'QBAS(X)': float, 'QBAS(Y)' : float, 'QBAS(Z)': float}, numbering='IQ',free_header=True, format='>22.14f', numbering_format='>5')),
      ]
      super().__init__(name, members, has_hidden_members=True)

  result_class = SitesSection


section = SitesSectionDefinition
