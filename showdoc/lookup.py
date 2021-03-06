# AUTOGENERATED! DO NOT EDIT! File to edit: ../00_lookup.ipynb.

#nbdev_cell auto 0
__all__ = ['nbdev_idxs', 'nbdev_idx_mods', 'ShowdocLookup', 'init_showdoc', 'showdoc_lookup']


#nbdev_cell ../../00_lookup.ipynb 1
#export
from fastcore.utils import *
from fastcore.foundation import *
import pkg_resources,importlib


#nbdev_cell ../../00_lookup.ipynb 8
#export
def _try_load(o):
    try: return o.dist.key,o.load()
    except ImportError: None

nbdev_idxs = dict(L(pkg_resources.iter_entry_points(group='nbdev')).map_filter(_try_load))


#nbdev_cell ../../00_lookup.ipynb 14
#export
nbdev_idx_mods = {mod:ep.modidx for lib,ep in nbdev_idxs.items() for mod in ep.modidx['syms']}


#nbdev_cell ../../00_lookup.ipynb 18
#export
class ShowdocLookup:
    "Mapping from symbol names to URLs with docs"
    def __init__(self, strip_libs=None, incl_libs=None, skip_mods=None):
        skip_mods,strip_libs = setify(skip_mods),L(strip_libs)
        if incl_libs is not None: incl_libs = (L(incl_libs)+strip_libs).unique()
        self.entries = filter_keys(nbdev_idxs, lambda k: incl_libs is None or k in incl_libs)
        py_syms = merge(*L(o.modidx['syms'].values() for o in self.entries.values()).concat())
        for m in strip_libs:
            _d = self.entries[m].modidx
            stripped = {remove_prefix(k,f"{mod}."):v
                        for mod,dets in _d['syms'].items() if mod not in skip_mods
                        for k,v in dets.items()}
            py_syms = merge(stripped, py_syms)
        self.syms = py_syms

    def __getitem__(self, s): return self.syms.get(s, None)


#nbdev_cell ../../00_lookup.ipynb 23
#export
from nbdev._nbdev import modidx


#nbdev_cell ../../00_lookup.ipynb 24
#export
_showdoc_lookup = None

def _settings(fr, mod=None):
    if mod is None: mod = fr.f_globals['__name__']
    return nested_idx(nbdev_idx_mods, mod, 'settings') or {}

def init_showdoc(settings=None, mod=None):
    "Create an `ShowdocLookup` using values from settings"
    if settings is None: settings = _settings(sys._getframe(1), mod)
    strip_libs  = settings.get('strip_libs',settings.get('lib_name','')).split()
    incl_libs  = settings.get('index_libs',None)
    if incl_libs is not None: incl_libs = incl_libs.split()
    global _showdoc_lookup
    _showdoc_lookup = ShowdocLookup(strip_libs=strip_libs, incl_libs=incl_libs)


#nbdev_cell ../../00_lookup.ipynb 25
#export
def showdoc_lookup():
    "`ShowdocLookup` singleton using settings from calling frame"
    if not _showdoc_lookup: init_showdoc(_settings(sys._getframe(1)))
    return _showdoc_lookup


#nbdev_cell ../../00_lookup.ipynb 29
#export
@patch
def _link_sym(self:ShowdocLookup, skipped, m):
    l = m.group(1)
    if l in skipped: return m.group(0)
    s = self[l]
    if s is None: return m.group(0)
    return rf"[{m.group(0)}]({s})"

_re_backticks = re.compile(r'`([^`\s]+)`')
@patch
def _link_line(self:ShowdocLookup, l, skipped):
    return _re_backticks.sub(partial(self._link_sym, skipped), l)

@patch
def linkify(self:ShowdocLookup, md, skipped=None):
    "Convert backtick code in `md` to doc links, except for symbols in `skipped`"
    in_fence=False
    lines = md.splitlines()
    for i,l in enumerate(lines):
        if l.startswith("```"): in_fence=not in_fence
        elif not l.startswith('    ') and not in_fence: lines[i] = self._link_line(l, L(skipped))
    return '\n'.join(lines)


