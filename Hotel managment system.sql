-- 1. Create the Database
CREATE DATABASE hotel_managment;

USE hotel_managment;


---------------------------------------------------------
-- MODULE 1: GUEST & ROOM MANAGEMENT (10 Tables)
---------------------------------------------------------
CREATE TABLE Room_Types (
TypeID INT PRIMARY KEY IDENTITY(1,1),
TypeName VARCHAR(50),
BasePrice DECIMAL(10,2),
Description TEXT);
---------------------------------------------------------
CREATE TABLE Rooms (
RoomID INT PRIMARY KEY IDENTITY(1,1),
RoomNumber VARCHAR(10) UNIQUE,
TypeID INT,
Status VARCHAR(20) DEFAULT 'Available',
FOREIGN KEY (TypeID) REFERENCES Room_Types(TypeID));
------------------------------------------------------------
CREATE TABLE Guests (
GuestID INT PRIMARY KEY IDENTITY(1,1),
FirstName VARCHAR(50),
LastName VARCHAR(50),
Email VARCHAR(100),
Phone VARCHAR(20),
Identity_No VARCHAR(50));
-------------------------------------------------------------
CREATE TABLE Reservations (ResID INT PRIMARY KEY IDENTITY(1,1),
GuestID INT, 
RoomID INT, 
CheckInDate DATE,
CheckOutDate DATE,
Status VARCHAR(20),
FOREIGN KEY (GuestID) REFERENCES Guests(GuestID), 
FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID));
----------------------------------------------
CREATE TABLE CheckIn_Records (
CheckInID INT PRIMARY KEY IDENTITY(1,1),
ResID INT,
ActualCheckIn DATETIME,
KeyCardNo VARCHAR(50),
FOREIGN KEY (ResID) REFERENCES Reservations(ResID));
--------------------------------------------------------
CREATE TABLE CheckOut_Records (
CheckOutID INT PRIMARY KEY IDENTITY(1,1),
CheckInID INT,
ActualCheckOut DATETIME, 
TotalBill DECIMAL(10,2),
FOREIGN KEY (CheckInID) REFERENCES CheckIn_Records(CheckInID));
--------------------------------------------------------------

CREATE TABLE Room_Amenities (
AmenityID INT PRIMARY KEY IDENTITY(1,1),
Name VARCHAR(50));
--------------------------------------------------------

CREATE TABLE Room_Amenity_Mapping (
RoomID INT,
AmenityID INT,
PRIMARY KEY(RoomID, AmenityID),
FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
FOREIGN KEY (AmenityID) REFERENCES Room_Amenities(AmenityID));
---------------------------------------------------------

CREATE TABLE Guest_Preferences (PrefID INT PRIMARY KEY IDENTITY(1,1), 
GuestID INT,
Preference TEXT, 
FOREIGN KEY (GuestID) REFERENCES Guests(GuestID));
-------------------------------------------------------------

CREATE TABLE Blacklisted_Guests (
BlacklistID INT PRIMARY KEY IDENTITY(1,1),
GuestID INT, 
Reason TEXT,
FOREIGN KEY (GuestID) REFERENCES Guests(GuestID));
------------------------------------------------------------

---------------------------------------------------------
-- MODULE 2: RESTAURANT & POS (10 Tables)
---------------------------------------------------------
CREATE TABLE Restaurant_Outlets (
OutletID INT PRIMARY KEY IDENTITY(1,1),
OutletName VARCHAR(50));
--------------------------------------------

CREATE TABLE Menu_Categories (
CategoryID INT PRIMARY KEY IDENTITY(1,1),
CategoryName VARCHAR(50));
----------------------------------

CREATE TABLE Menu_Items (
ItemID INT PRIMARY KEY IDENTITY(1,1),
ItemName VARCHAR(100),
Price DECIMAL(10,2),
CategoryID INT,
FOREIGN KEY (CategoryID) REFERENCES Menu_Categories(CategoryID));
--------------------------------------------------------

