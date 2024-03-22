def subs(sub, main):
    main_lower = main.lower()
    indices = []
    start = 0

    while start < len(main_lower):
        index = main_lower.find(sub, start)
        if index == -1:
            break
        indices.append(index)
        start = index + 1

    return indices
  
def capitalize(indexes, sql):
    for i in indexes:
        for j in range(i, len(sql)):
            if sql[j] == "'" or sql[j] == '"':
                for k in range(j+1, len(sql)):
                    if sql[k] != "'" and sql[k] != '"':
                        for l in range(k+1, len(sql)):
                            if sql[l] == "'" or sql[l] == '"':
                                # capitLize everything between j and l
                                sql = sql[:j+1] + sql[j+1:k].upper() + sql[k:]
                                return sql
    return sql
              
def capfirst(indexes, sql):
    for i in indexes:
    # find the next ' or "
        for j in range(i, len(sql)):
            if sql[j] == "'" or sql[j] == '"':
                # find the next character that is not ' or "
                for k in range(j+1, len(sql)):
                    if sql[k] != "'" and sql[k] != '"':
                        # make this character uppercase
                        sql = sql[:k] + sql[k].upper() + sql[k+1:]
                        return sql
    return sql
          
def syntax_fixer(sql):
    names = subs("name", sql)
    for i in names:
        # find the next ' or "
        for j in range(i, len(sql)):
            if sql[j] == "'" or sql[j] == '"':
                # find the next character that is not ' or "
                for k in range(j+1, len(sql)):
                    if sql[k] != "'" and sql[k] != '"':
                        # make this character uppercase
                        sql = sql[:k] + sql[k].upper() + sql[k+1:]
                        # find the next space
                        for l in range(k+1, len(sql)):
                            if sql[l] == ' ':
                                # make the next character uppercase
                                sql = sql[:l+1] + sql[l+1].upper() + sql[l+2:]
                                break
        
    
    marital = subs("marital_status", sql)
    sql = capitalize(marital, sql)
    
    language = subs("language", sql)
    sql = capitalize(language, sql)
    
    religion = subs("religion", sql)
    sql = capitalize(religion, sql)

    admission = subs("admission_type", sql)
    sql = capitalize(admission, sql)
    
    insurance = subs("insurance", sql)
    sql = capfirst(insurance, sql)
    
    ethnicity = subs("ethnicity", sql)
    sql = capitalize(ethnicity, sql)

    admission_loc = subs("admission_location", sql)
    sql = capitalize(admission_loc, sql)
    
    discharge_loc = subs("discharge_location", sql)
    sql = capitalize(discharge_loc, sql)
    
    diagnosis = subs("diagnosis", sql)
    sql = capitalize(diagnosis, sql)

    short = subs("short_title", sql)
    sql = capfirst(short, sql)

    long = subs("long_title", sql)
    sql = capfirst(long, sql)

    label = subs("label", sql)
    sql = capfirst(label, sql)
    
    fluid = subs("fluid", sql)
    sql = capfirst(fluid, sql)
    
    category = subs("category", sql)
    sql = capfirst(category, sql)
    
    drug_type = subs("drug_type", sql)
    sql = capitalize(drug_type, sql)
    
    drug = subs("drug", sql)
    sql = capfirst(drug, sql)
    
    formulary_drug_cd = subs("formulary_drug_cd", sql)
    sql = capitalize(formulary_drug_cd, sql)
    
    route = subs("route", sql)
    sql = capitalize(route, sql)
    return sql