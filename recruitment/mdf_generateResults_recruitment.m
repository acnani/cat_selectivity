function [] = mdf_generateResults_recruitment(catName, session, block, varargin)
    
    varargin = sanitizeVarargin(varargin);
    DEFINE_CONSTANTS
    filtOrder                = 1;
    cutoffFreq               = 500; 
    stim_blanking_period     = 0.5e-3;     % sec
    K                        = 200;        % bootstrap bill turner!
    threshold_mult           = 1;
    windowSize_sec           = 2.5e-4;      % sec
    winDisplace              = 2.5e-5;      % sec
    minimum_response_latency = 1e-3;        % ms
    RMSfn                    = @(y) sqrt(mean(y.^2));
    bootstrap_thresh         = .95;
    do_stim_blanking         = true;
    log_results              = false;
    show_debug_plots         = false;
    
    
    
    END_DEFINE_CONSTANTS

    for iBlock = 1:length(block)
        try
            NotifierManager.notify('status','Processing %s_ssn%03d_blk%03d', catName, session, block{iBlock})
            blockObj = mdf.load('subject',catName,'mdf_type','trial','session',session,'block',block{iBlock});
            fs = blockObj.engData(1).fs;
            [bf, af] = butter(filtOrder, cutoffFreq/(fs/2), 'high');       % parametrize

            all_stim_chans = blockObj.stimChan.channels;
            unique_chans    = unique(all_stim_chans);
            nStimChannels = length(unique_chans);
            all_amps      = blockObj.stimChan.amplitude;
            unique_amps     = unique(all_amps);

            stimStep = length(blockObj.stimChan.stimTime)/length(blockObj.stimChan.amplitude);
            all_stim_times = blockObj.stimChan.stimTime(1:stimStep:end);
            extract_time_range = [0 .9*median(diff(all_stim_times))];  % the problem using this is that the frequency per channel is different from the global frequency due to randperm/staggering
            extract_samples = round(fs*diff(extract_time_range));

            stim_start = min(all_stim_times);
            stim_end   = max(all_stim_times);

            nAnalogChannels = length(blockObj.engData);
            allCuffs = [blockObj.engData.location];
            eng_time = blockObj.engData(1).time;
            baseline_start = eng_time(1);

            % STIM BLANKING
            if do_stim_blanking
                stim_time_idx  = round(all_stim_times*fs)-round(eng_time(1)*fs);
                blanking_idx   = bsxfun(@plus,stim_time_idx',[-2:ceil(stim_blanking_period*fs)+5]);     % parametrize
            else
                blanking_idx = [];
            end

            % EXTRACT BASELINE
            if eng_time(end)-stim_end >  stim_start-eng_time(1)
                baseline_mask = eng_time >= stim_end+1;
            else
                baseline_mask = eng_time >= baseline_start & eng_time < stim_start;
            end
            baseline_time = eng_time(baseline_mask);
            baseline_duration = floor(diff(baseline_time([1 end])));
            nBaselineReps = floor(baseline_duration*fs/extract_samples)-1;              % im being lazy and subtracting 1 instead of adding a check for whether the windows are within range later
            time_windows  = bsxfun(@plus,extract_time_range,baseline_time(1)+[1:nBaselineReps]'*diff(extract_time_range));
            idx_windows  = floor(time_windows*fs);

            for iChan = 1:nStimChannels

                for iAmp = 1:length(unique_amps)
                    NotifierManager.notify('status','stim channel: %d; amp: %0.1f',unique_chans(iChan), unique_amps(iAmp))
                    stimTimes = all_stim_times(all_amps == unique_amps(iAmp) & all_stim_chans == unique_chans(iChan));
                    stimIdx = floor(stimTimes * fs);
                    numStimsEvts = length(stimIdx);  % = nReps for a given amplitude
                    N = 0.8*numStimsEvts;            % partition #beyonce

                    % PROCESS EACH CUFF
                    for iCuff = 1:length(allCuffs)
                        dataObj = blockObj.engData(iCuff);              % ignore or run LCC for tripolar?
                        NotifierManager.notify('status','cuff: %s',blockObj.engData(iCuff).location)
                        eng_wf = dataObj.wf;
                        blanking_value = cell2mat(arrayfun(@(x) linspace(eng_wf(blanking_idx(x,1))',eng_wf(blanking_idx(x,end))',size(blanking_idx,2)), 1:size(blanking_idx,1),'Uniformoutput',false)');
                        eng_wf(blanking_idx(:)) = blanking_value(:);
                        eng_wf = filtfilt(bf,af,eng_wf);

                        % GET BASELINE AND STIM TRIGGERED SNIPS
                        baselineSnips = cell2mat(arrayfun(@(x) eng_wf(idx_windows(x,1)+[0:extract_samples]), 1:nBaselineReps,'Uniformoutput',false))';
                        for i = 1:size(baselineSnips,1)                         % this is to get rid of dropped packet/random big artifacts that may appear in the baseline
                            if sum(baselineSnips(i,:)>1000)>0                   % typically appears in only 1 snippet but big enough to skew the RMS
                                baselineSnips(i,:) = baselineSnips(i-1,:);
                            end
                        end
                        engSnips = cell2mat(arrayfun(@(x) eng_wf(stimIdx(x)+[0:extract_samples]), 1:numStimsEvts,'Uniformoutput',false))';

                        % CALCULATE BASELINE RMS
                        rms_mean          = zeros(1,K);
                        rms_std          = zeros(1,K);
                        if numStimsEvts > nBaselineReps                             % in case you dont have as many baseline reps as stim reps
                            bootstrap_samples = randi([1 nBaselineReps],[K N]);
                        else
                            bootstrap_samples = randi([1 numStimsEvts],[K N]);
                        end
                        for iFold = 1:K
                            idx             = bootstrap_samples(iFold,:);
                            avg_baseline_wf = mean(baselineSnips(idx,:));
                            [baseline_rms, baseline_rms_time]= MovingWinFeats_v1(avg_baseline_wf, fs, RMSfn);
                            rms_mean(iFold) = mean(baseline_rms);
                            rms_std(iFold) = std(baseline_rms);        % lets put a smile on that face
                        end
                        rms_mean      = sort(rms_mean);
                        rms_std       = sort(rms_std); 
                        rms_threshold = rms_mean(round(.99*K))+threshold_mult*rms_std(round(.99*K));


                        % CALCULATE ENG RMS
                        bootstrap_samples = randi([1 numStimsEvts],[K N]);
                        full_rms = [];
                        for iiFold = 1:K
                            idx             = bootstrap_samples(iiFold,:);
                            avg_wf = mean(engSnips(idx,:));
                            [rms, rms_time]= MovingWinFeats_v1(avg_wf, fs, RMSfn);
                            full_rms(:,iiFold) = rms(:);                % c'mon mayn initialize this array
                        end

                        
                        % DETECT ENG RESPONSES
                        if N > nBaselineReps                            % in case you dont have as many baseline reps as stim reps
                            n = floor(0.8*nBaselineReps);
                        else
                            n = N;
                        end
                        avg_baseline_wf = mean(baselineSnips(1:n,:));
                        avg_wf          = mean(engSnips(1:N,:));

                        percent_significant_windows = sum(full_rms >= rms_threshold,2)/K;
                        sig_mask    = percent_significant_windows > bootstrap_thresh;
                        
                        consec_sig_windows = cumsum(sig_mask);
                        if any(consec_sig_windows > 3)
                            is_sig = 1;
                            edge_idx = diff(diff(consec_sig_windows));  % second difference gives all rising and falling edges. not foolproof logic in cases of edges that dont fall, but good enough
                            winStart_idx = find(edge_idx==1)+2;         % MATH!!
                            winEnd_idx = find(edge_idx==-1)+1;          % MORE MATH!!
                        else
                            is_sig = 0;
                            winStart_idx = [];
                            winEnd_idx = [];
                        end
                        
                        % PREPARE FOR PLOTTING/LOGGING
                        analysisObj = mdfObj;
                        analysisObj.setFiles(fullfile('<DATA_BASE>','analysis','recruitment',catName,sprintf('%s_ssn%03d_blk%03d_ch%03d_a%0.1f_%s',catName,session,block{iBlock},unique_chans(iChan),unique_amps(iAmp),blockObj.engData(iCuff).location)));
                        analysisObj.type = 'recruitment';
                        analysisObj.md.subject = catName;
                        analysisObj.md.session = session;
                        analysisObj.md.block = block{iBlock};
                        analysisObj.md.stimChan = unique_chans(iChan);
                        analysisObj.md.amplitude = unique_amps(iAmp);
                        analysisObj.md.location = blockObj.engData(iCuff).location;
                        analysisObj.md.fs = fs;
                        analysisObj.md.is_sig = is_sig;
                        
                        analysisObj.d.mean_full_rms = mean(full_rms,2);
                        analysisObj.d.rms_time = rms_time;
                        analysisObj.d.rms_threshold = rms_threshold;
                        analysisObj.d.avg_baseline_wf = avg_baseline_wf;
                        analysisObj.d.avg_wf = avg_wf;
                        analysisObj.d.bootstrap_thresh = bootstrap_thresh;
                        analysisObj.d.percent_significant_windows = percent_significant_windows;
                        analysisObj.d.xlims = [minimum_response_latency extract_time_range(2)];
                        if is_sig == 1
                            analysisObj.d.winStart_idx = winStart_idx;
                            analysisObj.d.winEnd_idx = winEnd_idx;
                        end
                        
                        % PLOT RESULTS
                        if show_debug_plots                   
                            plotRMSanalysis(analysisObj)
                            drawnow
%                             keyboard
                        end
                        
                        % TO DO: if log_results to MDF
                        if log_results
                            analysisObj.save;
                        end
                        
                    end
                end  
            end
        catch ME
            NotifierManager.notify('error','Error in %s_ssn%03d_blk%03d: %s', catName, session, block{iBlock}, ME.message)
%             keyboard
        end
    end
end