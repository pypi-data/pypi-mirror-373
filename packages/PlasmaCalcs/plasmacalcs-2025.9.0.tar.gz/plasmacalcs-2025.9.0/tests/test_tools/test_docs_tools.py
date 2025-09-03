"""
File Purpose: test docs_tools.
"""

import PlasmaCalcs as pc

def test_docstring_to_sphinx():
    '''ensures that DocstringInfo(docstring).to_sphinx() succeeds,
    for all modules, classes, functions, and methods in PlasmaCalcs.
    '''
    ll = pc.list_objs(pc)
    for obj in ll:
        doc = obj.__doc__
        if doc is not None:
            di = pc.DocstringInfo(doc)
            di.to_sphinx()  # just making sure it doesn't crash :)
