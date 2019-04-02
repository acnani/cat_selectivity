function C = experiment_constants
C.CAT_NAME            = 'HA02';
C.BUFFER_TYPE         = 'ripple';
C.IRIG_CHANNEL        = 3;
C.MAX_CHANNELS        = 4;
% =========================================================================
% STIMULATION PARAMETERS 
% =========================================================================
C.REPS_PER_SET        = [150 175 275];     % ACN currently only works for length==1 when grapevine stim is used
C.STIM_FREQUENCY      = 58;
C.FREQUENCY_RANGE     = [50 150];
C.STIMULATOR_TYPE     = 'grapevine';       % iz2/grapevine
C.STIM_EVENT_CHANNEL  = 2;    % 2
% =========================================================================
% ANALYSIS PARAMETERS 
% =========================================================================
C.SLIDING_WINDOW_DURATION  = 250e-6;
C.SLIDING_WINDOW_STEP      = 25e-6;
C.RMS_THRESHOLD_MULTIPLIER = 0;
C.MIN_RESPONSE_LATENCY     = 1e-3;
% =========================================================================
% TRIPOLAR PARAMETERS
% =========================================================================

cuff_mapping    = { ...
    15 'Femoral Proximal'
    16 'Femoral Distal'
    13 'Sciatic Proximal' 
    14 'Sciatic Distal' 
    };
C.TRIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.TRIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}];
C.TRIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';
C.TRIPOLAR.UPSAMPLE        = 10;
C.TRIPOLAR.FILTER_PIPELINE = { ...
    ButterworthFilterSpec('filtfiltm',2,300,'highpass')};
% Whether or not the selected channel is inverted before evaluating 

C.TRIPOLAR.INVERT_CHANNEL = {[false false ] [false false ]};

% =========================================================================
% BIPOLAR PARAMETERS
% =========================================================================

cuff_mapping = { ...
    0   'Dist Cmn Per'
    1   'Lat Cut'
    2   'Med Cut'
    3   'VMed'
    4   'Dist Cmn Per 2'
    5   'Sart'
    6   'Cmn Per' 
    7   'Saph'
    8   'Tibial'
    9   'Lat Gas'
    10  'Dist Tib'
    11  'Med Gas'
    };
    % 4  'BiFem'
    
C.BIPOLAR.CUFF_COLORS     = '';
C.BIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.BIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}];
C.BIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';
C.BIPOLAR.UPSAMPLE        = 1;
C.BIPOLAR.FILTER_PIPELINE = {ButterworthFilterSpec('filterm',2,300,'highpass')};

% =========================================================================
% EMG PARAMETERS
% =========================================================================

EMG.mapping = {...
    0   'L. Sart'
    1   'L. Semi M'
    2   'L. Semi T'
    3   'L. MG'
    4   'L. LG'
    5   'L. BiFem'
    6   'L. TA'
    7   'L. EDL'
    8   'L VL'
    9   'L. TFL'
    };

% EMG.mapping = EMG.mapping(8,:);

C.EMG.TYPE     = 'surfd_raw';
C.EMG.CHANNELS = [EMG.mapping{:,1}];
C.EMG.LABELS   = EMG.mapping(:,2)';
C.EMG.UPSAMPLE = 10;
C.EMG.FILTER_PIPELINE = { ...
    ButterworthFilterSpec('filtfiltm',2,70,'high')};
end