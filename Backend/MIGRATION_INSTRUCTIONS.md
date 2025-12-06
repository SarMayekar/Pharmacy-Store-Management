Run these commands on the target MySQL server to apply the migration.

1) Backup the database (recommended)

# From PowerShell (adjust paths/user as needed)
# Dump full DB to a file
mysqldump -u root -p --databases pharmacy_db > C:\temp\pharmacy_db_backup.sql

2) Apply migration SQL file (from repository)

# From PowerShell: run the SQL file using mysql client
mysql -u root -p pharmacy_db < "E:\ASTITVA-DRUG-HOUSE\Backend\migration_add_packing_free.sql"

Alternatively, open the SQL file and run the ALTER statements manually from a MySQL client.

3) Verify the schema

# Check medicines packing column
mysql -u root -p -e "USE pharmacy_db; SHOW COLUMNS FROM medicines LIKE 'packing';"
# Check purchase_items free column
mysql -u root -p -e "USE pharmacy_db; SHOW COLUMNS FROM purchase_items LIKE 'free';"
# Check purchase_return_items free column (if applied)
mysql -u root -p -e "USE pharmacy_db; SHOW COLUMNS FROM purchase_return_items LIKE 'free';"

Notes:
- The migration will add a `packing` VARCHAR(100) column to `medicines` and a `free` INT column (default 0) to `purchase_items` and `purchase_return_items`.
- Back up before running migration. Test on a staging DB first if possible.
- If your MySQL user requires a different host/port, add `-h host -P port` to the mysql/mysqldump commands.
- I did not execute these commands on your server; apply them on your environment when ready.
