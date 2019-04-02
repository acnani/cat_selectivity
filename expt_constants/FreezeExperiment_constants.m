function C = FreezeExperiment_constants
C.CAT_NAME            = 'Freeze';
C.REPS_PER_SET        = [150 175 275];
C.STIM_FREQUENCY      = 58;
C.STIMULATOR_TYPE     = 'iz2';
C.BUFFER_TYPE         = 'ripple';
C.STIM_EVENT_CHANNEL  = 2;
C.IRIG_CHANNEL        = 3;
% =========================================================================
% ANALYSIS PARAMETERS 
% =========================================================================
C.SLIDING_WINDOW_DURATION = 250e-6;
C.SLIDING_WINDOW_STEP     = 25e-6;
C.RMS_THRESHOLD_MULTIPLIER = 0;
C.MIN_RESPONSE_LATENCY    = 1e-3;
% =========================================================================
% TRIPOLAR PARAMETERS
% =========================================================================

cuff_mapping    = { ...
    0 'Femoral Proximal'
    1 'Femoral Disistal.'
    6 'Sciatic Proximal' 
    5 'Sciatic Distal' 
    };
% WE ARE CURRENTLY IGNORING THE FEMORAL TRUNK
% cuff_mapping               = cuff_mapping(3:4,:);

C.TRIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.TRIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}]+256;
C.TRIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';
C.TRIPOLAR.FILTER_PIPELINE = { ...
    ButterworthFilterSpec('filtfiltm',2,600,'highpass')};
% Whether or not the selected channel is inverted before evaluating 
C.TRIPOLAR.UPSAMPLE       = 10;
C.TRIPOLAR.INVERT_CHANNEL = {[false false] [false false]};

% =========================================================================
% BIPOLAR PARAMETERS
% =========================================================================

cuff_mapping = { ...
    2  'Med Fem'
    3  'Mid Fem'   
    4  'Lat Fem'
    7  'Cmn Per'
    8  'Tibial'
    9  'Med Gas'
    10 'Lat Gas'
    11 'Dist Tib'
    12 'Sens Branch'
    13 'Dist Cmn Per'
    14 'M.D. Cmn Per'
    15 'L.D. Cmn Per'
    };

% WE ARE CURRENTLY IGNORING THE FEMORAL BRANCHES
cuff_mapping(1:3,:) = [];

C.BIPOLAR.CUFF_COLORS     = '';
C.BIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.BIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}]+256;
C.BIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';
C.BIPOLAR.UPSAMPLE       = 2;
C.BIPOLAR.FILTER_PIPELINE = {...
    ButterworthFilterSpec('filtfiltm',2,600,'high')};

% =========================================================================
% EMG PARAMETERS
% =========================================================================

emg_mapping = {...
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
    10  'R. VL'
    11  'R. Sart'
    12  'R. LG'
    13  'R. MG'
    14  'R. BiFem'
    15  'R. SemiT'
    };

% emg_mapping = emg_mapping(8,:);

C.EMG_TYPE     = 'surfd_raw';
C.EMG_CHANNELS = [emg_mapping{:,1}];
C.EMG_LABELS   = emg_mapping(:,2)';
C.EMG_FILTER_PIPELINE = {ButterworthFilterSpec('filtfilt',2,70,'high')};
%{ ...
   % ButterworthFilterSpec('filtfiltm',2,70,'high')};
%     ButterworthFilterSpec('filtfiltm',2,1,'high')
%     ButterworthFilterSpec('filtfiltm',2,[55 65],'stop')};
end