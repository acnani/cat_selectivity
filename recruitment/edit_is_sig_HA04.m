% for j =1:12
%     asd = mdf.load('subject','HA04','mdf_type','recruitment','block',j,'amplitude',350);
% 
%     figure; 
%     hold on; 
%     for i = 1:length(asd)
%         plot(asd(i).data.avg_wf)
%     end
%     title(asd(i).stimChan)
% end

asd = mdf.load('subject','HA04','mdf_type','recruitment','stimChan',139,'amplitude',175);

figure; 
hold on; 
for i = 1:length(asd)
    plot(asd(i).data.avg_wf)
end
title(asd(i).stimChan)

%%

asd = mdf.load('subject','HA04','mdf_type','recruitment','stimChan',134);
for i = 1:length(asd)
    disp(i)
    tmp =asd(i);
    tmp.md.is_sig_manual = 0;
    tmp.save;
end