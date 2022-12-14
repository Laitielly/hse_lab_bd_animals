-- The authorization database, in addition to the main functions, 
-- stores the functions of creating the database we need.

-- Creating a table with the content of user logins and their rights.
CREATE TABLE Log_plus_pass (
  login text PRIMARY KEY,
  passwd text NOT NULL);

-- Password output function for a specific login.
CREATE OR REPLACE FUNCTION get_pass_right(cur_login text)
RETURNS Log_plus_pass
  AS $$
    select * FROM Log_plus_pass as l where l.login = cur_login;
 $$ LANGUAGE sql;

-- Registration procedure.
CREATE PROCEDURE uplogins(logname text, passw text)
  LANGUAGE SQL
		AS $$
		  INSERT INTO Log_plus_pass VALUES (logname, passw);
		$$;

-- Checks whether the database has been created. Returns bool.
CREATE OR REPLACE FUNCTION check_db(dbname text) RETURNS BOOL AS $check_db$
BEGIN
     RETURN (SELECT CASE
                        WHEN
                            (SELECT TRUE
                               FROM pg_database
                              WHERE datname=dbname)
                        THEN
                            TRUE
                        ELSE
                            FALSE
                        END);
END;
$check_db$ LANGUAGE plpgsql;

-- Database creation function. Creates a database and its triggers,
-- tables, functions, procedures, and indexes.
CREATE OR REPLACE FUNCTION create_db(dbname text) RETURNS VOID AS $create_db$
BEGIN
  PERFORM dblink_exec('dbname=logs port=5433 host=127.0.0.1 user=creator password=bkppasswd',
      'CREATE DATABASE ' || quote_ident(dbname));

  PERFORM dblink_connect('myconn', 'dbname=' || quote_ident(dbname) || ' port=5433 host=127.0.0.1 user=creator password=bkppasswd');

  PERFORM dblink_exec('myconn','BEGIN');

-- Create table about shop.
  PERFORM dblink_exec('myconn',
        'CREATE TABLE shop (
            id numeric(6) PRIMARY KEY,
            name text NOT NULL,
            district text NOT NULL,
            phone numeric(10) NOT NULL);');
			
-- Create table about animals.
  PERFORM dblink_exec('myconn',
        'CREATE TABLE animals (
            stamp numeric(6) PRIMARY KEY,
            species text NOT NULL,
            breed text NOT NULL,
            age integer CHECK (age >= 0),
            collars text NOT NULL,
            sex text NOT NULL,
            price NUMERIC(10, 2) CHECK (price >= 0),
            taken bool DEFAULT FALSE,
            idshop numeric(6) REFERENCES shop (id) ON DELETE CASCADE
            ON UPDATE CASCADE);');

-- Create table about buyer.
  PERFORM dblink_exec('myconn',
         'CREATE TABLE buyer (
            pasport numeric(10) PRIMARY KEY,
            name text NOT NULL,
            phone numeric(10) NOT NULL UNIQUE,
            discount integer CHECK (discount between 0 and 100));');

-- Create table about purchase.
  PERFORM dblink_exec('myconn',
        'CREATE TABLE purchase (
            id numeric(6) PRIMARY KEY,
            dat date NOT NULL DEFAULT CURRENT_DATE,
            price numeric(10, 2) CHECK (price >= 0),
            stamp numeric(6) REFERENCES animals (stamp) ON DELETE CASCADE
            	ON UPDATE CASCADE UNIQUE,
            idbuyer numeric(10) REFERENCES buyer (pasport) ON DELETE CASCADE
            ON UPDATE CASCADE);');

-- The function of filling in information about the animals.
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION insert_animal(stamp_inp numeric(6),
                              species_inp text,
                              breed_inp text,
                              age_inp integer,
                              color_inp text,
							  sex_inp text,
							  price_inp numeric(10,2),
							  idshop_inp numeric(6)) RETURNS VOID AS $insert_animal$
        BEGIN
             INSERT INTO animals(stamp, species, breed, age, collars, sex, price, idshop)
             VALUES (stamp_inp, species_inp, breed_inp, age_inp, color_inp, sex_inp, price_inp, idshop_inp);
        END;
        $insert_animal$ LANGUAGE plpgsql;');

-- The function of filling in information about the shop.
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION insert_shop(id_inp numeric(6),
                              name_inp text,
                              district_inp text,
                              phone_inp numeric(10)) RETURNS VOID AS $insert_shop$
        BEGIN
             INSERT INTO shop(id, name, district, phone)
             VALUES (id_inp, name_inp, district_inp, phone_inp);
        END;
        $insert_shop$ LANGUAGE plpgsql;');

