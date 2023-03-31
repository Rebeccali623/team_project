import re

def executeScriptsFromFile(filename, cur):
    with open(filename, 'r') as sql_file:
        cur.execute(sql_file.read())

def transformCreateTableCheckConstraints(filename_read, filename_save, cur):
    fd = open(filename_read, 'r')
    sqlFile = fd.read()
    fd.close()

    # get all check constraints
    str_list_check = re.findall(r"(?<=CHECK).*", sqlFile)
    str_list_constraint = re.findall(r"CONSTRAINT.*CHECK(.*)", sqlFile)
    str_list_constraint_name = re.findall(r"CONSTRAINT\s(.*)\sCHECK.*", sqlFile)
    str_list_check = [x for x in str_list_check if x not in str_list_constraint]

    str_list_check_column = findCheckColumnName(sqlFile)
    str_list_constraint_column = findConstraintColumnName(sqlFile)

    # TODO: for table name, now we assume format of CREATE TABLE table_name
    # What about CREATE TABLE IF NOT EXISTS table_name?
    table_name = re.findall(r"(?<=CREATE TABLE ).*", sqlFile)
    table_name = table_name[0].split()[0]

    # Remove all CHECK sections
    sqlFile = removeCheckConstraints(sqlFile, "CONSTRAINT")
    sqlFile = removeCheckConstraints(sqlFile, "CHECK")

    cur.execute(sqlFile)

    # Transform checks to triggers
    triggers_list = []
    addConstraintToTriggerList(table_name, str_list_constraint_column, str_list_constraint, str_list_constraint_name, triggers_list)
    addCheckToTriggerList(table_name, str_list_check_column, str_list_check, triggers_list)

    # Insert all triggers to the new file
    for trigger in triggers_list:
        sqlFile = sqlFile + "\n" + trigger
    with open(filename_save, 'w') as file:
        file.write(sqlFile)

def findCheckColumnName(sqlFile):
    sqlFile = sqlFile.replace('\t', '') 
    sqlCommands = sqlFile.split("\n")
    sqlCommands = [x for x in sqlCommands if "CHECK" in x and "CONSTRAINT" not in x]
    column_names = [x.split()[0] for x in sqlCommands]
    return column_names

def findConstraintColumnName(sqlFile):
    sqlFile = sqlFile.replace('\t', '') 
    sqlCommands = sqlFile.split("\n")
    sqlCommands = [x for x in sqlCommands if "CHECK" in x and "CONSTRAINT" in x]
    column_names = [x.split()[0] for x in sqlCommands]
    return column_names


def removeCheckConstraints(sqlFile, matchString):
    # Find all occurences of "CONSTRAINT"/"CHECK"
    index_check = [m.start() for m in re.finditer(matchString, sqlFile)]

    # Find occurences of ")" corresponding to each "CONSTRAINT"/"CHECK"
    index_right_par = []
    for i in range(len(index_check)):
        end_pos = -1 if i == len(index_check) - 1 else index_check[i+1]
        index = [m.start() for m in re.finditer('\)', sqlFile[index_check[i]: end_pos])][-2 if i == len(index_check)-1 else -1]  
        index_right_par.append(index + index_check[i])

    # Remove substrings "CONSTRAINT/CHECK...)" from end to start (so that index doesn't change)
    for i in range(len(index_check)-1, -1, -1):
        sqlFile = sqlFile[0:index_check[i]-1] + sqlFile[index_right_par[i]+1:]

    return sqlFile


def addConstraintToTriggerList(table_name, str_list_constraint_column, str_list_constraint, str_list_constraint_name, triggers_list):
    constraints_concat_list = appendConstraint(table_name, str_list_constraint)
    # transform each check constraint to a trigger
    fd = open("function_trigger_skeleton_specified_name.txt", 'r')
    skeleton = fd.read()
    fd.close()
    for i in range(len(str_list_constraint)):
        # construct the trigger
        trigger = skeleton.format(str_list_constraint_name[i], table_name, 
                            str_list_constraint_name[i],
                            str_list_constraint_name[i], 
                            constraints_concat_list[i], 
                            str_list_constraint_column[i], table_name, 
                            str_list_constraint_name[i], table_name, 
                            str_list_constraint_name[i])
        triggers_list.append(trigger)


def addCheckToTriggerList(table_name, str_list_check_column, str_list_check, triggers_list):
    checks_concat_list = appendConstraint(table_name, str_list_check)
    # transform each check constraint to a trigger
    fd = open("function_trigger_skeleton_default.txt", 'r')
    skeleton = fd.read()
    fd.close()
    for i in range(len(str_list_check)):
        trigger = skeleton.format(table_name, str_list_check_column[i], table_name, 
                            table_name, str_list_check_column[i],
                            table_name, str_list_check_column[i], 
                            checks_concat_list[i],
                            str_list_check_column[i], table_name, 
                            table_name, str_list_check_column[i], table_name, 
                            table_name, str_list_check_column[i])
        triggers_list.append(trigger)

