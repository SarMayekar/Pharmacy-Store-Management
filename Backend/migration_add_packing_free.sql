-- Migration: add packing to medicines and free to purchase_items
SET autocommit=0;
START TRANSACTION;

ALTER TABLE medicines
  ADD COLUMN packing VARCHAR(100) DEFAULT NULL;

ALTER TABLE purchase_items
  ADD COLUMN `free` INT NOT NULL DEFAULT 0;

-- Optionally add to purchase_return_items if you handle returns with free
ALTER TABLE purchase_return_items
  ADD COLUMN `free` INT NOT NULL DEFAULT 0;

COMMIT;
SET autocommit=1;

-- End migration
