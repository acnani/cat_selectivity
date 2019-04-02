function[returnVal] = validation_aggregateRecruitmentObj(subject, sessions)
    
    import com.mongodb.BasicDBObject
    import com.mongodb.BasicDBList
    
    match1 = BasicDBObject('mdf_def.mdf_type', BasicDBObject('$eq','recruitment')) ;                     
    match2 = BasicDBObject('mdf_metadata.subject', BasicDBObject('$eq',subject));
    match3 = BasicDBObject('mdf_metadata.session', BasicDBObject('$in',sessions));
    match4 = BasicDBObject('mdf_metadata.is_sig_manual', BasicDBObject('$exists',0));
    
    matchList = BasicDBList(); 
    matchList.add(match1);
    matchList.add(match2);
    matchList.add(match3);
    matchList.add(match4);
    matchAnd = BasicDBObject('$and', matchList);
    match  = BasicDBObject('$match',  matchAnd); 
    
    
    groupFields = BasicDBObject('_id','$mdf_metadata.subject') ;
    groupFields.put('stimAmp', BasicDBObject( '$push', '$mdf_metadata.amplitude'));
    groupFields.put('recruitObj', BasicDBObject( '$push', '$mdf_def.mdf_uuid'));
    group = BasicDBObject('$group', groupFields);
    
    
    pipe = BasicDBObject.parse('{"_id": 0,"objUUID": "$recruitObj"}');
    project  = BasicDBObject('$project',  pipe); 
    
    aggrListFinal = BasicDBList();
    aggrListFinal.add(match); 
    aggrListFinal.add(group);
    aggrListFinal.add(project);
    
    omdf = mdfDB.getInstance;
    output  = omdf.coll.aggregate(aggrListFinal); 
    res = loadjson(char(output.results));
    returnVal = res{1}.objUUID;
end