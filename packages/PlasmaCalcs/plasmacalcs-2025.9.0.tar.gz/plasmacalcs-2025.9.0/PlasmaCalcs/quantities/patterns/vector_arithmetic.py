"""
File Purpose: arithmetic for vectors or components.

[EFF] the idea for efficiency in vector methods
    is that it's more efficient to get the full vector instead of one component at a time,
    if you'll be using more than one component of it.
    For example, if you use electron momentum equation to solve for electric field,
        then 'E' is complicated to calculate, and involves some scalar factors.
        If you get 'E_x' then 'E_y', you'll need to recalculate those factors each time.
        But if you get 'E_xy', then you only need to calculate those factors once
            (assuming that get_E is written appropriately, with this in mind).

[TODO] compatibility with rotations (when implementing rotations):
    infer X,Y,Z from 'component' dimension of array, instead of imposing XYZ.
    E.g. if using a rotated coordinate system xprime, yprime, zprime,
        then infer X,Y,Z as xprime,yprime,zprime. And crash if mixing coordinate systems...?
"""
import numpy as np
import xarray as xr

from ..quantity_loader import QuantityLoader
from ...dimensions import XYZ, YZ_FROM_X, XHAT, YHAT, ZHAT
from ...errors import QuantCalcError
from ...tools import (
    UNSET,
    alias,
    take_along_dimension, join_along_dimension, xarray_assign, pcAccessor,
    xarray_sel,
    xarray_map,
)

_ANYVAR = r'.*?[^_]+?'  # lazy match (as few characters as possible), anything not ending with '_'
        # could use 'f' strings below to plug in ANYVAR.
        # Instead, copy-pasted the string, to make it easier to search the codebase for these patterns,
        # and to avoid complications with using the '{' and '}' elsewhere in the string.

VECTOR_ZERO = xr.DataArray([0,0,0], coords={'component': XYZ})


### --------------------- Vector Arithmetic Helper Methods --------------------- ###
# note - these are also provided as staticmethods in VectorArithmeticLoader.
#    thus, e.g., can use PlasmaCalculator.dot_product, if you prefer.
# also note - PlasmaCalculator methods using these functions should prefer the syntax self.dot_product,
#    instead of just using dot_product directly, so that subclasses can overwrite these methods if desired.

@pcAccessor.register('dot_product', aliases=['dot'])
def dot_product(A, B):
    '''return dot product of vectors A and B, assuming vector components along the dimension 'component'.'''
    # note: need to ensure to only sum across matching components
    #    (can't just take_along_dimension('component') without checking if components match)
    # also note: (A * B).sum('component') fails when component is a non-dimension coordinate,
    #    e.g. when there is only 1 component.
    A_dim = 'component' in A.dims
    B_dim = 'component' in B.dims
    # case: both have 'component' dimension. Easy - let xarray handle all the bookkeeping.
    if A_dim and B_dim:
        result = A * B
        return result.sum('component')
    # case: exactly one has 'component' dimension but the other does not.
    elif A_dim or B_dim:
        if A_dim:
            a, b = A, B
        else:
            a, b = B, A
        # now, 'a' has 'component' dimension while 'b' does not.
        if b.coords['component'].size != 1:
            raise NotImplementedError('dot_product, when component is a non-dimension coordinate with size > 1')
        idx = np.nonzero(a.coords['component'].values == b.coords['component'].values)[0]
        if len(idx) == 0:  # no matching components. Result is 0.
            return xr.zeros_like(b).drop_vars('component')  # drop_vars --> result has no 'component' coord.
        else:
            assert len(idx) == 1
            i = idx[0]
            result = a.isel(component=i) * b
            return result.drop_vars('component')  # drop_vars --> result has no 'component' coord.
    # case: A and B both do not have 'component' dimension.
    else:
        # first ensure A and B have the same 'component' coordinate, then it's easy, just multiply them.
        if not (A.coords['component'].size == 1 == B.coords['component'].size):
            raise NotImplementedError('dot_product, when component is a non-dimension coordinate with size > 1')
        A_comps = A.coords['component'].values
        B_comps = B.coords['component'].values
        if np.all(A_comps == B_comps):
            result = A * B
            return result.drop_vars('component')  # drop_vars --> result has no 'component' coord.
        else:
            return xr.zeros_like(A).drop_vars('component')  # drop_vars --> result has no 'component' coord.
    assert False, "if reached this line, made coding mistake."

