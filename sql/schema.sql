-- NOTE: if you're setting up the database for local development,
--       this does require that you have a calculator_service db
USE calculator_service;

DROP TABLE IF EXISTS record;
DROP TABLE IF EXISTS `user`;
DROP TABLE IF EXISTS operation;

-- user stores users with their login information
CREATE TABLE `user` (
    `id` MEDIUMINT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(255) UNIQUE NOT NULL,
    `password` VARCHAR(72) NOT NULL,
    `status` ENUM('active', 'inactive') NOT NULL,
    PRIMARY KEY (id)
);

-- operation stores a calculator operation (e.g. addition, subtraction)
CREATE TABLE operation (
    `id` MEDIUMINT NOT NULL AUTO_INCREMENT,
    `type` ENUM('addition', 'subtraction', 'multiplication', 'division', 'square_root', 'random_string') NOT NULL,
    `cost` DECIMAL(15, 2) NOT NULL,
    PRIMARY KEY (id)
);

-- record stores a calculation made by a user
CREATE TABLE record (
    `id` MEDIUMINT NOT NULL AUTO_INCREMENT,
    `operation_id` MEDIUMINT NOT NULL,
    `user_id` MEDIUMINT NOT NULL,
    `amount` SMALLINT NOT NULL,
    `user_balance` DECIMAL(15, 2) NOT NULL,
    `operation_response` JSON NOT NULL,
    `date` TIMESTAMP NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT `user_id` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `operation_id` FOREIGN KEY (`operation_id`) REFERENCES `operation`(`id`) ON DELETE RESTRICT ON UPDATE CASCADE
);
