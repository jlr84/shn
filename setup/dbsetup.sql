/*
Initial setup file for establishing required database, tables
users, and permissions required within mysql for SHN project.
    Usage:
        $ cat thisfile.sql | mysql -u root -p
        # Then type password when requested
*/

-- Create database
CREATE DATABASE shn_database;

-- Change to use just-created database
USE shn_database;

-- Create tables
CREATE TABLE status
(id SERIAL,
	timestamp DATETIME NOT NULL,
	agent char(30) NOT NULL,
	ctlrid bigint(20) NOT NULL,
	status INT NOT NULL,
	alias char(30),
	PRIMARY KEY (id));

CREATE TABLE agents
(id SERIAL,
	timestamp DATETIME NOT NULL,
	host char(30) NOT NULL,
	port INT NOT NULL,
	alias char(30),
	PRIMARY KEY (id));

-- Create monitor user and grant privileges
GRANT SELECT, INSERT
ON shn_database.status
TO 'monitor_admin'@'localhost'
IDENTIFIED BY 'monitorPassword';

GRANT SELECT
ON shn_database.agents
TO 'monitor_admin'@'localhost'
IDENTIFIED BY 'monitorPassword';

-- Create controller user and grant privileges
GRANT SELECT, INSERT, UPDATE, DELETE
ON shn_database.agents
TO 'controller_admin'@'localhost'
IDENTIFIED BY 'controlPassword';

GRANT SELECT
ON shn_database.status
TO 'controller_admin'@'localhost'
IDENTIFIED BY 'controlPassword';
