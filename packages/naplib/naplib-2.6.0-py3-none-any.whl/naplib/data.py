from collections.abc import Iterable
from itertools import groupby
from copy import deepcopy
import numpy as np
from mne import Info


STRICT_FIELDS_REQUIRED = set(['name','sound','soundf','resp','dataf'])


class Data(Iterable):
    '''
    Class for storing electrode response data along with
    task- and electrode-related variables. Under the hood, it consists
    of a list of dictionaries where each dictionary contains all the data
    for one trial.
    
    Parameters
    ----------
    data : dict or list of dictionaries
        If a list of dicts, then the Nth dictionary defines the Nth trial data, typically
        corresponding to the Nth stimulus. Each dictionary must contain the same keys if
        passed in as a list of multiple trials. If a single dict, then the keys specify the
        field names and the values specify the data across trials, and each value must be
        a list of length num_trials.
    strict : bool, default=False
        If True, requires strict adherance to the following standards:
        1) Each trial must contain at least the following fields:
        ['name','sound','soundf','resp','dataf']
        2) Each trial must contain the exact same set of fields
    
    Attributes
    ----------
    fields : list of strings
        Field names in the data.
    mne_info : mne.Info instance
        Measurement info object containing things like electrode locations
        (only if Data is created from reading a file format like BIDS).
    info : dict
        Extra info (not trial-specific) that a user wants to store
        using Data.set_info or Data.update_info

    Notes
    -----
    .. figure:: /figures/naplib-python-data-figure.png
        :width: 500px
        :alt: Data object layout
        :align: center

    The above is a depiction of the type of data that might be stored in an
    instance of the Data class. Any number of trials can be stored with any
    number and type of fields. Responses and information do not need to be
    aligned or the same length/shape across trials. Information can be retrieved
    from the Data instance by trial, by field, or by a combination of the two,
    using bracket indexing and slicing, as described below.

    Examples
    --------
    >>> import naplib as nl
    >>> import numpy as np
    >>> # Constructing Data from a dict, where keys give fields and values are lists of trial data
    >>> names = ['trial1', 'trial2'] # trial names
    >>> responses = [np.arange(6).reshape(3,2), np.arange(6,12).reshape(3,2)] # neural responses
    >>> dataf = [100, 100] # sampling rate
    >>> data = nl.Data({'name': names, 'resp': responses, 'dataf': dataf})
    >>> data
    Data object of 2 trials containing 3 fields
    [{"name": <class 'str'>, "resp": <class 'numpy.ndarray'>, "dataf": <class 'int'>}
    {"name": <class 'str'>, "resp": <class 'numpy.ndarray'>, "dataf": <class 'int'>}]
    >>> # Accessing a single trial returns a view of one trial as a dict
    >>> data[1]
    {'name': 'trial2',
     'resp': array([[ 6,  7],
            [ 8,  9],
            [10, 11]]),
     'dataf': 100}
    >>> # Accessing a single field returns a shallow copy of that field as a list over trials
    >>> data['name']
    ['trial1', 'trial2']
    >>> # Accessing multiple fields returns a shallow copy of those fields within a Data instance
    >>> data[['resp', 'dataf']]
    Data object of 2 trials containing 2 fields
    [{"resp": <class 'numpy.ndarray'>, "dataf": <class 'int'>}
    {"resp": <class 'numpy.ndarray'>, "dataf": <class 'int'>}]
    >>> # Accessing multiple trials with slice indexing returns a shallow copy of those
    >>> # trials in a Data instance
    >>> data[:2]
    Data object of 2 trials containing 3 fields
    [{"name": <class 'str'>, "resp": <class 'numpy.ndarray'>, "dataf": <class 'int'>}
    {"name": <class 'str'>, "resp": <class 'numpy.ndarray'>, "dataf": <class 'int'>}]
    '''
    def __init__(self, data, strict=False):

        if isinstance(data, dict):
            lengths = []
            for k, v in data.items():
                if not isinstance(v, list):
                    raise TypeError(
                        f'When creating a Data from a dict, each value in the '
                        f'dict must be a list, but for key "{k}" got type {type(v)}'
                    )
                lengths.append(len(v))
            if not _all_equal_list(lengths):
                raise ValueError(
                    f'When creating a Data from a dict, each value in the '
                    f'dict must be a list of the same length, but got different lengths: {lengths}'
                )
            data = [dict(zip(data, vals)) for vals in zip(*data.values())]
            self._data = data
        elif isinstance(data, list):
            self._data = data
        else:
            raise TypeError(f'Can only create Data from a dict or a list '
                            f'of dicts, but found type {type(data)}')
        self._strict = strict
        self._validate_new_out_data(data, strict=strict)
        self._info = {}
        self._mne_info = None

    def set_field(self, fielddata, fieldname):
        '''
        Set the information in a single field with a new list of data.

        Parameters
        ----------
        fielddata : list
            List containing data to add to each trial for this field. Must 
            be same length as this object
        fieldname : string
            Name of field to add. If this field already exists in the Data
            then the current field will be overwritten.
        '''
        if not isinstance(fielddata, list):
            raise TypeError(f'Input data must be a list, but found {type(fielddata)}')
        if len(fielddata) != len(self):
            raise Exception(f'Length of field ({len(fielddata)}) is not equal to length of this Data ({len(self)})')
        for i, trial in enumerate(self.data):
            trial[fieldname] = fielddata[i]

    def delete_field(self, fieldname):
        '''
        Remove an entire field from the Data object.

        Parameters
        ----------
        fieldname : string
            Name of field to delete.
        '''
        if not isinstance(fieldname, str):
            raise TypeError(f'Field must be a str, but found {type(fieldname)}')
        for trial in self.data:
            del trial[fieldname]
    
    def get_field(self, fieldname):
        '''
        Return all trials for a single field.
        
        Parameters
        ----------
        fieldname : string
            Which field to get.
        Returns
        -------
        field : list
            List containing each trial's value for this field.
        '''
        try:
            return [tmp[fieldname] for tmp in self.data]
        except KeyError:
            raise KeyError(f'Invalid fieldname: {fieldname} not found in data.')
    
    def __getitem__(self, index):
        '''
        Get either a trial or a field using bracket indexing. See notes and examples
        below for details.

        Parameters
        ----------
        index : int or string
            Which trial to get, or which field to get.

        Returns
        -------
        data : dict, list, or Data
            If index is an integer, returns the corresponding trial as a dict. If index
            is a string, returns the corresponding field, and if it is a list of strings,
            returns those fields together in a new Data object.

        Note
        ----
        Depending on how indexing and slicing is performed, the data returned may be a view of
        the underlying data, or it may be a shallow copy of the underlying data. The only way
        to get a view of the underlying data, meaning editing that view will also edit the
        underlying data, is to use integer indexing to get a single trial from the Data instance,
        which returns a dict for that trial. Indexing by field name first and indexing with slicing
        both return shallow copies of the data.

        For example, if we want to set the 'name' field in the first trial of our Data, we can only
        do it in the following way:

        >>> data[0]['name'] = 'trial0'

        Whereas following code will NOT actually change the underlying trial name:

        >>> data['name'][0] = 'trial0'

        Examples
        --------
        >>> # Get a specific trial based on its index, which returns a dict
        >>> from naplib import Data
        >>> trial_data = [{'name': 'Zero', 'trial': 0, 'resp': [[0,1],[2,3]]},
        ...               {'name': 'One', 'trial': 1, 'resp': [[4,5],[6,7]]}]
        >>> data = Data(trial_data, strict=False)
        >>> data[0]
        {'name': 'Zero', 'trial': 0, 'resp': [[0, 1], [2, 3]]}

        >>> # Get a slice of trials, which returns a shallow copy of those trials in a Data instance
        >>> out[:2]
        Data object of 2 trials containing 3 fields
        [{"name": <class 'str'>, "trial": <class 'int'>, "resp": <class 'list'>}
        {"name": <class 'str'>, "trial": <class 'int'>, "resp": <class 'list'>}]

        >>> # Get a list of trial data from a single field, which returns a shallow copy of
        >>> # each trial in that field
        >>> data['name']
        ['TrialZero', 'TrialOne']

        >>> # Get a single trial with integer indexing, returning a view of that trial as a dict
        >>> data[0]
        {'name': 'TrialZero', 'trial': 0, 'resp': [[0, 1], [2, 3]]}

        >>> # Get multiple fields using a list of fieldnames, which returns a shallow copy of that
        >>> # subset of fields
        >>> data[['resp','trial']]
        Data object of 2 trials containing 2 fields
        [{"resp": <class 'list'>, "trial": <class 'int'>}
        {"resp": <class 'list'>, "trial": <class 'int'>}]
        '''
        if isinstance(index, slice):
            return Data(self.data[index], strict=self._strict)
        if isinstance(index, str):
            return self.get_field(index)
        if isinstance(index, (list, np.ndarray)):
            if isinstance(index[0], str):
                return Data([{field:x[field] for field in index} for x in self], strict=False)
            else:
                return Data([self.data[i] for i in index], strict=False)
        try:
            return self.data[index]
        except IndexError:
            raise IndexError(f'Index invalid for this data. Tried to index {index} but length is {len(self)}.')
    
    def __setitem__(self, index, data):
        '''
        Set a specific trial or set of trials, or set a specific field, using
        bracket indexing. See examples below for details.

        Parameters
        ----------
        index : int or string
            Which trial to set, or which field to set. If an integer, must be <= the
            length of the Data, since you can only set a currently existing trial
            or append to the end, but you cannot set a trial that is beyond that. 
        data : dict or list of data
            Either trial data to add or field data to add. If index is an
            integer, dictionary should contain all the same fields as
            current Data object.

        Examples
        --------
        >>> # Set a field of a Data
        >>> from naplib import Data
        >>> trial_data = [{'name': 'Zero', 'trial': 0, 'resp': [[0,1],[2,3]]},
        ...               {'name': 'One', 'trial': 1, 'resp': [[4,5],[6,7]]}]
        >>> data = Data(trial_data)
        >>> data[0] = {'name': 'New', 'trial': 10, 'resp': [[0,-1],[-2,-3]]}
        >>> data[0]
        {'name': 'New', 'trial': 10, 'resp': [[0, -1], [-2, -3]]}

        >>> # We can also set all values of a field across trials
        >>> data['name'] = ['TrialZero','TrialOne']
        >>> data['name']
        ['TrialZero', 'TrialOne']
        '''
        if isinstance(index, str):
            self.set_field(data, index)
        else:
            if index > len(self):
                raise IndexError((f'Index is too large. Current data is length {len(self)} '
                    'but tried to set index {index}. If you want to add to the end of the list '
                    'of trials, use the Data.append() method.'))

            if index == len(self):
                self.append(data)
            else:
                self.data[index] = data

    def __delitem__(self, index):
        '''
        Delete a specific trial or set of trials, or delete a specific field, using
        bracket indexing. See examples below for details.

        Parameters
        ----------
        index : int or string
            Which trial to delete, or which field to delete. If an integer, must be 
            < the length of the Data, since you can only delete an existing trial 

        Examples
        --------
        >>> # Delete a field of a Data
        >>> from naplib import Data
        >>> trial_data = [{'name': 'Zero', 'trial': 0, 'resp': [[0,1],[2,3]]},
        ...               {'name': 'One', 'trial': 1, 'resp': [[4,5],[6,7]]}]
        >>> data = Data(trial_data)
        >>> del data[0]
        >>> data[0]
        {'name': 'One', 'trial': 1, 'resp': [[4, 5], [6, 7]]}

        >>> # We can also delete all values of a field across trials
        >>> trial_data = [{'name': 'Zero', 'trial': 0, 'resp': [[0,1],[2,3]]},
        ...               {'name': 'One', 'trial': 1, 'resp': [[4,5],[6,7]]}]
        >>> data = Data(trial_data)
        >>> del data['name']
        >>> data[0]
        {'trial': 0, 'resp': [[0, 1], [2, 3]]}
        '''
        if isinstance(index, str):
            self.delete_field(index)
        elif isinstance(index, int):
            if index >= len(self):
                raise IndexError((f'Index is too large. Current data is length {len(self)} '
                    'but tried to delete index {index}. If you want to add to the end of the list '
                    'of trials, use the Data.append() method.'))
            else:
                del self.data[index]
        else:
            raise TypeError(f'Found {type(index)} for index')

    def append(self, trial_data, strict=None):
        '''
        Append a single trial of data to the end of a Data.
        
        Parameters
        ----------
        trial_data : dict
            Dictionary containing all the same fields as current Data object.
        strict : bool, default=self._strict
            If true, enforces that new data contains the exact same set of fields as
            the current Data. Default value is self._strict, which is set based
            on the input when creating a new Data from scratch with __init__()

        Raises
        ------
        TypeError
            If input data is not a dict.
        ValueError
            If strict is `True` and the fields contained in the trial_data do
            not match the fields currently stored in the Data.

        Examples
        --------
        >>> # Set a field of a Data
        >>> from naplib import Data
        >>> trial_data = [{'name': 'Zero', 'trial': 0, 'resp': [[0,1],[2,3]]},
        ...               {'name': 'One', 'trial': 1, 'resp': [[4,5],[6,7]]}]
        >>> data = Data(trial_data)
        >>> new_trial_data = {'name': 'Two', 'trial': 2, 'resp': [[8,9],[10,11]]}
        >>> data.append(new_trial_data)
        >>> len(data)
        3
        '''
        if strict is None:
            strict = self._strict
        self._validate_new_out_data([trial_data], strict=strict)
        self.data.append(trial_data)
        
    def set_info(self, info):
        '''
        Set the info dict for this Data. If there is already data in the
        `info` attribute, it is replaced with this.
        
        Parameters
        ----------
        info : dict
            Dictionary containing info to store in the Data's `info` attribute.
            
        '''
        if not isinstance(info, dict):
            raise TypeError(f'info must be a dict but got {type(info)}')
        self._info = info
        
    def update_info(self, info):
        '''
        Add data from a dict to this object's `info` attribute. If there is already data in the
        `info` attribute, this new info is simply added. Keys which exist in the current
        `info` dict and also in this new dict will be replaced, while others will be kept.
        
        Parameters
        ----------
        info : dict
            Dictionary containing info to add to the Data's `info` attribute.
        '''
        self._info.update(info)
        
    def set_mne_info(self, info):
        '''
        Set the mne_info attribute, which contains measurement information.
        
        Parameters
        ----------
        info : mne.Info instance
            Info to set.
        '''
        if not isinstance(info, Info):
            raise TypeError(f'input info must be an instance of mne.Info, but got {type(info)}')
        self._mne_info = info
    
    def __iter__(self):
        return (self[i] for i in range(len(self)))

    def __len__(self):
        '''
        Get the number of trials in the Data object with ``len(Data)``.

        Examples
        --------
        >>> from naplib import Data
        >>> trial_data = [{'trial': 0, 'resp': [[0,1],[2,3]]},
                          {'trial': 1, 'resp': [[4,5],[6,7]]}]
        >>> data = Data(trial_data, strict=False)
        >>> len(data)
        2
        '''
        return len(self.data)
    
    def __repr__(self):
        return self.__str__() # until we can think of a better __repr__
    
    def __str__(self):
        to_return = f'Data object of {len(self)} trials containing {len(self.fields)} fields\n['
        to_print = 2 if len(self) > 3 else 3

        for trial_idx, trial in enumerate(self[:to_print]):
            fieldnames = list(trial.keys())
            to_return += '{'
            for f, fieldname in enumerate(fieldnames):
                to_return += f'"{fieldname}": {type(trial[fieldname])}'
                if f < len(fieldnames)-1:
                    to_return += ', '
            if trial_idx < len(self)-1:
                to_return += '}\n'
            else:
                to_return += '}'

        if to_print == 3:
            to_return += ']\n'
        elif to_print == 2:
            to_return += '\n...\n{'
            fieldnames = list(self[-1].keys())
            for f, fieldname in enumerate(fieldnames):
                to_return += f'"{fieldname}": {type(self[-1][fieldname])}'
                if f < len(fieldnames)-1:
                    to_return += ', '
            to_return += '}]\n'

        return to_return
    
    def _validate_new_out_data(self, input_data, strict=True):
        first_trial_fields = set(self.fields)
        for trial in input_data:
            if not isinstance(trial, dict):
                raise TypeError(f'input data is not a list of dicts, found {type(trial)}')
            trial_fields = set(trial.keys())
            if not trial_fields:
                raise ValueError('A trial should have at least one field.')
            if strict and trial_fields != first_trial_fields:
                raise ValueError('New data does not contain the same fields as the first trial.')
            if strict:
                for required_field in STRICT_FIELDS_REQUIRED:
                    if required_field not in trial_fields:
                        raise ValueError(f'For a "strict" Data object, the data does not contain the required field {required_field}.')
    
    @property
    def fields(self):
        '''List of strings containing names of all fields in this Data.'''
        return [k for k, _ in self._data[0].items()] if self._data else []
    
    @property
    def data(self):
        '''List of dictionaries containing data for each stimulus
        response and all associated variables.'''
        return self._data

    @property
    def info(self):
        '''Dictionary which can be used to store metadata info which does not
        change over trials, such as subject, recording, or task information.'''
        return self._info
    
    @property
    def mne_info(self):
        '''
        mne.Info instance
        which stores measurement information and can be used with mne's visualization
        functions. This is empty by default unless it is manually added or read in
        by a function like `naplib.io.load_bids`.
        '''
        if self._mne_info is None:
            raise ValueError('No mne_info is available for this Data. This must '
                             'be read in from external data or added manually to the Data.')
        return self._mne_info


