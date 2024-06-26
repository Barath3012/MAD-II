CREATE TABLE IF NOT EXISTS ROLES (ROLE_ID INTEGER PRIMARY KEY, ROLE_NAME VARCHAR(20) NOT NULL);
CREATE TABLE IF NOT EXISTS SECTIONS (SECTION_ID INTEGER PRIMARY KEY, SECTION_NAME VARCHAR(20) NOT NULL);
CREATE TABLE IF NOT EXISTS USER (USER_ID INTEGER PRIMARY KEY, ROLE_ID INT NOT NULL, USER_NAME VARCHAR(20) NOT NULL UNIQUE,USER_PASSWORD VARCHAR(20) NOT NULL, FOREIGN KEY(ROLE_ID) REFERENCES ROLES(ROLE_ID));
CREATE TABLE IF NOT EXISTS USER_BILLS (BILL_ID INTEGER PRIMARY KEY, USER_ID INT NOT NULL, BILL_ITEMS BLOB NOT NULL, BILL_AMOUNT INT NOT NULL, FOREIGN KEY(USER_ID) REFERENCES USER(USER_ID));
CREATE TABLE IF NOT EXISTS USER_CART (CART_ID INTEGER PRIMARY KEY, USER_ID INT NOT NULL, CART_ITEMS BLOB NOT NULL, FOREIGN KEY(USER_ID) REFERENCES USER(USER_ID));
CREATE TABLE IF NOT EXISTS PRODUCTS (PRODUCT_ID INTEGER PRIMARY KEY, PRODUCT_NAME VARCHAR(20) NOT NULL, SECTION_ID INT NOT NULL, PRODUCT_PRICE INT NOT NULL, PRODUCT_UNIT BLOB, FOREIGN KEY(SECTION_ID) REFERENCES SECTIONS(SECTION_ID));
CREATE TABLE IF NOT EXISTS PRODUCT_INVENTORY (INVENTORY_ID INTEGER PRIMARY KEY, PRODUCT_ID INT NOT NULL, PRODUCT_INVENTORY_QUANTITY INT, FOREIGN KEY(PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID));