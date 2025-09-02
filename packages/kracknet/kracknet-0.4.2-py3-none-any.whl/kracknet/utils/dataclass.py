import logging

class Unset:
  pass

class UnknownOption (Exception):
  pass

class InvalidType (Exception):
  pass

class InvalidRange (Exception):
  pass

class InvalidChoice (Exception):
  pass

class DataClass:
  STRICT_SETTING = False

  def __init__ (self, spec):
    self._spec = {it ['key']: it for it in spec}
    self._dict = {}
    self._init_data ()

  def get_spec (self, k):
    return self._spec [k]

  def get_value (self):
    return self._dict

  def help (self):
    b = []
    for it in self._spec.values ():
      if 'name' not in it:
        continue
      b.append ('{key}: {name}\n'.format (**it))
      b.append (f'  type: {it ["type"]}')
      if "default" in it:
        b.append (f', default: {it ["default"]}')
      b.append ('\n')
      if "valid_range" in it:
        b.append (f'  value range: {it ["valid_range"][0]} ~ {it ["valid_range"][1]}\n')
      if "choices" in it:
        b.append (f'  choices: {it ["choices"]}\n')
    out = ''.join (b)
    return out

  def asdict (self, ignore_unset = False):
    return { k: None if v is Unset else v for k, v in self._dict.items () }

  def validate (self):
    for k, v in self._dict.items ():
      assert v is not Unset, f"{k} value is required"

  def __str__ (self):
    b = []
    for k, v in self._dict.items ():
      b.append (f'{k}={v}')
    return ', '.join (b)

  def _init_data (self):
    for op in self._spec.values ():
      if not op ['settable']:
        continue
      self._dict [op ['key']] = op ['default'] if 'default' in op else Unset

  def fset (self, **kargs):
    # force set
    for k, v in kargs.items ():
      self._dict [k] = v

  def set (self, **kargs):
    for k, v in kargs.items ():
      setattr (self, k, v)

  def __getattr__ (self, k):
    if k.startswith ('_'):
      try:
        return self.__dict__ [k]
      except KeyError:
        raise AttributeError

    try:
      return self._dict [k]
    except KeyError:
      raise UnknownOption (f'setting {k} is unknown')

  def __setattr__ (self, k, v):
    if k.startswith ('_'):
      self.__dict__ [k] = v
      return

    if k not in self._dict:
      if self.STRICT_SETTING:
        raise UnknownOption (f'setting {k} is unknown')
      logging.warning (f'unknown setting `{k}` is ignored')
      return

    spec = self._spec [k]
    if 'depends' in spec:
      if not self._dict [spec ['depends']]:
        logging.warning (f'option `{k}` has been configured, but because it is a subordinate of option `{spec ["depends"]}`, which is disabled, it cannot take effect')

    if 'type' in spec:
      try:
        v = eval ('bool' if spec ['type'] == 'boolean' else spec ['type']) (v)
      except (TypeError, ValueError):
        raise InvalidType (f'option {k} should be {spec ["type"]} type')

    if 'choices' in spec:
      if v not in set (spec ['choices'].values ()):
        raise InvalidChoice (f'option {k} should be one of {spec ["choices"]}')

    if 'valid_range' in spec:
      if not (spec ['valid_range'][0] <= v <= spec ['valid_range'][1]):
        raise InvalidRange (f'option {k} should be between {spec ["valid_range"]}')

    self._dict [k] = v
