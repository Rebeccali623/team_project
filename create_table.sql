DROP TABLE IF EXISTS testdb2;
CREATE TABLE testdb2 (
	first_name VARCHAR (50),
	salary numeric CHECK(salary > 0)
);