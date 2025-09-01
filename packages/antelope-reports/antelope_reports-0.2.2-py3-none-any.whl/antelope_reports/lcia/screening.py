"""
A collection of handy functions for easily displaying information
"""


def process_screen(runner, _ind):
    """
    Show the most important processes. Right now just prints them all out.
    :param runner: A ScenarioRunner
    :param _ind:
    :return:
    """
    for s in runner.scenarios:
        r = runner.result(s, _ind)
        if r.total() == 0:
            continue
        print('\n%s' % s)
        r.terminal_nodes().show_components()


def substance_screen(runner, indicator, use_abs=True):
    """
    Put in a scenario runner and an indicator; generates a list of the most important compounds in each scenario
    (based on a flattened lcia result)
    :param runner: scenario runner
    :param indicator: indicator
    :param use_abs: [True] whether to strictly use absolute values to evaluate significance (the default is True)
    :return:
    """
    for s in runner.scenarios:
        r = runner.result(s, indicator).flatten()
        if use_abs:
            tot = sum(abs(c.cumulative_result) for c in r.components())
            thresh = 0.0045
        else:
            tot = r.total()
            thresh = 0.009
        if tot == 0:
            continue
        print('\n%s' % s)
        print(r)
        ems = sorted(r.components(), key=lambda x: abs(x.cumulative_result), reverse=True)
        c = d = 0
        _pf = True
        for em in ems:
            if use_abs:
                delta = abs(em.cumulative_result)
            else:
                delta = em.cumulative_result
            if _pf:
                c += delta
                print('%2.6g %% %s' % (100*delta/tot, em))
                if abs(delta) / abs(tot) < thresh:
                    _pf = False
            else:
                d += delta
        print('%2.6g %% remainder' % (100 * d / tot))


def show_top_n(res, threshold=0.0075):
    """
    An abortive attempt to to substance_screen for a single result.
    This should probably be an LciaResult method
    :param res:
    :param threshold:
    :return:
    """

    print(res)
    _ins = []
    _edz = []
    _thr = abs(res.total() * threshold)
    for dd in sorted(res.components(), key=lambda _x: _x.cumulative_result):
        if abs(dd.cumulative_result) > _thr:
            print(dd)
            _ins.append(dd)
        else:
            _edz.append(dd)
    _s = sum(_z.cumulative_result for _z in _edz)
    print('%d entries, %d saved' % (len(_ins + _edz), len(_ins)))
    print(': %g : Remainder = %2.2f %%' % (_s, 100*_s/res.total()))
    # return _ins


def nodes(_frag):
    """
    Print a list of terminal nodes contained within the fragment and subfragments.
    Should probably be an LcFragment method.
    :param _frag:
    :return:
    """
    _ns = set()
    for sc, t in _frag.terminations():
        if t.is_process:
            _ns.add(t.term_node)
        elif t.is_subfrag:
            _ns |= nodes(t.term_node)
    for cf in _frag.child_flows:
        if cf.term.is_context:
            _ns.add(_frag)
        else:
            _ns |= nodes(cf)
    return _ns


