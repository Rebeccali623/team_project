ALTER TABLE employees ADD CONSTRAINT salary_limit CHECK (salary < 5000);
ALTER TABLE employees DROP CONSTRAINT employees_birth_date_check;
ALTER TABLE employees DROP CONSTRAINT positive_salary;