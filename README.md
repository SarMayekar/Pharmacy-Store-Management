# Pharmacy Management System

## Overview
This is a Pharmacy Management System built with Flask (Backend) and MySQL (Database). It manages Medicines, Purchases, Sales, Patients, Doctors, and Distributors.

## Recent Enhancements (Sale Rate & Discount)
We have added support for **Sale Rate** and **Sale Discount %** to the Purchases and Inventory modules.

### Key Features
- **Purchase Rate**: The rate at which medicine is bought from the distributor.
- **Sale Discount %**: The discount percentage applied to the MRP to calculate the Sale Rate (typically for Branded medicines).
- **Sale Rate**: The rate at which medicine is sold to the patient.
    - **Branded**: Calculated as `MRP - (MRP * Sale Discount / 100)`.
    - **Generic**: Can be manually entered (Sale Discount is usually 0).

### Workflow
1.  **Adding a Purchase**:
    - Enter the **MRP**.
    - If **Branded**: Enter **Sale Discount %**. The **Sale Rate** is auto-calculated.
    - If **Generic**: Enter **Sale Rate** manually.
    - Saving the purchase automatically updates the **Medicines Inventory** with the new `Purchase Rate`, `Sale Rate`, and `Sale Discount %`.
    - **Note**: This update happens for both *new* medicines and *existing* medicines (updating their current rates).

2.  **Inventory**:
    - The `Medicines` table now stores the latest `Purchase Rate`, `Sale Rate`, and `Sale Discount %`.

## Setup & Running
1.  **Database**: Ensure MySQL is running and `pharmacy_db` is set up.
2.  **Backend**:
    ```bash
    cd Backend
    python app.py
    ```
3.  **Access**: Open browser at `http://127.0.0.1:5000`.

## Database Schema Changes
- **`purchase_items`**: Added `sale_rate`, `sale_discount_percent`.
- **`medicines`**: Added `purchase_rate`, `sale_rate`, `sale_discount_percent`.
