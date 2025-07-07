-- PostgreSQL database dump for random data insertion
--
-- This script generates random data and inserts it into the provided tables.
-- It respects foreign key constraints by inserting data into parent tables first.
-- Helper functions are created and dropped within this script.

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

-- Set a seed for reproducibility if needed (comment out for truly random data each run)
-- SELECT SETSEED(0.5);

-- Drop tables (optional, for a clean slate if re-running script)
-- Be careful with this in a production environment!
-- DROP TABLE IF EXISTS customer_customer_demo CASCADE;
-- DROP TABLE IF EXISTS customer_demographics CASCADE;
-- DROP TABLE IF EXISTS employee_territories CASCADE;
-- DROP TABLE IF EXISTS order_details CASCADE;
-- DROP TABLE IF EXISTS orders CASCADE;
-- DROP TABLE IF EXISTS customers CASCADE;
-- DROP TABLE IF EXISTS products CASCADE;
-- DROP TABLE IF EXISTS shippers CASCADE;
-- DROP TABLE IF EXISTS suppliers CASCADE;
-- DROP TABLE IF EXISTS territories CASCADE;
-- DROP TABLE IF EXISTS us_states CASCADE;
-- DROP TABLE IF EXISTS categories CASCADE;
-- DROP TABLE IF EXISTS region CASCADE;
-- DROP TABLE IF EXISTS employees CASCADE;

-- Start a transaction for atomicity
BEGIN;

-- Helper functions for random data generation (no MD5)
-- =============================================================================

-- Function to generate a random string of a given length
CREATE OR REPLACE FUNCTION generate_random_string(length INT) RETURNS TEXT AS $$
DECLARE
  chars TEXT := 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  result TEXT := '';
  i INT;
BEGIN
  FOR i IN 1..length LOOP
    result := result || SUBSTR(chars, FLOOR(RANDOM() * LENGTH(chars) + 1)::INT, 1);
  END LOOP;
  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random date within a specified range
CREATE OR REPLACE FUNCTION generate_random_date(start_date DATE, end_date DATE) RETURNS DATE AS $$
BEGIN
  RETURN start_date + (RANDOM() * (end_date - start_date))::INT;
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random bpchar (fixed-length character string, padded with spaces)
CREATE OR REPLACE FUNCTION generate_random_bpchar(len INT) RETURNS BPCHAR AS $$
DECLARE
  chars TEXT := 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  result TEXT := '';
  i INT;
