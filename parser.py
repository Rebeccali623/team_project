import re
f = open('create_table.sql', 'r')
create_file = f.read()
f.close()
str_list = re.findall(r"(?<=CHECK).*", create_file)

constraints_list = []
for i in range(len(str_list)):
    constraint = str_list[i]
    constraint = constraint[constraint.index('(')+1:constraint.index(')')].split()
    constraints_list.append(constraint)

