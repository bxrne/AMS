-- Data Definition Statements
CREATE TABLE DEPARTMENT (
    d_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    d_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (d_id)
);

CREATE TABLE JOB (
    j_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    title VARCHAR(255) NOT NULL,
    PRIMARY KEY (j_id)
);

CREATE TABLE COMPANY (
    c_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    c_name VARCHAR(255) NOT NULL,
    PRIMARY KEY (c_id)
);

CREATE TABLE ASSET (
    a_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    a_name VARCHAR(255) NOT NULL,
    brand VARCHAR(255) NOT NULL,
    company_id int NOT NULL,
    FOREIGN KEY (company_id) REFERENCES COMPANY(c_id),
    a_model VARCHAR(255) NOT NULL,
    is_available NUMBER(1) DEFAULT 1,
    CHECK (is_available IN (0, 1)),
    is_retired NUMBER(1) DEFAULT 0,
    CHECK (is_retired IN (0, 1)),
    PRIMARY KEY (a_id),

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_date TIMESTAMP
);

CREATE TABLE  LOGIN (
    l_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    email_address VARCHAR(255) UNIQUE NOT NULL,
    l_password VARCHAR(20) NOT NULL,
    PRIMARY KEY (l_id),

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_date TIMESTAMP
);

CREATE TABLE EMPLOYEE (
    employee_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,

    is_pending NUMBER(1) DEFAULT 1,
    is_approved NUMBER(1) DEFAULT 0,
    CHECK (is_pending IN (0, 1)),
    CHECK (is_approved IN (0, 1)),

    job_id int NOT NULL,
    FOREIGN KEY (job_id) REFERENCES JOB(j_id),

    dept_id int NOT NULL,
    FOREIGN KEY (dept_id) REFERENCES DEPARTMENT(d_id),

    login_id int NOT NULL,
    FOREIGN KEY (login_id) REFERENCES LOGIN(l_id),

    PRIMARY KEY (employee_id),

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_date TIMESTAMP
);

CREATE TABLE COORDINATOR (
    coordinator_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    employee_id int NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    PRIMARY KEY (coordinator_id)  ,

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_date TIMESTAMP
);

CREATE TABLE REQUEST (
    r_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),

    employee_id int NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),

    asset_id int NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES ASSET(a_id),

    is_open NUMBER(1) DEFAULT 1,
    CHECK (is_open IN (0, 1)),

    is_approved NUMBER(1) DEFAULT 0,
    CHECK (is_approved IN (0, 1)),

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_date TIMESTAMP,

    PRIMARY KEY (r_id)
);

CREATE TABLE ASSET_HISTORY (
    a_h_id int GENERATED ALWAYS as IDENTITY(START with 1 INCREMENT by 1),
    asset_id int NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES ASSET(a_id),
    employee_id int NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES EMPLOYEE(employee_id),
    request_id int NOT NULL,
    FOREIGN KEY (request_id) REFERENCES REQUEST(r_id),
    PRIMARY KEY (a_h_id),

    date_assigned TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    date_returned TIMESTAMP
);