-- The function of filling in information about the buyer.
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION insert_buyer(id_inp numeric(10),
                              name_inp text,
                              phone_inp numeric(10),
							                discount_inp integer) RETURNS VOID AS $insert_buyer$
        BEGIN
             INSERT INTO buyer(pasport, name, phone, discount)
             VALUES (id_inp, name_inp, phone_inp, discount_inp);
        END;
        $insert_buyer$ LANGUAGE plpgsql;');

-- The function of filling in information about the purchase.
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION insert_purchase(id_inp numeric(6),
                              dat_inp date,
                              stamp_inp numeric(6),
							  idbuyer_inp numeric(10)) RETURNS VOID AS $insert_purchase$
        BEGIN
             INSERT INTO purchase(id, dat, stamp, idbuyer)
             VALUES (id_inp, dat_inp, stamp_inp, idbuyer_inp);
        END;
        $insert_purchase$ LANGUAGE plpgsql;');

-- Function print_table() should be called like
-- SELECT print_table(NULL::animals);
-- SELECT print_table(NULL::shop);
	PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION print_table(_tbl anyelement)
            RETURNS SETOF anyelement AS
            $print_table$
              BEGIN
                  RETURN QUERY EXECUTE ''SELECT * FROM '' || pg_typeof(_tbl);
              END;
        $print_table$ LANGUAGE plpgsql;');

-- Function clear_table should be called like
-- SELECT clear_table(NULL::animals);
-- SELECT clear_table(NULL::shop);
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION clear_table(_tbl anyelement)
            RETURNs void AS
            $clear_table$
              BEGIN
                  EXECUTE ''TRUNCATE '' || pg_typeof(_tbl) || '' cascade'';
              END;
            $clear_table$ LANGUAGE plpgsql;');