@pcAccessor.register('magnitude', aliases=['mag', 'mod'])
def magnitude(A, *, squared=False):
    '''return vector magnitude of A, assuming vector components along the dimension 'component'.
    squared: bool, default False
        if True, return |A|**2 instead of |A|.
        [EFF] to get |A|**2, when |A| is not needed,
            magnitude(A, squared=True) is more efficient than magnitude(A)**2
    '''
    result = dot_product(A, A)
    return result if squared else result**0.5

@pcAccessor.register('unit_vector', aliases=['hat', 'dir', 'direction'])
def unit_vector(A):
    '''return a unit vector in the direction of A. Equivalent: A / |A|'''
    return A / magnitude(A)

@pcAccessor.register('angle_xy', aliases=['ang', 'hat2ang', 'angxy', 'dirxy'])
def angle_xy(A):
    '''return angle between +xhat and A, in the xy plane, in radians.
    A should be a DataArray (or Dataset) with x and y in 'component' dimension.
    A can be any vector (does not need to be a unit vector, but it can be.)
    '''
    x = xarray_sel(A, component='x', drop=True)
    y = xarray_sel(A, component='y', drop=True)
    return np.arctan2(y, x)

@pcAccessor.register('angle_xy_to_hat', aliases=['ang2hat', 'angxy2hat', 'dirxy2hat'])
def angle_xy_to_hat(A):
    '''return unit vector u, given angle [radians] between +xhat and u in the xy plane.
    Equivalent: cos(A) * xhat + sin(A) * yhat.
    '''
    return np.cos(A) * XHAT + np.sin(A) * YHAT

def rmscomps(A):
    '''return root mean squared of components of A.
    E.g., rmscomps(A) --> sqrt((Ax^2 + Ay^2 + Az^2) / 3), if A has 3 components.
    '''
    num_comps = A.coords['component'].size  # number of components
    mag2 = magnitude(A, squared=True)
    return np.sqrt(mag2 / num_comps)

@pcAccessor.register
def cross_component(A, B, x, *, yz=None, missing_ok=False):
    '''return x component of A cross B, given A and B which have values for y and z 'component'.

    x: int, str, or Component
        tells component (of result) to get. if int or str, use XYZ.get(x)
    A, B: xarray.DataArray
        vectors to take cross product of.
        must include 'component' dimension including coordinates y and z.
    yz: None or iterable of two (int, str, or Component) objects
        the other two components; (x,y,z) should form a right-handed coordinate system.
        if not provided, infer from x.
    missing_ok: bool, default False
        whether it is okay for 'component' dimension to be missing y or z components, of A or B.
        if True, treat any missing components as 0.
    '''
    if yz is None: yz = YZ_FROM_X[x]
    x = XYZ.get(x)
    default = 0 if missing_ok else UNSET
    Ay, Az = take_along_dimension('component', A, yz, default=default)
    By, Bz = take_along_dimension('component', B, yz, default=default)
    return xarray_assign(Ay * Bz - Az * By, coords={'component': x})

@pcAccessor.register('cross_product', aliases=['cross'])
def cross_product(A, B, *, components=None):
    '''return cross product of vectors A and B, along dimension 'component'.
    If A or B missing any components, treat them as 0.

    components: None or iterable of component specifiers (int, str, or Component)
        tells which components to get.
        None --> get all components (XYZ)
        e.g., (0, 'z') --> get component 0 and component 'z', i.e. X and Z.
    '''
    if components is None:
        components = XYZ
    result = [cross_component(A, B, x, missing_ok=True) for x in components]
    return join_along_dimension('component', result)

def take_perp_to(B, A):
    '''return the component of A perpendicular to B. Equivalent: A - (A dot Bhat) Bhat.
    Note that B is the first argument.
    '''
    Bhat = B / magnitude(B)
    return A - dot_product(A, Bhat) * Bhat

