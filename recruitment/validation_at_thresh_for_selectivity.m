asd = mdf.load('mdf_type','recruitment','subject','HA02','session',3,'stimChan',6,'location','Cmn_Per');
% currentThresh = 125;
%
% figure;
% hold on
% for i = 1:length(asd)
% %     if asd(i).amplitude == 200
%         plot(asd(i).data.avg_wf)
% %     end
% end
%%
for j = 1:25%length(asd)
    recruitObj = asd(j);
    recruitObj.md.is_sig_manual = 0;
    recruitObj.save;
end
%%
for iObj = 1:length(asd)
    recruitObj = asd(iObj);
    fprintf('%d/%d:\tProcessing %s_ssn%03d_blk%03d\tuid: %s\n', iObj, length(asd), recruitObj.subject, recruitObj.session, recruitObj.block, recruitObj.uuid)
    fprintf('Channel: %d, Amplitude: %0.1f, Cuff: %s\n',recruitObj.md.stimChan,recruitObj.md.amplitude,recruitObj.md.location)
    plotRMSanalysis(recruitObj);

    k = input('Is there an ENG response (0/1)?\n');
    recruitObj.md.is_sig_manual = k;
    recruitObj.save;
    close all;
end
disp('Finished validating results')