def concat(data_list, axis=0, copy=True):
    '''
    Concatenate Data objects across either trials or fields.
    This performs an inner join on the other dimension, meaning
    non-shared fields will be lost if concatenating over trials,
    and non-shared trials will be lost if concatenating over fields.
    If concatenating over fields and there are shared fields, then
    the field will only be taken from the first Data object in
    the input sequence and the rest will be ignored.
    
    Note: anything stored in the .info or .mne_info attributes of the
    objects will not be stored in the output.
    
    Parameters
    ----------
    data : list or tuple of Data instances
        Sequence containing the different Data objects to concatenate.
    axis : int, defualt=0
        To concantate over trials (default), axis should be 0. To concatenate
        over fields, axis should be 1.
    copy : bool, default=True
        Whether to deep copy each Data object before concatenating.
    Returns
    -------
    data_merged : Data instance
        A Data instance of the two merged objects.
    
    Examples
    --------
    >>> import naplib as nl
    >>> # First, try concatenating over trials from two different Data objects
    >>> d1 = nl.Data({'name': ['t1','t2'], 'resp': [[1,2],[3,4,5]], 'extra': ['ex1','ex2']})
    >>> d2 = nl.Data({'name': ['t3','t4'], 'resp': [[6,7],[9,10]], 'extra': ['ex3','ex4']})
    >>> d_concat = nl.concat((d1, d2))
    >>> len(d_concat)
    4
    >>> d_concat.fields
    ['name', 'resp', 'extra']
    >>> d_concat['name']
    ['t1', 't2', 't3', 't4']
    >>> d_concat['resp']
    [[1, 2], [3, 4, 5], [6, 7], [9, 10]]
    >>> d_concat['extra']
    ['ex1', 'ex2', 'ex3', 'ex4']
    >>> # We can also concatenate over fields if we have two Data objects for the same trials
    >>> # Duplicate fields will only be kept from the first Data object that they appear in
    >>> d3 = nl.Data({'name': ['t1-1','t2-1'], 'resp': [[1,2],[3,4,5]]})
    >>> d4 = nl.Data({'name': ['t1-2','t2-2'], 'meta_data': ['meta1', 'meta2']})
    >>> d_concat = nl.concat((d3, d4), axis=1)
    >>> len(d_concat)
    2
    >>> d_concat.fields
    ['name', 'resp', 'meta_data']
    >>> d_concat['name']
    ['t1-1', 't2-1']
    >>> d_concat['resp']
    [[1, 2], [3, 4, 5]]
    >>> d_concat['meta_data']
    ['meta1', 'meta2']
    '''
    if not isinstance(data_list, (list, tuple)):
        raise TypeError(f'data_list must be a list or tuple but got {type(data_list)}')
        
    if len(data_list) == 0:
        raise ValueError('need at least one Data object to concatenate')
        
    for out in data_list:
        if not isinstance(out, Data):
            raise TypeError(f'All inputs to data_list must be a Data instance but found {type(out)}')

    if len(data_list) == 1:
        return data_list[0]
    
    if axis == 0:
        field_set = set(data_list[0].fields)
        for data in data_list[1:]:
            field_set = field_set.intersection(set(data.fields))
        field_set = [ff for ff in data_list[0].fields if ff in field_set]
        
        if copy:
            data_merged = deepcopy(data_list[0][field_set])
        else:
            data_merged = data_list[0][field_set]
            
        for data in data_list[1:]:
            if copy:
                copied_data = deepcopy(data[field_set])
            else:
                copied_data = data[field_set]
            for trial in copied_data:
                data_merged.append(trial, strict=False)
        
    elif axis == 1:
        if not all(len(data_list[0])==len(d) for d in data_list):
            raise ValueError('All Data objects must be same length if concatenating over fields (axis=1).')
            
        if copy:
            data_merged = deepcopy(data_list[0])
        else:
            data_merged = data_list[0]
            
        for data in data_list[1:]:
            current_fields = data_merged.fields
            for field in data.fields:
                if field not in current_fields:
                    data_merged[field] = data[field]

    else:
        raise ValueError(f'axis must be 0 or 1 but got {axis}')
        
    return data_merged
    
