""" In this file the common containers of configuration values are,
either for task or potential.

Configuration containers are classes, that holds configuration values
and other containers, and are able to write them to a configuration file,
and that are results of parsing of a configuration file.
"""

from .configuration import Configuration
import itertools
import re
from typing import Union, Any, Dict
from .warnings import warnings, DataValidityError
from .section_adaptors import SectionAdaptor, MergeSectionAdaptor


class DisabledAttributeError(AttributeError):
      """ This exception is raised, if the attribute of a container exists,
      but it is disabled. E.g. because it has no sense for the current data.
      """


class BaseConfigurationContainer(Configuration):
    """ Configuration container, that holds members, either in classical way
    (see :class:ConfigurationContainer) or treat them in a special way
    """

    def copy(self, copy_values:bool=False):
        """ Create a copy of the container

        Parameters
        ----------
        copy_values
          If true, the copy of values is done, so their modifications do not affects the container.
          (e.g. for numpy arrays)
        """
        d=self._definition
        vals=self.as_dict(copy=copy_values, only_changed=True)
        out =d.result_class(definition=d)
        out.set(vals, unknown='add')
        return out

    def has_any_value(self) -> bool:
        """
        Return True if any member of the section has value.

        Return
        ------
          has_any_value: bool
              True, if no value in the container is set, False otherwise
        """
        for i in self._values():
          if i.has_any_value():
             return True
        return False

    @property
    def definition(self):
        """ The definition of the section.

        Returns
        -------
        ase2sprkkr.common.configuration_definitions.ContainerDefinition
        The definition of the section. I.e. the object that defines, which configuration values
        are in the section, their default values etc.
        """
        return self._definition


