-- Migration: add packing, free and header discount_percent
SET autocommit=0;
START TRANSACTION;

-- 1) Add packing to medicines
ALTER TABLE medicines
  ADD COLUMN packing VARCHAR(50) DEFAULT NULL;

-- 2) Add packing to purchases and sales headers (optional display field)
ALTER TABLE purchases
  ADD COLUMN packing VARCHAR(50) DEFAULT NULL;

ALTER TABLE sales
  ADD COLUMN packing VARCHAR(50) DEFAULT NULL;

-- 3) Add packing to item level tables
ALTER TABLE purchase_items
  ADD COLUMN packing VARCHAR(50) DEFAULT NULL;

ALTER TABLE sales_items
  ADD COLUMN packing VARCHAR(50) DEFAULT NULL;

ALTER TABLE purchase_return_items
  ADD COLUMN packing VARCHAR(50) DEFAULT NULL;

ALTER TABLE sales_return_items
  ADD COLUMN packing VARCHAR(50) DEFAULT NULL;

-- 4) Add `free` to purchase_items and purchase_return_items (default 0)
ALTER TABLE purchase_items
  ADD COLUMN `free` INT NOT NULL DEFAULT 0;

ALTER TABLE purchase_return_items
  ADD COLUMN `free` INT NOT NULL DEFAULT 0;

-- 5) Add header-level discount_percent to purchases and purchase_returns
ALTER TABLE purchases
  ADD COLUMN discount_percent DECIMAL(5,2) DEFAULT 0;

ALTER TABLE purchase_returns
  ADD COLUMN discount_percent DECIMAL(5,2) DEFAULT 0;

-- 6) Update existing medicines.stock_qty to include past `free` values
UPDATE medicines m
JOIN (
    SELECT product_id, COALESCE(SUM(`free`),0) AS free_sum
    FROM purchase_items
    GROUP BY product_id
) pi ON m.id = pi.product_id
SET m.stock_qty = m.stock_qty + pi.free_sum
WHERE pi.free_sum > 0;

COMMIT;
SET autocommit=1;

-- End migration
