\c daqss
START TRANSACTION;
INSERT INTO levels_of_data_granularity (level_name, ordering)
VALUES ('value', 0),
       ('row', 1),
       ('column', 1),
       ('table', 2),
       ('database', 3),
       ('system', 4);
END TRANSACTION;