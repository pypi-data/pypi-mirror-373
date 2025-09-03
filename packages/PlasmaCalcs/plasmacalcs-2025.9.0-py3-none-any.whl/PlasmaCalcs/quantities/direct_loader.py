"""
File Purpose: directly loading data from source.
Hookups which read data from files will probably want DirectLoader as a parent.
"""
import os
import re

from .quantity_loader import QuantityLoader

from ..dimensions import SnapHaver, INPUT_SNAP
from ..errors import CacheNotApplicableError
from ..tools import (
    simple_property,
    ProgressUpdater,
    nbytes_path,
)

### --------------------- DirectLoader --------------------- ###

class DirectLoader(SnapHaver, QuantityLoader):
    '''manages loading data directly from source.

    Not intended for direct use; use a subclass instead.
    '''

    _IMPLIED_IF_NOTES_DIRNAME = '_sim'  # skip including in title if it is the dirname.

    title = simple_property('_title', setdefaultvia='_default_title',
            doc='''title to help distinguish this calculator from others.
            E.g. might want to add self.title to plots.
            Default: os.path.basename(self.dirname) if self.notes_dirname == self.dirname,
                else basename(self.notes_dirname) + basename(self.dirname),
                    except skip basename(self.dirname) if '_sim'.
            Examples of default behavior:
                '/path/to/dir0' --> 'dir0'.
                '/path/to/dir1/_sim' --> 'dir1'.
                '/path/to/dir1/_check0' --> 'dir1_check0'.''')
    def _default_title(self):
        '''default title for self. Here, just returns os.path.basename(self.notes_dirname)'''
        notesdir = self.notes_dirname
        dirname = self.dirname
        if notesdir == dirname:
            return os.path.basename(dirname)
        else:
            if os.path.basename(dirname) == self._IMPLIED_IF_NOTES_DIRNAME:
                return os.path.basename(notesdir) # don't need to show +'_sim' everywhere...
            else:
                return os.path.basename(notesdir) + os.path.basename(dirname)


    # # # FILE PATH INFO # # #
    dirname = simple_property('_dirname',
        doc='''abspath to directory containing data for this DirectLoader.''')
    @dirname.getter
    def dirname(self):
        try:
            return self._dirname
        except AttributeError:
            # make a more helpful error message in case subclass didn't implement dirname yet...:
            raise NotImplementedError(f'{type(self).__name__}.dirname')

    @property
    def nbytes(self):
        '''number of bytes across all files in self.dirname (and subdirectories)'''
        return nbytes_path(self.dirname)

    @property
    def nMbytes(self):
        '''number of megabytes across all files in self.dirname (and subdirectories).
        == self.nbytes / 1024**2
        '''
        return self.nbytes / 1024**2

    @property
    def nGbytes(self):
        '''number of gigabytes across all files in self.dirname (and subdirectories).
        == self.nbytes / 1024**3
        '''
        return self.nbytes / 1024**3


    _INDICATES_NOTES_DIRNAME = {r'_sim.*', r'_check.*'}

    notes_dirname = simple_property('_notes_dirname',
        doc=''''abspath to directory containing plots/notes for a DirectLoader.
        Might be the same directory as self.dirname, but doesn't need to be;
            can explicitly set self.notes_dirname = value, if desired.

        If not set, use notes_dirname == self.dirname,
            unless self.dirname ends with one of the self._INDICATES_NOTES_DIRNAME options.
            E.g. dirname == 'path/to/dir0' --> notes_dirname == 'path/to/dir0'.
            E.g. dirname == 'path/to/dir1/_sim' --> notes_dirname == 'path/to/dir1'.
            E.g. dirname == 'path/to/dir1/_check0' --> notes_dirname == 'path/to/dir1'.

        See also: self.unique_notes_dirname''')
    @notes_dirname.getter
    def notes_dirname(self):
        try:
            return self._notes_dirname
        except AttributeError:
            pass  # get the default.
        dirname = self.dirname
        base = os.path.basename(dirname)
        for pattern in self._INDICATES_NOTES_DIRNAME:
            if re.fullmatch(pattern, base):
                return os.path.dirname(dirname)
        else:  # match not found in for loop
            return dirname

    _INDICATES_UNIQUE_NOTES_DIRNAME = {'_sim'}

    unique_notes_dirname = simple_property('_unique_notes_dirname',
        doc='''abspath to directory containing plots/notes for a DirectLoader,
        probably not shared by DirectLoaders corresponding to any other data.
        (E.g. if

        Might be the same directory as self.dirname, but doesn't need to be;
            can explicitly set self.notes_dirname = value, if desired.

        If not set, use unique_notes_dirname = self.dirname,
            unless dirname ends with one of the self._INDICATES_UNIQUE_NOTES_DIRNAME options.
            E.g. dirname == 'path/to/dir0' --> unique_notes_dirname == 'path/to/dir0'.
            E.g. dirname == 'path/to/dir1/_sim' --> unique_notes_dirname == 'path/to/dir1'.
            E.g. dirname == 'path/to/dir1/_check0' --> unique_notes_dirname == 'path/to/dir1/_check0'.

        See also: self.notes_dirname''')
    @unique_notes_dirname.getter
    def unique_notes_dirname(self):
        try:
            return self._unique_notes_dirname
        except AttributeError:
            pass  # get the default.
        dirname = self.dirname
        base = os.path.basename(dirname)
        for pattern in self._INDICATES_UNIQUE_NOTES_DIRNAME:
            if re.fullmatch(pattern, base):
                return os.path.dirname(dirname)
        else:  # match not found in for loop
            return dirname

    @property
    def snapdir(self):
        '''directory containing the snapshot files.
        [Not implemented by DirectLoader; subclass should implement]
        '''
        raise NotImplementedError(f'{type(self).__name__}.snapdir')

    def snap_filepath(self, snap=None):
        '''convert snap to full file path for this snap.
        snap: None, str, int, or Snap
            the snapshot to load. if None, use self.snap.

        [Not implemented by DirectLoader; subclass should implement]
        '''
        raise NotImplementedError(f'{type(self).__name__}.snap_filepath()')


    # # # DIRECT LOADING-RELATED INFO # # #
    def directly_loadable_vars(self, snap=None):
        '''return tuple of directly loadable variables for this snap.
        snap: None, str, int, or Snap
            the snapshot to load. if None, use self.snap.

        [Not implemented by DirectLoader; subclass should implement]
        '''
        raise NotImplementedError(f'{type(self).__name__}.directly_loadable_vars()')


    # # # LOAD FROMFILE # # #
    # [EFF] whether to slice directly when loading from files, if using self.slices.
    _slice_maindims_in_load_direct = False
    # if True, MainDimensionsHaver logic expects DirectLoader subclass to handle slicing
    #   in its implementation of load_fromfile(). Using self._slice_maindims_numpy might help.

    def _var_for_load_fromfile(self, varname_internal):
        '''return var, suitably adjusted to pass into load_fromfile().
        Any adjustments are acceptable, as long as load_fromfile() understands the result.

        Example: might want to adjust var based on self._loading_{dim}, e.g.:
            if getattr(self, '_loading_component', False):
                return varname_internal + str(self.component)
            # e.g. 'b' --> 'bz', when loading across 'component' dim and self.component=='z'.

        The implementation here just returns varname_internal, unchanged.
        Subclass might want to override.
        '''
        return varname_internal

    def load_fromfile(self, fromfile_var, *args, **kw):
        '''load fromfile_var directly from file, returning raw data.
        E.g. result might be a numpy array with dims corresponding to self.maindims.

        (if called load_direct() via self.load_maindims_var_across_dims,
            then result should definitely have maindims dims.
            But it is also perfectly acceptable to have other dims.)

        (To hook these results into the main PlasmaCalcs architecture,
            define a BasesLoader inheriting from AllBasesLoader & SimpleDerivedLoader.
            See hookups subpackage for examples.)

        [Not implemented by DirectLoader; subclass should implement]
        '''
        raise LoadingNotImplementedError(f'{type(self).__name__}.load_fromfile({fromfile_var!r})')


    # # # LOAD INPUT # # #
    def load_input(self, fromfile_var, *args, **kw):
        '''load value of fromfile_var but when self.snap is INPUT_SNAP.
        [Not implemented for this subclass; loading direct when self.snap is INPUT_SNAP will crash]
        (optional; subclass can override in order to implement INPUT_SNAP functionality.
            see EppicCalculator.load_input() for an example.)
        '''
        errmsg = f'{type(self).__name__}.load_input() not implemented.'
        if self.snap is INPUT_SNAP:
            errmsg += ' (this causes load_direct() to fail when self.snap is INPUT_SNAP)'
        raise LoadingNotImplementedError(errmsg)


    # # # LOAD DIRECT # # #
    # [TODO][MV] consider moving the load_direct() implementation here to QuantityLoader instead.
    def load_direct(self, var, *args, **kw):
        '''load var "directly", either from a file, self.setvars, self.direct_overrides,
        or via self.load_input() if self.snap is INPUT_SNAP.

        Steps:
            1) attempt to get var from cache or self.setvars.
                [EFF] only tries this if we are not self._inside_quantity_loader_call_logic,
                to avoid redundant calls to self.get_set_or_cached.
            2) adjust var name if appropriate, via new_varname = self._var_for_load_fromfile(var).
                if new_varname != old varname, attempt to get new_varname from cache or setvars.
            3) if self.snap is INPUT_SNAP, return self.load_input(new_varname).
            4) super().load_direct(adjusted_var, *args, **kw),
                which will use self.load_fromfile(...) unless any overrides apply here.
        '''
        # (0) - bookkeeping; delete any previous value of self._load_direct_used_override
        try:
            del self._load_direct_used_override
        except AttributeError:
            pass   # that's fine. Just want to reset it before running this function.
        # (1)
        if not getattr(self, '_inside_quantity_loader_call_logic', False):
            try:
                result = self.get_set_or_cached(var)
            except CacheNotApplicableError:
                pass
            else:
                self._load_direct_used_override = var
                return result
        # (2)
        fromfile_var = self._var_for_load_fromfile(var)
        if fromfile_var != var:  # check setvars & cache
            try:
                result = self.get_set_or_cached(fromfile_var)
            except CacheNotApplicableError:
                pass
            else:
                self._load_direct_used_override = fromfile_var
                return result
        # (3)
        if self.snap is INPUT_SNAP:
            return self.load_input(fromfile_var, *args, **kw)
        # (4)
        return super().load_direct(fromfile_var, *args, **kw)


    # # # KNOWN VARS # # #
    @known_pattern(r'load_(.+)', dims=['snap'])  # load_{var} pattern
    def get_load_direct_maindims_var(self, var, *, _match=None):
        '''load maindims var directly (from files, cache, or setvars; see self.load_direct()).
        var should be name of a directly loadable var (see self.directly_loadable_vars()).
        Output always uses 'raw' units, regardless of self.units,
            but coords are in self.coords_units (default: same as self.units).
        '''
        # [TODO] doesn't currently interact well with other patterns, but it should...
        #       (workaround: use parenthesis e.g. load_tg/m fails but (load_tg)/m is fine)
        here, = _match.groups()
        with self.using(coords_units=self.coords_units_explicit, units='raw'):
            result = self.load_maindims_var_across_dims(here, dims=['snap'])
        return result


    # # # CONVENIENT MISC. METHODS (subclass doesn't need to override) # # #
    def _check_files_readable(self):
        '''check that all files in self.dirname are readable (checks recursively inside directories too).
        return number of files checked, number of files readable, and number of files not readable.

        print exceptions along the way if any files are not readable!
        '''
        total = len([f for _, _, files in os.walk(self.dirname) for f in files])
        successes = 0
        failures = 0
        i = 0
        updater = ProgressUpdater(1, wait=True)  # at most 1 update per second; wait before first printout.
        for dirpath, dirnames, filenames in os.walk(self.dirname):
            for filename in filenames:
                i += 1
                updater.print(f"Checking files... at {i} out of {total}")
                filepath = os.path.join(dirpath, filename)
                try:
                    with open(filepath, 'rb') as f:  # read 1 bit of file to check if it is readable.
                        f.read(1)
                except Exception as e:
                    print(f'Error reading {filepath}: {e}')
                    failures += 1
                else:
                    successes += 1
        updater.finalize(f"Checking files")
        return successes + failures, successes, failures
