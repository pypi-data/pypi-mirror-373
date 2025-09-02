import os
import toml
import logging
from rs4.attrdict import AttrDict

CONFIG_PATH = os.path.expanduser ('~/.kracknet/config')

def get_config (backend, access_key):
  user_config = {'server': {}}
  if os.path.isfile (CONFIG_PATH):
    with open (CONFIG_PATH) as f:
      user_config = toml.load (f)

  if access_key is None:
    access_key = os.getenv ('KRACKNET_ACCESS_KEY') or user_config ['server'].get ('access_key')
  assert access_key, 'Access key is missing'

  if backend is None:
    backend = os.getenv ('KRACKNET_BACKEND') or user_config ['server'].get ('backend', 'https://kracknet.com')

  while backend [-1] == '/':
    backend = backend [:-1]

  logging.info (f'API backend: {backend}')
  config = AttrDict ()
  config.server = AttrDict ()
  config.server.backend = backend
  config.server.access_key = access_key
  return config
