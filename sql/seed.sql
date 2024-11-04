-- NOTE: This script assumes that at least one user exists in the
--       `users` table. Seeding users is not included here as a 
--       safety measure as it would involve setting passwords.
--       Please make sure you at least have a user (ID 1) in your
--       table before executing this script.


USE calculator_service;


DELETE FROM record;
DELETE FROM operation;

ALTER TABLE record AUTO_INCREMENT = 1;
ALTER TABLE operation AUTO_INCREMENT = 1;


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
INSERT INTO record (
    `operation_id`,
    `user_id`,
    `amount`,
    `user_balance`,
    `operation_response`,
    `date`
)
VALUES
    (
        6,
        1,
        1,
        24.0,
        JSON_OBJECT('operation', 'random_string', 'operands', JSON_ARRAY(), 'result', 'ABC123'),
        TIMESTAMP('2024-11-02 12:30')
    ),
    (
        1,
        1,
        1,
        23.9,
        JSON_OBJECT('operation', 'addition', 'operands', JSON_ARRAY(1, 2), 'result', 3),
        TIMESTAMP('2024-11-02 12:33')
    ),
    (
        3,
        1,
        1,
        23.65,
        JSON_OBJECT('operation', 'multiplication', 'operands', JSON_ARRAY(21, 2), 'result', 42),
        TIMESTAMP('2024-11-02 13:17')
    );