-- This function deletes all the information in all tables.
PERFORM dblink_exec('myconn',
        'CREATE PROCEDURE clear_all_tables()
           	LANGUAGE SQL
          		AS $$
          		  TRUNCATE animals, shop, buyer, purchase cascade;
          		$$;');

-- Deletes a line by ID.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION delete_row(_tbl regclass, key_col text, key_val anyelement)
            RETURNS BOOL AS
            $delete_row$
            DECLARE
              success BOOL;
            BEGIN
                EXECUTE format(''
                    DELETE FROM %s
                    WHERE %I = $1
                    RETURNING TRUE'', _tbl, key_col)
                USING key_val
                INTO success;
                IF success IS TRUE
                THEN
                    RETURN TRUE;
                ELSE
                    RETURN FALSE;
                END IF;
            END;
        $delete_row$ LANGUAGE plpgsql;');

-- A function that changes the price in the purchase, 
-- taking into account the buyer's discount and the price of the animal.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION counter_function()
            RETURNS trigger AS
            $counter_function$
              BEGIN
                  NEW.price := (SELECT a.price - (a.price * buyer.discount/100)
            			from animals as a, buyer
            			where NEW.stamp = a.stamp and buyer.pasport = NEW.idbuyer);

                  RETURN NEW;
              END;
            $counter_function$
            LANGUAGE plpgsql;');

-- Trigger.
PERFORM dblink_exec('myconn',
        'CREATE TRIGGER price_with_disc
            BEFORE INSERT OR UPDATE
            ON purchase
            FOR EACH ROW
            EXECUTE PROCEDURE counter_function();');

-- Trigger function that changes the condition of 
-- the animal to purchased or not, depending on the table purchase.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION bought_animal()
            RETURNS trigger AS
            $bought_animal$
            BEGIN
    		        IF (TG_OP = ''INSERT'' or TG_OP = ''UPDATE'') THEN
                    UPDATE animals SET taken = true
                    WHERE animals.stamp = NEW.stamp;
    		        ELSIF (TG_OP = ''DELETE'') THEN
    			          UPDATE animals SET taken = false
                    WHERE animals.stamp = OLD.stamp;
                END IF;

                RETURN NULL;
            END;
            $bought_animal$ LANGUAGE plpgsql;');

-- Trigger.
PERFORM dblink_exec('myconn',
        'CREATE TRIGGER is_bought
            AFTER INSERT OR UPDATE OR DELETE
            ON purchase
            FOR EACH ROW
        EXECUTE PROCEDURE bought_animal();');

-- Index.
PERFORM dblink_exec('myconn',
        'create index find_by_phenotype on animals (species, breed, collars);');

-- Index.
PERFORM dblink_exec('myconn',
        'create index find_by_phone on buyer (phone);');

-- The function of searching for an animal by its phenotype.
-- SELECT find_animal_by_phenotype('dog', 'akita', 'ginger');
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION find_animal_by_phenotype(species_inp text,
													breed_inp text,
													collars_inp text)
        	RETURNS TABLE(
                      		id_anim numeric(6),
                      		species text,
                      		breed text,
                      		collars text,
                      		sex text,
                      		age integer,
                      		taken bool,
                      		id_shop numeric(6),
                      		name text,
                      		dist text,
                      		phone numeric(10)
        	) AS $find_animal_by_phenotype$
        		BEGIN
        			RETURN QUERY SELECT a.stamp, a.species, a.breed, a.collars, a.sex, a.age,
        			a.taken, a.idshop, s.name, s.district, s.phone
        			FROM animals AS a, shop AS s
        			WHERE species_inp = a.species AND breed_inp = a.breed AND
        			collars_inp = a.collars AND a.idshop = s.id;
        		END;
        		$find_animal_by_phenotype$ LANGUAGE plpgsql;');

-- The function of searching for a buyer by his phone.
-- SELECT find_buyer_by_phone(9407865145);
	PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION find_buyer_by_phone(phone_inp numeric(10))
        	RETURNS TABLE(
          		id numeric(10),
          		name text,
          		phone numeric(10),
          		discount integer
        	) AS $find_buyer_by_phone$
        		BEGIN
        			RETURN QUERY SELECT b.pasport, b.name, b.phone, b.discount
        			FROM buyer AS b
        			WHERE b.phone = phone_inp;
        		END;
        		$find_buyer_by_phone$ LANGUAGE plpgsql;');

-- Store search function by location and name.
-- SELECT find_shop_by_location_name('Sovetskyi', 'Zooptorg');
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION find_shop_by_location_name(district_inp text,
													 name_inp text)
        	RETURNS TABLE(
            		idshop numeric(6),
            		name text,
            		district text,
            		phone numeric(10)
        	) AS $find_shop_by_location_name$
        		BEGIN
          			RETURN QUERY SELECT s.id, s.name, s.district, s.phone
          			FROM shop AS s
          			WHERE district_inp = s.district AND name_inp = s.name;
        		END;
        		$find_shop_by_location_name$ LANGUAGE plpgsql;');

-- Chip purchase search function.
-- SELECT find_purchase_by_stamp(000001);
	PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION find_purchase_by_stamp(stamp_inp numeric(6))
        	RETURNS TABLE(
          		dat date,
          		price numeric(10, 2),
          		idshop numeric(6),
          		idbuyer numeric(10)
        	) AS $find_purchase_by_stamp$
        		BEGIN
        			RETURN QUERY SELECT p.dat, p.price, a.idshop, p.idbuyer
        			FROM purchase AS p, animals a
        			WHERE stamp_inp = p.stamp and a.stamp = p.stamp;
        		END;
        		$find_purchase_by_stamp$ LANGUAGE plpgsql;');

-- Find any information on id.
-- SELECT find_with_id(NULL::animals, 'stamp', 000001);
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION find_with_id(_tbl anyelement, key_col text, key_val numeric)
            RETURNS SETOF anyelement AS
            $find_with_id$
            BEGIN
                RETURN QUERY EXECUTE (''SELECT * FROM '' || pg_typeof(_tbl) || '' WHERE ''
    			                             || key_col || ''='' || key_val);
            END;
            $find_with_id$ LANGUAGE plpgsql;');

-- Removing a buyer by phone.
-- SELECT delete_buyer_by_phone(9407865145);
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION delete_buyer_by_phone(phone_inp numeric(10))
            RETURNS BOOL AS
            $delete_buyer_by_phone$
            DECLARE
              success BOOL;
            BEGIN
                EXECUTE format(''
    				                    DELETE FROM buyer
                                WHERE phone = ''|| phone_inp || ''
                                RETURNING TRUE'')
                INTO success;
                IF success IS TRUE
                THEN
                    RETURN TRUE;
                ELSE
                    RETURN FALSE;
                END IF;
            END;
            $delete_buyer_by_phone$ LANGUAGE plpgsql;');

-- Delete a purchase by the buyer's phone number and the animal's chip.
-- SELECT delete_purchase_by_stamp_phone(9407865145, 000001);
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION delete_purchase_by_stamp_phone(phone_inp numeric(10), stamp_inp numeric(6))
            RETURNS BOOL AS
            $delete_purchase_by_stamp_phone$
            DECLARE
              success BOOL;
            BEGIN
                EXECUTE format(''
    				                      DELETE from purchase as p USING buyer as b, animals as a
    				                      WHERE p.idbuyer = b.pasport AND a.stamp = p.stamp AND
    				                      b.phone = '' || phone_inp ||'' and a.stamp = ''|| stamp_inp ||
                                  '' RETURNING TRUE'')
                INTO success;
                IF success IS TRUE
                THEN
                    RETURN TRUE;
                ELSE
                    RETURN FALSE;
                END IF;
            END;
            $delete_purchase_by_stamp_phone$ LANGUAGE plpgsql;');

-- Delete a store by location and name.
-- SELECT delete_shop_by_location('Sovetskyi', 'Zooptorg');
  PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION delete_shop_by_location(district_inp text, name_inp text)
            RETURNS BOOL AS
            $delete_shop_by_location$
            DECLARE
              success BOOL;
            BEGIN
                EXECUTE format(''
    				                    DELETE from shop WHERE district = $1 and name = $2
    				                    RETURNING TRUE'')
                INTO success
    			         USING district_inp, name_inp;
                IF success IS TRUE
                THEN
                    RETURN TRUE;
                ELSE
                    RETURN FALSE;
                END IF;
            END;
            $delete_shop_by_location$ LANGUAGE plpgsql;');

-- Find purchased or not purchased animals. Accepts bool, returns id strings.
-- SELECT find_not_bought(true);
-- SELECT find_not_bought(false);
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION find_not_bought(mark bool)
        	RETURNS TABLE(
          		stamp numeric,
          		species text,
          		breed text,
          		age integer,
          		collars text,
          		sex text,
          		idshop numeric
        	) AS $find_not_bought$
        		BEGIN
        			RETURN QUERY SELECT a.stamp, a.species, a.breed, a.age, a.collars,
        			a.sex, a.idshop
        			FROM animals AS a
        			WHERE mark = a.taken;
        		END;
        		$find_not_bought$ LANGUAGE plpgsql;');

-- Updating animals data on the chip.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION update_animal_by_stamp(old_stamp numeric, new_stamp numeric,
											new_species text, new_breed text,
											new_age integer, new_collars text,
											new_sex text, new_price numeric(10,2),
											new_idshop numeric(6))
	RETURNS VOID AS $update_animal_by_stamp$
		BEGIN
			UPDATE animals a SET (stamp, species, breed, age, collars, sex,
							               price, idshop) =
			                       (new_stamp, new_species, new_breed, new_age, new_collars,
			                       new_sex, new_price, new_idshop)
			 WHERE a.stamp = old_stamp;
		END;
		$update_animal_by_stamp$ LANGUAGE plpgsql;');


-- Updating buyer data on the passport.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION update_buyer_by_passport(old_passport numeric, new_passport numeric,
											new_name text, new_phone numeric,
											new_discount integer)
          	RETURNS VOID AS $update_buyer_by_passport$
          		BEGIN
                			UPDATE buyer b SET (pasport, name, phone, discount) =
                			(new_passport, new_name, new_phone, new_discount)
                			 WHERE b.pasport = old_passport;
          		END;
          		$update_buyer_by_passport$ LANGUAGE plpgsql;');

-- Updating purchase data on the id.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION update_purchase_by_id(old_id numeric, new_id numeric,
											new_dat date)
        	RETURNS VOID AS $update_purchase_by_id$
        		BEGIN
            			UPDATE purchase p SET (id, dat) =
            			(new_id, new_dat)
            			 WHERE p.id = old_id;
        		END;
        		$update_purchase_by_id$ LANGUAGE plpgsql;');

-- Updating shop data on the id.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE FUNCTION update_shop_by_id(old_id numeric, new_id numeric,
											new_name text, new_dist text, new_phone numeric(10))
          	RETURNS VOID AS $update_shop_by_id$
          		BEGIN
            			UPDATE shop s SET (id, name, district, phone) =
            			(new_id, new_name, new_dist, new_phone)
            			 WHERE s.id = old_id;
          		END;
          		$update_shop_by_id$ LANGUAGE plpgsql;');

-- After creation, give all rights to the client to use the database.
PERFORM dblink_exec('myconn',
        'CREATE OR REPLACE PROCEDURE create_role_client()
			LANGUAGE SQL
				AS $$
				GRANT CONNECT ON DATABASE animals to client;
				GRANT USAGE ON SCHEMA public TO client;
				GRANT SELECT ON ALL TABLES IN SCHEMA public TO client;
				GRANT UPDATE ON ALL TABLES IN SCHEMA public TO client;
				GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO client;
				GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO client;
				GRANT INSERT ON ALL TABLES IN SCHEMA public TO client;
				GRANT DELETE ON ALL TABLES IN SCHEMA public TO client;
				GRANT TRUNCATE ON ALL TABLES IN SCHEMA public TO client;
		$$;');

  PERFORM dblink_exec('myconn','COMMIT');

  PERFORM dblink_disconnect('myconn');

  END;
$create_db$ LANGUAGE plpgsql;


-- Disable all database connections and delete it.
CREATE OR REPLACE FUNCTION drop_db(dbname text) RETURNS VOID AS $drop_db$
BEGIN
	PERFORM pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = dbname
            AND pid <> pg_backend_pid();

  PERFORM dblink_exec('dbname=logs port=5433 host=127.0.0.1 user=creator password=bkppasswd',
                                'DROP DATABASE ' || quote_ident(dbname));
END;
$drop_db$ LANGUAGE plpgsql;
