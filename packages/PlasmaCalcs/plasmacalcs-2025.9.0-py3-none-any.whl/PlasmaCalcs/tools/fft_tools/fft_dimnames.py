"""
File Purpose: make it easier to deal with renaming fft dimensions

Easiest would be if always 'dim' --> 'freq_{dim}'.
However, dimname should include 'rad' if rad=True.
Additionally, there are well-known custom names for some rad fft dimensions,
    e.g. when rad=True, 'x' --> 'k_x', and 't' --> 'omega'.
"""

from ...errors import DimensionKeyError
from ...defaults import DEFAULTS

class FFTDimname():
    '''fft dimension name, along with methods to get post-fft name.
    name: the pre-fft name.
    rad: whether rad==True. Default None.

    self.pre is the pre-fft name.
    self.post is the post-fft name. Alternatively, use str(self) to see the post-fft name.
    '''
    # # # CREATION / INITIALIZATION # # #
    def __init__(self, name, *, rad=None):
        self.name = name
        self.rad = rad

    @classmethod
    def from_post(cls, post, *, rad=None):
        '''create FFTDimname from post-fft name.

        rad: None or bool
            if incompatible with inferred rad, raise DimensionKeyError.
            None --> compatible with any inferred rad; doesn't cause DimensionKeyError.
        post: str
            the post-fft name, used to infer the pre-fft name and possibly also rad.
            if rad is False, post MUST look like 'freq_{dim}'.
            Otherwise:
                if post looks like any DEFAULTS.FFT_FREQ_RAD_DIMNAMES.values(),
                    use name = the associated key (and infer rad=True).
                elif post looks like 'freqrad_{dim}', use name = dim (and infer rad=True).
                elif post looks like 'freq_{dim}', use name = dim (and infer rad=False).
                else, raise DimensionKeyError.        
        '''
        input_rad = rad
        if (rad is not None) and (not rad):  # rad is False
            if post.startswith('freq_'):
                name = post[len('freq_'):]
                inferred_rad = False
            else:
                raise DimensionKeyError(f'rad=False, but post does not start with "freq_". post={post!r}')
        else:  # rad is None or True
            for key, val in DEFAULTS.FFT_FREQ_RAD_DIMNAMES.items():
                if post == val:
                    name = key
                    inferred_rad = True
                    break
            else:  # did not break
                if post.startswith('freqrad_'):
                    name = post[len('freqrad_'):]
                    inferred_rad = True
                elif post.startswith('freq_'):
                    name = post[len('freq_'):]
                    inferred_rad = False
                else:
                    errmsg = (f'cannot determine name for pre-fft dimension associated with post={post!r}.\n'
                            'Expected post="freq_{dim}" or "freqrad_{dim}", or in DEFAULTS.FFT_FREQ_RAD_DIMNAMES.values()')
                    raise DimensionKeyError(errmsg)
        if input_rad is None:
            use_rad = inferred_rad
        else:
            if inferred_rad != input_rad:
                errmsg = (f'input rad={input_rad!r} incompatible with inferred rad={inferred_rad!r}, for post={post!r}')
                raise DimensionKeyError(errmsg)
            use_rad = input_rad
        return cls(name, rad=use_rad)

    @classmethod
    def implied_from(cls, s, array_dims, *, rad=None, post_fft=False):
        '''returns FFTDimname from s corresponding to one of the array_dims.

        s: str
            the pre-fft or post-fft name, corresponding to one of the array_dims.
            Might match an array_dim exactly, or might match array_dim pre or post fft.
        array_dims: iterable of str
            result will be appropriate for taking an fft of array with these dims.
            (Can also contain non-dimension coordinates of array.)
        rad: None or bool
            rad to use when creating FFTDimname from s.
            If None, use rad inferred from s & array_dims.
            Otherwise, ensure rad is compatible with inferred rad (else raise DimensionKeyError).
        post_fft: bool, default False
            True --> array_dims tell the post-fft dimensions.
            False --> array_dims tell the pre-fft dimensions.
            Use True when taking an ifft of an array with array.dims == array_dims.

        Examples:
            ('x', ['x', 'y']) --> cls('x', rad=rad)  # by default, rad=None)
            ('k_x', ['x', 'y']) --> cls('x', rad=True)
            ('freq_x', ['x', 'y']) --> cls('x', rad=False)
            ('x', ['k_x', 'k_y'], post_fft=True) --> cls('x', rad=True)
            ('k_x', ['k_x', 'k_y'], post_fft=True) --> cls('x', rad=True)
            ('freq_x', ['k_x', 'k_y'], post_fft=True) --> raise DimensionKeyError
            ('x', ['k_y', 't']) --> raise DimensionKeyError
        '''
        array_dims = tuple(array_dims)
        input_rad = rad
        attempt_rad = [False, True] if rad is None else [rad]
        if post_fft:
            for d in array_dims:
                for rad in attempt_rad:
                    try:
                        fname = cls.from_post(d, rad=rad)
                    except DimensionKeyError:
                        continue  # can't create fname from d & rad.
                    # else
                    if s == fname.pre:
                        return fname
                    if s == fname.post:
                        return fname
        else:  # post_fft=False. This is the default behavior.
            for d in array_dims:
                fname = cls(d, rad=input_rad)
                if s == fname.pre:  # <-- fname.pre is independent of rad
                    return fname
                for rad in attempt_rad:
                    fname.rad = rad
                    if s == fname.post:
                        return fname
        # <-- didn't find a match.
        errmsg = f'no corresponding dim for s={s!r} in array_dims={array_dims!r}'
        if rad is not None: errmsg += f' when rad={rad!r}'
        if post_fft: errmsg += ' when post_fft=True'
        raise DimensionKeyError(errmsg)
    
    # # # PROPERTIES # # #
    @property
    def pre(self):
        '''the pre-fft name.'''
        return self.name

    @property
    def post(self):
        '''the post-fft name.'''
        if self.rad:
            defaults = DEFAULTS.FFT_FREQ_RAD_DIMNAMES
            if (defaults is None) or (self.name in defaults):
                return defaults[self.name]
            return f'freqrad_{self.name}'
        else:
            return f'freq_{self.name}'

    # # # EQUALITY # # #
    def __eq__(self, other):
        '''self == other. True when self.name == other.name and self.rad == other.rad.
        if other not an instance of type(self), return False.
        '''
        if not isinstance(other, type(self)):
            return False
        return (self.name == other.name) and (self.rad == other.rad)

    # # # MISC. METHODS # # #
    @classmethod
    def is_valid_post(cls, post, *, rad=None):
        '''returns whether post is a valid post-fft name, given rad.
        valid if can create FFTDimname from post & rad without raising DimensionKeyError.
        '''
        try:
            cls.from_post(post, rad=rad)
            return True
        except DimensionKeyError:
            return False

    # # # DISPLAY # # #
    def __str__(self):
        '''str(self). Equivalent to str(self.post).'''
        return str(self.post)

    def __repr__(self):
        '''repr(self).'''
        return f'{type(self).__name__}({self.name!r}, rad={self.rad!r})'
