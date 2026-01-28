import streamlit as st
import pyodbc
import pandas as pd
import hashlib

# --- 1. DATABASE CONFIGURATION ---
SERVER = 'DESKTOP-HL2SR3H'
DATABASE = 'grand_perl'

def get_conn():
    conn_str = (
        f"Driver={{ODBC Driver 18 for SQL Server}};"
        f"Server={SERVER};"
        f"Database={DATABASE};"
        f"Trusted_Connection=yes;"
        f"Encrypt=yes;"
        f"TrustServerCertificate=yes;"
        f"MultipleActiveResultSets=True;"
    )
    return pyodbc.connect(conn_str)

def run_query(query, params=None, is_select=True):
    try:
        conn = get_conn()
        cursor = conn.cursor()
        
        # FIX: Get the actual logged-in ID. If not logged in, use a 'System' ID (e.g., 0)
        # Avoid defaulting to 1 if 1 is a real user like 'ahthackes'
        current_uid = st.session_state.get('user_id')
        
        if current_uid is None:
            # If someone is not logged in (like during a failed login), use ID 0
            current_uid = 0 
            
        # Passing the correct ID to the SQL Server Context
        cursor.execute("EXEC sp_set_session_context 'UserID', ?", (current_uid,))
        
        if params: cursor.execute(query, params)
        else: cursor.execute(query)
        
        if is_select:
            df = pd.DataFrame.from_records(cursor.fetchall(), 
                                           columns=[c[0] for c in cursor.description])
            conn.close()
            return df
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Database Error: {e}")
        return None
# --- 2. AUTHENTICATION ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if 'logged_in' not in st.session_state:
    st.session_state.update({'logged_in': False, 'user': None, 'user_id': 1, 'role': None})

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Grand Pearl HMS: Enterprise", layout="wide")

if not st.session_state.logged_in:
    st.title("🛡️ Secure HMS Gateway")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    user_ip = "127.0.0.1" 

    if st.button("Login"):
        h_pwd = hash_password(p)
        query = """
            SELECT U.UserID, U.Username, R.RoleName 
            FROM System_Users U 
            JOIN User_Roles_Security R ON U.RoleID = R.SecRoleID 
            WHERE U.Username = ? AND U.PasswordHash = ?
        """
        res = run_query(query, (u, h_pwd))
        if res is not None and not res.empty:
            st.session_state.update({
                'logged_in': True, 
                'user': res['Username'].iloc[0], 
                'user_id': int(res['UserID'].iloc[0]),
                'role': res['RoleName'].iloc[0]
            })
            st.rerun()
        else:
            st.error("Invalid Login Credentials.")
            log_fail_sql = "INSERT INTO Failed_Logins (Username, IP_Address, AttemptTime) VALUES (?, ?, GETDATE())"
            run_query(log_fail_sql, (u, user_ip), is_select=False)