CREATE TABLE Restaurant_Tables (
TableID INT PRIMARY KEY IDENTITY(1,1),
OutletID INT,
TableNo INT,
Capacity INT, 
FOREIGN KEY (OutletID) REFERENCES Restaurant_Outlets(OutletID));
-------------------------------------------------------------

CREATE TABLE Orders (
OrderID INT PRIMARY KEY IDENTITY(1,1), 
TableID INT, 
GuestID INT,
OrderTime DATETIME DEFAULT GETDATE(),
FOREIGN KEY (TableID) REFERENCES Restaurant_Tables(TableID));
--------------------------------------

CREATE TABLE Order_Details (
DetailID INT PRIMARY KEY IDENTITY(1,1),
OrderID INT,
ItemID INT,
Qty INT, 
FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
FOREIGN KEY (ItemID) REFERENCES Menu_Items(ItemID));
-------------------------------------------------------

CREATE TABLE Kitchen_Tickets (
KOT_ID INT PRIMARY KEY IDENTITY(1,1),
OrderID INT,
Status VARCHAR(20), 
FOREIGN KEY (OrderID) REFERENCES Orders(OrderID));
----------------------------------------------------------

CREATE TABLE Restaurant_Payments (
PayID INT PRIMARY KEY IDENTITY(1,1),
OrderID INT,
Amount DECIMAL(10,2),
PaymentMode VARCHAR(20),
FOREIGN KEY (OrderID) REFERENCES Orders(OrderID));
----------------------------------------------------------------------

CREATE TABLE Table_Reservations (
TabResID INT PRIMARY KEY IDENTITY(1,1),
TableID INT, 
GuestID INT, 
ResTime DATETIME,
FOREIGN KEY (TableID) REFERENCES Restaurant_Tables(TableID));
--------------------------------------------------------------------------

CREATE TABLE Menu_Discounts (
DiscountID INT PRIMARY KEY IDENTITY(1,1),
ItemID INT,
Perc INT,
FOREIGN KEY (ItemID) REFERENCES Menu_Items(ItemID));

-----------------------------------------------------------
-- MODULE 3: HR & PAYROLL (10 Tables)
---------------------------------------------------------
CREATE TABLE Departments (
DeptID INT PRIMARY KEY IDENTITY(1,1), 
DeptName VARCHAR(50));
----------------------

CREATE TABLE Designations (
DesigID INT PRIMARY KEY IDENTITY(1,1), 
Title VARCHAR(50));
------------------------------------------------

CREATE TABLE Employees (
EmpID INT PRIMARY KEY IDENTITY(1,1),
FullName VARCHAR(100),
DeptID INT,
DesigID INT,
Salary DECIMAL(10,2),
FOREIGN KEY (DeptID) REFERENCES Departments(DeptID), 
FOREIGN KEY (DesigID) REFERENCES Designations(DesigID));
-------------------------------------------------------------------

CREATE TABLE Shifts (
ShiftID INT PRIMARY KEY IDENTITY(1,1), 
ShiftName VARCHAR(20),
StartTime TIME,
EndTime TIME);
--------------------------------------------------

CREATE TABLE Attendance (
AttID INT PRIMARY KEY IDENTITY(1,1),
EmpID INT,
Date DATE,
Status VARCHAR(10),
FOREIGN KEY (EmpID) REFERENCES Employees(EmpID));
--------------------------------------

CREATE TABLE Leave_Records (
LeaveID INT PRIMARY KEY IDENTITY(1,1), 
EmpID INT,
LeaveType VARCHAR(20),
Status VARCHAR(20),
FOREIGN KEY (EmpID) REFERENCES Employees(EmpID));
-----------------------------------------------------------------

CREATE TABLE Salary_Slips (
SlipID INT PRIMARY KEY IDENTITY(1,1),
EmpID INT,
Month VARCHAR(20),
NetPay DECIMAL(10,2),
FOREIGN KEY (EmpID) REFERENCES Employees(EmpID));
---------------------------------------------------------