def take_parallel_to(B, A):
    '''return the component of A parallel to B. Equivalent: (A dot Bhat) Bhat.
    Note that B is the first argument.
    '''
    Bhat = B / magnitude(B)
    return dot_product(A, Bhat) * Bhat

# # rephrase take_perp_to and take_parallel_to for xarray accessor (e.g. arr.pc.perp(B)). # #
@pcAccessor.register
def perp(A, B):
    '''return the component of A perpendicular to B. Equivalent: A - (A dot Bhat) Bhat.'''
    return take_perp_to(B, A)

@pcAccessor.register
def parallel(A, B):
    '''return the component of A parallel to B. Equivalent: (A dot Bhat) Bhat.'''
    return take_parallel_to(B, A)

@pcAccessor.register('perpmod', aliases=['perpmag'])
def perpmod(A, B):
    '''return the magnitude of the component of A perpendicular to B. Equivalent: |A - (A dot Bhat) Bhat|'''
    return magnitude(perp(A, B))

@pcAccessor.register('parmod', aliases=['parmag'])
def parmod(A, B):
    '''return the magnitude of the component of A parallel to B. Equivalent: |(A dot Bhat) Bhat|'''
    return magnitude(dot_product(A, unit_vector(B)))


### --------------------- Vector Arithmetic Loader --------------------- ###

