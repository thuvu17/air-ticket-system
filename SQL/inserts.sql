INSERT INTO airline VALUES('Jet Blue');
INSERT INTO airline VALUES('Frontier');

INSERT INTO airplane VALUES('Jet Blue', 'bo123', 400, 'Boeing', '2010-12-12');
INSERT INTO airplane VALUES('Jet Blue', 'ab456', 800, 'Airbus', '2020-10-30');
INSERT INTO airplane VALUES('Frontier', 'ab147', 900, 'Airbus', '2015-7-27');


INSERT INTO airline_staff VALUES('jd123', 'Jet Blue', 'c9ebd9d560a780ca06d0fb94f046dc26', 'Jane', 'Doe', '1996-11-14');
INSERT INTO airline_staff VALUES('jb456', 'Frontier', 'ae992f6cc79682aacc4d17220cb152c3', 'James', 'Brown', '1997-11-17');


INSERT INTO staff_email VALUES('jd123', 'jane.doe@gmail.com');
INSERT INTO staff_email VALUES('jb456', 'james.brown@gmail.com');


INSERT INTO staff_phone VALUES('jd123', '7183145130');
INSERT INTO staff_phone VALUES('jb456', '6443225833');


INSERT INTO airport VALUES('JFKUS', 'JFK', 'NYC', 'US', 'both');
INSERT INTO airport VALUES('LAXUS', 'LAX', 'Los Angeles', 'US', 'both');
INSERT INTO airport VALUES('PVGSH', 'PVG', 'Shanghai', 'China', 'international');


INSERT INTO flight VALUES('Jet Blue', 'jb123', '2023-4-5 09:00', 'Jet Blue', 'bo123', '2023-4-5 13:00', 'LAXUS', 'JFKUS', 'on-time', 410.75);
INSERT INTO flight VALUES('Jet Blue', 'jb790', '2023-4-14 10:00', 'Jet Blue', 'ab456', '2023-4-14 15:00', 'LAXUS', 'JFKUS', 'on-time', 580.14);
INSERT INTO flight VALUES('Frontier', 'ft489', '2023-4-5 08:00', 'Frontier', 'ab147', '2023-4-6 9:00', 'LAXUS', 'PVGSH', 'delayed', 1534.25);
INSERT INTO flight VALUES('Frontier', 'ft984', '2023-5-5 08:00', 'Frontier', 'ab147', '2023-5-6 9:00', 'PVGSH', 'LAXUS', 'on-time', 1501.25);
INSERT INTO flight VALUES('Frontier', 'ft000', '2023-5-14 08:00', 'Jet Blue', 'ab456', '2023-5-14 9:00', 'PVGSH', 'LAXUS', 'on-time', 248.25);


INSERT INTO ticket VALUES('ec045', 'Jet Blue', 'jb123', '2023-4-5 09:00', 'Mary', 'Green', '1980-3-21');
INSERT INTO ticket VALUES('fc001', 'Frontier', 'ft489', '2023-4-5 08:00', 'John', 'Paul', '1975-4-20');
INSERT INTO ticket VALUES('ec145', 'Jet Blue', 'jb790', '2023-4-14 10:00', 'Tracy', 'Brown', '2000-7-15');


INSERT INTO payment_info VALUES('1234567898765432', 'Credit', 'Mary Green', '2030-4-15');
INSERT INTO payment_info VALUES('1734367598205431', 'Debit', 'John Paul', '2026-2-10');
INSERT INTO payment_info VALUES('1040507258104965', 'Debit', 'Alex Brown', '2027-9-4');


INSERT INTO customer VALUES('mary.green@gmail.com', '2824a83956ba375031872d3b3bd272c4', 'Mary', 'Green', '300', 'Clark', null, 'New York', 'New York', '10017', 'A8305156', '2040-5-4', 'United States', '1980-3-21');
INSERT INTO customer VALUES('john.paul@gmail.com', '530e1d17307fcea31ab6eb9609db1075', 'John', 'Paul', '456', 'High', 'C8', 'Brooklyn', 'New York', '11201', 'A9275123', '2030-1-1', 'United States', '1975-4-20');
INSERT INTO customer VALUES('t.brown@gmail.com', 'f048dac168f2cc18d12a60a424e1748c', 'Tracy', 'Brown', '12', 'Green', '36C', 'Brooklyn', 'New York', '11201', 'A1858392', '2024-11-12', 'United States', '2000-7-15');


INSERT INTO purchases VALUES('ec045', '1234567898765432', 'mary.green@gmail.com', '2023-3-23 19:04', 410.75, null, null);
INSERT INTO purchases VALUES('fc001', '1734367598205431', 'john.paul@gmail.com', '2023-2-19 07:20', 600.25, null, null);
INSERT INTO purchases VALUES('ec145', '1040507258104965', 't.brown@gmail.com', '2023-1-1 05:14', 1503.24, null, null);


INSERT INTO cust_contact VALUES('6473926485', 'mary.green@gmail.com');
INSERT INTO cust_contact VALUES('7463027466', 'john.paul@gmail.com');
INSERT INTO cust_contact VALUES('7778883647', 't.brown@gmail.com');