else:
    user_role = str(st.session_state.role).strip()
    nav_options = ["📁 Table Explorer", "📊 Quick Insights"]
    if user_role == "SuperAdmin":
        nav_options += ["📞 Guest Inquiries", "👤 User Management", "📈 Executive Dashboard", "🛡️ Security Logs", "🛠️ SQL Console"]
    
    st.sidebar.title("Grand Pearl HMS")
    st.sidebar.info(f"User: **{st.session_state.user}**\nRole: `{user_role}`")
    choice = st.sidebar.radio("Navigation", nav_options)
    
    if st.sidebar.button("Logout"):
        st.session_state.update({'logged_in': False, 'user': None, 'user_id': 1, 'role': None})
        st.rerun()

    if choice == "📞 Guest Inquiries":
        st.title("📞 Guest Booking Inquiries")
        st.subheader("Manage leads captured from the Faisalabad public website")
        
        # This query pulls the Name, Phone, and Room Type from your new table
        # We order by BookingDate DESC so the latest requests appear at the top
        query = "SELECT InquiryID, FullName, GuestPhone, ServiceName, BookingDate FROM Booking_Inquiries ORDER BY BookingDate DESC"
        df_inquiry = run_query(query)
        
        if df_inquiry is not None and not df_inquiry.empty:
            st.metric("Total Active Leads", len(df_inquiry))
            st.dataframe(df_inquiry, use_container_width=True)
            
            # Simple Search Feature
            search = st.text_input("🔍 Search by Name or Phone")
            if search:
                filtered = df_inquiry[
                    df_inquiry['FullName'].str.contains(search, case=False, na=False) | 
                    df_inquiry['GuestPhone'].str.contains(search, na=False)
                ]
                st.write("Search Results:")
                st.table(filtered)
        else:
            st.info("No guest inquiries found in the database yet.")

    # --- 📁 Table Explorer Handler ---
    if choice == "📁 Table Explorer":
        st.header("📁 Database Table Explorer")
        search_query = st.text_input("🔍 Search for a table...")
        tables_df = run_query("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        
        if tables_df is not None:
            all_tables = tables_df['TABLE_NAME'].tolist()
            if user_role != "SuperAdmin":
                forbidden = ['Audit_Logs', 'Failed_Logins', 'System_Users', 'User_Roles_Security']
                all_tables = [t for t in all_tables if t not in forbidden]
            if search_query:
                all_tables = [t for t in all_tables if search_query.lower() in t.lower()]
            
            selected_table = st.selectbox("Select Table", all_tables)
            if selected_table:
                df = run_query(f"SELECT * FROM [{selected_table}]")
                st.dataframe(df, use_container_width=True)
                
                t_add, t_edit, t_del = st.tabs(["➕ Add Record", "📝 Edit Record", "🗑️ Delete Record"])
                
                with t_add:
                    st.subheader("Add New Record")
                    input_cols = df.columns[1:] if len(df.columns) > 1 else df.columns
                    form_payload = {c: st.text_input(f"Enter {c}", key=f"add_{c}") for c in input_cols}
                    if st.button("Save Record"):
                        cols = ", ".join([f"[{k}]" for k in form_payload.keys()])
                        params = ", ".join(["?" for _ in form_payload])
                        run_query(f"INSERT INTO [{selected_table}] ({cols}) VALUES ({params})", list(form_payload.values()), False)
                        st.success("✅ Record Added Successfully!")
                        st.rerun()

                with t_edit:
                    st.subheader("Update Existing Record")
                    pk = df.columns[0]
                    up_id = st.number_input(f"Row ID to Update ({pk})", step=1)
                    up_col = st.selectbox("Select Column", df.columns)
                    up_val = st.text_input("New Value")
                    if st.button("Apply Update"):
                        run_query(f"UPDATE [{selected_table}] SET [{up_col}] = ? WHERE [{pk}] = ?", (up_val, up_id), False)
                        st.success("✅ Record Updated!")
                        st.rerun()

                with t_del:
                    st.subheader("Delete Record")
                    pk = df.columns[0]
                    d_id = st.number_input(f"ID to Remove ({pk})", step=1)
                    if st.button("Permanently Delete", type="primary"):
                        run_query(f"DELETE FROM [{selected_table}] WHERE [{pk}] = ?", (d_id,), False)
                        st.warning("🗑️ Record Deleted.")
                        st.rerun()

    # --- 📊 Quick Insights (UPDATED WITH DATE, DEPT FILTERS & MORE FUNCTIONS) ---
    elif choice == "📊 Quick Insights":
        st.title("📊 Strategic Relational Insights")
        
        # --- SIDEBAR FILTERS FOR INSIGHTS ---
        st.sidebar.markdown("---")
        st.sidebar.subheader("🎯 Report Filters")
        
        # Date Filter
        start_date, end_date = st.sidebar.date_input(
            "Select Date Range", 
            [pd.to_datetime('2025-01-01'), pd.to_datetime('2026-12-31')]
        )
        
        # Department Filter
        dept_df = run_query("SELECT DeptName FROM Departments")
        all_depts = ["All Departments"] + dept_df['DeptName'].tolist()
        sel_dept = st.sidebar.selectbox("Filter by Department", all_depts)

        # Expanded report list
        insight = st.selectbox("Select Report Category", [
            "Current Occupancy", 
            "Guest Service & Preference History", 
            "Room Maintenance & Housekeeping Status",
            "Detailed Restaurant Order Breakdown",
            "Staff Directory & Payroll", 
            "Low Stock Alerts"
        ])
        
        # Convert dates to strings for SQL
        d1, d2 = start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

        if insight == "Current Occupancy":
            st.subheader(f"🛌 Occupancy from {d1} to {d2}")
            q = f"""SELECT G.FirstName + ' ' + G.LastName AS [Guest], R.RoomNumber, RT.TypeName, Res.CheckInDate, Res.Status
                   FROM Reservations Res JOIN Guests G ON Res.GuestID = G.GuestID 
                   JOIN Rooms R ON Res.RoomID = R.RoomID JOIN Room_Types RT ON R.TypeID = RT.TypeID
                   WHERE Res.CheckInDate BETWEEN '{d1}' AND '{d2}'"""
            st.dataframe(run_query(q), use_container_width=True)

        elif insight == "Guest Service & Preference History":
            st.subheader("💎 Guest Profile & Service Usage")
            # Joins Guests with Preferences, Blacklist status, and Spa Bookings
            q = f"""SELECT G.FirstName + ' ' + G.LastName AS [Guest], 
                          GP.Preference, 
                          ISNULL(BG.Reason, 'Not Blacklisted') AS [Security Status],
                          S.ServiceName AS [Last Spa Service],
                          SB.Date AS [Service Date]
                   FROM Guests G
                   LEFT JOIN Guest_Preferences GP ON G.GuestID = GP.GuestID
                   LEFT JOIN Blacklisted_Guests BG ON G.GuestID = BG.GuestID
                   LEFT JOIN Spa_Bookings SB ON G.GuestID = SB.GuestID
                   LEFT JOIN Spa_Services S ON SB.SpaID = S.SpaID
                   WHERE SB.Date BETWEEN '{d1} 00:00:00' AND '{d2} 23:59:59' OR SB.Date IS NULL"""
            st.dataframe(run_query(q), use_container_width=True)

        elif insight == "Room Maintenance & Housekeeping Status":
            st.subheader(f"🧹 Maintenance Tasks for {sel_dept}")
            # Filters by Department dynamically
            dept_filter = "" if sel_dept == "All Departments" else f"AND D.DeptName = '{sel_dept}'"
            q = f"""SELECT R.RoomNumber, R.Status AS [Room Status], 
                          HT.Status AS [Task Status], 
                          E.FullName AS [Assigned Staff],
                          D.DeptName AS [Department]
                   FROM Rooms R
                   LEFT JOIN Housekeeping_Tasks HT ON R.RoomID = HT.RoomID
                   LEFT JOIN Employees E ON HT.EmpID = E.EmpID
                   LEFT JOIN Departments D ON E.DeptID = D.DeptID
                   WHERE 1=1 {dept_filter}"""
            st.dataframe(run_query(q), use_container_width=True)

        elif insight == "Detailed Restaurant Order Breakdown":
            st.subheader(f"🍴 Item-wise Sales from {d1} to {d2}")
            # Joins Orders with Menu Items, Categories, and Outlets
            q = f"""SELECT RO.OutletName, MC.CategoryName, MI.ItemName, 
                          OD.Qty, (OD.Qty * MI.Price) AS [Line Total], O.OrderTime
                   FROM Order_Details OD
                   JOIN Menu_Items MI ON OD.ItemID = MI.ItemID
                   JOIN Menu_Categories MC ON MI.CategoryID = MC.CategoryID
                   JOIN Orders O ON OD.OrderID = O.OrderID
                   JOIN Restaurant_Tables RT ON O.TableID = RT.TableID
                   JOIN Restaurant_Outlets RO ON RT.OutletID = RO.OutletID
                   WHERE O.OrderTime BETWEEN '{d1} 00:00:00' AND '{d2} 23:59:59'"""
            st.dataframe(run_query(q), use_container_width=True)

        elif insight == "Staff Directory & Payroll":
            st.subheader(f"👥 Employee Hierarchy in {sel_dept}")
            dept_filter = "" if sel_dept == "All Departments" else f"WHERE D.DeptName = '{sel_dept}'"
            q = f"""SELECT E.FullName, D.DeptName, Des.Title, E.Salary FROM Employees E 
                   JOIN Departments D ON E.DeptID = D.DeptID JOIN Designations Des ON E.DesigID = Des.DesigID
                   {dept_filter}"""
            st.dataframe(run_query(q), use_container_width=True)

        elif insight == "Low Stock Alerts":
            st.subheader("🚨 Inventory Reorder List")
            q = """SELECT S.ItemName, IC.CatName, I.Qty, S.MinQty 
                   FROM Current_Inventory I 
                   JOIN Stock_Items S ON I.StockID = S.StockID 
                   JOIN Inventory_Cats IC ON S.InvCatID = IC.InvCatID
                   WHERE I.Qty <= S.MinQty"""
            data = run_query(q)
            if data is not None and not data.empty:
                st.warning("Warning: Stock levels below minimum threshold!")
            st.dataframe(data, use_container_width=True)

    # --- 📈 Executive Dashboard Handler ---
    elif choice == "📈 Executive Dashboard":
        st.title("📈 Executive Analytics")
        m1, m2, m3, m4 = st.columns(4)
        
        rev = run_query("SELECT (SELECT ISNULL(SUM(TotalBill),0) FROM CheckOut_Records) + (SELECT ISNULL(SUM(Amount),0) FROM Restaurant_Payments) as t")['t'].iloc[0]
        m1.metric("Total Revenue", f"PKR {rev:,.0f}")
        
        occ_q = run_query("SELECT COUNT(*) as tot, SUM(CASE WHEN Status='Occupied' THEN 1 ELSE 0 END) as occ FROM Rooms")
        rate = (occ_q['occ'].iloc[0] / occ_q['tot'].iloc[0]) * 100
        m2.metric("Occupancy", f"{rate:.1f}%")
        
        m3.metric("Total Guests", run_query("SELECT COUNT(*) as c FROM Guests")['c'].iloc[0])
        m4.metric("Pending Tasks", run_query("SELECT COUNT(*) as c FROM Housekeeping_Tasks WHERE Status != 'Completed'")['c'].iloc[0])

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Food Sales (Top 5)")
            food = run_query("SELECT TOP 5 MI.ItemName, SUM(OD.Qty) as Sales FROM Order_Details OD JOIN Menu_Items MI ON OD.ItemID = MI.ItemID GROUP BY MI.ItemName ORDER BY Sales DESC")
            if not food.empty: st.bar_chart(food.set_index('ItemName'))
        with c2:
            st.subheader("Revenue by Outlet")
            out = run_query("SELECT RO.OutletName, SUM(RP.Amount) as Rev FROM Restaurant_Payments RP JOIN Orders O ON RP.OrderID=O.OrderID JOIN Restaurant_Tables RT ON O.TableID=RT.TableID JOIN Restaurant_Outlets RO ON RT.OutletID=RO.OutletID GROUP BY RO.OutletName")
            if not out.empty: st.area_chart(out.set_index('OutletName'))

    # --- 👤 User Management Handler (FIXED) ---
    elif choice == "👤 User Management":
        st.title("👤 System User Administration")
        # Added 'Delete User' tab for complete management
        t_list, t_add, t_pass, t_del = st.tabs(["List Users", "Create User", "Change Password", "Delete User"])
        
        with t_list:
            q = "SELECT U.UserID, U.Username, R.RoleName, E.FullName FROM System_Users U JOIN User_Roles_Security R ON U.RoleID = R.SecRoleID JOIN Employees E ON U.EmpID = E.EmpID"
            st.dataframe(run_query(q), use_container_width=True)
            
        with t_add:
            st.subheader("Register New Staff Access")
            u_name = st.text_input("New Username", key="new_user_input")
            u_pass = st.text_input("Temporary Password", type="password", key="new_pass_input")
            
            emp_df = run_query("SELECT EmpID, FullName FROM Employees")
            role_df = run_query("SELECT SecRoleID, RoleName FROM User_Roles_Security")
            
            if emp_df is not None and role_df is not None:
                e_id_label = st.selectbox("Link to Employee Profile", emp_df['FullName'])
                r_id_label = st.selectbox("Assign System Role", role_df['RoleName'])
                
                if st.button("Register User Account"):
                    eid = emp_df[emp_df['FullName'] == e_id_label]['EmpID'].iloc[0]
                    rid = role_df[role_df['RoleName'] == r_id_label]['SecRoleID'].iloc[0]
                    # Hashing password before storage
                    run_query("INSERT INTO System_Users (EmpID, Username, PasswordHash, RoleID) VALUES (?,?,?,?)", 
                              (int(eid), u_name, hash_password(u_pass), int(rid)), False)
                    st.success(f"✅ Account created for {u_name}")
                    st.rerun()

        with t_pass:
            st.subheader("Reset User Password")
            user_list = run_query("SELECT Username FROM System_Users")
            if user_list is not None:
                target_user = st.selectbox("Select User Account", user_list['Username'], key="pass_reset_user")
                new_pass = st.text_input("Enter New Password", type="password", key="reset_pass_val")
                confirm_pass = st.text_input("Confirm New Password", type="password", key="reset_pass_conf")
                
                if st.button("Update Password"):
                    if new_pass == confirm_pass:
                        h_pass = hash_password(new_pass)
                        # Updating the password hash for the specific user
                        run_query("UPDATE System_Users SET PasswordHash = ? WHERE Username = ?", (h_pass, target_user), is_select=False)
                        st.success(f"✅ Password updated for {target_user}")
                    else:
                        st.error("❌ Passwords do not match!")

        with t_del:
            st.subheader("Terminate User Access")
            user_list_del = run_query("SELECT Username FROM System_Users")
            if user_list_del is not None:
                user_to_del = st.selectbox("Select User to Remove", user_list_del['Username'], key="del_user_box")
                st.warning(f"⚠️ Are you sure you want to permanently delete `{user_to_del}`?")
                
                if st.button("Confirm Permanent Deletion", type="primary"):
                    # Protection logic to prevent self-deletion
                    if user_to_del == st.session_state.user:
                        st.error("❌ Error: You cannot delete your own account while logged in!")
                    else:
                        run_query("DELETE FROM System_Users WHERE Username = ?", (user_to_del,), is_select=False)
                        st.error(f"🗑️ User account `{user_to_del}` removed.")
                        st.rerun()
    # --- 🛡️ Security Logs & SQL Console Handlers ---
    elif choice == "🛡️ Security Logs":
        st.title("🛡️ Audit Center")
        tab1, tab2 = st.tabs(["Failed Logins", "Audit Trail"])
        with tab1: st.table(run_query("SELECT Username, IP_Address, AttemptTime FROM Failed_Logins ORDER BY AttemptTime DESC"))
        with tab2: st.dataframe(run_query("SELECT a.LogTime, u.Username, a.Action, a.TableAffected FROM Audit_Logs a JOIN System_Users u ON a.UserID = u.UserID ORDER BY a.LogTime DESC"), use_container_width=True)

    elif choice == "🛠️ SQL Console":
        st.title("🛠️ SQL Console")
        cmd = st.text_area("Command")
        if st.button("Run"):
            is_sel = cmd.strip().lower().startswith("select")
            res = run_query(cmd, is_select=is_sel)
            if res is not None:
                st.success("Success"); st.dataframe(res) if is_sel else None