class ConfigurationContainer(BaseConfigurationContainer):
  """ A container for configuration (problem-definition) options and/or sections.

  Options in the configuration (problem-definition) files are grouped to
  sections, sections are then grouped in a configuration file object.
  This is a base class for these containers.

  """

  def __init__(self, definition, container=None):
      """ Create the container and its members, according to the definition """
      super().__init__(definition, container)
      """
      The members of the container, in a form of ``{obj.name : obj}``
      """
      self._init_members_from_the_definition()

  def _init_members_from_the_definition(self):
      self._members = {}
      self._lowercase_members = {}
      """
      Non-hidden members of the containers, accesible via sanitized names.
      I.e. via names with whitespaces and other special characters replaced by underscore.
      These sanitized names are then used as names for "attributes" of this container, to
      make the members accesible via ``<container>.<member>`` notation.
      """
      self._interactive_members = {}
      for v in self._definition.members():
          if v.create_object:
             self._add(v.create_object(self))

  def items(self):
      """ Members of the container. I.e. the options of the section, or sections
      of the configuration file e.t.c.

      Returns
      -------
      members: dict
      A dictionary of the shape ``{ name : member }``

      """
      return self._members

  def _get_member(self, name):
      """
      Return the member of the container of a given name.
      It search either the members and interactive_members containers
      """
      if name in self._members:
          out = self._members[name]
      elif name in self._interactive_members:
          out = self._interactive_members[name]
      else:
          raise AttributeError(f'No {name} member of {self._definition}')
      d = out._definition
      if d.is_hidden:
          raise DisabledAttributeError(f'member {name} of {self} is not directly accessible. '
                                       'Probably it''s a hidden attribute used for some kind of logic, '
                                       'for which a direct access has no sense. If you really need '
                                       'an access to the attribute, you can use the "container[''name'']" notation.')
      allowed = d.allowed(self)
      if not allowed:
          if allowed is False:
              raise DisabledAttributeError(f'member {name} of {self} is not accessible for '
                              'the current data. It is probably not available or has no sense '
                              'in this particular case (e.g. data file does not contain needed '
                              'data for it). If you eally need an access to the attribute, you can use the '
                              '"container[''name'']" notation.')
          else:
              raise DisabledAttributeError(str(allowed))
      return out

  def __getattr__(self, name):
      """
      The members of the container are accesible as attributes of the container, too.
      Either using their normal, or ``sanitized`` names.
      """
      try:
        out = self._get_member(name)
      except AttributeError as e:
        if isinstance(e, DisabledAttributeError):
           msg = str(e)
           cls = DisabledAttributeError
        else:
           msg = f"There is no value with name {name} in {self}.\nMaybe, you want to add a custom value using the add method?"
           cls = AttributeError
        raise cls(msg) from e
      return out

  def __getitem__(self, name):
      """
      The members of the container are accesible using ``container["member name"]`` notation.
      """
      if isinstance(name, tuple):
         if not name:
             raise KeyError('An empty tuple not allowed as a key.')
         out = self._members[name[0]]
         ll = len(name)
         if ll == 1:
             return out
         if ll == 2:
             return out[name[1]]
         return out[name[1:]]

      return self._members[name]

  def _get(self, name, default=None):
      return self._members.get(name, default)

  def __dir__(self):
      """
      Expose the interactive_members in the container attribute listing.
      Interactive_members are the non-hidden members identified by their sanitized names.
      """
      # def ok(member):
      #    d = member._defintion
      #    return not d.condtion or d.condition(self)

      members = ( k.name for i,k in self._interactive_members.items() )
      if self._definition.dir_common_attributes:
          members = itertools.chain( members, super().__dir__())
      return members

  def __contains__(self, name):
      """ The check for existence of a member with the given name."""
      if isinstance(name, tuple):
          ll=len(name)
          if ll==0:
              return False
          n = name[0]
          if not n in self._members:
              return False
          if ll==1:
              return True
          member = self._members[n]
          if ll==2:
              return name[1] in member
          else:
              return name[1:] in member
      return name in self._members

  def clear(self, do_not_check_required=False, call_hooks=True, generated=None):
      """
      Erase all values (or reset to default) from all options in the container
      (ad subcontainers)

      Parameters
      ----------
      do_not_check_required: bool
        Do not check validity of the values after clearing. If ``False`` (default)
        is passed as this argument, the required option without a default value
        (or a section containing such value) throw an exception, which prevents the
        clearing (neverthenless, previous values in the section will be cleared anyway).

      call_hooks: bool
        If False, the cleared values do not raise theirs hooks

      generated: bool
        If True
      """
      for i in self._members.values():
          i.clear(do_not_check_required, call_hooks=call_hooks, generated=False if generated is None else generated)

  def get_members(self, name=None, unknown='find', is_option=None, lower_case=True):
      """
      Get all the members of given name. According to ``unknown`` parameter,
      either only from self, or from any child containers, too.

      Parameters
      ----------
      name: None or str
        If None, return contained values as a dictionary.
        Otherwise, return the value of the member with the given name.

      unknown: str or None
        If unknown == 'find' and there is no member with a given name,
        try to find the first such-named item (case insensitive)
        in the descendant conainers.

      is_option: bool
        If set, limit to either Option or non-option items

      lower_case: bool
        If true, try to search for the lower-cased name

      Return
      ------
      value: mixed
      """
      if name is None:
          yield self
          return
      if '.' in name:
          name, child = name.split('.')
      else:
          child=None

      def values():
          try:
              yield self._members[name]
              return
          except KeyError:
              n = name.lower() if lower_case else name
              if unknown=='find':
                  for i in self:
                      yield from i._find_members(n, is_option, lower_case)
              elif lower_case:
                  v = self._lowercase_members[n]
                  yield v

      if child:
          for v in values():
              yield from v.get_members(child, unknown, is_option, lower_case)
      else:
          yield from values()

  def get(self, name=None, unknown='find', is_option=True):
      """
      Get the value, either of self or of a child of a given name.

      Parameters
      ----------
      name: None or str
        If None, return contained values as a dictionary.
        Otherwise, return the value of the member with the given name.

      unknown: str or None
        If unknown == 'find' and there is no member with a given name,
        try to find the first such-named item (case insensitive)
        in the descendant conainers.
        unknown == 'find_exact' do the same, case sensitive.

      Return
      ------
      value: mixed
      """
      item = self.get_members(name, unknown, is_option)
      try:
          item=next(item)
      except StopIteration:
         raise ValueError(f"No {name} member of {self}")
      return item.as_dict(only_changed=False)

  def set(self, values:Union[Dict[str,Any],str,None]={}, value=None, *, unknown='find', error=None, **kwargs):
      error = error or 'section'
      self._set(values, value, unknown=unknown, error=error, **kwargs)
      self.validate(why='warning')

  def _set(self, values:Union[Dict[str,Any],str,None]={}, value=None, *, unknown='find', error=None, **kwargs):
      """
      Set the value(s) of parameter(s). Usage:

      > input_parameters.set({'NITER': 5, 'NE': [10]})
      or
      > input_parameters.set(NITER=5, NE=[10])

      Parameters
      ----------

      values:
        Dictionary of values to be set, or the name of the value, if the value is given.

      value:
        Value to be set. Setting this argument require to pass string name to the values argument.

      unkwnown: 'add', 'find' or None
        How to handle unknown (not known by the definition) parameters.
        If 'find', try to find the values in descendant containers.
        If 'add', add unknown values as custom values.
        If None, throw an exception.
        Keyword only argument.

      **kwargs: dict
        The values to be set (an alternative syntax as syntactical sugar)
      """
      if values.__class__ is str:
         values = { values : value }
      elif value is not None:
         raise ValueError("If value argument of Container.set method is given,"
         " the values have to be string name of the value")

      def set_value(name, value):
        if '.' in name:
            section, name = name.split('.', 1)
            if not section in self:
               if unknown == 'add':
                   self.add(section)
               else:
                   raise KeyError(f"There is no section {section} in {self} to set{section}.{name} to {value}")
            self._members[section]._set({name:value}, unknown='fail' if unknown == 'find' else unknown, error=error)
            return
        option = self._members.get(name, None)
        if not option or not option._definition.accept_value(value):
           if unknown == 'find':
              option = self._find_member(name.lower(), True, True)
              if option:
                 option._set(value, error=error)
                 return
           if unknown == 'ignore':
               return
           if not unknown == 'add':
              raise KeyError("No option with name {} in {}".format(name, str(self)))
              return
           self.add(name, value)
        else:
           option._set(value, unknown=unknown, error=error)

      if values:
        try:
           items = values.items()
        except AttributeError:
          raise ValueError('Only a dictionary can be assigned to a section.')
        for i,v in items:
           set_value(i,v)

      if kwargs:
          self.validate_section(why='set', section_adaptor=MergeSectionAdaptor(kwargs, self))
          for i,v in kwargs.items():
              set_value(i,v)

  def add(self, name:str, value=None):
      """
      Add custom value to the container

      Parameters
      ----------
      name: str
        Name of the added value

      value: value
        Value of the added value
      """
      if not getattr(self._definition, 'custom_class', False):
         raise TypeError(f'Can not add custom members to a configuration class {self._definition}')
      if name in self._members:
         raise TypeError(f'Section member {name} is already in the section {self._definition}')
      cc = self._definition.custom_class
      self._add(cc(name, self))
      if value is not None:
          self._members[name].set(value, unknown='add')

  def remove_member(self, name:str):
      """
      Remove a (previously added) custom value from the container
      """
      cclass = getattr(self._definition, 'custom_class', False)
      if not cclass:
         raise TypeError("Can not remove items of {}".format(name))
      if not getattr(self._members[name], 'remove'):
         raise KeyError("No custom member with name {} to remove".format(name))
      member = self._members[name]
      del self._members[name]
      iname = self._interactive_member_name(name)
      if iname in self._interactive_members and \
           self._interactive_members[iname] is member:
                del self._interactive_members[iname]
      for i in name.lower(), iname.lower():
          if i in self._lowercase_members and self._lowercase_members[i] is member:
                del self._lowercase_members[i]

  def __iter__(self):
      """ Iterate over all members of the container """
      yield from self._members.values()

  def _values(self):
      """ Iterate over all members of the container """
      yield from self._members.values()

  def _as_dict(self, get):
      """
      Return the content of the container as a dictionary.
      Nested containers will be transformed to dictionaries as well.

      Parameters
      ----------
      get
        This function will be applied to the options to (possible) obtain
        the values
      """
      out = {}
      for i in self._values():
          value = i._as_dict(get)
          if value is not None:
              out[i._definition.real_name] = value
      return out or None

  def _find_members(self, name:str, is_option=None, lower:bool=False):
      """
      Iterates over a value of a given name in self or in any
      of owned subcontainers.

      Parameters
      ----------
      name: str
      A name of the sought options

      is_option:bool
      If True, find only options, if False, find only the others.

      lower:bool
      If True, find an option with given lowercased name (case insensitive)

      Returns
      -------
      value:typing.Optional[ase2sprkkr.common.options.Option]
      The first option of the given name, if such exists. ``None`` otherwise.
      """
      if is_option is not True and \
         name == (self.name.lower() if lower else self.name):
            yield self
      for i in self._values():
          if i._definition.is_hidden:
             continue
          yield from i._find_members(name, is_option, lower)

  @staticmethod
  def _interactive_member_name(name):
      """ Create a sanitized name from a member-name.

      The sanitized names are keys in ``interactive_members`` array, and thus
      the members are accesible by ``<container>.<member>`` notation.
      """
      return re.sub(r'[()]','', re.sub(r'[-\s.]','_',name))

  def _add(self, member):
      name = member.name
      self._members[name] = member

      lname = name.lower()
      if not lname in self._lowercase_members:
          self._lowercase_members[lname] = member

      if not member._definition.is_hidden:
          iname = self._interactive_member_name(name)
          if not iname in self._interactive_members:
              self._interactive_members[iname] = member
              iname = iname.lower()
              if not iname in self._lowercase_members:
                  self._lowercase_members[iname] = member

  def is_changed(self):
      for i in self._values():
          if i.is_changed():
              return True
      return False

  def _save_to_file(self, file, always=False, name_in_grammar=None, delimiter='')->bool:
      """ Save the content of the container to the file (according to the definition)

      Parameters
      ----------
      file: file
        File object (open for writing), where the data should be written

      always:
        Do not consider conditions

      Returns
      -------
      something_have_been_written
        If any value have been written return True, otherwise return False.
      """
      return self._definition._save_to_file(file, self, always, name_in_grammar, delimiter)

  def __setattr__(self, name, value):
      """ Setting the (unknown) attribute of a section sets the value of the member
      with a given name """
      if name[0]=='_' or name in self.__dict__ \
         or hasattr(getattr(self.__class__, name, None),'__set__'):
              super().__setattr__(name, value)
      else:
        val = self._get_member(name)
        val.set(value)

  def _validate(self, why:str='save'):
      """ Validate the configuration data. Raise an exception, if the validation fail.

      Parameters
      ----------
      why
        Type of the validation. Possible values
        ``save`` - Full validation, during save.
        ``set`` - Validation on user input. Allow required values not to be set.
        ``parse`` - Validation during parsing - some check, that are enforced by the parser, can be skipped.
      """
      sa = SectionAdaptor(self)
      self._definition.validate(sa, why)
      if why == 'save' and not self._definition.is_optional and not self.has_any_value():
          raise ValueError(f"Non-optional section {self._definition.name} has no value to save")
      for o in self._values():
          d = o._definition
          if d.allowed(self):
              o._validate(why)
      self.validate_section(why, sa)

  def validate_section(self, why:str='save', section_adaptor=None):
      if why == 'warning':
          self._validate_section('save', section_adaptor)
      else:
          with warnings.catch_warnings():
              warnings.simplefilter("error", DataValidityError)
              self._validate_section(why)

  def _validate_section(self, why:str='save', section_adaptor=None):
      if section_adaptor is None:
          section_adaptor = SectionAdaptor(self)

      for o in self._values():
          d = o._definition
          if d.allowed(section_adaptor) and d.validate_section:
                  d.validate_section(section_adaptor, why)

  def has_any_value(self) -> bool:
      """
      Return True if any member of the section has value.

      Return
      ------
        has_any_value: bool
            True, if no value in the container is set, False otherwise
      """
      for i in self._values():
        if i.has_any_value():
           return True
      return False