BEGIN
  FOR i IN 1..len LOOP
    result := result || SUBSTR(chars, FLOOR(RANDOM() * LENGTH(chars) + 1)::INT, 1);
  END LOOP;
  RETURN RPAD(result, len, ' ')::BPCHAR; -- Pad with spaces for bpchar
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random phone number
CREATE OR REPLACE FUNCTION generate_random_phone() RETURNS VARCHAR AS $$
BEGIN
  RETURN '(' || LPAD(FLOOR(RANDOM() * 900 + 100)::TEXT, 3, '0') || ') ' ||
         LPAD(FLOOR(RANDOM() * 900 + 100)::TEXT, 3, '0') || '-' ||
         LPAD(FLOOR(RANDOM() * 9000 + 1000)::TEXT, 4, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random postal code
CREATE OR REPLACE FUNCTION generate_random_postal_code() RETURNS VARCHAR AS $$
BEGIN
  RETURN LPAD(FLOOR(RANDOM() * 90000 + 10000)::TEXT, 5, '0');
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random freight value (real)
CREATE OR REPLACE FUNCTION generate_random_freight() RETURNS REAL AS $$
BEGIN
  RETURN (RANDOM() * 100.0 + 5.0)::REAL; -- Between 5.0 and 105.0
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random unit price (real)
CREATE OR REPLACE FUNCTION generate_random_unit_price() RETURNS REAL AS $$
BEGIN
  RETURN (RANDOM() * 50.0 + 1.0)::REAL; -- Between 1.0 and 51.0
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random quantity (smallint)
CREATE OR REPLACE FUNCTION generate_random_quantity() RETURNS SMALLINT AS $$
BEGIN
  RETURN (FLOOR(RANDOM() * 50) + 1)::SMALLINT; -- Between 1 and 50
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random discount (real, multiples of 0.05)
CREATE OR REPLACE FUNCTION generate_random_discount() RETURNS REAL AS $$
BEGIN
  RETURN (FLOOR(RANDOM() * 5) * 0.05)::REAL; -- 0, 0.05, 0.10, 0.15, 0.20
END;
$$ LANGUAGE plpgsql;

-- Function to generate a random reorder level (smallint)
CREATE OR REPLACE FUNCTION generate_random_reorder_level() RETURNS SMALLINT AS $$
BEGIN
  RETURN (FLOOR(RANDOM() * 20) + 1)::SMALLINT; -- Between 1 and 20
END;
$$ LANGUAGE plpgsql;

-- Function to generate random units in stock/on order (smallint)
CREATE OR REPLACE FUNCTION generate_random_units() RETURNS SMALLINT AS $$
BEGIN
  RETURN (FLOOR(RANDOM() * 200) + 10)::SMALLINT; -- Between 10 and 210
END;
$$ LANGUAGE plpgsql;

-- =============================================================================

-- TRUNCATE tables to ensure a clean insert (optional, uncomment if needed)
-- TRUNCATE TABLE order_details, employee_territories, orders, products,
--                customer_customer_demo, customer_demographics, customers,
--                territories, employees, us_states, suppliers, shippers,
--                region, categories RESTART IDENTITY CASCADE;

-- Insert data into tables respecting foreign key dependencies
-- =============================================================================

-- 1. Insert into categories
INSERT INTO categories (category_id, category_name, description, picture)
SELECT
  id,
  CASE id
    WHEN 1 THEN 'Beverages'
    WHEN 2 THEN 'Condiments'
    WHEN 3 THEN 'Confections'
    WHEN 4 THEN 'Dairy Products'
    WHEN 5 THEN 'Grains/Cereals'
    WHEN 6 THEN 'Meat/Poultry'
    WHEN 7 THEN 'Produce'
    WHEN 8 THEN 'Seafood'
    ELSE 'Category ' || id
  END,
  'Description for ' || generate_random_string(20),
  NULL -- picture (bytea)
FROM GENERATE_SERIES(1, 8) AS id; -- Generate 8 categories

-- 2. Insert into region
INSERT INTO region (region_id, region_description)
SELECT
  id,
  RPAD(
    CASE id
      WHEN 1 THEN 'Eastern'
      WHEN 2 THEN 'Western'
      WHEN 3 THEN 'Northern'
      WHEN 4 THEN 'Southern'
      ELSE 'Region ' || id
    END, 15, ' ')::bpchar
FROM GENERATE_SERIES(1, 4) AS id; -- Generate 4 regions

-- 3. Insert into shippers
INSERT INTO shippers (shipper_id, company_name, phone)
SELECT
  id,
  CASE id
    WHEN 1 THEN 'Speedy Express'
    WHEN 2 THEN 'United Package'
    WHEN 3 THEN 'Federal Shipping'
    ELSE 'Shipper ' || id
  END,
  generate_random_phone()
FROM GENERATE_SERIES(1, 3) AS id; -- Generate 3 shippers

-- 4. Insert into suppliers
INSERT INTO suppliers (supplier_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax, homepage)
SELECT
  id,
  'Supplier Co. ' || generate_random_string(5),
  'Contact ' || generate_random_string(8),
  CASE FLOOR(RANDOM() * 3)
    WHEN 0 THEN 'Sales Manager'
    WHEN 1 THEN 'Purchasing Agent'
    ELSE 'Marketing Rep'
  END,
  generate_random_string(30) || ' St.',
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'London'
    WHEN 1 THEN 'Berlin'
    WHEN 2 THEN 'Paris'
    WHEN 3 THEN 'Tokyo'
    ELSE 'New York'
  END,
  CASE FLOOR(RANDOM() * 3) WHEN 0 THEN 'WA' WHEN 1 THEN 'CA' ELSE NULL END,
  generate_random_postal_code(),
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'UK'
    WHEN 1 THEN 'Germany'
    WHEN 2 THEN 'France'
    WHEN 3 THEN 'Japan'
    ELSE 'USA'
  END,
  generate_random_phone(),
  generate_random_phone(),
  'http://www.' || generate_random_string(10) || '.com'
FROM GENERATE_SERIES(1, 10) AS id; -- Generate 10 suppliers

-- 5. Insert into us_states
INSERT INTO us_states (state_id, state_name, state_abbr, state_region)
SELECT
  id,
  CASE id
    WHEN 1 THEN 'California'
    WHEN 2 THEN 'Texas'
    WHEN 3 THEN 'New York'
    WHEN 4 THEN 'Florida'
    WHEN 5 THEN 'Washington'
    WHEN 6 THEN 'Illinois'
    WHEN 7 THEN 'Pennsylvania'
    WHEN 8 THEN 'Ohio'
    WHEN 9 THEN 'Georgia'
    WHEN 10 THEN 'North Carolina'
    ELSE 'State ' || generate_random_string(5)
  END,
  CASE id
    WHEN 1 THEN 'CA'
    WHEN 2 THEN 'TX'
    WHEN 3 THEN 'NY'
    WHEN 4 THEN 'FL'
    WHEN 5 THEN 'WA'
    WHEN 6 THEN 'IL'
    WHEN 7 THEN 'PA'
    WHEN 8 THEN 'OH'
    WHEN 9 THEN 'GA'
    WHEN 10 THEN 'NC'
    ELSE generate_random_bpchar(2)
  END::varchar(2),
  CASE FLOOR(RANDOM() * 4)
    WHEN 0 THEN 'West'
    WHEN 1 THEN 'South'
    WHEN 2 THEN 'Northeast'
    ELSE 'Midwest'
  END
FROM GENERATE_SERIES(1, 15) AS id; -- Generate 15 states

-- 6. Insert into employees
INSERT INTO employees (employee_id, last_name, first_name, title, title_of_courtesy, birth_date, hire_date, address, city, region, postal_code, country, home_phone, extension, photo, notes, reports_to, photo_path)
SELECT
  id,
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'Davolio'
    WHEN 1 THEN 'Fuller'
    WHEN 2 THEN 'Leverling'
    WHEN 3 THEN 'Peacock'
    ELSE 'Buchanan'
  END,
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'Nancy'
    WHEN 1 THEN 'Andrew'
    WHEN 2 THEN 'Janet'
    WHEN 3 THEN 'Margaret'
    ELSE 'Steven'
  END,
  'Sales Representative',
  CASE FLOOR(RANDOM() * 3) WHEN 0 THEN 'Mr.' WHEN 1 THEN 'Ms.' ELSE 'Dr.' END,
  generate_random_date('1960-01-01'::DATE, '1975-12-31'::DATE),
  generate_random_date('1990-01-01'::DATE, '1995-12-31'::DATE),
  generate_random_string(30) || ' Rd.',
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'Seattle'
    WHEN 1 THEN 'Tacoma'
    WHEN 2 THEN 'London'
    WHEN 3 THEN 'Kirkland'
    ELSE 'Redmond'
  END,
  CASE FLOOR(RANDOM() * 3) WHEN 0 THEN 'WA' WHEN 1 THEN 'UK' ELSE NULL END,
  generate_random_postal_code(),
  CASE FLOOR(RANDOM() * 3) WHEN 0 THEN 'USA' WHEN 1 THEN 'UK' ELSE 'Canada' END,
  generate_random_phone(),
  LPAD(FLOOR(RANDOM() * 9000 + 1000)::TEXT, 4, '0'),
  NULL, -- photo (bytea)
  'Notes for employee ' || id || ': ' || generate_random_string(50),
  CASE WHEN id > 1 AND RANDOM() < 0.7 THEN (FLOOR(RANDOM() * (id - 1)) + 1)::smallint ELSE NULL END, -- reports_to (randomly picks an earlier employee, or NULL)
  '/photos/' || id || '.bmp'
FROM GENERATE_SERIES(1, 9) AS id; -- Generate 9 employees

-- 7. Insert into territories (depends on region)
INSERT INTO territories (territory_id, territory_description, region_id)
SELECT
  id::TEXT,
  RPAD('Territory ' || id, 20, ' ')::bpchar,
  (SELECT region_id FROM region ORDER BY RANDOM() LIMIT 1)
FROM GENERATE_SERIES(1, 20) AS id; -- Generate 20 territories

-- 8. Insert into customers
INSERT INTO customers (customer_id, company_name, contact_name, contact_title, address, city, region, postal_code, country, phone, fax)
SELECT
  generate_random_bpchar(5),
  'Customer Co. ' || generate_random_string(5),
  'Customer Contact ' || generate_random_string(8),
  CASE FLOOR(RANDOM() * 3)
    WHEN 0 THEN 'Owner'
    WHEN 1 THEN 'Sales Representative'
    ELSE 'Marketing Manager'
  END,
  generate_random_string(30) || ' Ave.',
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'Mexico D.F.'
    WHEN 1 THEN 'Buenos Aires'
    WHEN 2 THEN 'Sao Paulo'
    WHEN 3 THEN 'Caracas'
    ELSE 'Madrid'
  END,
  CASE FLOOR(RANDOM() * 3) WHEN 0 THEN 'DF' WHEN 1 THEN 'SP' ELSE NULL END,
  generate_random_postal_code(),
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'Mexico'
    WHEN 1 THEN 'Argentina'
    WHEN 2 THEN 'Brazil'
    WHEN 3 THEN 'Venezuela'
    ELSE 'Spain'
  END,
  generate_random_phone(),
  generate_random_phone()
FROM GENERATE_SERIES(1, 20) AS id; -- Generate 20 customers

-- 9. Insert into customer_demographics
INSERT INTO customer_demographics (customer_type_id, customer_desc)
SELECT
  generate_random_bpchar(10),
  'Description for customer type ' || id || ': ' || generate_random_string(50)
FROM GENERATE_SERIES(1, 5) AS id; -- Generate 5 customer demographics

-- 10. Insert into customer_customer_demo (depends on customers, customer_demographics)
INSERT INTO customer_customer_demo (customer_id, customer_type_id)
SELECT
  (SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT 1),
  (SELECT customer_type_id FROM customer_demographics ORDER BY RANDOM() LIMIT 1)
FROM GENERATE_SERIES(1, 30) AS id
ON CONFLICT (customer_id, customer_type_id) DO NOTHING; -- Handle potential primary key conflicts

-- 11. Insert into products (depends on categories, suppliers)
INSERT INTO products (product_id, product_name, supplier_id, category_id, quantity_per_unit, unit_price, units_in_stock, units_on_order, reorder_level, discontinued)
SELECT
  id,
  'Product ' || generate_random_string(10),
  (SELECT supplier_id FROM suppliers ORDER BY RANDOM() LIMIT 1),
  (SELECT category_id FROM categories ORDER BY RANDOM() LIMIT 1),
  (FLOOR(RANDOM() * 10) + 1)::TEXT || ' boxes',
  generate_random_unit_price(),
  generate_random_units(),
  generate_random_units(),
  generate_random_reorder_level(),
  (FLOOR(RANDOM() * 2))::INT -- 0 or 1 for discontinued
FROM GENERATE_SERIES(1, 50) AS id; -- Generate 50 products

-- 12. Insert into orders (depends on customers, employees, shippers)
INSERT INTO orders (order_id, customer_id, employee_id, order_date, required_date, shipped_date, ship_via, freight, ship_name, ship_address, ship_city, ship_region, ship_postal_code, ship_country)
SELECT
  id,
  (SELECT customer_id FROM customers ORDER BY RANDOM() LIMIT 1),
  (SELECT employee_id FROM employees ORDER BY RANDOM() LIMIT 1),
  generate_random_date('2023-01-01'::DATE, '2024-12-31'::DATE), -- order_date
  generate_random_date('2025-01-01'::DATE, '2025-06-30'::DATE), -- required_date
  CASE WHEN RANDOM() < 0.8 THEN generate_random_date('2024-01-01'::DATE, '2025-05-31'::DATE) ELSE NULL END, -- shipped_date (80% chance of being shipped)
  (SELECT shipper_id FROM shippers ORDER BY RANDOM() LIMIT 1),
  generate_random_freight(),
  'Ship Name ' || generate_random_string(10),
  generate_random_string(40) || ' St.',
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'London'
    WHEN 1 THEN 'Berlin'
    WHEN 2 THEN 'Paris'
    WHEN 3 THEN 'Tokyo'
    ELSE 'New York'
  END,
  CASE FLOOR(RANDOM() * 3) WHEN 0 THEN 'WA' WHEN 1 THEN 'CA' ELSE NULL END,
  generate_random_postal_code(),
  CASE FLOOR(RANDOM() * 5)
    WHEN 0 THEN 'UK'
    WHEN 1 THEN 'Germany'
    WHEN 2 THEN 'France'
    WHEN 3 THEN 'Japan'
    ELSE 'USA'
  END
FROM GENERATE_SERIES(1, 100) AS id; -- Generate 100 orders

-- 13. Insert into employee_territories (depends on employees, territories)
INSERT INTO employee_territories (employee_id, territory_id)
SELECT DISTINCT
  (SELECT employee_id FROM employees ORDER BY RANDOM() LIMIT 1),
  (SELECT territory_id FROM territories ORDER BY RANDOM() LIMIT 1)
FROM GENERATE_SERIES(1, 50) AS id
ON CONFLICT (employee_id, territory_id) DO NOTHING; -- Handle potential primary key conflicts

-- 14. Insert into order_details (depends on orders, products)
INSERT INTO order_details (order_id, product_id, unit_price, quantity, discount)
SELECT
  (SELECT order_id FROM orders ORDER BY RANDOM() LIMIT 1),
  (SELECT product_id FROM products ORDER BY RANDOM() LIMIT 1),
  generate_random_unit_price(),
  generate_random_quantity(),
  generate_random_discount()
FROM GENERATE_SERIES(1, 300) AS id
ON CONFLICT (order_id, product_id) DO NOTHING; -- Handle potential primary key conflicts

-- =============================================================================

-- Drop helper functions
DROP FUNCTION generate_random_string(INT);
DROP FUNCTION generate_random_date(DATE, DATE);
DROP FUNCTION generate_random_bpchar(INT);
DROP FUNCTION generate_random_phone();
DROP FUNCTION generate_random_postal_code();
DROP FUNCTION generate_random_freight();
DROP FUNCTION generate_random_unit_price();
DROP FUNCTION generate_random_quantity();
DROP FUNCTION generate_random_discount();
DROP FUNCTION generate_random_reorder_level();
DROP FUNCTION generate_random_units();

-- Commit the transaction
COMMIT;