CREATE TABLE Employee_Documents (
DocID INT PRIMARY KEY IDENTITY(1,1),
EmpID INT,
DocType VARCHAR(50),
FOREIGN KEY (EmpID) REFERENCES Employees(EmpID));
-------------------------------------------------------------

CREATE TABLE Performance_Reviews (
ReviewID INT PRIMARY KEY IDENTITY(1,1),
EmpID INT,
Rating INT,
FOREIGN KEY (EmpID) REFERENCES Employees(EmpID));
------------------------------------

CREATE TABLE Staff_Training (
TrainID INT PRIMARY KEY IDENTITY(1,1), 
Topic VARCHAR(100),
Date DATE);


----------------------------------------------
-- MODULE 4: INVENTORY & PROCUREMENT (10 Tables)
---------------------------------------------------------
CREATE TABLE Vendors (
VendorID INT PRIMARY KEY IDENTITY(1,1),
VendorName VARCHAR(100));
------------------------------------------------------------------------------
CREATE TABLE Inventory_Cats (
InvCatID INT PRIMARY KEY IDENTITY(1,1),
CatName VARCHAR(50));
------------------------------------------------

CREATE TABLE Stock_Items (
StockID INT PRIMARY KEY IDENTITY(1,1),
ItemName VARCHAR(100),
InvCatID INT,
MinQty INT,
FOREIGN KEY (InvCatID) REFERENCES Inventory_Cats(InvCatID));

----------------------------------------------------------------

CREATE TABLE Current_Inventory (
InvID INT PRIMARY KEY IDENTITY(1,1),
StockID INT,
Qty INT,
FOREIGN KEY (StockID) REFERENCES Stock_Items(StockID));
----------------------------------------------------

CREATE TABLE Purchase_Orders (
PO_ID INT PRIMARY KEY IDENTITY(1,1), 
VendorID INT, 
TotalAmount DECIMAL(10,2),
FOREIGN KEY (VendorID) REFERENCES Vendors(VendorID));
---------------------------------------------------------------

CREATE TABLE PO_Details (
PODetailID INT PRIMARY KEY IDENTITY(1,1),
PO_ID INT,
StockID INT,
Qty INT,
FOREIGN KEY (PO_ID) REFERENCES Purchase_Orders(PO_ID),
FOREIGN KEY (StockID) REFERENCES Stock_Items(StockID));
------------------------------------------------------------------------

CREATE TABLE Goods_Received (
GRN_ID INT PRIMARY KEY IDENTITY(1,1),
PO_ID INT,
DateReceived DATE,
FOREIGN KEY (PO_ID) REFERENCES Purchase_Orders(PO_ID));
-----------------------------------------------------------------

CREATE TABLE Stock_Issues (
IssueID INT PRIMARY KEY IDENTITY(1,1), 
StockID INT,
DeptID INT,
Qty INT,
FOREIGN KEY (StockID) REFERENCES Stock_Items(StockID),
FOREIGN KEY (DeptID) REFERENCES Departments(DeptID));
-----------------------------------------------------------

CREATE TABLE Damaged_Stock (
DamageID INT PRIMARY KEY IDENTITY(1,1),
StockID INT,
Qty INT,
Reason TEXT,
FOREIGN KEY (StockID) REFERENCES Stock_Items(StockID));
---------------------------------------------------------------

CREATE TABLE Unit_Master (
UnitID INT PRIMARY KEY IDENTITY(1,1), 
UnitName VARCHAR(20));

-----------------------------------------------------------------------
-- MODULE 5: FACILITIES & HOUSEKEEPING (10 Tables)
--------------------------------------------------------------
CREATE TABLE Spa_Services (
SpaID INT PRIMARY KEY IDENTITY(1,1),
ServiceName VARCHAR(50), 
Price DECIMAL(10,2));
-------------------------------------

