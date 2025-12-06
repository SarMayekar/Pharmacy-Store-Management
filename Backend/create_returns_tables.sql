-- Table for Sales Returns
CREATE TABLE IF NOT EXISTS sales_returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    invoice_no VARCHAR(50) NOT NULL UNIQUE,
    return_datetime DATETIME NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_value DECIMAL(10,2) DEFAULT 0,
    gst_value DECIMAL(10,2) DEFAULT 0,
    remarks TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL
);

-- Table for Sales Return Items
CREATE TABLE IF NOT EXISTS sales_return_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sales_return_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    batch_no VARCHAR(50),
    expiry_date DATE,
    hsn_code VARCHAR(50),
    mrp DECIMAL(10,2),
    sgst_percent DECIMAL(5,2),
    cgst_percent DECIMAL(5,2),
    discount_percent DECIMAL(5,2) DEFAULT 0,
        -- packing column removed to keep original schema
    FOREIGN KEY (sales_return_id) REFERENCES sales_returns(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES medicines(id) ON DELETE RESTRICT
);

-- Table for Purchase Returns
CREATE TABLE IF NOT EXISTS purchase_returns (
    id INT AUTO_INCREMENT PRIMARY KEY,
    distributor_id INT,
    invoice_no VARCHAR(50) NOT NULL UNIQUE,
    return_datetime DATETIME NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_value DECIMAL(10,2) DEFAULT 0,
    -- discount_percent column removed to keep original schema
    gst_value DECIMAL(10,2) DEFAULT 0,
    remarks TEXT,
    FOREIGN KEY (distributor_id) REFERENCES distributors(id) ON DELETE SET NULL
);

-- Table for Purchase Return Items
CREATE TABLE IF NOT EXISTS purchase_return_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_return_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    batch_no VARCHAR(50),
    expiry_date DATE,
    hsn_code VARCHAR(50),
    mrp DECIMAL(10,2),
    sgst_percent DECIMAL(5,2),
    cgst_percent DECIMAL(5,2),
    -- packing and free columns removed to keep original schema
    FOREIGN KEY (purchase_return_id) REFERENCES purchase_returns(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES medicines(id) ON DELETE RESTRICT
);