class VectorArithmeticLoader(QuantityLoader):
    '''arithmetic for vectors or components.
    E.g. var_x --> x component of var, i.e. self(var)[..., 0]

    for vector derivatives, see VectorDerivativeLoader.
    '''
    # {var}_{x}; x from characters in 'xyz'; 1 <= len(x) <= 3
    @known_pattern(r'(.*?[^_]+?)_([xyz]{1,3})', deps=[0], ignores_dims=['component'])
    def get_xyz(self, var, *, _match=None):
        '''x, y, and/or z components of var.'''
        base, components = _match.groups()
        cc = [x for x in components] if len(components)>1 else components
        with self.using(component=cc):
            return self(base)

    # # # DOT & CROSS (& magnitude) # # #
    # {var0}_dot_{var1}; optional "__{axes}"
    @known_pattern(r'(.+)_dot_(.+?)(__[xyz]{1,3})?', deps=[0,1], ignores_dims=['component'])
    def get_dot(self, var, *, _match=None, _val0=None, _val1=None, **_known_vals):
        '''dot product. {A}_dot_{B} --> A dot B.
        if component(s) is provided, only include that component(s) during the calculation.
            e.g. A_dot_B__xy --> Ax * Bx + Ay * By.

        [EFF] can provide known vals for A or B, to avoid recalculating them. (include leading underscores.)
            e.g. self('u_dot_E', _u=u, _E=E) --> u dot E, using u and E which are already known.
            if providing value as None, it will be treated as if value not provided.
            CAUTION: Not tested when simultaneously providing components such as A_dot_B__xy.
            can alternatively provide _val0 for A and/or _val1 for B.
        ''' 
        A, B, components = _match.groups()
        Aval = self._provided_val(A, _val0, _known_vals)
        Bval = self._provided_val(B, _val1, _known_vals)
        components = 'xyz' if (components is None) else components[len('__'):]  # remove '__'. e.g. '__x' --> 'x'
        with self.using(component=tuple(components)):
            if Aval is None:
                Aval = self(A)
            if Bval is None:
                Bval = self(B) if A != B else Aval  # [EFF] if A == B, only calculate once.
        return self.dot_product(Aval, Bval)  # use self.dot_product in case subclass overwrites.

    dot_product = staticmethod(dot_product)
    dot = alias('dot_product')

    # mod_{var} or mag_{var}; optional "__{axes}"
    @known_pattern(r'(mod|mag)_(.+?)(__[xyz]{1,3})?', deps=[1], ignores_dims=['component'])
    def get_mod(self, var, *, _match=None, _val0=None, **_known_vals):
        '''magnitude of var. mod_{A} --> |A|.  == sqrt(A dot A) == sqrt(Ax^2 + Ay^2 + Az^2).
        alias: 'mag_{A}' is equivalent to 'mod_{A}'
        if component(s) is provided, only include that component(s) during the calculation.
            e.g. mod_A__xy --> sqrt(Ax^2 + Ay^2).

        [EFF] can provide known vals for {var} to avoid recalculating it. (include leading underscore.)
            e.g. self('mod_E', _E=E) --> |E|, using E which is already known.
            CAUTION: Not tested when simultaneously providing components such as mod_A__xy.
            can alternatively provide _val0 for A.
        '''
        _alias, A, components = _match.groups()   # _alias is 'mod' or 'mag'
        if components is None: components = ''
        vdotv = self(f'{A}_dot_{A}{components}', _val0=_val0, _val1=_val0, **_known_vals)
        return vdotv ** 0.5

    magnitude = staticmethod(magnitude)

    # mod2_{var} or mag2_{var}; optional "__{axes}"
    @known_pattern(r'(mod2|mag2)_(.+?)(__[xyz]{1,3})?', deps=[1], ignores_dims=['component'])
    def get_mod2(self, var, *, _match=None, _val0=None, **_known_vals):
        '''magnitude squared of var. mod2_{A} --> |A|^2.  == A dot A == Ax^2 + Ay^2 + Az^2.
        alias: 'mag2_{A}' is equivalent to 'mod2_{A}'
        if component(s) is provided, only include that component(s) during the calculation.
            e.g. mod2_A__xy --> Ax^2 + Ay^2.

        [EFF] can provide known vals for {var} to avoid recalculating it. (include leading underscore.)
            e.g. self('mod2_E', _E=E) --> |E|**2, using E which is already known.
            CAUTION: Not tested when simultaneously providing components such as mod_A__xy.
            can alternatively provide _val0 for A.
        '''
        _alias, A, components = _match.groups()  # _alias is 'mod2' or 'mag2'
        if components is None: components = ''
        return self(f'{A}_dot_{A}{components}', _val0=_val0, _val1=_val0, **_known_vals)

    # rmscomps_{var}
    @known_pattern(r'rmscomps_(.+)', deps=[0], reduces_dims=['component'])
    def get_rmscomps(self, var, *, _match=None):
        '''root mean squared of components.
        E.g., rmscomps_{A} --> sqrt((Ax^2 + Ay^2 + Az^2) / 3), if A has 3 components.
        '''
        A, = _match.groups()
        Aval = self(A)
        return self.rmscomps(Aval)

    rmscomps = staticmethod(rmscomps)

    # {var0}_cross_{var1}
    @known_pattern(r'(.+)_cross_(.+)', deps=[0,1], ignores_dims=['component'])
    def get_cross(self, var, *, _match=None, _val0=None, _val1=None, **_known_vals):
        '''cross product. {A}_cross_{B} --> A cross B.
        returned components are determined by self.component.
            (see also: the get_xyz pattern. E.g., {A}_cross_{B}_x --> x component of A cross B)

        [EFF] can provide known vals for A or B, to avoid recalculating them. (include leading underscores.)
            e.g. self('u_cross_E', _u=u, _E=E) --> u cross E, using u and E which are already known.
            CAUTION: if providing values, include all self.cross_components_needed() components;
                missing components will be assumed to be 0.
            E.g. if providing u to calculate u_cross_E, but u doesn't have x component, assumes u_x=0.

            can alternatively provide _val0 for A and/or _val1 for B.
        '''
        A, B = _match.groups()
        Aval = self._provided_val(A, _val0, _known_vals)
        Bval = self._provided_val(B, _val1, _known_vals)
        components_needed = self.cross_components_needed()
        with self.using(component=components_needed):
            if Aval is None:
                Aval = self(A)
            if Bval is None:
                Bval = self(B) if A != B else Aval  # [EFF] if A == B, only calculate once.
        components_result = self.component_list()
        return self.cross_product(Aval, Bval, components=components_result)

    cross_component = staticmethod(cross_component)
    
    cross_product = staticmethod(cross_product)
    cross = alias('cross_product')

    def cross_components_needed(self):
        '''return the components vectors need in order to find all cross product components in self.component_list
        e.g. if self.component == 'x', return ('y', 'z'), because (A_cross_B)_x needs Ay, Az, By, Bz but not Ax, Bx.
        '''
        components = self.component_list()  # iterable of Component objects
        if len(components) == 1:
            x = components[0]
            return YZ_FROM_X[x]
        else:
            return tuple(XYZ)
        return YZ_FROM_X[self.component]

    # # # DIRECTIONS # # #
    @known_var(dims=['component'])
    def get_xhat(self):
        '''unit vector in the x direction.
        result components determined by self.component, e.g. xhat_x == 1; xhat_y == 0.
        '''
        c = self.component   # below: sel crashes with tuple but not list.
        return XHAT.sel(component=(list(c) if isinstance(c, tuple) else c))

    @known_var(dims=['component'])
    def get_yhat(self):
        '''unit vector in the y direction.
        result components determined by self.component, e.g. yhat_x == 0; yhat_y == 1.
        '''
        c = self.component   # below: sel crashes with tuple but not list.
        return YHAT.sel(component=(list(c) if isinstance(c, tuple) else c))

    @known_var(dims=['component'])
    def get_zhat(self):
        '''unit vector in the z direction.
        result components determined by self.component, e.g. zhat_x == 0; zhat_z == 1.
        '''
        c = self.component   # below: sel crashes with tuple but not list.
        return ZHAT.sel(component=(list(c) if isinstance(c, tuple) else c))

    # hat_{var}, dir_{var}, direction_{var}, or unit_vector_{var}.
    @known_pattern(r'(hat|dir|direction|unit_vector)_(.+)', deps=[1])
    def get_hat(self, var, *, _match=None, _val0=None, **_known_vals):
        '''unit vector in the direction of var. hat_{A} --> A / |A|.
        returned components are determined by self.component.
            (e.g. when self.component=='x', hat_A --> A_x / |A|.)

        [EFF] can provide known val for A, to avoid recalculating it. (include leading underscore.)
            e.g. self('hat_E', _E=E) --> E / |E|, using E which is already known.
            can alternatively provide _val0 for A.
        '''
        _alias, A = _match.groups()   # _alias is 'hat', 'dir', 'direction', or 'unit_vector'
        Aval = self._provided_val(A, _val0, _known_vals)
        if Aval is None:
            Aval = self(A)
        return Aval / self(f'mod_{A}', _val0=Aval)

    angle_xy = staticmethod(angle_xy)
    angle_xy_to_hat = staticmethod(angle_xy_to_hat)

    # angle_xy_{var}, angxy_{var}, ang_{var}, dirxy_{var}
    @known_pattern(r'(angle_xy|angxy|ang|dirxy)_(.+)', deps=[1], ignores_dims=['component'])
    def get_angle_xy(self, var, *, _match=None, _val0=None, **_known_vals):
        '''angle between +xhat and var, in the xy plane, in radians.

        CAUTION: does not "unwrap"; all angles will be reported in the range -pi to pi.
        See unwrapt2pi for example of unwrapping (see also: np.unwrap)

        angle_xy_{A} --> atan2(Ay, Ax).

        [EFF] can provide known val for A, to avoid recalculating it. (include leading underscore.)
            e.g. self('angle_xy_E', _E=E) --> angle between +xhat and E, using E which is already known.
        '''
        _alias, A = _match.groups()
        Aval = self._provided_val(A, _val0, _known_vals)
        if Aval is None:
            Aval = self(A, component=['x', 'y'])
        return self.angle_xy(Aval)

    @known_pattern(r'unwrapt(2pi)?_(.+)', deps=[1])
    def get_unwrapt_2pi_var(self, var, *, _match=None):
        '''unwrapt_{A} --> unwrapped self(A) along 't', via np.unwrap with period=2*pi.

        CAUTION: result at a given snapshot can vary depending on self.snap,
            (though, (result % 2*pi) will always be the same.)

        E.g. self('unwrapt_angle_xy_E') --> angle between +xhat and E, but unwrapped,
            so e.g. if results change from just above -pi to just below -pi,
            the values below -pi will actually be below -pi,
            instead of being reported as 2*pi + (value just below -pi).
        '''
        _, here = _match.groups()
        val = self(here)
        if 't' not in val.coords:
            raise QuantCalcError(f'cannot unwrapt for val missing "t" coord (coords={list(coords)})')
        tt = val['t']
        if tt.ndim == 0:
            return val  # nothing to unwrap!
        elif tt.ndim == 1:
            tdim = tt.dims[0]
        else:
            raise QuantCalcError(f'cannot unwrapt when val["t"].ndim > 1.')
        # unwrap along the 't' dimension, using np.unwrap with period=2*pi.
        result = xarray_map(val, np.unwrap, axis=tdim, period=2*np.pi)
        return result

    # angle_xy_to_hat_{var}, angxy2hat_{var}, ang2hat_{var}, dirxy2hat_{var}
    @known_pattern(r'(angle_xy_to_hat|angxy2hat|ang2hat|dirxy2hat)_(.+)', deps=[1])
    def get_angle_xy_to_hat(self, var, *, _match=None, _val0=None, **_known_vals):
        '''unit vector u, given angle [radians] between +xhat and u in the xy plane.
        angle_xy_to_hat_{A} --> cos(A) * xhat + sin(A) * yhat.
        '''
        _alias, A = _match.groups()
        Aval = self._provided_val(A, _val0, _known_vals)
        if Aval is None:
            Aval = self(A)
        return self.angle_xy_to_hat(Aval)

    @known_pattern(r'rad2deg_(.+)', deps=[0], ignores_dims=['component'])
    def get_rad2deg(self, var, *, _match=None):
        '''convert radians to degrees. rad2deg_{A} --> A * 180 / pi.
        self('rad2deg_var') == np.rad2deg(self('var'))
        '''
        A, = _match.groups()
        return np.rad2deg(self(A))

    @known_pattern(r'deg2rad_(.+)', deps=[0], ignores_dims=['component'])
    def get_deg2rad(self, var, *, _match=None):
        '''convert degrees to radians. deg2rad_{A} --> A * pi / 180.
        self('deg2rad_var') == np.deg2rad(self('var'))
        '''
        A, = _match.groups()
        return np.deg2rad(self(A))

    # # # ZERO VECTOR # # #
    @known_pattern(r'vector_(\d+)', dims=['component'])  # vector_{n}
    def get_vector_N(self, var, *, _match=None):
        '''vector_n --> vector with n in each component. E.g. vector_0 --> vector with components (0,0,0).
        result components determined by self.component.'''
        n, = _match.groups()
        n = int(n)
        c = self.component
        result = VECTOR_ZERO.sel(component=(list(c) if isinstance(c, tuple) else c))
        return result if n==0 else result + n

    # # # PARALLEL & PERPENDICULAR COMPONENTS # # #
    take_perp_to = staticmethod(take_perp_to)
    take_parallel_to = staticmethod(take_parallel_to)

    # {A}_perp_{B}
    @known_pattern(r'(.+)_perp_(.+)', deps=[0,1])
    def get_perp(self, var, *, _match=None, _val0=None, _val1=None, **_known_vals):
        '''A_perp_B --> A after removing the component of A parallel to B.
        Equivalent to self.take_perp_to(B, A) == A - (A dot Bhat) Bhat.

        [EFF] can provide known vals for A or B, to avoid recalculating them. (include leading underscores.)
            e.g. self('E_perp_B', _E=E, _B=B) --> E perp to B, using E and B which are already known.
            can alternatively provide _val0 for A and/or _val1 for B.
        '''
        A, B = _match.groups()
        Aval = self._provided_val(A, _val0, _known_vals)
        Bval = self._provided_val(B, _val1, _known_vals)
        if Aval is None:
            Aval = self(A, component=None)  # [TODO][EFF] load fewer components here if self.component != XYZ ?
        if Bval is None:
            Bval = self(B, component=None) if A != B else Aval  # [EFF] if A == B, only calculate once.
        result = self.take_perp_to(Bval, Aval)
        if self.component != self.components:  # i.e. only asking for some of the vector components of result
            result = xarray_sel(result, component=self.component)
        return result

    # {A}_par_{B}
    @known_pattern(r'(.+)_par_(.+)', deps=[0,1])
    def get_parallel(self, var, *, _match=None, _val0=None, _val1=None, **_known_vals):
        '''A_par_B --> the component of A parallel to B.
        Equivalent to self.take_parallel_to(B, A) == (A dot Bhat) Bhat.
        see also: A_dot_hat_B, which is equivalent to mod_(A_par_B)

        [EFF] can provide known vals for A or B, to avoid recalculating them. (include leading underscores.)
            e.g. self('E_par_B', _E=E, _B=B) --> E par to B, using E and B which are already known.
            can alternatively provide _val0 for A and/or _val1 for B.
        '''
        A, B = _match.groups()
        Aval = self._provided_val(A, _val0, _known_vals)
        Bval = self._provided_val(B, _val1, _known_vals)
        if Aval is None:
            Aval = self(A, component=None)  # [TODO][EFF] load fewer components here if self.component != XYZ ?
        if Bval is None:
            Bval = self(B, component=None) if A != B else Aval  # [EFF] if A == B, only calculate once.
        result = self.take_parallel_to(Bval, Aval)
        if self.component != self.components:  # i.e. only asking for some of the vector components of result
            result = xarray_sel(result, component=self.component)
        return result

    # {A}_perpmod_{B} or {A}_perpmag_{B}
    @known_pattern(r'(.+)_perp(mod|mag)_(.+)', deps=[0,2], ignores_dims=['component'])
    def get_perpmod(self, var, *, _match=None, _val0=None, _val1=None, **_known_vals):
        '''magnitude of A after removing the component of A parallel to B.
        Equivalent to mod(A_perp_B).

        [EFF] can provide known vals for A or B, to avoid recalculating them. (include leading underscores.)
            e.g. self('E_perpmod_B', _E=E, _B=B) --> |E perp to B|, using E and B which are already known.
            can alternatively provide _val0 for A and/or _val1 for B.
        '''
        A, _mod_or_mag, B = _match.groups()
        with self.using(component=None):  # get A_perp_B across all vector components
            A_perp_B = self(f'{A}_perp_{B}', _val0=_val0, _val1=_val1, **_known_vals)
        return self.magnitude(A_perp_B)

    # {A}_sparmod_{B} or {A}_sparmag_{B}
    @known_pattern(r'(.+)_spar(mod|mag)_(.+)', deps=[0,2], ignores_dims=['component'])
    def get_sparmod(self, var, *, _match=None, _val0=None, _val1=None, **_known_vals):
        '''signed "magnitude" of the component of A parallel to B.
        Equivalent to A_dot_hat_B. Also abs(A_sparmod_B) is equivalent to mod(A_par_B).

        [EFF] can provide known vals for A or B, to avoid recalculating them. (include leading underscores.)
            e.g. self('E_parmod_B', _E=E, _B=B) --> |E par to B|, using E and B which are already known.
            can alternatively provide _val0 for A and/or _val1 for B.
        '''
        A, _mod_or_mag, B = _match.groups()
        if f'_hat_{B}' not in _known_vals:
            _known_vals[f'_hat_{B}'] = self(f'hat_{B}', _val0=_val1, **_known_vals)
        return self(f'{A}_dot_hat_{B}', _val0=_val0, **_known_vals)

    # {A}_parmod_{B} or {A}_parmag_{B}
    @known_pattern(r'(.+)_par(mod|mag)_(.+)', deps=[0,2], ignores_dims=['component'])
    def get_parmod(self, var, *, _match=None, _val0=None, _val1=None, **_known_vals):
        '''magnitude of the component of A parallel to B.
        Equivalent to mod(A_par_B). Also equivalent to abs(A_dot_hat_B)

        [EFF] can provide known vals for A or B, to avoid recalculating them. (include leading underscores.)
            e.g. self('E_parmod_B', _E=E, _B=B) --> |E par to B|, using E and B which are already known.
            can alternatively provide _val0 for A and/or _val1 for B.
        '''
        A, _mod_or_mag, B = _match.groups()
        result = self(f'{A}_sparmod_{B}', _val0=_val0, _val1=_val1, **_known_vals)
        return np.abs(result)
