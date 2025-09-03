"""
File Purpose: making eppic.i file based on an EppicInstabilityCalculator.
E.g., "make eppic.i file using safe simulation size values, given these physical parameters"
"""
import os
import re

import xarray as xr

from ..eppic_calculator import EppicCalculator
from ....dimensions import XYZ
from ....errors import DimensionalityError, FileContentsMissingError
from ....quantities import QuantityLoader
from ....tools import (
    UNSET,
    is_integer,
    code_snapshot_info,
    xarray_nondim_coords,
)
from ....defaults import DEFAULTS


### --------------------- Helper functions --------------------- ###

def eppici_dict(ds, *, item=UNSET):
    '''return a dict to use for making an eppic.i file.
    result is like: {
        paramA: valueA,
        paramB: valueB,
        ...  # and similarly, for all global inputs
        0: {
            param0a: value0a,
            param0b: value0b,
            ...  # and similarly, for all dist0 values
        },
        1: {...},
        ...,  # and similarly, for all dists
        N: {...}
    }

    ds: Dataset
        dataset with inputs for eppic.i file.
        data vars will be treated as dist-specific if they contain '{N}' (including curly brackets.)
        internally expands data vars with '{N}' into a value for each dist.
        internally expands data vars with '{x}' into a value for each vector component (x,y,z).
        (if data vars with '{N}' or '{x}' don't vary across 'fluid' or 'component',
            assume that var should have the same value for every fluid or component.)
    item: UNSET or bool
        whether to convert all values to items (i.e., not DataArrays anymore).
        UNSET --> True if dataset dims are only 'fluid' and/or 'component', else False.
    '''
    result = {}

    if item is UNSET:
        item = (set(ds.dims) <= {'fluid', 'component'})
    if item and set(ds.dims) > {'fluid', 'component'}:
        ds_extra_dims = set(ds.dims) - {'fluid', 'component'}
        raise DimensionalityError(f'ds with unrecognized dims when item=True: {ds_extra_dims}')
    to_handle = [(k, v) for k, v in ds.items()]
    # expand '{x}' into components (while maintaining order):
    components = XYZ
    new_to_handle = []
    for var, value in to_handle:
        if '{x}' in var:
            for i, x in enumerate(components):
                vali = value.isel(component=i) if 'component' in value.dims else value
                newvar = var.replace('{x}', str(x))
                new_to_handle.append((newvar, vali))
        else:
            new_to_handle.append((var, value))
    to_handle = new_to_handle
    # put stuff without '{N}' into global params:
    new_to_handle = []
    for var, value in to_handle:
        if '{N}' in var:
            new_to_handle.append((var, value))
            continue
        if item:
            value = value.item()
        result[var] = value
    to_handle = new_to_handle
    # expand '{N}' into fluids, and put into dist params:
    fluids = list(ds['fluid'].values)
    for var, value in to_handle:
        assert '{N}' in var, 'expect all vars to have {N} at this point...'
        for i, f in enumerate(fluids):
            vali = value.isel(fluid=i) if 'fluid' in value.dims else value
            newvar = var.replace('{N}', str(i))
            if item:
                vali = vali.item()
            result.setdefault(i, {})[newvar] = vali
    # done!
    return result

