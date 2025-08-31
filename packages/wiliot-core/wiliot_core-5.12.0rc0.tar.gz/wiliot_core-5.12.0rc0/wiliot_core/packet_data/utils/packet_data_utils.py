import inspect


def run_all_functions(object_var, needed_methods=None, filter_out_methods=None):
    s_attr = (getattr(object_var, name) for name in dir(object_var) if not name.startswith('_'))
    s_methods = [a for a in s_attr if inspect.ismethod(a)]
    all_results = {}
    for method in s_methods:
        if needed_methods is not None and method not in needed_methods:
            continue
        if filter_out_methods is not None and method in filter_out_methods:
            continue
        calc_data = method()
        all_results = {**all_results, **calc_data}
    return all_results
