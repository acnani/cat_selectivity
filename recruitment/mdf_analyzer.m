set(0,'DefaultTextInterpreter','none')
om = mdfManage.getInstance;

% aggregate query from in mdf
trialDict = ReadYaml('R:\users\amn69\Projects\cat\selectivity\surface paper\v2018\sortedTrials.yml');
subject = fieldnames(trialDict)';

NotifierManager.enableStreams({'status','error'})

for iSub = subject
    subDict = trialDict.(iSub{1});
    [sortedSessions, ix] = sort(cell2mat(subDict.session));
    blocks = subDict.blocks(ix);
    
    for iSesh = 1:length(sortedSessions)
        logFileName = sprintf('runlogs/%s_runlog/ssn%03d_%s', iSub{1}, sortedSessions(iSesh), datestr(now,'yyyymmddHHMMSS'));
        
        NotifierManager.enableBackup('status',logFileName,1)
        NotifierManager.enableBackup('error',logFileName,1)
        
        mdf_generateResults_recruitment(iSub{1},sortedSessions(iSesh), blocks{iSesh},...
            'stim blanking period',0.8e-3,...
            'show_debug_plots', false,...
            'log_results', true);
        
        NotifierManager.disableBackup('status')
        NotifierManager.disableBackup('error')
        om.clearAll;
    end
    clc
end
disp('Finished generating Results')



%% HA04 - only difference is:
% 1ms stim blanking & 
% 2nd order butterworth filter

set(0,'DefaultTextInterpreter','none')
om = mdfManage.getInstance;

% aggregate query from in mdf
hostname = char( getHostName( java.net.InetAddress.getLocalHost ) );
NotifierManager.enableStreams({'status','error'})

iSub = 'HA04';
sortedSessions = 1:41;
blocks = 1:41;

for iSesh = 1:length(sortedSessions)
    logFileName = sprintf('runlogs/%s_runlog/ssn%03d_%s', iSub, sortedSessions(iSesh), datestr(now,'yyyymmddHHMMSS'));

    NotifierManager.enableBackup('status',logFileName,1)
    NotifierManager.enableBackup('error',logFileName,1)

    mdf_generateResults_recruitment(iSub,sortedSessions(iSesh), {blocks(iSesh)},...
        'stim blanking period',1e-3,...
        'filtOrder', 2,...
        'show_debug_plots', false,...
        'log_results', true);

    NotifierManager.disableBackup('status')
    NotifierManager.disableBackup('error')
    om.clearAll;
end
disp('Finished generating Results')
