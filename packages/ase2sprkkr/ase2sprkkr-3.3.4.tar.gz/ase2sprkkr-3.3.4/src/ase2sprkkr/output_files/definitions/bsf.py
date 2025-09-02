from ..output_files_definitions import OutputFileValueDefinition as V, create_output_file_definition, OutputFileDefinition,Separator
from typing import Optional
import numpy as np

from ..output_files import Arithmetic, CommonOutputFile
from ...common.grammar_types import Array, NumpyArray, Keyword
from ...common.generated_configuration_definitions import NumpyViewDefinition as NV
from ...common.configuration_definitions import gather,switch
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from functools import lru_cache
import warnings
from ase.units import Rydberg
from ...gui.plot import colormesh, Multiplot


class BSFOutputFile(CommonOutputFile, Arithmetic):

    plot_parameters = { 'layer', 'fermi', 'seperate_plots' }

    """
    Output file for Bloch spectral functions
    """


    def plot(self, layout=(2,2), figsize=(10,6), latex=None,
             filename:Optional[str]=None, show:Optional[bool]=None, dpi=600,
             layer=None, separate_plots=False, **kwargs
             ):

            with Multiplot(layout=layout, figsize=figsize, latex=latex,
                         filename=filename, show=show, dpi=dpi,
                         separate_plots=separate_plots,
                         adjust={'left':0.12, 'right': 0.95,'bottom': 0.17, 'top':0.90, 'hspace': 0.75, 'wspace':0.5 },
                         **kwargs) as mp:

                if self.KEYWORD() in ['BSF-SPN', 'BSF-SPOL']:
                    mp.plot(self.I)
                    mp.plot(self.I_X)
                    mp.plot(self.I_Y)
                    mp.plot(self.I_Z)
                else:
                    mp.plot(self.I)
                    mp.plot(self.I_UP)
                    mp.plot(self.I_DOWN)

    _arithmetic_values = [('RAW_DATA', slice(None))]

    def _assert_arithmetic(self, other):
         """ Check, that the file can be summed/subtracked from an other file """
         assert self.MODE() == other.MODE()
         assert self.KEYWORD() == other.KEYWORD()
         for i in ['SHAPE','NQ_EFF', 'NK2']:
             assert self[i]() == other[i]()
         if self.MODE() == 'EK_REL':
             assert np.allclose(self.K(), other.K())


class BSFDefinition(OutputFileDefinition):

    result_class = BSFOutputFile