def eppici(ds, dst=None, *,
           meta=True, title=None, coords=True, infos=None,
           TAB=DEFAULTS.TAB, overwrite=False):
    r'''return string suitable for use as an entire eppic.i file.
    (or, return abspath to dst, if wrote to file.)

    ds: Dataset
        dataset with inputs to eppic.i file.
        Must be suitable for being passed to eppici_dict.
        E.g., can use result of EppicInstabilityCalculator('eppici_all').
    dst: None or str
        if provided, write result to the indicated file,
            os.makedirs(exist_ok=True) as needed.
            and return abspath to dst, instead of the usual eppici() result.
    meta: bool
        whether to include metadata near the beginning, as comments.
        E.g., includes datetime when the str was created.
    title: None or str
        if provided, put title=title near the beginning.
    coords: bool, dict, DataArray, or Dataset
        coord info to put after title,
            putting '_coord_' before each key name (to ensure no overlap with eppic inputs.)
            Notes:
                - each coord should probably be a scalar.
                - if any coord has ndim and ndim==0, will be converted to item().
                - string coord will be string (wrapped by single quotes) in eppic.i file.
        True --> use ds.
        DataArray or Dataset --> use coords.nondim_coords(scalars_only=True, item=True).
        Example:
            coords={'kappae': 10.0, 'ngrid_index': 3, 'nice': np.array(7)}
            --> '_coord_kappae = 10.0\n_coord_ngrid_index = 3\n_coord_nice = 7'
    infos: None or dict
        if provided, after coords put this info,
            putting '_info_' before each key name (to ensure no overlap with eppic inputs.)
            Notes:
                - each value should probably be a scalar.
                - if any value has ndim and ndim==0, will be converted to item().
                - string coord will be string (wrapped by single quotes) in eppic.i file.
    TAB: str
        start parameter-defining lines with TAB, to make result prettier.
        (comment lines will not start with tab)
    overwrite: bool
        if dst provided, tells whether to overwrite existing files.
        default False --> by default, never overwrite files.
    '''
    edict = eppici_dict(ds, item=True)  # must use item=True if writing to string!
    lines = []
    if meta:
        # PlasmaCalcs meta
        mstr = '; Created by PlasmaCalcs'
        info = code_snapshot_info()
        if 'pc__version__' in info:
            mstr = mstr + f" version {info['pc__version__']}"
        if 'pc__commit_hash' in info:
            mstr = mstr + f" (commit {info['pc__commit_hash']})"
        if 'datetime' in info:
            mstr = mstr + f"\n; {TAB}at time={info['datetime']}"
        lines.append(mstr)
        # instructions for where to learn meanings of parameters
        lines.append('; For parameter meanings, see src/eppic.h, from gitlab.com/oppenheim/eppic')
        # [TODO] other meta, e.g. values of safety factors,
        #  or other convenient parameters to know at a glance, e.g. temperatures?
    if title is not None:
        lines.append('')
        lines.append(f"title = '{title}'")
    if coords == True:
        coords = ds
    if isinstance(coords, (xr.DataArray, xr.Dataset)):
        coords = xarray_nondim_coords(coords, scalars_only=True, item=True)
    if coords != False:
        lines.append('')
        lines.append('; Coords (ignored by eppic. For bookkeeping purposes.)')
        for key, value in coords.items():
            try:
                value = f'{value:.4g}'
            except (ValueError, TypeError):
                value = f"'{value}'" if isinstance(value, str) else str(value)
            lines.append(f"{TAB}_coord_{key} = {value}")
    if infos is not None:
        lines.append('')
        lines.append('; Infos (ignored by eppic. For bookkeeping purposes.)')
        for key, value in infos.items():
            if hasattr(value, 'ndim') and value.ndim == 0: value = value.item()
            try:
                value = f'{value:.4g}'
            except (ValueError, TypeError):
                value = f"'{value}'" if isinstance(value, str) else str(value)
            lines.append(f"{TAB}_info_{key} = {value}")
    # global parameters:
    lines.append('')
    lines.append('')
    lines.append('; Global parameters')
    for var, value in list(edict.items()):
        if isinstance(var, int):  # dist-info skipped for now
            continue
        if hasattr(value, 'ndim') and value.ndim == 0: value = value.item()
        if not is_integer(value):  # never convert ints to sci notation for eppic.i
            try:
                value = f'{value:.7g}'  # 7 sigfigs should be plenty.
            except (ValueError, TypeError):
                pass  # it's fine, just use default string conversion then.
        lines.append(f'{TAB}{var} = {value}')
        del edict[var]
    # fluid-specific parameters:
    lines.append('')
    lines.append('')
    lines.append('; Fluid parameters')
    lines.append(f'{TAB}ndist = {len(ds["fluid"])}')
    for i, fdict in edict.items():
        lines.append('')
        lines.append('')
        fname = str(ds['fluid'].isel(fluid=i).item())
        lines.append(f'; ----- {fname} -----')
        lines.append(f'{TAB}dist = {i}')
        for var, value in fdict.items():
            if hasattr(value, 'ndim') and value.ndim == 0: value = value.item()
            if not is_integer(value):  # never convert ints to sci notation for eppic.i
                try:
                    value = f'{value:.7g}'  # 7 sigfigs should be plenty.
                except (ValueError, TypeError):
                    pass  # it's fine, just use default string conversion then.
            lines.append(f'{TAB}{var} = {value}')
    lines.append('')
    result = '\n'.join(lines)
    # write to file, if relevant.
    if dst is None:
        return result
    else:
        if os.path.exists(dst) and not overwrite:
            raise FileExistsError(f'{dst!r}, when overwrite=False')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        with open(dst, 'w' if overwrite else 'x') as f:
            f.write(result)
        return os.path.abspath(dst)


