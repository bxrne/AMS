# AMS

**DB NAME is XE or XEPDB1 depending on the image**

1. INSTALL: ```pip install -r requirements.txt```
2. RUN: ```flask run```

## DB View definitions:

--VIEW REQUESTS ASSOCIATED WITH GIVEN USER
CREATE  VIEW myrequests
(e_id, request_id, asset_name, asset_brand, asset_model, company_name, request_created, request_updated) 
AS
SELECT r.EMPLOYEE_ID, r.R_ID, a.A_NAME, a.BRAND, a.A_MODEL,  c.C_NAME, r.CREATED_DATE, r.UPDATED_DATE 
FROM  REQUEST r 
JOIN ASSET a ON r.ASSET_ID = a.A_ID 
JOIN COMPANY c ON c.C_ID = a.COMPANY_ID;

SELECT * FROM MYrequests WHERE e_id = 1

-- VIEW ASSETS ASSIGNED TO GIVEN USER
CREATE  VIEW myassets
(e_id, request_id, asset_name, asset_brand, company_name, request_created, request_updated) 
AS
SELECT r.EMPLOYEE_ID, r.R_ID, a.A_NAME, a.BRAND, c.C_NAME, r.CREATED_DATE, r.UPDATED_DATE 
FROM  REQUEST r 
JOIN ASSET a ON r.ASSET_ID = a.A_ID 
JOIN COMPANY c ON c.C_ID = a.COMPANY_ID
WHERE r.IS_OPEN = 0

SELECT * FROM MYASSETS WHERE e_id = 2