def create_definition():
    cmap1 = plt.cm.bone_r(np.linspace(0.,1.,256))
    cmap2 = plt.cm.hot(np.linspace(0.,1.,256))
    cmap = np.vstack((cmap1,cmap2))
    mymap = mcolors.LinearSegmentedColormap.from_list('my_colormap',cmap)

    def plot(title, colormap='bwr', negative=True):

        def plot(option, colormap=colormap, layer=None, fermi=None, **kwargs):
          c = option._container
          mesh = c.MESH()
          data = option()
          if fermi is True:
               fermi = 0.5

          def check_layer(layer):
              limit = data.shape[0]
              if layer < 0 or layer >= limit:
                  raise ValueError(f"Layer number should be between {1} and {limit}.")

          if layer is None:
              data = data.sum(axis = 0)
          elif isinstance(layer, int):
              check_layer(layer)
              data = data[layer]
          else:
              check_layer(layer.start)
              check_layer(layer.stop)
              if layer.start >= layer.stop:
                  raise ValueError(f"Empty layer range.")
              data = data[layer].sum(axis = 0)

          if negative:
            vmax = max(np.max(data), -np.min(data))
            vmin = -vmax
          else:
            vmin = 0
            vmax = np.max(data)
          k = mesh[0,0]
          kw = {
              'vmin' : vmin,
              'vmax' : vmax,
              'colormap' : colormap,
              'xticks' : np.insert(k[[x - 1 for x in c.INDKDIR()]], 0, 0),
              'xticklabels' : [],
              'xlabel' : r'K',
              'colorbar' : True,
              'title' : title,
              'show_zero_line' : fermi,
          }

          if c.MODE()=='CONST-E':
            kw.update({
              'ylabel' : r'$E-E_{\rm F}$ (eV)',
              'yrange' : (c.E[0], c.E[-1]),
            })
          else:
            kw.update({
              'ylabel' : r'$E-E_{\rm F}$ (eV)'
            })

          def callback(ax):
              for index in c.INDKDIR()[:-1]:
                  ax.plot([k[index - 1],k[index - 1]],[mesh[1,0,1], mesh[1,-1,1]],color='black',lw=0.5)

          kw.update(kwargs)
          colormesh(*mesh, data, callback=callback, **kw)

        return plot

    reorder = (1, 0, 2)

    def init_veck_start(option):
        warnings.warn("VECK_START attribute was not set! It should be set to the KA attribute "
        "of the input file, however, this value is not available in the BSF file, so it is inited "
        "to the [0,0,0] vector. K-point coordinates for CONST-E mode will can be wrong.")
        return [0,0,0]

    @lru_cache(maxsize=2)
    def k_points(start, end, num):
        return np.linspace(start, end, num)

    @lru_cache(maxsize=2)
    def energy_points(start, end, fermi, num):
        return np.linspace(start - fermi, end - fermi, num) * Rydberg

    def i(type):
        def index(data, c):
          """
          Returns data in the shape
          ('NE/NK1','NQ_EFF', 'NK2')
          for a given type.
          Reorder parameter then change the order of the axes to
          ('NQ_EFF', 'NE/NK1', 'NK2')

          Data structure:
            IX,Y,Z (BSF-SPOL/SPN)
                k-e: NE, type, NQ, NK  types(I,x,y,z)
                k-k: type, K1, NQ, K2, types(I,x,y,z)

           Iup,dn (BSF) two sets
                k-e: NE, type, NQ, NK   types(u,d)
                     NE, type, NQ, NK   types(I)
                k-k: NK, type, NQ, NK   types(u,d)
                     NK, NQ, NK   types(I)
          """
          nq=c.NQ_EFF()
          nk2=c.NK2()
          if c.KEYWORD() == 'BSF':
             nk1 = c.NE() if c.MODE() == 'EK-REL' else c.NK1()
             limit = nq * nk1 * nk2 * 2
             if type >= 0:
                return data[:limit].reshape(nk1, 2, nq, nk2)[:,type]
             else:
                return data[limit:].reshape(nk1,nq,nk2)
          else:
             if c.MODE() == 'EK-REL':
                return data.reshape(c.NE(), 4, nq, nk2)[:,type + 1]
             else:
                return data.reshape(4, c.NK1(), nq, nk2)[:,type + 1]
        return index

    norm = np.linalg.norm

    definition = create_output_file_definition(Keyword('BSF-SPOL', 'BSF-SPN', 'BSF'), [
      Separator(),
      V('DATASET', str, written_name='#DATASET'),
      V('MODE', Keyword('EK-REL', 'CONST-E')),
      *switch('MODE', {
          'EK-REL' : [
              V('NE2', int, written_name='NE', info="Number of energies (the second axis)"),
              V('NK', int, info="Number of K points (the same as NK2)"),
              Separator(),
              *gather(
                V('EMIN', float),
                V('EMAX', float)
              ),
              Separator(),
              V('NKDIR', int),
              V('LBLKDIR', NumpyArray(written_shape=(-1,1), shape=(-1,), lines='NKDIR', dtype='line'),
                           name_in_grammar=False),
              Separator(),
              V('INDKDIR', int, is_repeated=True),
              Separator(),
              V('NK2', int, written_name='NK', info="Number of K points (the last axis)"),
              V('K', NumpyArray(written_shape=(-1,1), shape=(-1,), lines='NK'), name_in_grammar=False),
              Separator(),
              V('E', Array(float), default_value_from_container=lambda o:
                 energy_points(o.EMIN(),o.EMAX(),o.EFERMI(), o.NE()), is_stored=False, info='Energy (relative to Fermi energy)'),
            ],
          'CONST-E' : [
              V('NK1', int, info='Number of K points (the first axis)'),
              V('NK2', int, info='Number of K points (the first axis)'),
              V('ERYD', Array(float, length=2)),
              V('VECK_START', Array(float, length=3), is_stored=False, default_value=init_veck_start, init_by_default=True),
              V('NK1_1', int, written_name='NK1', is_hidden=True),
              V('VECK1', Array(float, length=3)),
              V('NK2_1', int, written_name='NK2', is_hidden=True),
              V('VECK2', Array(float, length=3)),
              Separator(),
              V('K1', Array(float), init_by_default=True, default_value_from_container=lambda o:
                 k_points(norm(o.VECK_START()),
                          norm(o.VECK1()),
                          norm(o.NK1()),
                 ), is_stored=False, info='First axis for the data'),
              V('K2', Array(float), init_by_default=True, default_value_from_container=lambda o:
                 k_points(norm(o.VECK_START()),
                          norm(o.VECK2()),
                          norm(o.NK2()),
                 ), is_stored=False, info='Second axis for the data'),
          ]}
      ),

      V('MESH', NumpyArray(float), is_stored=False, init_by_default=True,
                default_value_from_container=lambda c:
          np.meshgrid(c.K1(),c.K2()) if c.MODE()=='CONST-E' else
          np.meshgrid(c.K(), c.E())
      ),

      V('RAW_DATA', NumpyArray(written_shape=(-1,1), shape=(-1,)), name_in_grammar=False),
      *switch('KEYWORD', {
        'BSF' : [
            NV('I_UP', 'RAW_DATA', i(0), reorder=reorder, plot=plot(title='Spin up', negative=False, colormap='Reds') ),
            NV('I_DOWN', 'RAW_DATA', i(1), reorder=reorder, plot=plot(title='Spin down', negative=False, colormap='Blues') ),
        ],
        'BSF-SPOL': [
            NV('I_X', 'RAW_DATA', i(0), reorder=reorder, plot=plot(title=r'$\sigma_x$') ),
            NV('I_Y', 'RAW_DATA', i(1), reorder=reorder, plot=plot(title=r'$\sigma_y$')),
            NV('I_Z', 'RAW_DATA', i(2), reorder=reorder, plot=plot(title=r'$\sigma_z$') ),
        ],
        'BSF-SPN' : 'BSF-SPOL',
      }),
      NV('I', 'RAW_DATA', i(-1), reorder=reorder, plot=plot(negative=False, colormap=mymap, title='Total') ),

    ], cls=BSFDefinition, name='BSF', info='BSF output file')

    return definition


definition = create_definition()
