%% HA04 session correction in analysis objects
% 134,136,138,140 - L5
% 129:132 - L6
% 133,135,137,139 - L7

% block = 0; BLOCK NUMBERING SHOULD CONTINUE
% allUniqAmps =  150:5:350;
% 
% for iChan = [133,135,137,139]
%     block = block+1;
%     for iAmp = 1:length(allUniqAmps)
%         if ismember(iChan,[129:132])
%             location = 'DRG - L6';
%             session = 3;
%         elseif ismember(iChan,[134,136,138,140])
%             location = 'DRG - L5';
%             session = 2;
%         elseif ismember(iChan,[133,135,137,139])
%             location = 'DRG - L7';
%             session = 4;
%         end
%         qwe = mdf.load('mdf_type','recruitment','subject','HA04','stimChan',iChan,'amplitude',allUniqAmps(iAmp));
%         for iCuff = 1:length(qwe)
%             tmpObj = qwe(iCuff);
%             tmpObj.md.old_session = tmpObj.md.session;
%             tmpObj.md.old_block = tmpObj.md.block;
%             tmpObj.md.DRG = location;
%             tmpObj.md.session = session;
%             tmpObj.md.block = block;
%             tmpObj.save;
%         end
%     end
% end
% 
% disp('finished HA04')

% HA04 add location to analysis objects


%% HA04 session correction in CV objects
% 134,136,138,140 - L5
% 129:132 - L6
% 133,135,137,139 - L7

% block = 0; % BLOCK NUMBERING SHOULD CONTINUE
% allUniqAmps =  150:5:350;
% 
% for iChan = [133,135,137,139]
%     block = block+1;
%     for iAmp = 1:length(allUniqAmps)
%         if ismember(iChan,[129:132])
%             location = 'DRG - L6';
%             session = 3;
%         elseif ismember(iChan,[134,136,138,140])
%             location = 'DRG - L5';
%             session = 2;
%         elseif ismember(iChan,[133,135,137,139])
%             location = 'DRG - L7';
%             session = 4;
%         end
%         qwe = mdf.load('mdf_type','CV','subject','HA04','stimChan',iChan,'amplitude',allUniqAmps(iAmp));
%         for iCuff = 1:length(qwe)
%             tmpObj = qwe(iCuff);
%             tmpObj.md.old_session = tmpObj.md.session;
%             tmpObj.md.old_block = tmpObj.md.block;
%             tmpObj.md.DRG = location;
%             tmpObj.md.session = session;
%             tmpObj.md.block = block;
%             tmpObj.save;
%         end
%     end
% end
% 
% disp('finished HA04')


%% copy is_sig_manual from analysis to CV objects
subject = 'Galactus';
allCVobj = mdf.load('mdf_type','CV','subject',subject);
for iObj = 1:length(allCVobj)
    iObj
    tmp = allCVobj(iObj);
    recruitObj = mdf.load('mdf_type','recruitment','session',tmp.session,'block',tmp.block, 'stimChan', tmp.stimChan,'amplitude',tmp.amplitude,'location',{[tmp.location,'_Distal'], [tmp.location,'_Proximal']});
    x = zeros(1,length(recruitObj));
    for t = 1:length(recruitObj)
        x(t) = recruitObj(t).is_sig;
    end
    if any(x)
        tmp.md.is_sig_manual = 1;
    else
        tmp.md.is_sig_manual = 0;
    end
    tmp.save;
end
disp('finished')

%% all cats add location to recruit or CV objects

import com.mongodb.BasicDBObject
import com.mongodb.BasicDBList
objToEdit = 'CV';

for sub = {'Galactus'} % 'Hobgoblin'

    match1 = BasicDBObject('mdf_def.mdf_type', BasicDBObject('$eq','trial')) ;                     
    match2 = BasicDBObject('mdf_metadata.subject', BasicDBObject('$eq',sub{1}));
    matchList = BasicDBList(); 
    matchList.add(match1);
    matchList.add(match2);
    matchAnd = BasicDBObject('$and', matchList);
    match  = BasicDBObject('$match',  matchAnd);
    
    groupFields = BasicDBObject('_id','$mdf_metadata.location') ;
    groupFields.put('session', BasicDBObject( '$addToSet', '$mdf_metadata.session'));
    group = BasicDBObject('$group', groupFields);
    
    pipe = BasicDBObject.parse('{"_id": 1,"session": "$session"}');
    project  = BasicDBObject('$project',  pipe); 
    
    aggrListFinal = BasicDBList();
    aggrListFinal.add(match); 
    aggrListFinal.add(group);
    aggrListFinal.add(project);
    
    omdf = mdfDB.getInstance;
    output  = omdf.coll.aggregate(aggrListFinal); 
    res = loadjson(char(output.results));

%     for iDRG = 1:length(res)
%         if ~isempty(res{iDRG}.x0x5F_id) 
%             if ismember(res{iDRG}.x0x5F_id, {'DRG - L5', 'DRG - L6', 'DRG - L7','DRG - S1'})
%                 allSesh = res{iDRG}.session;
%                 for iSesh = 1:length(allSesh)
%                     disp([sub{1},' ', res{iDRG}.x0x5F_id, ' session: ', num2str(allSesh(iSesh))])
%                     seshObjVec = mdf.load('subject',sub,'mdf_type',objToEdit,'session', allSesh(iSesh));
%                     for iObj = 1:length(seshObjVec)
%                         tmpObj = seshObjVec(iObj);
%                         tmpObj.md.DRG = res{iDRG}.x0x5F_id;
%                         tmpObj.save;
%                     end
%                 end
%             end
%         end
%     end
    
end

disp('finished')


%%

% subject = 'Electro';
% for corrCuff = {'Lat_Fem', 'Mid_Fem', 'Med_Fem'}
%     asd = mdf.load('location',corrCuff{1},'subject',subject,'mdf_type','ENGdata');
%     length(asd)
%     for i = 1:length(asd)
%         tmp = asd(i);
%         oldloc = tmp.md.location;
%         tmp.md.old_location = oldloc;
%         if strcmp(oldloc, 'Lat_Fem')
%             tmp.md.location = 'Sart';
%         elseif strcmp(oldloc, 'Mid_Fem')
%             tmp.md.location = 'VMed';
%         elseif strcmp(oldloc, 'Med_Fem')
%             tmp.md.location = 'Saph';
%         end
%         tmp.save;
%     end
% end
% disp('done')