def join_fields(data_list, fieldname='resp', axis=-1, return_as_data=False):
    '''
    Join trials from a field in multiple Data objects by zipping them
    together and concatenating each trial together. The field must be of type
    np.ndarray and concatenation is done with np.concatenate().
    
    Parameters
    ----------
    data : sequence of Data instances
        Sequence containing the different Data objects to join.
    fieldname : string, default='resp'
        Name of the field to concatenate from each Data object. For each trial in
        each Data instance, this field must be of type np.ndarray or something which
        can be input to np.concatenate().
    axis : int, default = -1
        Axis along which to concatenate each trial's data. The default corresponds
        to the channel dimension of the conventional 'resp' field of a Data object.
    return_as_data : bool, default=False
        If True, returns data as a Data object with a single field named fieldname.

    Returns
    -------
    joined_data : list of np.ndarrays, or Data instance
        Joined data of same length as each of the Data objects containing concatenated data
        for each trial.

    Examples
    --------
    >>> import naplib as nl
    >>> data1 = nl.Data({'resp': [np.array([0,1,2]).reshape(-1,1), np.array([3,4]).reshape(-1,1)]})
    >>> data2 = nl.Data({'resp': [np.array([5,6,7]).reshape(-1,1), np.array([8,9]).reshape(-1,1)]})
    >>> data1
    [array([[0],
            [1],
            [2]]),
     array([[3],
            [4]])]
    >>> data2
    [array([[5],
            [6],
            [7]]),
     array([[8],
            [9]])]
    >>> resp_joined = nl.join_fields((data1, data2))
    >>> resp_joined
    [array([[0, 5],
            [1, 6],
            [2, 7]]),
     array([[3, 8],
            [4, 9]])]
    >>> resp_joined2 = nl.join_fields((data1, data2), axis=0)
    >>> resp_joined2
    [array([[0],
            [1],
            [2],
            [5],
            [6],
            [7]]),
     array([[3],
            [4],
            [8],
            [9]])]
    '''
    
    for out in data_list:
        if not isinstance(out, Data):
            raise TypeError(f'All inputs to data_list must be Data instance but found {type(out)}')
        field = out.get_field(fieldname)
        if not isinstance(field[0], np.ndarray):
            raise TypeError(f'Can only concatenate np.ndarrays, but found {type(field[0])} in this field')

    starting_fields = [out.get_field(fieldname) for out in data_list] # each one should be a list of np.arrays
    
    to_return = []
    
    zipped_fields = list(zip(*starting_fields))
    for field_set in zipped_fields:
        to_return.append(np.concatenate(field_set, axis=axis))
        
    if return_as_data:
        return Data([dict([(fieldname, x)]) for x in to_return], strict=False)
    return to_return
        
def _all_equal_list(iterable):
    g = groupby(iterable)
    return next(g, True) and not next(g, False)
