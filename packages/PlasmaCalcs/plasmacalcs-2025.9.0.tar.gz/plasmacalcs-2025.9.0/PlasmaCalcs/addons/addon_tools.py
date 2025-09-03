"""
File Purpose: tools for addons
"""

ADDON_LOADERS = []  # list of QuantityLoader addon classes
ADDONS_FAILED = dict()  # {name: ImportFailed object or list of ImportFailed objects}

def register_addon_loader(loader):
    '''registers loader as an existing addon loader. Then returns loader.'''
    ADDON_LOADERS.append(loader)
    return loader

def register_addon_loader_if(condition):
    '''returns registers_addon_loader function if condition, else function that does nothing.'''
    return register_addon_loader if condition else lambda x: x

def register_addon_failed(name):
    '''registers name as a failed addon.'''
    ADDONS_FAILED.append(name)