def appendConstraint(table_name, inputList):
    constraints_list = []
    for constraint in inputList:
        start_index = [m.start() for m in re.finditer('\(', constraint)][0]
        end_index = [m.start() for m in re.finditer('\)', constraint)][-1]
        constraint = constraint[start_index+1:end_index]
        constraints_list.append(constraint)

    outputList = []
    for constraint in constraints_list:
        constraint_split = constraint.split()
        # split those with "(" or ")"
        constraint_split_copy = []
        for substring in constraint_split:
            if "(" in substring:
                constraint_split_copy.append("(")
                constraint_split_copy.append(substring[1:]) 
            elif ")" in substring:
                constraint_split_copy.append(substring[:-1])
                constraint_split_copy.append(")" ) 
            else:
                constraint_split_copy.append(substring)

        # if the right side is a column name, add "new." in front of it
        for j, substring in enumerate(constraint_split_copy):
            if bool(re.search('[a-zA-Z]$',substring))==True:
                command  = """SELECT EXISTS(SELECT 1
                            FROM information_schema.columns 
                            WHERE table_name='{}' AND column_name={});""".format(table_name, 
                            substring if substring[0] == "\'" or substring[0] == "\"" else "\'"+substring+"\'")
                cur.execute(command)
                results = cur.fetchall()
                constraint_split_copy[j] = substring if results[0][0] == False else "new."+substring
        constraint_concat = " ".join([str(item) for item in constraint_split_copy])
        outputList.append(constraint_concat)

    return outputList


def transformAlterTableCheckConstraints(filename_read, filename_save):
    fd = open(filename_read, 'r')
    sqlFile = fd.read()
    fd.close()

    # TODO: for table name, now we assume format of ALTER TABLE table_name
    # What about ALTER TABLE IF EXISTS table_name?
    table_name = re.findall(r"(?<=ALTER TABLE ).*", sqlFile)
    table_name = table_name[0].split()[0]

    # Transform ADD CONSTRAINT .. CHECK()
    str_list_constraint = re.findall(r"CONSTRAINT.*CHECK(.*)", sqlFile)
    str_list_constraint_name = re.findall(r"CONSTRAINT\s(.*)\sCHECK.*", sqlFile)
    sqlFile = removeAddDropConstraint(sqlFile, "CHECK")

    add_drop_triggers_list = []
    addConstraintCheckToTriggerList(table_name, str_list_constraint, str_list_constraint_name, add_drop_triggers_list)

    # Transform DROP CONSTRAINT
    str_list_drop = re.findall(r"DROP CONSTRAINT\s(.*);", sqlFile)
    sqlFile = removeAddDropConstraint(sqlFile, "DROP CONSTRAINT")

    fd = open("drop_trigger_skeleton.txt", 'r')
    skeleton = fd.read()
    fd.close()

    for drop_constraint in str_list_drop:
        drop = skeleton.format(drop_constraint, table_name, drop_constraint)
        add_drop_triggers_list.append(drop)

    # Insert all triggers to the new file
    for drop in add_drop_triggers_list:
        sqlFile = sqlFile + "\n" + drop
    with open(filename_save, 'w') as file:
        file.write(sqlFile)


def removeAddDropConstraint(sqlFile, matchString):
    # Find all occurences of "CHECK"/"DROP CONSTRAINT"
    index_check = [m.start() for m in re.finditer(matchString, sqlFile)]

    # Find occurences of ";" corresponding to each "CHECK"/"DROP CONSTRAINT"
    index_semicolon = []
    for i in range(len(index_check)):
        end_pos = len(sqlFile) if i == len(index_check) - 1 else index_check[i+1]
        index = [m.start() for m in re.finditer(';', sqlFile[index_check[i]: end_pos])][0]
        index_semicolon.append(index + index_check[i])

    # Find occurences of "ALTER TABLE" corresponding to each "CHECK"/"DROP CONSTRAINT"
    index_alter_table = []
    for i in range(len(index_check)):
        start_pos = 0 if i == 0 else index_check[i-1]
        index = [m.start() for m in re.finditer("ALTER TABLE", sqlFile[start_pos: index_check[i]])][-1]
        index_alter_table.append(start_pos + index)

    # Remove substrings "ALTER TABLE ...;" from end to start (so that index doesn't change)
    for i in range(len(index_check)-1, -1, -1):
        sqlFile = sqlFile[0:index_alter_table[i]] + sqlFile[index_semicolon[i]+2:]

    return sqlFile