### --------------------- EppiciMaker --------------------- ###

class EppiciMaker(QuantityLoader):
    '''makes eppic.i input file based on an EppicInstabilityCalculator.
    E.g., "make eppic.i file using safe simulation size values, given these physical parameters".
    For details on inputs, see EppicGlobInputsLoader and EppicDistInputsLoader.
    '''

    # # # RENAMING DIST & GLOB INPUTS TO EPPICI NAMES # # #

    @known_var(deps=['dist_inputs'])
    def get_eppici_dist(self):
        '''Dataset of dist-related input values which go to eppic.i, using eppic.i datavar names.

        Similar to self('dist_inputs') however vars have been renamed to eppic.i names,
            with {x} indicating "replace with component (x, y, or z)",
            and {N} indicating "replace with fluid index".
        Still using PlasmaCalcs dimensions.
            e.g. var='pv{x}min{N}' (keeping curly braces!) varies across 'component' and 'fluid'.
        
        Result keys determined by renaming dist_inputs keys via self.DIST_INPUTS.
            (dict-valued keys there are expanded here into multiple keys)

        if self.dspace_mode doesn't start with 'safe_', use 'safe_{mode}' instead.
            (this affects, e.g., safe_pow2_subcycle)
        '''
        result = self('dist_inputs')
        return self._handle_renaming_ds(result, self.DIST_INPUTS)

    @known_var(deps=['glob_inputs'])
    def get_eppici_glob(self):
        '''Dataset of global input values which go to eppic.i, using eppic.i datavar names.
        Similar to self('glob_inputs') however vars have been renamed to eppic.i names,
            with {x} indicating "replace with component (x, y, or z)".
        Still using PlasmaCalcs dimensions.
            e.g. var='E{x}0_external' (keeping curly braces!) varies across 'component'.
        internally uses self.dspace_mode = self.safe_dspace_mode.
        Result keys are determined by renaming glob_inputs keys via self.GLOB_INPUTS.
            (dict-valued keys there are expanded here into multiple keys)
        '''
        result = self('glob_inputs')
        return self._handle_renaming_ds(result, self.GLOB_INPUTS)

    @staticmethod
    def _renaming_instructions(renaming):
        '''flatten dict like GLOB_INPUTS into a single dict, for renaming.
        Result order is in order used by renaming, with dict values expanded in-place.
        '''
        result = {}
        for var, name in list(renaming.items()):
            if isinstance(name, dict):
                for subvar, subname in name.items():
                    result[subvar] = subname
            else:
                result[var] = name
        return result

    def _handle_renaming_ds(self, ds, renaming):
        '''handle renaming the vars in ds according to a dict like GLOB_INPUTS.
        Result order is in order implied by renaming, when dict values expanded in-place.
        '''
        renaming = self._renaming_instructions(renaming)
        result = ds.rename(renaming)
        # style: sort data vars by order implied by renaming.
        newnames = list(renaming.values())
        assert set(result.data_vars) == set(newnames), 'unexpected var in result...'
        return result[newnames]


    # # # COMBINING DIST & GLOB INPUTS # # #

    @known_var(deps=['glob_inputs', 'dist_inputs'])
    def get_all_inputs(self):
        '''Dataset of all input values which go to eppic.i, here using PlasmaCalcs datavar names.

        Named & dimensioned here with PlasmaCalcs conventions,
            e.g. uses 'E_un0' which varies across 'component' dim,
            instead of labeling Ex0_external, Ey0_external, Ez0_external like in eppic.i.
        Result has all keys from dist_inputs and glob_inputs;
            see self.help('dist_inputs') and self.help('glob_inputs') for more details.

        if self.dspace_mode doesn't start with 'safe_', use 'safe_{mode}' instead.
            (this affects, e.g., safe_pow2_subcycle)
        '''
        return self(['glob_inputs', 'dist_inputs'], dspace_mode=self.safe_dspace_mode)

    @known_var(deps=['eppici_glob', 'eppici_dist'])
    def get_eppici_all(self):
        '''Dataset of all input values which go to eppic.i, using eppic.i datavar names.

        Similar to self('all_inputs') however vars have been renamed to eppic.i names,
            with {x} indicating "replace with component (x, y, or z)",
            and {N} indicating "replace with fluid index".
        Still using PlasmaCalcs dimensions.
            e.g. var='pv{x}min{N}' (keeping curly braces!) varies across 'component' and 'fluid'.
        
        Result keys are determined by renaming all_inputs keys via self.DIST_INPUTS and self.GLOB_INPUTS.
            (dict-valued keys there are expanded here into multiple keys)

        if self.dspace_mode doesn't start with 'safe_', use 'safe_{mode}' instead.
            (this affects, e.g., safe_pow2_subcycle)
        '''
        return self(['eppici_glob', 'eppici_dist'])


    # # # MAKING EPPIC.I FILE # # #

    def eppici_dict(self, ds=None, *, item=UNSET):
        '''return a dict to use for making an eppic.i file.
        result has global params as keys,
        also fluid indexes (e.g. 0, 1, 2) as keys, with dict values telling fluid params.

        ds: None or Dataset
            dataset with inputs for eppic.i file.
            None --> self('eppici_all').
        item: UNSET or bool
            whether to convert all values to items (i.e., not DataArrays anymore).
            UNSET --> True if dataset dims are only 'fluid' and/or 'component', else False.
        '''
        if ds is None:
            ds = self('eppici_all')
        return eppici_dict(ds, item=item)

    def eppici(self, dst=None, *, ds=None, title=None, coords=True,
               infos=None, safety_infos=True, safe_sim_size_infos=True,
               makeslurm='attempt', **kw_eppici):
        '''return string for new eppic.i file contents, or write to dst and return abspath.
        uses 'safe' values from self to decide params: ds=self('eppici_all') if not provided.
        
        dst: None or str
            str --> filepath for where to write result; os.makedirs(exist_ok=True) as needed.
                    And, this function returns abspath to dst.
            None --> do not write to any file.
                    And, this function returns string for eppic.i contents.
        ds: None or Dataset
            dataset with inputs to eppic.i file. Passed to eppici_dict.
            None --> uses self('eppici_all').
        title: None or str
            if provided, put title=title near the beginning.
        coords: bool, dict, DataArray, or Dataset
            coord info to put after title, replacing keys with '_coord_{key}'.
            True --> infer coords from scalar nondim_coords of ds.
        infos: None or dict
            additional infos to put after coords, replacing keys with '_info_{key}'.
        safety_infos: bool
            whether to include self('safety_details') values, replacing keys with '_info_{key}'.
        safe_sim_size_infos: bool
            whether to include self('safe_sim_size') values, replacing keys with '_info_{key}'.
        makeslurm: 'attempt', True, False, or dict
            whether to call self.makeslurm() after making eppic.i file (if dst provided).
            'attempt' --> try it, but skip if can't find slurm template file.
            True --> call self.makeslurm(). If it fails, crash.
            False --> don't self.makeslurm().
            dict --> dict of kwargs to pass to self.makeslurm().
        overwrite: bool
            if dst provided, tells whether to overwrite existing files.
            default False --> by default, never overwrite files.

        additional kwargs go to the eppici helper function,
            from hookups/eppic/eppic_instability_calculator/eppici_maker.py
        '''
        if ds is None:
            ds = self('eppici_all')
        if safety_infos or safe_sim_size_infos:
            infos = {} if infos is None else {**infos}
        if safety_infos:
            infos.update(self('safety_details'))
        if safe_sim_size_infos:
            infos.update(self('safe_sim_size'))
        result = eppici(ds, dst=dst, title=title, coords=coords, infos=infos, **kw_eppici)
        if dst is None or makeslurm == False:
            return result
        else:
            eppici_path = result
            if makeslurm == True:
                makeslurm = {}
            if makeslurm == 'attempt':
                try:
                    self.makeslurm(eppici_path)
                except FileNotFoundError:
                    pass
            else:
                self.makeslurm(eppici_path, **makeslurm)
            return result

    def _slurm_template_path(self, eppici, template=None):
        '''return path to template slurm file. If not provided, infer it:
            (1) ec = EppicCalculator.from_here(eppici)  # eppici is filepath
            (2) look in ec.notes_dirname for slurm file with appropriate basename
                ("appropriate" means .i --> .slurm. E.g. 'eppic_0.i' --> 'eppic_0.slurm')
            (3) look in os.path.dirname(ec.notes_dirname) for slurm file like that^
            (4) give up, crash with FileNotFoundError
        If provided, check to make sure it exists, then return abspath to it.
        '''
        if template is not None:
            template = os.path.abspath(template)
            if not os.path.exists(template):
                raise FileNotFoundError(f'slurm template not found: {template!r}')
            return template
        # else
        eppici = os.path.abspath(eppici)  # <-- ensures result will be abspath
        ec = EppicCalculator.from_here(eppici, u_t=1)  # u_t=1 prevents pic ambiguous unit crash.
        ec_notes = ec.notes_dirname
        basename = os.path.splitext(os.path.basename(eppici))[0] + '.slurm'
        template2 = os.path.join(ec_notes, basename)
        if os.path.exists(template2):
            return template2
        template3 = os.path.join(os.path.dirname(ec_notes), basename)
        if os.path.exists(template3):
            return template3
        errmsg = f'slurm template for{eppici!r}.\nChecked {template2!r}\nand {template3!r}'
        raise FileNotFoundError(errmsg)

    def makeslurm(self, eppici, template=None, *, dst=UNSET):
        '''write a slurm file using details from eppic.i file as input.

        Expects template file to have lines like:
            #SBATCH -N 8     # possibly with comments too.
            #SBATCH --tasks-per-node=56
            #SBATCH -t 01:00:00
        which specify number of nodes, tasks per node, and wall clock time requested.
        These will be replaced by params from eppici file:
            _info_n_nodes,
            _info_tasks_per_node,
            _info_safe_runtime_HMS.
        ([TODO] more flexible slurm options, e.g. specifying n_processors instead of n_nodes.)

        eppici: str
            path to eppic.i file.
        template: None or str
            path to template slurm file.
            None --> infer from eppici path. Check in default notes_dirname associated with eppici,
                    for file with similar basename but .slurm (e.g. 'eppic_0.i' --> 'eppic_0.slurm').
                    If that doesn't exist, check in dirname of notes_dirname.
                    If that also doesn't exist, crash.
        dst: UNSET, None, or str
            name for the resulting slurm file.
            UNSET --> same path as eppici path, but using .slurm extension instead.
            None --> return str of slurm contents instead of making slurmfile.
            str --> write to that path, os.makedirs(exist_ok=True) as needed.

        returns abspath to created slurmfile. (unless dst=None; see above for details.)
        '''
        if dst is UNSET:
            dst = os.path.splitext(eppici)[0] + '.slurm'
        template = self._slurm_template_path(eppici, template=template)
        ec = EppicCalculator.from_here(eppici, u_t=1)  # u_t=1 prevents pic ambiguous unit crash.
        slurmkeys = ['_info_n_nodes', '_info_tasks_per_node', '_info_safe_runtime_HMS']
        _missing = [k for k in slurmkeys if k not in ec.input_deck.keys()]
        if len(_missing) > 0:
            errmsg = f'expected all keys {slurmkeys} in eppic.i file; missing {_missing}'
            raise FileContentsMissingError(errmsg)
        slurmvals = {k: ec.input_deck[k] for k in slurmkeys}
        with open(template, 'r') as f:
            slurmlines = f.readlines()
        to_match = {
            '_info_n_nodes': r'(#SBATCH)(\s+)(-N)(\s+)(\d+)(\s*)(#.*)?',
            '_info_tasks_per_node': r'(#SBATCH)(\s+)(--tasks-per-node=)()(\d+)(\s*)(#.*)?',
            '_info_safe_runtime_HMS': r'(#SBATCH)(\s+)(-t)(\s+)(\d+:\d+:\d+)(\s*)(#.*)?',
        }
        for i, line in enumerate(slurmlines):
            for key, pattern in to_match.items():
                match = re.match(pattern, line)
                if match is not None:
                    sbatch, space0, option, space1, value, space2, comment = match.groups()
                    slurmlines[i] = f'{sbatch}{space0}{option}{space1}{slurmvals[key]}{space2}{comment}\n'
                    to_match.pop(key)
                    break
        if len(to_match) > 0:
            errmsg = f'template slurm file missing lines like: {list(to_match.values())}'
            raise FileContentsMissingError(errmsg)
        result = ''.join(slurmlines)
        if dst is None:
            return result
        else:
            with open(dst, 'w') as f:
                f.write(result)
            return os.path.abspath(dst)
