function [fcn_result, windowStarts_sec] = MovingWinFeats_v1(wf, fs, featFn, varargin)

    DEFINE_CONSTANTS
    windowSize_sec = 2.5e-4;
    winDisplace = 2.5e-5;
    END_DEFINE_CONSTANTS

    NumWins = @(signalLen, winLen, winDisp) floor((signalLen-winLen)/(winDisp))+1;
     
    windowSize_samples = windowSize_sec*fs;
    duration_sec = length(wf)/fs;
    overlap_sec = windowSize_sec - winDisplace;

    numWindows = NumWins(duration_sec, windowSize_sec, winDisplace);
    windowStarts_sec = (0:(windowSize_sec-overlap_sec):duration_sec-windowSize_sec);
    windowStarts_idx = round(windowStarts_sec*fs);
    
    window_idx   = bsxfun(@plus,[1:windowSize_samples]',windowStarts_idx);
    sliding_data = wf(window_idx);
    fcn_result   = featFn(sliding_data);
    
end