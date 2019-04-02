function [] = mdf_generateResults_CV(catName, session, block, varargin)
    
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
    cuff_electrode_separation = .008;
    min_cv                    = 30;
    max_cv                    = 120;
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
            extract_time_range = [0 .9*median(diff(all_stim_times))];
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
                    cuffNames = {'Sciatic', 'Femoral'};
                    
                    % PROCESS EACH CUFF
                    for iCuff = 1:length(cuffNames)
                        
                        proxName = [cuffNames{iCuff},'_Proximal'];
                        distName = [cuffNames{iCuff},'_Distal'];
                        recruitmentObj = getRecruitmentObj(catName, session, ...
                            block{iBlock}, unique_chans(iChan), unique_amps(iAmp), {proxName,distName});
                        
                        % run LCC only iff rms thresh crossed
                        if any(cell2mat(recruitmentObj(:).is_sig))
                            NotifierManager.notify('status','Processing %s LCC',cuffNames{iCuff})
                            
                            prox_mask = ismember(allCuffs,proxName);
                            prox_dataObj = blockObj.engData(prox_mask);
                            prox_eng = prox_dataObj.wf;
                            blanking_value = cell2mat(arrayfun(@(x) linspace(prox_eng(blanking_idx(x,1))',prox_eng(blanking_idx(x,end))',size(blanking_idx,2)), 1:size(blanking_idx,1),'Uniformoutput',false)');
                            prox_eng(blanking_idx(:)) = blanking_value(:);
                            prox_eng = filtfilt(bf,af,prox_eng);
                                              
                            distal_mask = ismember(allCuffs,distName);
                            distal_maskObj = blockObj.engData(distal_mask);
                            distal_eng = distal_maskObj.wf;
                            blanking_value = cell2mat(arrayfun(@(x) linspace(distal_eng(blanking_idx(x,1))',distal_eng(blanking_idx(x,end))',size(blanking_idx,2)), 1:size(blanking_idx,1),'Uniformoutput',false)');
                            distal_eng(blanking_idx(:)) = blanking_value(:);
                            distal_eng = filtfilt(bf,af,distal_eng);
                            
                            % GET BASELINE SNIPS
                            prox_baselineSnips = cell2mat(arrayfun(@(x) prox_eng(idx_windows(x,1)+[0:extract_samples]), 1:nBaselineReps,'Uniformoutput',false))';
                            for i = 1:size(prox_baselineSnips,1)                         % this is to get rid of dropped packet/random big artifacts that may appear in the baseline
                                if sum(prox_baselineSnips(i,:)>1000)>0                   % typically appears in only 1 snippet but big enough to skew the RMS
                                    prox_baselineSnips(i,:) = prox_baselineSnips(i-1,:);
                                end
                            end
                            prox_engSnips = cell2mat(arrayfun(@(x) prox_eng(stimIdx(x)+[0:extract_samples]), 1:numStimsEvts,'Uniformoutput',false))';

                            distal_baselineSnips = cell2mat(arrayfun(@(x) distal_eng(idx_windows(x,1)+[0:extract_samples]), 1:nBaselineReps,'Uniformoutput',false))';
                            for i = 1:size(distal_baselineSnips,1)                         % this is to get rid of dropped packet/random big artifacts that may appear in the baseline
                                if sum(distal_baselineSnips(i,:)>1000)>0                   % typically appears in only 1 snippet but big enough to skew the RMS
                                    distal_baselineSnips(i,:) = distal_baselineSnips(i-1,:);
                                end
                            end
                            distal_engSnips = cell2mat(arrayfun(@(x) distal_eng(stimIdx(x)+[0:extract_samples]), 1:numStimsEvts,'Uniformoutput',false))';
                            
                            baseline_lcc_mean          = zeros(1,K);
                            baseline_lcc_std           = zeros(1,K);
                            if numStimsEvts > nBaselineReps                             % in case you dont have as many baseline reps as stim reps
                                bootstrap_samples = randi([1 nBaselineReps],[K N]);
                            else
                                bootstrap_samples = randi([1 numStimsEvts],[K N]);
                            end
                            for iFold = 1:K
                                idx             = bootstrap_samples(iFold,:);
                                prox_avg_baseline_wf = mean(prox_baselineSnips(idx,:));
                                dist_avg_baseline_wf = mean(distal_baselineSnips(idx,:));
                                
                                baseline_avg_time = linspace(0,length(dist_avg_baseline_wf)/fs,length(dist_avg_baseline_wf));
%                                 [~, baseline_avg_time]= MovingWinFeats_v1(prox_avg_baseline_wf, fs, RMSfn);
                                
                                [baseline_full_lcc,baseline_lcc_time_shifts,baseline_lcc_time] = ...
                                        xcorrLocal(baseline_avg_time,prox_avg_baseline_wf,dist_avg_baseline_wf, ...
                                        'sliding_window_duration',  windowSize_sec,...
                                        'sliding_window_step',      winDisplace,...
                                        'option',                   'coeff',...
                                        'shift relative to windows',true);
                                
                                
                                mask  = baseline_lcc_time_shifts >= -cuff_electrode_separation/min_cv ...
                                        & baseline_lcc_time_shifts <= -cuff_electrode_separation/max_cv;
                                [baseline_lcc,iiLccMax] = max(baseline_full_lcc(:,mask),[],2);
                                baseline_lcc_mean(iFold)       = mean(baseline_lcc);
                                baseline_lcc_std(iFold)       = std(baseline_lcc);
                            end
                            lcc_mean      = sort(baseline_lcc_mean);
                            lcc_std       = sort(baseline_lcc_std); 
                            lcc_threshold = lcc_mean(round(.99*K))+threshold_mult*lcc_std(round(.99*K));
                            
                            
                            
                            % CALCULATE ENG LCC
                            bootstrap_samples = randi([1 numStimsEvts],[K N]);
                            bootstrap_lcc = [];
                            for iiFold = 1:K
                                idx             = bootstrap_samples(iiFold,:);
                                prox_avg_wf = mean(prox_engSnips(idx,:));
                                distal_avg_wf = mean(distal_engSnips(idx,:));
                                snip_avg_time = linspace(0,length(distal_avg_wf)/fs,length(distal_avg_wf));
                                
                                prox_avg_wf(snip_avg_time < minimum_response_latency) = 0;
                                distal_avg_wf(snip_avg_time   < minimum_response_latency) = 0;
                                
                                [full_lcc,full_lcc_time_shifts,lcc_time] = xcorrLocal(snip_avg_time,prox_avg_wf,distal_avg_wf, ...
                                            'sliding_window_duration',  windowSize_sec,...
                                            'sliding_window_step',      winDisplace,...
                                            'option',                   'coeff',...
                                            'shift relative to windows',true);
                                mask  = full_lcc_time_shifts >= -cuff_electrode_separation/min_cv ...
                                        & full_lcc_time_shifts <= -cuff_electrode_separation/max_cv;
                                [lcc,iiLccMax] = max(full_lcc(:,mask),[],2);
                                bootstrap_lcc(:,iiFold)       = lcc;
                                tmp             = full_lcc_time_shifts(mask);
                                lcc_time_shifts = tmp(iiLccMax);
                            end
                            
                            % DETECT RESPONSES CALC CV
                            analysisObj = mdfObj;
                            analysisObj.setFiles(fullfile('<DATA_BASE>','analysis','CV',catName,sprintf('%s_ssn%03d_blk%03d_ch%03d_a%0.1f_%s',catName,session,block{iBlock},unique_chans(iChan),unique_amps(iAmp),cuffNames{iCuff})));
                            analysisObj.type = 'CV';
                            analysisObj.md.subject = catName;
                            analysisObj.md.session = session;
                            analysisObj.md.block = block{iBlock};
                            analysisObj.md.stimChan = unique_chans(iChan);
                            analysisObj.md.amplitude = unique_amps(iAmp);
                            analysisObj.md.location = cuffNames{iCuff};
                            analysisObj.md.fs = fs;

                            analysisObj.d.proximal_wf = prox_avg_wf;
                            analysisObj.d.distal_wf = distal_avg_wf;
                            analysisObj.d.wf_time = snip_avg_time;

                            analysisObj.d.lcc_threshold = lcc_threshold;
                            analysisObj.d.lcc_time = lcc_time;
                            analysisObj.d.lcc = lcc;
                            
                            sig_mask     = sum(bootstrap_lcc > lcc_threshold,2) > .95*K & lcc_time(:)-windowSize_sec/2 > minimum_response_latency;
                            consec_sig_windows = cumsum(sig_mask);
                            if any(consec_sig_windows > 3)
                                edge_idx = diff(diff(consec_sig_windows));  % second difference gives all rising and falling edges. not foolproof logic in cases of edges that dont fall, but good enough
                                winStart_idx = find(edge_idx==1)+2;         % MATH!!
                                winEnd_idx = find(edge_idx==-1)+1;          % MORE MATH!!
                                
                                edges = [winStart_idx winEnd_idx];
                                len          = (edges(:,2) - edges(:,1))+ 1;
                                edges(len < 2,:) = [];
                            
                                condVel = zeros(1,length(winStart_idx));
                                best_shift = zeros(1,length(winStart_idx));
                                window_mask = cell(1,length(winStart_idx));
                                for iiEdge = 1:size(edges,1)
                                    time_window = [lcc_time(edges(iiEdge,1))-windowSize_sec/2 lcc_time(edges(iiEdge,2))+windowSize_sec/2];
                                    [lcc_max, iiLccMax] = max(lcc(edges(iiEdge,1):edges(iiEdge,2)));
                                    window_max_lcc_time = lcc_time(edges(iiEdge,1)+(iiLccMax-1));
                                    condVel(iiEdge) = cuff_electrode_separation/abs(lcc_time_shifts(edges(iiEdge,1)+(iiLccMax-1)));

                                    best_shift(iiEdge)     = cuff_electrode_separation/condVel(iiEdge);
                                    window_mask{iiEdge} = snip_avg_time >= window_max_lcc_time-windowSize_sec/2-best_shift(iiEdge) & snip_avg_time <= time_window(2)+windowSize_sec/2-best_shift(iiEdge);
                                end

                                % PREPARE FOR PLOTTING/LOGGING
                                analysisObj.md.cv = condVel;
                                analysisObj.d.window_mask = window_mask;
                                analysisObj.d.best_shift = best_shift;
                                analysisObj.d.sig_mask = sig_mask;
                                
                                % PLOT RESULTS
                                if show_debug_plots                   
                                    plotCVanalysis(analysisObj)
                                    drawnow
                                end

                                % TO DO: if log_results to MDF
                                if log_results
                                    analysisObj.save;
                                end
                            else
                                analysisObj.md.cv = '999';
                                analysisObj.save;
                                NotifierManager.notify('warning','Consecutive significant windows not detected for %s_ssn%03d_blk%03d_ch%03d_a%0.1f_%s', catName,session,block{iBlock},unique_chans(iChan),unique_amps(iAmp),cuffNames{iCuff})
%                                 keyboard
                            end
                        else
                            NotifierManager.notify('status','No response on %s cuff', cuffNames{iCuff})
                        end
                    end
                end  
            end
        catch ME
            NotifierManager.notify('error','Error in %s_ssn%03d_blk%03d: %s', catName, session, block{iBlock}, ME.message)
            keyboard
        end
    end
end