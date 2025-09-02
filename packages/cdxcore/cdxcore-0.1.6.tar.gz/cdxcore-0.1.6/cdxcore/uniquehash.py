"""
Basic utilities for Python
Hans Buehler 2022
"""

import datetime as datetime
import types as types
import hashlib as hashlib
import inspect as inspect
from collections.abc import Mapping, Collection, Sequence, Iterator, Callable
from collections import OrderedDict
import numpy as np
import pandas as pd
import struct as struct
from .util import isFunction, DEF_FILE_NAME_MAP, fmt_filename
from .prettyobject import PrettyObject

def _qual_name(x, with_mod=False):
    q = getattr(x, '__qualname__', x.__name__)
    if with_mod:
        m = getattr(x, "__module__", None)
        if not m is None:
            q += "@" + m
    return q

# =============================================================================
# Hashing
# =============================================================================

class UniqueHash( object ):
    """
    Object to compute recursively unique hashes with.
    See UniqueHash.__init__ for documentation
    """
    
    def __init__(self, length                 : int = 32, *,
                       parse_underscore       : str  = "none",
                       sort_dicts             : bool = True,
                       parse_functions        : bool = False,
                       # micro settings
                       pd_ignore_column_order : bool = True,
                       np_nan_equal           : bool = False,
                       f_include_defaults     : bool = True,
                       f_include_closure      : bool = True,
                       f_include_globals      : bool = True,
                       ):
        """
        Initializes a callable object which iteratively generates hashes of length at most 'length'.
        The algorithm is meant to be mostly hands-off, but there are a few considerations with making:
            
        Private and Protected members
        -----------------------------
        When an object is passed to this functional its members are iterated using __dict__ or __slots__, respectively.
        By default this process ignores any fields in objects or dictionaries which start with "_". The idea here is
        that 'functional' parameters are stored as members, but any derived data is stored in protected members.
        This behaviour can be chanhed with 'parse_underscore'.

        Objects can optionally implement their own hashing scheme by implementing
        
            __unique_hash__( self, uniqueHash : UniqueHash, debug_trace : DebugTrace  )
            
        This function may return a unique string, or any other non-None Python object which will then be passed to
        UniqueHash.__call__. A common use case is to return a tuple of the members of the class which are
        pertinent for hashing.
                
        Dictionaries
        ------------
        Since Python 3.7 dictionaries preserve the order in which they were constructed https://mail.python.org/pipermail/python-dev/2017-December/151283.html.
        However, Python semantics otherwise remain order invariant, i.e. {'x':1, 'y':2} tests equal to {'y':2',x':1}.
        For this reasom the default behaviour for dictonaries is to sort them before hasing their content
        (also recall that objects are typicall treated via their __dict__).
        This can be turned off with 'sort_dicts'.
        OrderedDicts are not sorted in any case.

        Functions
        ---------
        By default function members of objects and dictionaries (which include @properties) are
        ignored. You can set 'parse_functions' = True to parse a reduced text of the function code.
        There are a number of expert settings for handling functions, see below.
        
        Numpy, Pandas
        -------------
        Hashing of large datasets is not advised. Use hashes on the generating parameter set instead.
        
        Implementing custom object hashing
        ----------------------------------
        An object may implement
            __unique_hash__( self, uniqueHashExt : UniqueHash  )
        which is passed a unique hash object which contains all current run time parameters.
        A good use case is:

        Parameters
        ----------
            length : int
                Intended length of the hash function.
            parse_underscore : bool
                How to handle object members starting with '_'.
                 * 'none' : ignore members starting with '_' (the default)               
                 * 'protected' : ignore 'private' members declared starting with '_' and containing '__' (*)
                 * 'private' : consider all members
            sort_dicts : bool
                From python 3.7 dictionaries are ordered. That means that strictly speaking
                the two dictionaries {'x':1, 'y':2} and {'y':2, 'x':1} are not indentical;
                however Python will sematicallly assume they are as == between the two will return True.
                Accordingly, this function by default sorts first the keys of mappings before
                hashing their items. (If dictionaries are derived from OrderedDict, the function will still process those
                in order.)
                This can be turned off by setting sort_dicts=False.
            parse_functions : bool
                If True, then the function will attempt to generate
                unique hashes for function and property objects
                using compress_function_code
                
        Fine tuning
        -----------
            pd_ignore_column_order : bool
                Whether to ingore the order of panda columns. The default is True
            np_nan_equal : bool
                Whether to ignore the specific type of a NaN. The default is False.
            f_include_defaults : bool
                When parsing functions whether to include default values. Default is True.
            f_include_closure : bool
                When parsing functions whether to include the function colusure. This can be expensive. Default is True.
            f_include_globals : bool
                When parsing functions whether to include globals used by the function. This can be expensicve. Default is False.
        """
        self.length             = int(length)

        digest_size = self.length//2
        if digest_size <= 0:
            raise ValueError("'length' must be at least 2")
        if digest_size > 64:
            raise ValueError("'length' can be at most 128 (limitation of 'haslib.blake2b')")

        self.parse_underscore   = str(parse_underscore)
        self.sort_dicts         = bool(sort_dicts)
        self.parse_functions    = bool(parse_functions)
        
        self.pd_ignore_column_order = bool(pd_ignore_column_order)
        self.np_nan_equal           = bool(np_nan_equal)

        self.f_include_defaults = bool(f_include_defaults)
        self.f_include_closure  = bool(f_include_closure)
        self.f_include_globals  = bool(f_include_globals)
        
        if parse_underscore == "none":
            self._pi = 0
        elif parse_underscore == "protected":
            self._pi = 1
        else:
            if parse_underscore != "private": raise ValueError("'parse_underscore' must be 'none', 'private', or 'protected'. Found '{self.parse_underscore}'")
            self._pi = 2

    @property
    def name(self) -> str:
        return f"uniqueHash({self.length};{self.parse_underscore},{self.sort_dicts},{self.parse_functions})"
    
    def clone(self):
        """ Return copy of 'self' """
        return UniqueHash( **{ k:v for k,v in self.__dict__.items() if not k[:1] == "_"} )

    def __call__(self, *args, debug_trace = None, **kwargs):
        """
        Returns a unique hash for the parameters passed to this function.

        Hashing can have curious side effect, in particular when handling objects and functions.
        For this reason this function allows tracing all hashing activity using its debug_trace
        parameter.
        
        Parameters
        ----------
            args, kwargs:
                Parameters to hash.
            debug_trace : DebugTrace
                Allows tracing of hashing activity.
                Two classes are implemented:
                    DebugTraceVerbose()
                        Simply prints out hashing activity to stdout.
                    DebugTraceCollect()
                        Collects an array of tracing information.
                        The object itself is an iterable which contains
                        the respective tracing information.
        
        Returns
        -------
            String of at most length 'length'
        """
        h, _ = self._mk_blake( h=self.length//2 )
        if len(args) > 0:
            self._hash_any( h, args, debug_trace = debug_trace )
        if len(kwargs) > 0:
            self._hash_any( h, kwargs, debug_trace = debug_trace )
        return h.hexdigest()

    # Utility functions
    # -----------------
    
    @staticmethod
    def _mk_blake( h ):
        """ utility function to allow passing a hash 'h' or an 'int' """
        if not isinstance(h, int):
            return h, False
        h = int(h)
        assert h//2>0 and h//2<64, ("'h' must be at least 2 and not exceed 128", h)
        h = hashlib.blake2b( digest_size=h ) if h > 16 else hashlib.blake2s( digest_size=h )
        return h, True
    
    def _hash_any(self, h, x, *, debug_trace = None ):
        """
        Recursive function to hash "any" object.
        
        Parameters
        ----------
            h : hash
                Hashlib algorithm
            x : any
                Value to hash.
            debug_trace :
                Optional DebugTrace object to debug uniqueHash calculations.
        """
        if x is None:
            h.update(b'\x00')
            return
        # numpy atomic
        if isinstance(x, np.generic):
            sz = x.itemsize
            if sz==1:
                x = x.view(np.int8)
            elif sz==2:
                x = x.view(np.int16)
            elif sz==4:
                x = x.view(np.int32)
            else:
                assert sz==8, ("Cannot handle itemsize",sz,"for numpy generic", type(x), "with value", x)
                x = x.view(np.int64)
            h.update(x.tobytes())
            if not debug_trace is None: debug_trace.update( x )
            return
        # basic elements
        if isinstance( x, bool ):
            h.update( x.to_bytes(1,'little', signed=True) )
            if not debug_trace is None: debug_trace.update( x )
            return
        if isinstance( x, int ):
            h.update( x.to_bytes(8,'little', signed=True) )
            if not debug_trace is None: debug_trace.update( x )
            return
        if isinstance( x, ( float, complex ) ):
            h.update( struct.pack('<d', x) )  # little-endian double
            if not debug_trace is None: debug_trace.update( x )
            return
        if isinstance( x, bytes ):
            h.update( x )
            if not debug_trace is None: debug_trace.update( x )
            return
        if isinstance( x, str ):
            h.update( x.encode('utf-8') )
            if not debug_trace is None: debug_trace.update( x )
            return
        # datetime etc
        if isinstance(x,datetime.datetime):
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )
            ts = float( x.timestamp() )
            td = x.tzinfo.utcoffset(x) if not x.tzinfo is None else None
            self._hash_any(h, ts, debug_trace=debug_trace)
            if not td is None:
                self._hash_any(h, td.total_seconds, debug_trace=debug_trace)
            return
        if isinstance(x,datetime.time):
            """
            tzinfo for time is useless
            if not x.tzinfo is None:
                h.update( x.utcoffset().total_seconds.to_bytes(4,'little', signed=True) )
            else:
                h.update( int(0).to_bytes(4,'little', signed=True) )                
            """
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )
            total_seconds = float(x.hour*60*60+x.minute*60+x.second) +\
                            float(x.microsecond) / 1000000.
            self._hash_any(h, total_seconds, debug_trace=debug_trace)
            """            
            h.update( x.hour.to_bytes(2,'little', signed=True) )
            h.update( x.minute.to_bytes(2,'little', signed=True) )
            h.update( x.second.to_bytes(2,'little', signed=True) )
            h.update( x.microsecond.to_bytes(4,'little', signed=True))
            if not debug_trace is None:
                debug_trace = debug_trace.update_topic( x )
                debug_trace.update( x.hour, "hour")
                debug_trace.update( x.minute, "minute")
                debug_trace.update( x.second, "second")
                debug_trace.update( x.microsecond, "microsecond")
                if not x.tzinfo is None:
                    debug_trace.warning( "datetime.time support for tzinfo is not working well. Use datetime.datetime")
            """
            return
        if isinstance(x,datetime.date):
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )            
            full = x.year * 10000 + x.month * 100 + x.day
            self._hash_any(h, full, debug_trace=debug_trace)
            """
            h.update( x.year.to_bytes(4,'little', signed=True) )
            h.update( x.month.to_bytes(1,'little', signed=True) )
            h.update( x.day.to_bytes(2,'little', signed=True) )
            if not debug_trace is None:
                debug_trace = debug_trace.update_topic( x )
                debug_trace.update( x.year, "year" )
                debug_trace.update( x.month, "month" )
                debug_trace.update( x.day, "day" )
            """
            return
        if isinstance(x,datetime.timedelta):
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )
            self._hash_any(h, x.total_seconds(), debug_trace=debug_trace )
            return
        # functions
        if isFunction(x) or isinstance(x,property):
            if self.parse_functions:
                self._hash_function( h, x, debug_trace=debug_trace )
            elif not debug_trace is None:
                debug_trace.warning( f"Ignored function: {x.__qualname__}")                
            return
        # slice -> tuple
        if isinstance(x,slice):
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )
            self._hash_any(h, (x.start,x.stop,x.step), debug_trace=debug_trace )
            return
        # test presence of __unique_hash__()
        # objects can now simply set this member to a string
        if hasattr(x,"__unique_hash__"):
            unique_hash = x.__unique_hash__
            if isinstance(unique_hash, str):
                h.update(unique_hash.encode('utf-8') )
                if not debug_trace is None:
                    debug_trace = debug_trace.update_topic( x, msg="__unique_hash__ str" )
                    debug_trace.update( unique_hash )
                return                        
            debug_trace = None if debug_trace is None else debug_trace.update_topic( x, msg="__unique_hash__ function" )
            try:
                unique_hash = unique_hash( self.clone(), debug_trace=debug_trace )
            except Exception as e:
                raise type(e)( e, f"Exception encountered while calling '__unique_hash__' of object of type {type(x)}.")
            if unique_hash is None:
                raise TypeError(f"{type(x).__qualname__}: __unique_hash__() cannot return None")
            if isinstance(unique_hash, str):
                h.update(unique_hash.encode('utf-8') )
                if not debug_trace is None:
                    debug_trace.update( unique_hash )
            else:
                if not debug_trace is None:
                    debug_trace = debug_trace.update_topic( unique_hash )
                self._hash_any(h, unique_hash, debug_trace=debug_trace )
            return
        # numpy
        if isinstance(x,np.ndarray):
            self._hash_numpy(h, x, debug_trace=debug_trace )
            return
        # pandas
        if isinstance(x,pd.DataFrame):
            self._hash_dataFrame(h, x, debug_trace=debug_trace )
            return
        # dictionaries, and similar
        # note that objects with a __dict__ will
        # be hashed using that dictionary
        if isinstance(x,Mapping):
            assert not isinstance(x, Sequence)
            # from Python 3.7 onwards, dictionaries are ordered.
            # however, we here assume here that unless they are
            # specified as ordered, we can assume that the
            # order does not matter.
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )
            keys = sorted(x) if self.sort_dicts and not isinstance(x,OrderedDict) else list(x)
            for k in keys: 
                if isinstance(k,str):
                    if k[:1] == '_':
                        if self._pi == 0:
                            continue
                        if self._pi == 1 and k.find("__") != -1:
                            continue
                self._hash_any(h, (k, x[k]), debug_trace=debug_trace)
            return
        # lists, tuples and everything which looks like it --> lists
        if isinstance(x, (Sequence, Iterator)):
            assert not isinstance(x, dict)
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )
            for k in x:
                self._hash_any(h, k, debug_trace=debug_trace)
            return
        # all others such as sets need sorting first
        if isinstance(x, Collection):
            assert not isinstance(x, dict)
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x )
            x = sorted(x)
            for k in x:
                self._hash_any(h, k, debug_trace=debug_trace)
            return
        # objects: treat like dictionaries
        if hasattr(x,"__dict__"):
            """
            1)
             from python 3.7 onwards dictionaries are ordered.
             however, except in rare cases that order should not
             impede the equivalence of objects
            2)
             private member handling in Python is subject to name space mangling which can have curious effects.
             That's why we consider private any members staring with '_' and containing '__':
                class A(object):
                    def f(self):
                        class X(object):
                            pass
                        x = X()
                        x.__p = 1
                        print(x.__dict__)
                A().f() will print '{'_A__p': 1}' even though 'x.__p' is a private member to X.
            """
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x, "object with __dict__" )
            self._hash_any( h, _qual_name( type(x),False), debug_trace=debug_trace)
            x    = x.__dict__
            keys = sorted(x) if self.sort_dicts else list(x)
            for k in keys:
                if isinstance(k,str):
                    if k[:1] == '_':
                        if self._pi == 0:
                            continue
                        if self._pi == 1 and k.find("__") != -1:
                            continue
                self._hash_any(h, k, debug_trace=debug_trace)
                self._hash_any(h, x[k], debug_trace=debug_trace)
            return
            self._hash_any(h, x.__dict__)
            return
        if hasattr(x,"__slots__"):
            if not debug_trace is None: debug_trace = debug_trace.update_topic( x, "object with __slots__" )
            self._hash_any( h, _qual_name( type(x),False), debug_trace=debug_trace)
            for k in  x.__slots__:
                if isinstance(k,str):
                    if k[:1] == '_':
                        if self._pi == 0:
                            continue
                        if self._pi == 1 and k.find("__") != -1:
                            continue
                self._hash_any(h, k, debug_trace=debug_trace)
                self._hash_any(h, getattr(x,k), debug_trace=debug_trace)
            return
        raise TypeError(f"Cannot generate unique hash for type '{_qual_name(type(x),True)}': it does not have __dict__ or __slots__")
    
    def _hash_function( self, h, fn : Callable, *, debug_trace = None ):
        """
        Hash a function
        """
        fn = inspect.unwrap(getattr(fn, "__func__", fn))
        if inspect.isbuiltin(fn):
            # Builtins: best we can do is identity by module + qualname
            ident = _qual_name(fn,False)
            h.update( ident.encode("utf-8") )
            if not debug_trace is None: debug_trace.update( ident, "builtin function" )
            return
    
        if not inspect.isfunction(fn):
            if hasattr(fn, "__call__"):
                obj_name = _qual_name(type(fn),False)
                h.update( obj_name.encode("utf-8") )                
                if not debug_trace is None:
                    debug_trace = debug_trace.update_topic( fn, "using __call__" )
                    debug_trace.update( obj_name )
                return self._hash_function(h, fn.__call__, debug_trace = debug_trace )
            raise TypeError(f"'fn' is not a function but of type {type(fn)}.")
    
        debug_trace = None if debug_trace is None else debug_trace.update_topic( fn )
        func_name   = _qual_name(fn,False)
        self._hash_any( h, func_name )

        src = inspect.getsourcelines( fn )[0]
        if isinstance(fn,types.LambdaType) and fn.__name__ == "<lambda>":
            assert len(src) > 0, "No source code ??"
            l = src[0]
            i = l.lower().find("lambda ")
            assert i!=-1, (f"Cannot find keyword 'lambda' even though {func_name} is a LambdaType?")
            src[0] = l[i+len("lambda "):]
        # Compressed version of the code of the function 'f' where all blanks are removed"""
        src = [ l.replace("\t"," ").replace(" ","").replace("\n","") for l in src ]    
        self._hash_any( h, src )
        if not debug_trace is None:
            debug_trace.update( func_name )
            debug_trace.update( src, "reduced source code")
        del src, func_name

        if self.f_include_defaults:
            # Defaults
            if not fn.__defaults__ is None and len(fn.__defaults__) > 0:
                def_debug_trace = None if debug_trace is None else debug_trace.update_topic( fn.__defaults__, "position defaults")
                self._hash_any( h, fn.__defaults__, debug_trace = def_debug_trace )
                del def_debug_trace

            if not fn.__kwdefaults__ is None and len(fn.__kwdefaults__) > 0:
                def_debug_trace = None if debug_trace is None else debug_trace.update_topic(fn.__kwdefaults__, "keyword defauls")
                self._hash_any( h, fn.__kwdefaults__, debug_trace = def_debug_trace )
                del def_debug_trace
    
        if self.f_include_closure and not fn.__closure__ is None and len(fn.__closure__) > 0:
            # Closure cells (can be large; disable if that’s a concern)
            closure_debug_trace = None if debug_trace is None else debug_trace.update_topic( fn.__closure__, "closure" )
            for cell in fn.__closure__:
                self._hash_any( h, cell.cell_contents, debug_trace=closure_debug_trace )
            del closure_debug_trace
    
        if self.f_include_globals and len(fn.__globals__) > 0 and len(fn.__code__.co_names) > 0:
            # Referenced globals (names actually used by the code)
            g = fn.__globals__
            glb_debug_trace = None if debug_trace is None else debug_trace.update_topic( fn.__code__.co_names, "linked globals" )
            for name in sorted(fn.__code__.co_names):
                if name in g:
                    self._hash_any( h, (name, g[name]), debug_trace=glb_debug_trace )
            del glb_debug_trace
            del g
    
    def _hash_dataFrame( self, h, df : pd.DataFrame, *, debug_trace = None ):
        """
        Compute hash for a dataframe, c.f. https://stackoverflow.com/questions/49883236/how-to-generate-a-hash-or-checksum-value-on-python-dataframe-created-from-a-fix    
        Returns a hex digest that changes if the DataFrame's *content* changes.
        Does not hash attributes.
        """
        assert isinstance(df, pd.DataFrame), ("DataFrame expected", type(df))
        debug_trace = None if debug_trace is None else debug_trace.update_topic( df )
        if self.pd_ignore_column_order:
            df = df.reindex(sorted(df.columns), axis=1)
    
        # hash index
        idx_h = pd.util.hash_pandas_object(df.index, index=False, categorize=True).values
        h.update(idx_h.tobytes())
        if not debug_trace is None: debug_trace.update( idx_h )
    
        # hash each column’s content + its name + dtype
        for name, col in df.items():
            h.update(str(name).encode('utf-8'))
            h.update(str(col.dtype).encode('utf-8'))
            col_h = pd.util.hash_pandas_object(col, index=False, categorize=True).values
            h.update(col_h.tobytes())
            if not debug_trace is None:
                debug_trace.update( str(name) )
                debug_trace.update( str(col.dtype) )
                debug_trace.update( col_h )

        # attrs, if any
        attrs = getattr(df, "attrs", None)
        if not attrs is None:
            self._hash_any(h, attrs)
            if not debug_trace is None: debug_trace.update( attrs, "attrs" )
    
    def _hash_numpy( self, h, a : np.ndarray, *, debug_trace = None ):
        """
        Numpy hash
        """
        assert isinstance(a, np.ndarray), ("ndarray expected", type(a))
        a = np.asarray(a)
    
        debug_trace = None if debug_trace is None else debug_trace.update_topic( a )
        # Disallow arbitrary Python objects (define your own encoding first)
        if a.dtype.kind == 'O':
            raise TypeError("object-dtype array: map elements to bytes first (e.g., via str/utf-8).")
    
        # Datetime/timedelta: hash their int64 representation
        if a.dtype.kind in 'Mm':
            a = a.view(np.int64)
    
        # Make contiguous and normalize to little-endian for numeric types
        a_dtype = a.dtype
        # a       = np.ascontiguousarray(a)
        if a.dtype.byteorder == '>' or (a.dtype.byteorder == '=' and not np.little_endian):
            a = a.byteswap().newbyteorder()
    
        # Canonicalize NaN bits so all NaNs hash the same (float16/32/64, complex64/128)
        if self.np_nan_equal and a.dtype.kind in 'fc':
            base_bytes = (a.dtype.itemsize // (2 if a.dtype.kind == 'c' else 1))
            if base_bytes == 2:
                base = np.float16
            elif base_bytes == 4:
                base = np.float32
            else:
                assert base_bytes == 8, ("Internal error: cannot handle base_bytes", base_bytes)
                base= np.float64
            a = a.view(base)
            if np.isnan(a).any():
                a = a.copy()
                if base is np.float16:
                    qnan = np.frombuffer(np.uint16(0x7e00).tobytes(), dtype=np.float16)[0]
                elif base is np.float32:
                    qnan = np.frombuffer(np.uint32(0x7fc00000).tobytes(), dtype=np.float32)[0]
                else:  # float64
                    qnan = np.frombuffer(np.uint64(0x7ff8000000000000).tobytes(), dtype=np.float64)[0]
                a[np.isnan(a)] = qnan
                a = a.view(a_dtype)
    
        # shapes
        h.update( len(a.shape).to_bytes(4,'little', signed=False) )
        for i in a.shape:
            h.update( i.to_bytes(4,'little', signed=False) )        
        # dtype
        h.update(a.dtype.str.encode('utf-8'))    
        h.update(a.tobytes())
        if not debug_trace is None:
            debug_trace.update( a.shape )
            debug_trace.update( a.dtype.str )
            debug_trace.update( a.tobytes() )
    
# Debugging
# =========

class DebugTrace(object):
    def update( self, x, msg : str = None ):
        """ Notify processing of 'x', with an optional process 'msg' """
        raise NotImplementedError()        
    def update_topic( self, x, msg : str = None ):
        """ Notify and return a sub-trace context """
        raise NotImplementedError()        
    def warning( self, msg : str):
        """ Issue warning """
        raise NotImplementedError()        

class DebugTraceCollect(DebugTrace):
    """
    Simple collection of all arguments parsed with DebugTrace
    """
    def __init__(self, tostr : int = None ):
        """ Initialize data collection """
        if tostr and tostr<=0: raise ValueError("'tostr' must be None or a positive integer")
        self.tostr = tostr
        self.trace = []        
    def _update( self, x, msg, child ):
        """ Notify processing of 'x', with an optional process 'msg' """
        if self.tostr:
            y = PrettyObject(   typex = type(x),
                                reprx = repr(x)[:self.tostr],
                                msg   = msg,
                                child = child )
        else:
            y = PrettyObject(   x     = x,
                                msg   = msg,
                                child = child )
        self.trace.append( y )        
    def update( self, x, msg : str = None ):
        """ Notify processing of 'x', with an optional process 'msg' """
        self._update( x, msg, None )
    def update_topic( self, x, msg : str = None ):
        """ Notify and return a sub-trace context """
        child = DebugTraceCollect(tostr=self.tostr)
        self._update( x, msg, child )
        return child
    def warning( self, msg : str):
        """ Issue warning """
        self._update( None, msg, None )
        
    # results
    # -------
    
    def __getitem__(self, item):
        return self.trace[item]
    def __len__(self):
        return len(self.trace)
    def __iter__(self):
        for y in self.trace:
            yield y
    def __str__(self):
        return self.trace.__repr__()
    def __repr__(self):
        return f"DebugTraceCollect({self.trace.__str__()})"
        
class DebugTraceVerbose(DebugTrace):
    """
    Live printing of tracing information with cdxbasics.verbose.Context
    for some formatting. All objects will be reported by type and
    their string representation, sufficiently reduced if necessary.
    """
    def __init__(self, strsize : int = 50, verbose = None ):
        """
        Initialize tracer.
        
        Parameters
        ----------
            strsize : int
                Maximum string size when using repr() on reported objects.
            verbose :
                Context object or None for a new context object.
        """                
        from .verbose import Context
        if strsize<=3: ValueError("'strsize' must exceed 3")
        self.strsize = strsize
        self.verbose = Context("all") if verbose is None else verbose
    def update( self, x, msg : str = None ):
        """ Notify processing of 'x', with an optional process 'msg' """
        xstr = repr(x)
        if xstr[:1] == "'" and xstr[-1] == "'":
            xstr = xstr[1:-1]
        if len(xstr) > self.strsize:
            xstr = xstr[:self.strsize-3] + "..."
        if msg is None or len(msg) == 0:
            self.verbose.write( f"{type(x).__name__}: '{xstr}'" )
        else:
            self.verbose.write( f"{msg} {type(x).__name__}: '{xstr}'" )
    def update_topic( self, x, msg : str = None ):
        """ Notify and return a sub-trace context """
        self.update( x, msg )
        return DebugTraceVerbose( self.strsize, self.verbose(1) )    
    def warning( self, msg : str):
        """ Issue warning """
        self.verbose.write( msg )
                
# =============================================================================
# Utility wrappers
# =============================================================================

def uniqueHashExt(**parameters) -> UniqueHash:    
    return UniqueHash(**parameters)
uniqueHashExt.__doc__ = UniqueHash.__init__.__doc__

def namedUniqueHashExt( max_length       : int = 60,
                        id_length        : int = 16,  *,
                        separator        : str = ' ',
                        filename_by      : str = None,
                        **unique_hash_arguments
                        ):
    """
    Returns a function 
    
        f( label, **argv, **argp )
    
    which generates unique strings of at most a length of max_length of the format
        label + separator + ID
    where ID has length id_length.

    The maximum length of the returned string is 'max_length'.
    If total_lengths is id_length+len(separator) then the function just returns the ID of length max_length.

    This function does not suppose that 'label' is unqiue, hence the ID is prioritized.
    See uniqueLabelExt() for a function which assumes the label is unique.
    
    The function optionally makes sure that the returned string is a valid file name using cdxbasics.util.fmt_filename.

    Important
    ---------
    It is strongly recommended to read the documentation for UniqueHash.__init__() for details on hashing logic
    and the available parameters

    Parameters
    ----------
        max_length : int
            Total length of the returned string including the ID.
            Defaults to 60 to allow file names with extensions with three letters.
        id_length : int
            Intended length of the hash function, default 16
        separator : str
            Separator between label and id_length.
            Note that the separator will be included in the ID calculation, hence different separators
            lead to different IDs.
        filename_by : str, None
            If not None, use fmt_filename( *, by=filename_by ) to ensure the returned string is a valid
            filename for both windows and linux, of at most 'max_length' size.
            If set to the string "default", use DEF_FILE_NAME_MAP as the default mapping of cdxbasics.util.fmt_filename
        **unique_hash_arguments:
            Parameters passed to UniqueHash.__init__.

    Returns
    -------
        hash function with signature (label, *args, **kwargs).
        All arguments including label and separator will be used to generate the hash key.
    """
    if id_length < 4: raise ValueError("'id_length' must be at least 4. Found {id_length}")
    if id_length > max_length: raise ValueError(f"'max_length' must not be less than 'id_length'. Founb {max_length} and {id_length}, respectivelty")
    if 'length' in unique_hash_arguments: raise ValueError("Cannot specify 'length' here. Used 'id_length' and 'max_length'")
    filename_by  = ( DEF_FILE_NAME_MAP if filename_by=="default" else filename_by ) if not filename_by is None else None
    fseparator   = fmt_filename( separator, by=filename_by ) if not filename_by is None else separator

    label_length = max_length-id_length-len(fseparator)
    if label_length<=0:
        id_length    = max_length
        label_length = 0
    unique_hash  = UniqueHash( length=id_length, **unique_hash_arguments )

    def named_unique_hash(label, *args, **kwargs) -> str:
        if label_length>0:
            assert not label is None, ("'label' cannot be None", args, kwargs)
            label        = fmt_filename( label, by=filename_by ) if not filename_by is None else label
            base_hash    = unique_hash( label, separator, *args, **kwargs )
            label        = label[:label_length] + fseparator + base_hash
        else:
            label        = unique_hash( separator, *args, **kwargs )  # using 'separator' here to allow distinction at that level
        return label
    return named_unique_hash

def uniqueLabelExt(     max_length       : int = 60,
                        id_length        : int = 8,
                        separator        : str = ' ',
                        filename_by      : str = None ):
    """
    Returns a function 
    
        f( unique_label )
    
    which generates strings of at most max_length of the format:
    If len(unique_label) <= max_length:
        unique_label
    else:
        unique_label + separator + ID
    where the ID is of maximum length 'id_length'.

    This function assumes that 'unique_label' is unique, hence the ID is dropped if 'unique_label' is less than 'max_length'
    See namedUniqueHashExt() for a function does not assume the label is unique, hence the ID is always appended.
    Note that if file name conversion is used, then this function will always attach the unique ID to the filename because
    the reduction of the label to a filename is no longer guaranteed to be unique. If your label is unique as a filename, do not
    use 'filename_by'. The function will return valid file names if label is a valid file name.

    Parameters
    ----------
        max_length : int
            Total length of the returned string including the ID.
            Defaults to 60 to allow file names with extensions with three letters.
        id_length : int
            Indicative length of the hash function, default 8.
            id_length will be reduced to max_length if neccessary.
        separator : str
            Separator between label and id_length.
            Note that the separator will be included in the ID calculation, hence different separators
            lead to different IDs.
        filename_by : str, None
            If not None, use fmt_filename( *, by=filename_by ) to ensure the returned string is a valid
            filename for both windows and linux, of at most 'max_length' size.
            If set to the string "default", use DEF_FILE_NAME_MAP as the default mapping of cdxbasics.util.fmt_filename

    Returns
    -------
        hash function with signature (unique_label).
    """
    if id_length < 4: raise ValueError("'id_length' must be at least 4. Found {id_length}")
    if id_length > max_length: raise ValueError(f"'max_length' must not be less than 'id_length'. Founb {max_length} and {id_length}, respectivelty")

    filename_by  = ( DEF_FILE_NAME_MAP if filename_by=="default" else filename_by ) if not filename_by is None else None
    fseparator   = fmt_filename( separator, by=filename_by ) if not filename_by is None else separator

    if id_length>=max_length+len(fseparator):
        id_length = max_length+len(fseparator)

    unique_hash = UniqueHash( length=id_length )

    def unique_label_hash(label) -> str:
        if filename_by is None and len(label) <= max_length and len(label) > 0:
            # no filename convertsion and label is short enough --> use this name
            return label
            
        base_hash    = unique_hash( label, separator )
        label_hash   = fseparator + base_hash
        if len(label_hash) >= max_length or len(label) == 0:
            # hash and separator exceed total length. Note that len(base_hash) <= max_length
            label = base_hash
        else:
            # convert label to filename
            label = fmt_filename( label, by=filename_by ) if not filename_by is None else label
            label = label[:max_length-len(label_hash)] + label_hash
        return label
    return unique_label_hash

# =============================================================================
# Short cuts
# =============================================================================

def uniqueHash8( *args, **argv ) -> str:
    """
    Compute a unique ID of length 8 for the provided arguments.

    The function
        1) uses the repr() function to feed objects to the hash algorithm.
           that means is only distinguishes floats up to str conversion precision
        2) keys of dictionaries, and sets are sorted to ensure equality of hashes
           accross different memory setups of strings
        3) Members with leading '_' are ignored (*)
        4) Functions and properties are ignored (*)
        (*) you can create a hash function with different behaviour by using uniqueHashExt()

    To support hashing directly in one of your objects, implement

        __unique_hash__( length : int, parse_functions : bool, parse_underscore : str )

        The parameters are the same as for uniqueHashExt.
        The function is expected to return a hashable object, ideally a string.
    """
    return UniqueHash(8)(*args,**argv)

def uniqueHash16( *args, **argv ) -> str:
    """
    Compute a unique ID of length 16 for the provided arguments.
    The function
        1) uses the repr() function to feed objects to the hash algorithm.
           that means is only distinguishes floats up to str conversion precision
        2) keys of dictionaries, and sets are sorted to ensure equality of hashes
           accross different memory setups of strings
        3) Members with leading '_' are ignored (*)
        4) Functions and properties are ignored (*)
        (*) you can create a hash function with different behaviour by using uniqueHashExt()

    To support hashing directly in one of your objects, implement

        __unique_hash__( length : int, parse_functions : bool, parse_underscore : str )

        The parameters are the same as for uniqueHashExt.
        The function is expected to return a hashable object, ideally a string.
    """
    return UniqueHash(16)(*args,**argv)

def uniqueHash32( *args, **argv ) -> str:
    """
    Compute a unique ID of length 32 for the provided arguments.
    The function
        1) uses the repr() function to feed objects to the hash algorithm.
           that means is only distinguishes floats up to str conversion precision
        2) keys of dictionaries, and sets are sorted to ensure equality of hashes
           accross different memory setups of strings
        3) Members with leading '_' are ignored (*)
        4) Functions and properties are ignored (*)
        (*) you can create a hash function with different behaviour by using uniqueHashExt()

    To support hashing directly in one of your objects, implement

        __unique_hash__( length : int, parse_functions : bool, parse_underscore : str )

        The parameters are the same as for uniqueHashExt.
        The function is expected to return a hashable object, ideally a string.
    """
    return UniqueHash(32)(*args,**argv)

uniqueHash = uniqueHash32

def uniqueHash48( *args, **argv ) -> str:
    """
    Compute a unique ID of length 48 for the provided arguments.
    The function
        1) uses the repr() function to feed objects to the hash algorithm.
           that means is only distinguishes floats up to str conversion precision
        2) keys of dictionaries, and sets are sorted to ensure equality of hashes
           accross different memory setups of strings
        3) Members with leading '_' are ignored (*)
        4) Functions and properties are ignored (*)
        (*) you can create a hash function with different behaviour by using uniqueHashExt()

    To support hashing directly in one of your objects, implement

        __unique_hash__( length : int, parse_functions : bool, parse_underscore : str )

        The parameters are the same as for uniqueHashExt.
        The function is expected to return a hashable object, ideally a string.
    """
    return UniqueHash(48)(*args,**argv)

def uniqueHash64( *args, **argv ) -> str:
    """
    Compute a unique ID of length 64 for the provided arguments.
    The function
        1) uses the repr() function to feed objects to the hash algorithm.
           that means is only distinguishes floats up to str conversion precision
        2) keys of dictionaries, and sets are sorted to ensure equality of hashes
           accross different memory setups of strings
        3) Members with leading '_' are ignored (*)
        4) Functions and properties are ignored (*)
        (*) you can create a hash function with different behaviour by using uniqueHashExt()

    To support hashing directly in one of your objects, implement

        __unique_hash__( length : int, parse_functions : bool, parse_underscore : str )

        The parameters are the same as for uniqueHashExt.
        The function is expected to return a hashable object, ideally a string.
    """
    return UniqueHash(64)(*args,**argv)
