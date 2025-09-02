""" The ARPES reader and result. """

from ..task_result import TaskResult, KkrProcess
from .default import DefaultOutputReader
from ...common.decorators import cached_property
from ...output_files.output_files import OutputFile
import os


class ArpesResult(TaskResult):
  """ ARPES result provides acces to the generated SPC output file
  containing the results of Angle resolved photoelectron electroscopy,
  using the :py:attr:`~spc` property. """

  @cached_property
  def spc_filename(self):
      """ New (output) potential file name """
      fname = self.input_parameters.CONTROL.DATASET() + '_ARPES_data.spc'
      if self.directory:
         fname = os.path.join(self.directory, fname)
      return fname

  @cached_property
  def spc(self):
      """ The new (output) potential - that contains the converged charge density etc. """
      return OutputFile.from_file(self.spc_filename, try_only='spc')


class ArpesProcess(KkrProcess):
  """ ARPES task output reader currently do nothing, just have a special
  result, that allow easy acces to spc output file """

  result_class = ArpesResult
  reader_class = DefaultOutputReader
