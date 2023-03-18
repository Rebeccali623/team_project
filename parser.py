fd = open('create_table.sql', 'r')
sqlFile = fd.read()
fd.close()

print(sqlFile)