class BaseSection(ConfigurationContainer):
  """ A section of SPRKKR configuration - i.e. part of the configuration file. """


class Section(BaseSection):
  """ A standard section of a task or potential (whose content is predefinded by SectionDefinition) """

  @property
  def definition(self):
      """ The definition of the section.

      Returns
      -------
      ase2sprkkr.common.configuration_definitions.ContainerDefinition
      The definition of the section. I.e. the object that defines, which configuration values
      are in the section, their default values etc.
      """
      return self._definition


class CustomSection(BaseSection):
  """ Custom task section. Section created by user with no definition """

  def remove(self):
      """ Remove the custom section from the parent container """
      self._container.remove(self.name)

  @classmethod
  def factory(cls, definition_type):
      """ Create a factory for custom values.

      Parameters
      ----------
      definition_type: ase2sprkkr.common.configuration_definitions.BaseDefinition
        Type (definitions) of the custom values created by
        the resulting function

      Return
      ------
      factory: callable
        Factory function of the signature (name: str, container: ase2sprkkr.common.configuration_containers.ConfigurationContainer)
        that created a custom value or section of the given definition

      """
      def create(name, container):
          definition = definition_type(name)
          definition.removable = True
          return cls(definition, container)
      return create


class RootConfigurationContainer(ConfigurationContainer):
  """ Base class for data of configuration/problem-definition files

  In addition to container capabilities, it can read its data from/to file.
  """
  name_in_grammar = False

  def read_from_file(self, file, clear_first:bool=True, allow_dangerous:bool=False):
      """ Read data from a file

      Parameters
      ----------
      file: str or file
        File to read the data from

      clear_first
        Clear the container first.
        Otherwise, the data in the sections that are not present in the
        file are preserved.
      allow_dangerous
        Allow to load dangerous_values, i.e. the values that do not pass the requirements for the input values (e.g. of a different type or constraint-violating)
      """
      values = self._definition.parse_file(file, allow_dangerous=allow_dangerous)
      if clear_first:
         self.clear(True)
      self.set(values, unknown='add')

  def find(self, name, unknown='find', is_option=True, lower_case=True, first=True):
      """ Find a configuration value of a given name in the owned sections """
      out = self.get_members(name, unknown, is_option, lower_case)
      if first:
          try:
              return next(out)
          except StopIteration:
              raise ValueError(f"No {name} member of {self}")
      else:
          return out
