from tqdm.auto import tqdm

from naplib import logger
from ..data import Data

ACCEPTED_CROP_BY = ['onset', 'durations']

def load_bids(root,
              subject,
              datatype,
              task,
              suffix,
              session=None,
              befaft=[0, 0],
              crop_by='onset',
              info_include=['sfreq', 'ch_names'],
              resp_channels=None):
    '''
    Load data from the `BIDS file structure <https://bids.neuroimaging.io/>`_ [1]
    to create a Data object. The BIDS file structure is a commonly used structure
    for storing neural recordings such as EEG, MEG, or iEEG.
    
    The channels in the BIDS files are either stored in the 'resp' field of the
    Data object or the 'stim' field, depending on whether the `channel_type` is 'stim'.
    
    Parameters
    ----------
    root : string, path-like
        Root directory of BIDS file structure.
    datatype : string
        Likely one of ['meg','eeg','ieeg'].
    task : string
        Task name.
    suffix : string
        Suffix name in file naming. This is often the same as datatype.
    session : string
        Session name.
    befaft : list or array-like or length 2, default=[0, 0]
        Amount of time (in sec.) before and after each trial's true duration to include
        in the trial for the Data. For example, if befaft=[1,1] then if each trial's
        recording is 10 seconds long, each trial in the resulting Data object will contain
        12 seconds of data, since 1 second of recording before the onset of the event
        and 1 second of data after the end of the event are included on either end.
    crop_by : string, default='onset'
        One of ['onset', 'durations']. If crop by 'onset', each trial is split
        by the onset of each event defined in the BIDS file structure and each
        trial ends when the next trial begins. If crop by 'durations', each trial is split
        by the onset of each event defined in the BIDS file structure and each
        trial lasts the duration specified by the event. This is typically not desired
        when the events are momentary stimulus presentations that have very short duration
        because only the responses during the short duration of the event will be saved, and
        all of the following responses are truncated.
    info_include : list of strings, default=['sfreq, ch_names']
        List of metadata info to include from the raw info. For example, you may wish to include
        other items such as 'file_id', 'line_freq', etc, for later use, if they are stored in
        the BIDS data.
    resp_channels : list, default=None
        List of channel names to select as response channels to be put in the 'resp' field of
        the Data object. By default, all channels which are not of type 'stim' will be included.
        Note, the order of these channels may not be conserved.
    
    Returns
    -------
    out : Data
        Event/trial responses, stim, and other basic data in naplib.Data format.
        
    Notes
    -----
    The measurement information that is read-in by this function is stored in the Data.mne_info
    attribute. This info can be used in conjunction with
    `mne's visualization functions <https://mne.tools/stable/visualization.html>`_. 
    
    References
    ----------
    .. [1] Pernet, Cyril R., et al. "EEG-BIDS, an extension to the brain imaging
        data structure for electroencephalography." Scientific data 6.1 (2019): 1-5.
    '''
    
    try:
        from mne_bids import BIDSPath, read_raw_bids
    except Exception:
        raise Exception(
            'Missing package MNE-BIDS which is required for reading data from BIDS. Please '
            'install it with "pip install --user -U mne-bids" or by following the instructions '
            'at https://mne.tools/mne-bids/stable/install.html'
        )
    
    if crop_by not in ACCEPTED_CROP_BY:
        raise ValueError(f'Invalid "crop_by" input. Expected one of {ACCEPTED_CROP_BY} but got "{crop_by}"')
    
    bids_path = BIDSPath(subject=subject, root=root, session=session, task=task,
                         suffix=suffix, datatype=datatype)
    
    raw = read_raw_bids(bids_path=bids_path)
            
    raws = _crop_raw_bids(raw, crop_by, befaft)
    
    raw_info = None
    
    # figure out which channels are stimulus channels
    stim_channels = [ch for ch, ch_type in zip(raw.ch_names, raw.get_channel_types()) if ch_type == 'stim']

    # for each trial, separate into stim and response channels
    raw_responses = []
    raw_stims = []
    for raw_trial in raws:
        raw_resp = raw_trial.copy().drop_channels(stim_channels)
        if resp_channels is not None:
            raw_resp = raw_resp.pick_channels(resp_channels)
        raw_responses.append(raw_resp)
        
        if raw_info is None:
            raw_info = raw_resp.info

        # if any of the channels are 'stim' channels, store them separately from responses
        if 'stim' in raw_trial.get_channel_types():
            raw_stims.append(raw_trial.pick_types(stim=True))
        else:
            raw_stims.append(None)
    
    # build Data
    new_data = []
    for trial in tqdm(range(len(raws))):
        trial_data = {}
        trial_data['event_index'] = trial
        if 'description' in raw_responses[trial].annotations[0]:
            trial_data['description'] = raw_responses[trial].annotations[0]['description']
        if raw_stims[trial] is not None:
            trial_data['stim'] = raw_stims[trial].get_data().transpose(1,0) # time by channels
            trial_data['stim_ch_names'] = raw_stims[trial].info['ch_names']
        trial_data['resp'] = raw_responses[trial].get_data().transpose(1,0) # time by channels
        trial_data['befaft'] = befaft
        for info_key in info_include:
            if info_key not in info_include:
                logger.warning(f'info_include key "{info_key}" not found in raw info')
            else:
                trial_data[info_key] = raw_responses[trial].info[info_key]
        new_data.append(trial_data)  

    data_ = Data(new_data, strict=False)
    data_.set_mne_info(raw_info)
    return data_
    
    
def _crop_raw_bids(raw_instance, crop_by, befaft):
    '''
    Crop the raw data to trials based on events in its annotations.
    
    Parameters
    ----------  
    raw_instance : mne.io.Raw-like object
    
    crop_by : string, default='onset'
        One of ['onset', 'annotations']. If crop by 'onset', each trial is split
        by the onset of each event defined in the BIDS file structure and each
        trial ends when the next trial begins. If crop by 'annotations', each trial is split
        by the onset of each event defined in the BIDS file structure and each
        trial lasts the duration specified by the event. This is typically not desired
        when the events are momentary stimulus presentations that have very short duration
        because only the responses during the short duration of the event will be saved, and
        all of the following responses are truncated.
    
     Returns
     -------
     raws : list
         The cropped raw objects.

    '''

    max_time = (raw_instance.n_times - 1) / raw_instance.info['sfreq']
    
    raws = []
    for i, annot in enumerate(raw_instance.annotations):
        onset = annot["onset"] - raw_instance.first_time - befaft[0]
        if -raw_instance.info['sfreq'] / 2 < onset < 0:
            onset = 0
        if crop_by == 'onset':
            if i == len(raw_instance.annotations)-1:
                tmax = max_time
            else:
                if befaft[1] > 0:
                    logger.warning('befaft[1] is positive, but crop_by is "onset", so the ending of each trial will include a portion of the next trial')
                tmax = raw_instance.annotations[i+1]["onset"] + befaft[1]
            tmax = min([tmax, max_time])
            raw_crop = raw_instance.copy().crop(onset, tmax)
        
        else:
            tmax = onset + annot["duration"] + befaft[1]
            tmax = min([tmax, max_time])
            raw_crop = raw_instance.copy().crop(onset, tmax)
        
        raws.append(raw_crop)
    
    return raws