CREATE TABLE Spa_Bookings (
SpaBookID INT PRIMARY KEY IDENTITY(1,1),
GuestID INT,
SpaID INT,
Date DATETIME,
FOREIGN KEY (GuestID) REFERENCES Guests(GuestID),
FOREIGN KEY (SpaID) REFERENCES Spa_Services(SpaID));
------------------------------------------------

CREATE TABLE Gym_Memberships (
GymID INT PRIMARY KEY IDENTITY(1,1),
GuestID INT,
PlanName VARCHAR(20),
FOREIGN KEY (GuestID) REFERENCES Guests(GuestID));
--------------------------------

CREATE TABLE Event_Halls (
HallID INT PRIMARY KEY IDENTITY(1,1),
HallName VARCHAR(50),
Capacity INT);
--------------------------------------------

CREATE TABLE Hall_Bookings (
HallBookID INT PRIMARY KEY IDENTITY(1,1),
HallID INT,
GuestID INT,
EventDate DATE,
FOREIGN KEY (HallID) REFERENCES Event_Halls(HallID),
FOREIGN KEY (GuestID) REFERENCES Guests(GuestID));
--------------------------------------------------------------

CREATE TABLE Laundry_Items (
LaundryID INT PRIMARY KEY IDENTITY(1,1),
ItemName VARCHAR(50),
Price DECIMAL(10,2));
----------------------------------------

CREATE TABLE Laundry_Orders (
LOrderID INT PRIMARY KEY IDENTITY(1,1), 
GuestID INT, 
OrderDate DATE,
FOREIGN KEY (GuestID) REFERENCES Guests(GuestID));
-------------------------------------------------------------

CREATE TABLE Housekeeping_Tasks (
TaskID INT PRIMARY KEY IDENTITY(1,1),
RoomID INT,
EmpID INT,
Status VARCHAR(20),
FOREIGN KEY (RoomID) REFERENCES Rooms(RoomID),
FOREIGN KEY (EmpID) REFERENCES Employees(EmpID));
----------------------------------------------------------------------

CREATE TABLE Cleaning_Supplies (
SupplyID INT PRIMARY KEY IDENTITY(1,1), 
Name VARCHAR(50));
---------------------------------------

CREATE TABLE Lost_Found (
LF_ID INT PRIMARY KEY IDENTITY(1,1),
Description TEXT,
FoundDate DATE,
Status VARCHAR(20));

-----------------------------------------------------------------
-- MODULE 6: CYBERSECURITY & SYSTEM AUDIT (10 Tables)
-------------------------------------------------------------------
CREATE TABLE User_Roles_Security (
SecRoleID INT PRIMARY KEY IDENTITY(1,1),
RoleName VARCHAR(20));
---------------------------------------

CREATE TABLE System_Users (
UserID INT PRIMARY KEY IDENTITY(1,1),
EmpID INT, 
Username VARCHAR(50) UNIQUE,
PasswordHash VARCHAR(255), 
RoleID INT, 
FOREIGN KEY (EmpID) REFERENCES Employees(EmpID),
FOREIGN KEY (RoleID) REFERENCES User_Roles_Security(SecRoleID));
-----------------------------------------------------------

CREATE TABLE Audit_Logs (LogID INT PRIMARY KEY IDENTITY(1,1), 
UserID INT, 
Action TEXT, 
TableAffected VARCHAR(50), 
LogTime DATETIME DEFAULT GETDATE(), 
FOREIGN KEY (UserID) REFERENCES System_Users(UserID));
---------------------------------------------

CREATE TABLE Failed_Logins (
AttemptID INT PRIMARY KEY IDENTITY(1,1),
Username VARCHAR(50),
IP_Address VARCHAR(45),
AttemptTime DATETIME DEFAULT GETDATE());
------------------------------------------------------------------

