from ..output_files_definitions import OutputFileValueDefinition as V, OutputFileDefinition, StarSeparator, BlankSeparator
from typing import Optional
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import copy

from ..output_files import CommonOutputFile, Arithmetic
from ...common.grammar_types import RawData, Table, Sequence, Array, Integer, String
from ...common.decorators import cached_property
from ...common.generated_configuration_definitions import \
    NumpyViewDefinition as NV
from ...common.configuration_definitions import SeparatorDefinition
from ...gui.plot import Multiplot, set_up_common_plot

from ase.units import Rydberg
from packaging.version import Version


class DijOutputFile(CommonOutputFile):

    def __init__(self, definition, container=None):
        super().__init__(definition, container)

    def plot(self, spin=None, l=None, layout=2, figsize=(6,4), latex=None,  # NOQA
             filename:Optional[str]=None, show:Optional[bool]=None, dpi=600,
             **kwargs
             ):
        if isinstance(layout, int):
          layout = ( (self.n_types() ) // layout +1, layout)
        mp=Multiplot(layout=layout, figsize=figsize, latex=latex, **kwargs)
        plt.subplots_adjust(left=0.12,right=0.95,bottom=0.1,top=0.9, hspace=0.6, wspace=0.4)
        for dos in self.iterate_dos(spin, l, total=True):
            mp.plot(dos)
        mp.finish(filename, show, dpi)

class DijDefinition(OutputFileDefinition):
    """ Definition of a Dij File """
    result_class = DijOutputFile

from pyparsing import ParserElement
ParserElement.verbose_stacktrace = True

def create_definition():
    int3 = Integer(format='{:3d}', prefix=' '*10)
    return OutputFileDefinition("Dij",[
        BlankSeparator(),
        StarSeparator(),
        V('HEADER', RawData(ends_with='\n ******************')),
        StarSeparator(),
        BlankSeparator(),
        BlankSeparator(),
        V('NQ', int3, written_name='number of sites   NQ'),
        V('NQ', int3, written_name='number of types   NT'),
        SeparatorDefinition(' '*30+'site occupation:'),
        V('OCCUPATION', Table(
          IQ = Integer(prefix = 10*' '+'IQ = ', format='{:4d}'),
          NIT = Integer(format='{:3d}'),
          IT = Array(Sequence(Integer(format='{:3d}'), String(format='{:>10}', prefix='-')), prefix='   IT: ')
        ))
    ])


definition = create_definition()
extension = 'Dij.dat'
