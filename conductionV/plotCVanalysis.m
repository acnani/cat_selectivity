function [] = plotCVanalysis(analObj)
    numWins = length(analObj.d.window_mask);

    figure;
    subplot(3,1,1)
    hold on
    plot(analObj.d.wf_time, analObj.d.proximal_wf)
    plot(analObj.d.wf_time, analObj.d.distal_wf)
%     title(sprintf('%s cuff trace', analObj.md.location))
    
    parent = subplot(3,1,2);
    hold all
    plot(analObj.d.lcc_time,analObj.d.lcc,'-o');
    plot(xlim(parent),analObj.d.lcc_threshold*[1 1],'--',...
        'Color',[1 0 0],...
        'parent',parent);
%     title(sprintf('%s LCC', analObj.md.location))
    
    subplot(3,1,3)
    hold all
    plot(analObj.d.wf_time,analObj.d.proximal_wf,'-','color',[.8 .8 .8],'Linewidth',3);
    plot(analObj.d.wf_time,analObj.d.distal_wf,'-','color',[0 0 1]);
    for iWin  = 1:numWins
        plot(analObj.d.wf_time(analObj.d.window_mask{iWin})+analObj.d.best_shift(iWin),analObj.d.proximal_wf(analObj.d.window_mask{iWin}),'-','color',[1 0 0]);
    end
    legend('proximal','distal','shifted proximal')
%     patch(time_window([1 2 2 1]),ylimits([1 1 2 2]),[.4 .4 .4],'FaceAlpha',.5)
    set(findobj(gcf,'type','patch'),'hittest','off')
    linkFigureAxes(gcf,'x')
    suptitle(sprintf('sesh%03d_block%03d_%s cuff', analObj.md.session, analObj.md.block, analObj.md.location))
    
end