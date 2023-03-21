
DROP TRIGGER IF EXISTS salary_limit on employees;
DROP FUNCTION IF EXISTS verify_salary_limit;

CREATE FUNCTION verify_salary_limit()
RETURNS trigger AS $$
BEGIN
IF new.salary < 5000 THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid salary in employees';
END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER salary_limit BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE verify_salary_limit();
            
DROP TRIGGER IF EXISTS employees_birth_date_check on employees;
DROP FUNCTION IF EXISTS verify_employees_birth_date_check;

DROP TRIGGER IF EXISTS positive_salary on employees;
DROP FUNCTION IF EXISTS verify_positive_salary;
