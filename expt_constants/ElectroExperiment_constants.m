function C = ElectroExperiment_constants
C.CAT_NAME             = 'Electro';
C.REPS_PER_SET         = [150 175 275];
C.STIM_FREQUENCY       = 58;
C.STIMULATOR_TYPE      = 'iz2';
C.BUFFER_TYPE          = 'ripple';
C.STIM_EVENT_CHANNEL   = 2;
C.IRIG_CHANNEL         = 3;
C.MIN_RESPONSE_LATENCY = .25e-3;
C.SLIDING_WINDOW_DURATION = 250e-6;
C.SLIDING_WINDOW_STEP     = 25e-6;
C.RMS_THRESHOLD_MULTIPLIER = 0;
% =========================================================================
% TRIPOLAR PARAMETERS
% =========================================================================

cuff_mapping    = { ...
    0 'Femoral Proximal'
    1 'Femoral Distal'
    2 'Sciatic Proximal' 
    3 'Sciatic Distal' 
    };
% WE ARE CURRENTLY IGNORING THE FEMORAL TRUNK
% cuff_mapping               = cuff_mapping(3:4,:);

C.TRIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.TRIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}];
C.TRIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';
C.TRIPOLAR.UPSAMPLE        = 10;
C.TRIPOLAR.FILTER_PIPELINE = { ...
    ButterworthFilterSpec('filtfiltm',2,600,'highpass')};
% Whether or not the selected channel is inverted before evaluating 

C.TRIPOLAR.INVERT_CHANNEL = {[false false] [false false]};

% =========================================================================
% BIPOLAR PARAMETERS
% =========================================================================

cuff_mapping = { ...
    4  'Med Fem'
    5  'Mid Fem'   
    6  'Lat Fem'
    7  'Cmn Per'
    8  'Dist Cmn Per'
    10 'Lat Gas'
    11 'Med Gas'
    12 'Tibial'
    13 'Dist Tib'};

% WE ARE CURRENTLY IGNORING THE FEMORAL TRUNK
cuff_mapping(1:3,:) = [];

% C.BIPOLAR.CUFF_LABELS     = {{'Femoral' 'Lat. Fem (Sart)' 'Mid. Fem.' 'Med. Fem.'} ...
%     {'Sciatic' 'Semi. Ten.' 'Cmn. Per.' 'Tibial' 'Dis. Cmn. Pre.'}};
C.BIPOLAR.CUFF_COLORS     = '';
C.BIPOLAR.CUFF_TYPE       = 'surfd_raw';
C.BIPOLAR.CUFF_CHANNELS   = [cuff_mapping{:,1}];
C.BIPOLAR.CUFF_LABELS     = cuff_mapping(:,2)';
C.BIPOLAR.UPSAMPLE        = 2;
C.BIPOLAR.FILTER_PIPELINE = {...
    ButterworthFilterSpec('filtfiltm',2,600,'high')};

% =========================================================================
% EMG PARAMETERS
% =========================================================================

emg_mapping = {...
    0   'L. LG'
    1   'L. MG'
    2   'L. TA'
    3   'L. EDL'
    4   'L. VL'
    5   'L. Sart'
    6   'L. BiFem'
    7   'L. TFL'
    8   'L. SemiT'
    9   'L. SemiM'
    10  'R. VL'
    11  'R. Sart'
    12  'R. MG'
    13  'R. LG'
    14  'R. BiFem'
    15  'R. SemiM'
    };

% emg_mapping = emg_mapping(8,:);

C.EMG_TYPE     = 'surfd_raw';
C.EMG_CHANNELS = [emg_mapping{:,1}]+256;
C.EMG_LABELS   = emg_mapping(:,2)';
C.EMG_FILTER_PIPELINE = { ...
    ButterworthFilterSpec('filtfiltm',2,70,'high')};
%     ButterworthFilterSpec('filtfiltm',2,1,'high')
%     ButterworthFilterSpec('filtfiltm',2,[55 65],'stop')};
end