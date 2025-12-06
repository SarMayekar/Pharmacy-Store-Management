# Purchase Edit and Detail View Fix

## Summary
Fixed issue where purchase edit and purchase detail views only showed one row instead of all rows with filled fields, similar to sales edit.

## Changes Made
- [x] Updated `startedit_id` query in `purchases_view` to use LEFT JOIN and COALESCE for deleted medicines
- [x] Updated `showdetail_id` query in `purchases_view` to use LEFT JOIN and COALESCE for deleted medicines
- [x] Updated `purchase_detail_view` function to use LEFT JOIN and COALESCE for deleted medicines
- [x] Ran tests to verify functionality

## Testing
- [x] test_view_purchase.py passed
- [x] test_edit_purchase.py passed
- [x] test_add_purchase.py passed
- [x] Started application server for manual testing

## Result
Purchase edit and detail views now show all rows, including items where the medicine has been deleted (displayed as "Deleted Product").
