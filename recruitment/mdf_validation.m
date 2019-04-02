cd ('R:\users\amn69\Projects\cat\selectivity\surface paper\v2018\recruitment')
set(0,'DefaultTextInterpreter','none')
om = mdfManage.getInstance;

subject = 'Hobgoblin';
eType = 'epineural';

% output of sessionPerElectrodeType query from python hf.helperFcns
switch subject
    case 'Electro'
        switch eType
            case 'epineural'
                objUUID = validation_aggregateRecruitmentObj('Electro', [1, 5, 10, 11, 13, 14, 15]);
            case 'penetrating'
                objUUID = validation_aggregateRecruitmentObj('Electro', [20, 22, 26, 27, 28, 32]);
        end
    case 'Freeze'
        switch eType
            case 'epineural'
                objUUID = validation_aggregateRecruitmentObj('Freeze', [7, 11, 20]);
            case 'penetrating'
                objUUID = validation_aggregateRecruitmentObj('Freeze', [55, 56, 59, 60, 61, 63, 68, 999]);
        end
    case 'Galactus'
        switch eType
            case 'epineural'
                objUUID = validation_aggregateRecruitmentObj('Galactus', [15, 30, 40, 41, 48, 57]);
            case 'penetrating'
                objUUID = validation_aggregateRecruitmentObj('Galactus', [91, 94, 97, 98]);
        end
    case 'Hobgoblin'
        switch eType
            case 'epineural'
                objUUID = validation_aggregateRecruitmentObj('Hobgoblin', [6, 7, 10, 12, 14, 16, 20, 23]);
            case 'penetrating'
                objUUID = validation_aggregateRecruitmentObj('Hobgoblin', [47, 49, 52]);
        end
    case 'HA02'
        switch eType
            case 'epineural'
                objUUID = validation_aggregateRecruitmentObj('HA02', [2, 3, 4]);
            case 'penetrating'
                objUUID = [];
        end
    case 'HA04'
        switch eType
            case 'epineural'
                objUUID = validation_aggregateRecruitmentObj('HA04', [2, 3, 4]);
            case 'penetrating'
                objUUID = [];
        end
end
numObj = numel(objUUID);
objUUID = objUUID(randperm(numObj));

%% validation loop
for iObj = 1:numObj
    recruitObj = mdf.load(objUUID{iObj});
    fprintf('%d/%d:\tProcessing %s_ssn%03d_blk%03d\tuid: %s\n', iObj, numObj, recruitObj.subject, recruitObj.session, recruitObj.block, recruitObj.uuid)
    fprintf('Channel: %d, Amplitude: %0.1f, Cuff: %s\n',recruitObj.md.stimChan,recruitObj.md.amplitude,recruitObj.md.location)
    plotRMSanalysis(recruitObj);

    k = input('Is there an ENG response (0/1)?\n');
    recruitObj.md.is_sig_manual = k;
    recruitObj.save;
    close all;
end
disp('Finished validating results')

 