CREATE TABLE User_Permissions (
PermID INT PRIMARY KEY IDENTITY(1,1), 
RoleID INT,
PermissionName VARCHAR(50),
FOREIGN KEY (RoleID) REFERENCES User_Roles_Security(SecRoleID));
-----------------------------------------------------------------------------

CREATE TABLE Backup_Logs (
BackupID INT PRIMARY KEY IDENTITY(1,1),
BackupDate DATETIME DEFAULT GETDATE(), 
FilePath VARCHAR(255));
----------------------------------------------------------

CREATE TABLE Session_Tokens (
SessionID INT PRIMARY KEY IDENTITY(1,1),
UserID INT, 
Token VARCHAR(255),
Expiry DATETIME, 
FOREIGN KEY (UserID) REFERENCES System_Users(UserID));
----------------------

CREATE TABLE Password_History (
PassHistID INT PRIMARY KEY IDENTITY(1,1),
UserID INT,
OldHash VARCHAR(255), 
ChangeDate DATETIME DEFAULT GETDATE(),
FOREIGN KEY (UserID) REFERENCES System_Users(UserID));
--------------------------------------------------

CREATE TABLE IP_Whitelist (
WhitelistID INT PRIMARY KEY IDENTITY(1,1),
IP_Address VARCHAR(45),
Description VARCHAR(100));
----------------------------

CREATE TABLE System_Settings (
ConfigID INT PRIMARY KEY IDENTITY(1,1),
ConfigKey VARCHAR(50),
ConfigValue VARCHAR(100));
-------------------------------------------



---------------------------------------------------------
-- Module 7 Feedback & Marketing

---------------------------------------------
CREATE TABLE Guest_Feedback (
    FeedbackID INT PRIMARY KEY IDENTITY(1,1),
    GuestID INT,
    Rating INT CHECK (Rating >= 1 AND Rating <= 5),
    Comments TEXT,
    FeedbackDate DATE DEFAULT GETDATE(),
    FOREIGN KEY (GuestID) REFERENCES Guests(GuestID)
);


CREATE TABLE Promotions_Marketing (
    PromoID INT PRIMARY KEY IDENTITY(1,1),
    PromoName VARCHAR(50),
    DiscountPercentage DECIMAL(5,2),
    StartDate DATE,
    EndDate DATE,
    PromoCode VARCHAR(20) UNIQUE
);




----------------------------------------

-- Triger for security audit on tables modification

----------------------------------------

DECLARE @TableName NVARCHAR(128)
DECLARE @SQL NVARCHAR(MAX)

-- This cursor finds all your tables except the security/audit tables themselves
DECLARE table_cursor CURSOR FOR 
SELECT name FROM sys.tables 
WHERE name NOT IN ('Audit_Logs', 'Failed_Logins', 'Session_Tokens', 'Backup_Logs', 'IP_Whitelist')

OPEN table_cursor
FETCH NEXT FROM table_cursor INTO @TableName

WHILE @@FETCH_STATUS = 0
BEGIN
    SET @SQL = '
    CREATE OR ALTER TRIGGER trg_' + @TableName + '_Audit
    ON [' + @TableName + ']
    AFTER UPDATE, DELETE
    AS
    BEGIN
        SET NOCOUNT ON;
        DECLARE @UserID INT = ISNULL(CAST(SESSION_CONTEXT(N''UserID'') AS INT), 1);
        DECLARE @Action VARCHAR(100);
        DECLARE @Details VARCHAR(MAX);

        IF EXISTS (SELECT * FROM deleted) AND NOT EXISTS (SELECT * FROM inserted)
        BEGIN
            SET @Action = ''DELETE'';
            INSERT INTO Audit_Logs (UserID, Action, TableAffected)
            VALUES (@UserID, @Action + '' operation performed'', ''' + @TableName + ''');
        END

        IF EXISTS (SELECT * FROM deleted) AND EXISTS (SELECT * FROM inserted)
        BEGIN
            SET @Action = ''UPDATE'';
            INSERT INTO Audit_Logs (UserID, Action, TableAffected)
            VALUES (@UserID, @Action + '' operation performed'', ''' + @TableName + ''');
        END
    END'
    
    EXEC sp_executesql @SQL
    PRINT 'Trigger created for: ' + @TableName
    
    FETCH NEXT FROM table_cursor INTO @TableName
