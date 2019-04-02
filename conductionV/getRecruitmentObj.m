function analObj = getRecruitmentObj(sub, sesh, blk, chan, amp, cuff)
    
    import com.mongodb.BasicDBObject
    import com.mongodb.BasicDBList    
    
    match1 = BasicDBObject('mdf_def.mdf_type', BasicDBObject('$eq','recruitment')) ;                     
    match2 = BasicDBObject('mdf_metadata.subject', BasicDBObject('$eq',sub));
    match3 = BasicDBObject('mdf_metadata.old_session', BasicDBObject('$eq',sesh));
    match4 = BasicDBObject('mdf_metadata.old_block', BasicDBObject('$eq',blk));
    match5 = BasicDBObject('mdf_metadata.stimChan', BasicDBObject('$eq',chan));
    match6 = BasicDBObject('mdf_metadata.amplitude', BasicDBObject('$gt',amp-0.1));
    match7 = BasicDBObject('mdf_metadata.amplitude', BasicDBObject('$lt',amp+0.1));
    match8 = BasicDBObject('mdf_metadata.location', BasicDBObject('$in',cuff));
    
    groupFields = BasicDBObject('_id','$mdf_uuid') ;
    groupFields.put('uuid', BasicDBObject( '$addToSet', '$mdf_def.mdf_uuid'));
    
    group = BasicDBObject('$group', groupFields);

    pipe = BasicDBObject.parse('{"_id": 0,"uuid": "$uuid"}');
    project  = BasicDBObject('$project',  pipe);
    
    matchList = BasicDBList(); 
    matchList.add(match1);
    matchList.add(match2);
    matchList.add(match3);
    matchList.add(match4);
    matchList.add(match5);
    matchList.add(match6);
    matchList.add(match7);
    matchList.add(match8);
    matchAnd = BasicDBObject('$and', matchList);
    match  = BasicDBObject('$match',  matchAnd); 
    
    aggrListFinal = BasicDBList();
    aggrListFinal.add(match); 
    aggrListFinal.add(group);
    aggrListFinal.add(project);

    omdf = mdfDB.getInstance;
    output  = omdf.coll.aggregate(aggrListFinal); 
    
    res = loadjson(char(output.results));
    analObj = mdf.load('mdf_uuid',res{1}.uuid);
end