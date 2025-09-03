"""
File Purpose: pytest configuration
"""

def pytest_collection_modifyitems(items):
    '''ordering of tests - here, puts multiprocessing tests last.'''
    module_mapping = {item: item.module.__name__ for item in items}
    default_order = 0  # default order for test modules without a specified order
    order = {
        'init_test': -100,  # run this first!
        'test_multiprocessing': 10,
        'test_eppic_tfbi': 12,
        'test_eppic_reading_misc': 15,
        'test_eppic_reading_basics': 20,
    }  # larger --> get tested later.
    items.sort(key=lambda item: order.get(module_mapping[item], default_order))
