DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
	id SERIAL PRIMARY KEY,
	first_name VARCHAR (50),
	last_name VARCHAR (50),
	birth_date DATE,
	joined_date DATE,
	salary numeric
);
DROP TRIGGER IF EXISTS positive_salary on employees;
DROP FUNCTION IF EXISTS verify_positive_salary;

CREATE FUNCTION verify_positive_salary()
RETURNS trigger AS $$
BEGIN
IF new.salary > 0 THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid salary in employees';
END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER positive_salary BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE verify_positive_salary();
            
DROP TRIGGER IF EXISTS employees_birth_date_check on employees;
DROP FUNCTION IF EXISTS verify_employees_birth_date;

CREATE FUNCTION verify_employees_birth_date()
RETURNS trigger AS $$
BEGIN
IF new.birth_date > '1900-01-01' THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid birth_date in employees';
END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER employees_birth_date_check BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE verify_employees_birth_date();
            
DROP TRIGGER IF EXISTS employees_joined_date_check on employees;
DROP FUNCTION IF EXISTS verify_employees_joined_date;

CREATE FUNCTION verify_employees_joined_date()
RETURNS trigger AS $$
BEGIN
IF new.joined_date > new.birth_date THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid joined_date in employees';
END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER employees_joined_date_check BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE verify_employees_joined_date(); 
            