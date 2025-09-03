"""Provides a suite of I/O routine to load and save parameters in
yml file format.
"""

import re
import yaml
from astropy import units
#from astropy.io.misc import yaml

#q_pattern = re.compile(r'([-+]?\d*\.\d+|\d+)\s(\D+$)') # astropy quantity
q_pattern = re.compile(r'([-+]?\d*\.\d+e[+-]?\d+|\d+|[-+]?\d*\.\d+)\s(\D+$)') # include scientific notation

def quantity_constructor(loader, node):
    value = loader.construct_scalar(node)
    a,b = q_pattern.match(value).groups()
    return units.Quantity(a, unit=b)

def quantity_representer(dumper, data):
    return dumper.represent_scalar('!astropy.units.Quantity', '%s %s' % (data.value, str(data.unit)))

yaml.add_representer(units.Quantity, quantity_representer)
yaml.add_constructor('!astropy.units.Quantity', quantity_constructor)
yaml.add_implicit_resolver('!astropy.units.Quantity', q_pattern)


def save_config(filename, cfg, name="config", mode="a"):
    """ Write config to yml file

    >>> save_config("test.yml", {'author':'me', 'date':'today'})
    >>> print(load_config("test.yml"))
    {'author': 'me', 'date': 'today'}
    """
    if name in cfg.keys():
        cfg = cfg[name]
    with open(filename, mode) as f:
        yaml.dump(cfg, f, default_flow_style=False)


def load_config(filename, name="config"):
    """ Load config from yml file
    """
    with open(filename, "r") as f:
        cfg = yaml.load(f, Loader=yaml.UnsafeLoader)
    if name in cfg.keys():
        cfg = cfg[name]
    #for k, v in cfg.items():
    #    cfg[k] = decode(v)
    return cfg


if __name__ == "__main__":
    import doctest
    doctest.testmod()