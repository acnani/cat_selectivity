function C = GalactusExperiment_constants
C.CAT_NAME            = 'Galactus';
C.REPS_PER_SET        = [150 175 275];
C.STIM_FREQUENCY      = 58;
C.FREQUENCY_RANGE     = [50 150];
C.STIMULATOR_TYPE     = 'iz2';
C.BUFFER_TYPE         = 'ripple';
C.STIM_EVENT_CHANNEL  = 2;
C.IRIG_CHANNEL        = 3;
C.MAX_CHANNELS        = 4;
% =========================================================================
% ANALYSIS PARAMETERS 
% =========================================================================
C.SLIDING_WINDOW_DURATION  = 250e-6;
C.SLIDING_WINDOW_STEP      = 25e-6;
C.RMS_THRESHOLD_MULTIPLIER = 1;
C.MIN_RESPONSE_LATENCY     = 1e-3;
% =========================================================================
% TRIPOLAR PARAMETERS
% =========================================================================

cuff_mapping    = { ...
    14 'Femoral Proximal'
    15 'Femoral Disistal'
    5 'Sciatic Proximal' 
    4 'Sciatic Distal' 
    };
C.TRIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.TRIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}];
C.TRIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';
C.TRIPOLAR.UPSAMPLE        = 10;
C.TRIPOLAR.FILTER_PIPELINE = { ...
    ButterworthFilterSpec('filtfiltm',2,300,'highpass')};
% Whether or not the selected channel is inverted before evaluating 

C.TRIPOLAR.INVERT_CHANNEL = {[false false] [false false]};

% =========================================================================
% BIPOLAR PARAMETERS
% =========================================================================    
cuff_mapping = { ...
    0  'Dist Tib'
    1  'Cmn Per'
    2  'Sural'
    3  'Lat Gas'
    6  'Med Gas'
    7  'BiFem'
    8  'Tibial'
    9  'Dist Cmn Per'
    10 'VMed'
    11 'VLat'
    12 'Sart'
    13 'Saph'
    };
    
C.BIPOLAR.CUFF_COLORS     = '';
C.BIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.BIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}];
C.BIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';

C.BIPOLAR.UPSAMPLE        = 2;
C.BIPOLAR.FILTER_PIPELINE = {ButterworthFilterSpec('filtfiltm',2,400,'high')};

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