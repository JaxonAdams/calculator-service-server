-- NOTE: This script assumes that at least one user exists in the
--       `users` table. Seeding users is not included here as a 
--       safety measure as it would involve setting passwords.
--       Please make sure you at least have a user (ID 1) in your
--       table before executing this script.


USE calculator_service;


DELETE FROM operation;
DELETE FROM record;

ALTER TABLE operation AUTO_INCREMENT = 1;
ALTER TABLE record AUTO_INCREMENT = 1;


-- Seed initial operations
INSERT INTO operation (
    `type`,
    `cost`
)
VALUES
    ('addition', 0.1),
    ('subtraction', 0.1),
    ('multiplication', 0.25),
    ('division', 0.25),
    ('square_root', 0.75),
    ('random_string', 1.0);


-- Seed some dummy transactions for user ID 1
-- TODO: Update operation_response to match actual JSON response
INSERT INTO record (
    `operation_id`,
    `user_id`,
    `amount`,
    `user_balance`,
    `operation_response`
)
VALUES
    (
        6,
        1,
        1,
        24.0,
        JSON_OBJECT('status', 'success', 'result', 'ABC123')
    ),
    (
        1,
        1,
        1,
        23.9,
        JSON_OBJECT('status', 'success', 'result', 42)
    ),
    (
        3,
        1,
        1,
        23.65,
        JSON_OBJECT('status', 'success', 'result', 72520)
    );