END

CLOSE table_cursor
DEALLOCATE table_cursor



-----------------------------------------------------------------------------------------



--------------------------------------------------
CREATE VIEW vw_RoomStatus AS
SELECT 
    R.RoomNumber,
    RT.TypeName,
    R.Status AS RoomStatus,
    ISNULL(G.FirstName + ' ' + G.LastName, 'Vacant') AS GuestName,
    Res.CheckInDate,
    Res.CheckOutDate
FROM Rooms R
JOIN Room_Types RT ON R.TypeID = RT.TypeID
LEFT JOIN Reservations Res ON R.RoomID = Res.RoomID AND Res.Status = 'Confirmed'
LEFT JOIN Guests G ON Res.GuestID = G.GuestID;


SELECT * FROM vw_RoomStatus;

----------------------------------------------------------------------------------

CREATE VIEW vw_VIPs AS
SELECT 
    G.FirstName + ' ' + G.LastName AS TargetName,
    R.RoomNumber,
    RT.TypeName AS RoomClass,
    RT.BasePrice,
    GP.Preference AS Intel_Preferences
FROM Guests G
JOIN Reservations Res ON G.GuestID = Res.GuestID
JOIN Rooms R ON Res.RoomID = R.RoomID
JOIN Room_Types RT ON R.TypeID = RT.TypeID
JOIN Guest_Preferences GP ON G.GuestID = GP.GuestID
WHERE RT.BasePrice > 20000; -- Filtering only rich/VIP targets


SELECT * FROM vw_VIPs;
----------------------------------------------------------------

CREATE VIEW vw_Staff_info AS
SELECT 
    E.EmpID,
    E.FullName,
    D.DeptName,
    Deg.Title AS Designation,
    S.ShiftName,
    S.StartTime,
    S.EndTime
FROM Employees E
JOIN Departments D ON E.DeptID = D.DeptID
JOIN Designations Deg ON E.DesigID = Deg.DesigID
JOIN Shifts S ON E.EmpID % 5 + 1 = S.ShiftID; -- Logic to simulate shift assignment


select * from vw_Staff_info

-------------------------------------------------

CREATE VIEW vw_Stock_Alerts AS
SELECT 
    S.StockID,
    S.ItemName,
    V.VendorName AS PreferredVendor,
    CI.Qty AS Current_Quantity,
    S.MinQty AS Minimum_Required,
    (S.MinQty - CI.Qty) AS Order_Quantity_Needed
FROM Stock_Items S
JOIN Current_Inventory CI ON S.StockID = CI.StockID
JOIN Vendors V ON S.InvCatID = V.VendorID -- Simply mapping vendor to category for display
WHERE CI.Qty <= S.MinQty;


select * from vw_Stock_Alerts

-----------------------------------------------------

CREATE VIEW vw_Kitchen_Orders AS
SELECT 
    O.OrderID,
    RO.OutletName,
    RT.TableNo,
    MI.ItemName,
    OD.Qty,
    KT.Status AS CookingStatus,
    DATEDIFF(MINUTE, O.OrderTime, GETDATE()) AS Minutes_Elapsed
FROM Orders O
JOIN Order_Details OD ON O.OrderID = OD.OrderID
JOIN Menu_Items MI ON OD.ItemID = MI.ItemID
JOIN Restaurant_Tables RT ON O.TableID = RT.TableID
JOIN Restaurant_Outlets RO ON RT.OutletID = RO.OutletID
LEFT JOIN Kitchen_Tickets KT ON O.OrderID = KT.OrderID
WHERE KT.Status IN ('Pending', 'Preparing');


select * from vw_Kitchen_Orders

-------------------------------------------------------
