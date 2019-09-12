function [] = plotRMSanalysis(analObj)

    windowSize_sec           = 2.5e-4;      % sec
    
    figure;
    subplot(3,1,1)
    hold on
    plot(analObj.d.rms_time, analObj.d.percent_significant_windows*100, 'linewidth',2)
    plot(analObj.d.xlims,100*analObj.d.bootstrap_thresh*[1 1],'--r');
%     xlim(analObj.d.xlims)
    xlim([0.0005, analObj.d.xlims(2)])
    title('Percent Superthreshold')

    subplot(3,1,2)
    hold on
    plot(linspace(0,length(analObj.d.avg_baseline_wf)/analObj.md.fs,length(analObj.d.avg_baseline_wf)),analObj.d.avg_baseline_wf,'-', ...
        'linewidth',2,...
        'color',[.8 .8 .8])
    plot(linspace(0,length(analObj.d.avg_wf)/analObj.md.fs,length(analObj.d.avg_wf)),analObj.d.avg_wf,'-',...
        'color',    [0 0 1],...
        'linewidth',2)
%     xlim(analObj.d.xlims)
    xlim([0.0005, analObj.d.xlims(2)])
%     ylim([-1, 1])
    title('Voltage')
    if analObj.md.is_sig == 1
        for iEdge = 1:length(analObj.d.winStart_idx)         % assuming there are even numbered edges...else add a check
            winStart = analObj.d.rms_time(analObj.d.winStart_idx(iEdge))-windowSize_sec/2 ;
            if iEdge <= length(analObj.d.winEnd_idx)                                                % sometimes winEnd is outside the time window and does not get written to object
                winEnd = analObj.d.rms_time(analObj.d.winEnd_idx(iEdge))+ windowSize_sec/2;
            else
                winEnd = winStart+20;
            end
            time_window     = [winStart, winEnd];
            ylimits = get(gca,'YLim');
            x = time_window([1 2 2 1]);
            y = ylimits([1 1 2 2]);
            uistack(patch(x,y,[.8 .8 .9],...
                'edgecolor','none'),'bottom');
            alpha(0.6)
        end
    end

    subplot(3,1,3)
    hold on
    plot(analObj.d.rms_time,analObj.d.mean_full_rms,'.','MarkerSize',10)
    plot(analObj.d.xlims,analObj.d.rms_threshold*[1 1],'--r')
%     xlim(analObj.d.xlims)
%     xlim([0.0005, analObj.d.xlims(2)])
    xlabel('Time (ms)')
    title('Mean Bootstrap RMS')                
    
    suptitle(sprintf('Channel: %d, Amplitude: %0.1f, Cuff: %s',analObj.md.stimChan,analObj.md.amplitude,analObj.md.location))

end