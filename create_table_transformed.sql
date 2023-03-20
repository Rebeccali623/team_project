DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
	id SERIAL PRIMARY KEY,
	first_name VARCHAR (50),
	last_name VARCHAR (50),
	birth_date DATE,
	joined_date DATE,
	salary numeric
);

DROP TRIGGER IF EXISTS verify_birth_date on employees;
DROP FUNCTION IF EXISTS birth_date;

CREATE FUNCTION birth_date()
RETURNS trigger AS $$
BEGIN
IF new.birth_date > '1900-01-01' THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid birth_date';
END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER verify_birth_date BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE birth_date();

DROP TRIGGER IF EXISTS verify_joined_date on employees;
DROP FUNCTION IF EXISTS joined_date;

CREATE FUNCTION joined_date()
RETURNS trigger AS $$
BEGIN
IF new.joined_date > new.birth_date THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid joined_date';
END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER verify_joined_date BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE joined_date();

DROP TRIGGER IF EXISTS verify_salary on employees;
DROP FUNCTION IF EXISTS salary;

CREATE FUNCTION salary()
RETURNS trigger AS $$
BEGIN
IF new.salary > 0 THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid salary';
END IF;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER verify_salary BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE salary();