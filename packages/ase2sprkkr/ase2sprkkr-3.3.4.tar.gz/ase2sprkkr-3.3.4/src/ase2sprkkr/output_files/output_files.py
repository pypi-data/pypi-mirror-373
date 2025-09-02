""" This module describe common header, that appears in the output
files of SPRKKR """

from ..sprkkr.configuration import ConfigurationFile, ConfigurationValue
import pyparsing as pp
import numpy as np
import pkgutil
import sys
from ..common.decorators import cached_class_property
from ..common.grammar_types.data import RestOfTheFile
import io
import os
import re


class UnknownDataValue(ConfigurationValue):

  def as_array(self):
      out = self()
      if not isinstance(out, np.ndarray):
          out = np.genfromtxt( io.StringIO(out) )
      return out


class OutputFile(ConfigurationFile):
  """ Objects of this class holds datas of an output file """

  plot_parameters = {}

  @cached_class_property
  def unknown_output_file_definition(cls):
      """ a definition of unwnown (not yet known) output file that can hold any data in the rest
      of the file """
      V = output_files_definitions.OutputFileValueDefinition
      return output_files_definitions.create_output_file_definition(
          V('KEYWORD', str),
          [ V('DATA', RestOfTheFile(), name_in_grammar=False, result_class=UnknownDataValue) ]
      )

  @cached_class_property
  def definitions(cls):
      """ Return all known definitions of the SPR-KKR output files """
      out = {}
      path = os.path.dirname(__file__)
      path = os.path.join( path, 'definitions')
      name = __name__
      name = name.rsplit('.',1)[0] + '.definitions.'
      for imp, module, ispackage in pkgutil.iter_modules(path=[path], prefix=name):
           __import__(module)
           mod = sys.modules[module]
           ext = getattr(mod, "extension", None) or mod.__name__.rsplit('.',1)[1]
           out[ext] = mod
      return out

  @classmethod
  def from_file(cls, filename, first_try=None, try_only=None, unknown=None):
      """
      Read SPRKKR output file (DOS, BSF....). The type of content of the
      output file is guessed from the content, however you can get hint what
      to try first or force to read only certain file type(s).

      Parameters
      ----------
      filename
        The file to read

      first_try
        List of output file types to be tried first. If it is None, it is guessed
        from the file extension.

      try_only
        List of the output file types, that can be read.
        None mean read any known file type.

      unknown
        If True, at last, an unknown output file is readed: such file has just
        parsed header and then one property that holds the rest of the file as
        text.
        If False, raise an exception if no known (and allowed) file type is
        recognized.
        None means True if try_only is None, False otherwise.
      """
      if first_try is None and not try_only:
         fname = filename
         if hasattr(filename, 'name'):
             fname = filename.name
         if isinstance(filename, str):
             first_try = fname.rsplit('.',1)[1].lower()
             #nektere soubory jsou typu _Dij.data
             special = re.match( r"^.+_([^/\\]+\.[^/\\]+)$", filename)
             if special:
                first_try = [ special.groups(1)[0], first_try ]
         else:
             first_try = ''
      if isinstance(first_try,str):
          first_try=[ first_try ]

      first = None
      if first_try:
         out=None
         try:
             out = cls.from_file(filename, first_try=False, try_only=first_try)
         except Exception as e:
             first = e
         if out:
             return out
      else:
         last = None

      if try_only:
         for i in try_only:
             if i in cls.definitions:
                 try:
                    out = cls.definitions[i].definition.read_from_file(filename)
                    return out
                 except Exception as e:
                    last = e
      else:
          for ext, i in cls.definitions.items():
              if first_try and ext in first_try:
                 continue
              try:
                 out = i.definition.read_from_file(filename)
                 return out
              except Exception as e:
                 last = e
      if unknown is None:
         unknown = try_only is None
      if unknown:
          try:
              return cls.unknown_output_file_definition.read_from_file(filename)
          except pp.ParseBaseException as e:
              raise Exception(f'Can not parse file: {filename}') from e
      raise first or last or ValueError(f'File is not recognized as any known file type')


class CommonOutputFile(OutputFile):

    def n_atoms(self):
        return len(self.ORBITALS)

    def n_types(self):
        return len(self.TYPES)

    def site_type_index(self, type):
        if isinstance(type, int):
            return type
        for i,t in enumerate(self.TYPES):
            if t['TXT_T'] == type:
               return i
        raise ValueError(f'There is no {type} atom in the output file')

    def n_orbitals(self, type):
        type = self.site_type_index(type)
        return self.ORBITALS[self.TYPES[type]['IQAT'][0]]['NLQ']


class Arithmetic:

    def _check_arithmetic(self, other):
        if hasattr(self, '_assert_arithmetic'):
            try:
                self._assert_arithmetic(other)
            except AssertionError as e:
                raise ValueError("The outputs are not compatibile to be summed or subtracted.") from e
        pass

    def __add__(self, other):
        out = self.copy(copy_values=True)
        out+=other
        return out

    def __sub__(self, other):
        out = self.copy(copy_values=True)
        out-=other
        return out

    def __mul__(self, other):
        out = self.copy(copy_values=True)
        out*=other
        return out

    def __div__(self, other):
        out = self.copy(copy_values=True)
        out/=other
        return out

    def __rmul__(self, other):
        out = self.copy()
        out*=other
        return out

    def _do_arithmetic(self, func, other):
        """ Run given function for all "summable/subtractable/etc... data"""
        for val, selector in self._arithmetic_values:
            getattr(self[val]()[selector],func)(other[val]()[selector])

    def __iadd__(self, other):
        self._check_arithmetic(other)
        self._do_arithmetic('__iadd__', other)
        return self

    def __isub__(self, other):
        self._check_arithmetic(other)
        self._do_arithmetic('__isub__', other)
        return self

    def __imul__(self, other):
        self._do_arithmetic('__imul__', other)
        return self

    def __idiv__(self, other):
        self._do_arithmetic('__idiv__', other)
        return self


# at last, import this file that need this module
from . import output_files_definitions  # NOQA: E402
