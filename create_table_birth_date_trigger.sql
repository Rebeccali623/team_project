DROP TABLE IF EXISTS employees;
CREATE TABLE employees (
	id SERIAL PRIMARY KEY,
	first_name VARCHAR (50),
	last_name VARCHAR (50),
	birth_date DATE,
	joined_date DATE CHECK (joined_date > birth_date),
	salary numeric CHECK (salary > 0)
);

DROP TRIGGER IF EXISTS verify_birth_date on employees;
DROP FUNCTION IF EXISTS birth_date;

CREATE FUNCTION birth_date()
RETURNS trigger AS $BODY$

BEGIN
IF new.birth_date > '1900-01-01' THEN
    RETURN NEW;
ELSE 
    RAISE EXCEPTION 'Invalid birth date';
END IF;
END;
$BODY$
LANGUAGE 'plpgsql';

CREATE TRIGGER verify_birth_date BEFORE INSERT OR UPDATE ON employees
            FOR EACH ROW EXECUTE PROCEDURE birth_date();