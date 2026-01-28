import streamlit as st
import pyodbc
import pandas as pd

# --- 1. DATABASE CONFIGURATION ---
SERVER = 'DESKTOP-HL2SR3H'
DATABASE = 'grand_perl'

# Updated function to support both SELECT and INSERT commands
def run_query(query, params=None, is_select=True):
    try:
        conn_str = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={SERVER};"
            f"Database={DATABASE};"
            f"Trusted_Connection=yes;"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
            f"MultipleActiveResultSets=True;"
        )
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        if is_select:
            df = pd.DataFrame.from_records(cursor.fetchall(), 
                                           columns=[c[0] for c in cursor.description])
            conn.close()
            return df
        else:
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        st.error(f"Database Error: {e}")
        return None

# --- 2. 5-STAR UI STYLING (CSS) ---
st.set_page_config(page_title="The Grand Pearl | Faisalabad", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
    html, body, [data-testid="stVerticalBlock"] {
        font-family: 'Poppins', sans-serif;
        background-color: #fdfdfd;
    }
    .hero-container {
        position: relative;
        height: 550px;
        background: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.5)), 
                    url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1350&q=80');
        background-size: cover;
        background-position: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        color: #f1f1f1;
        border-radius: 20px;
        margin-bottom: 50px;
    }
    .hero-container h1 {
        font-family: 'Playfair Display', serif;
        font-size: 5rem;
        margin-bottom: 0;
    }
    .room-info {
        padding: 20px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    .price-tag {
        color: #d4af37;
        font-weight: 600;
        font-size: 1.4rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. WEBSITE CONTENT ---

# Hero
st.markdown("""
    <div class="hero-container">
        <h1>THE GRAND PEARL</h1>
        <p>REDEFINING LUXURY IN FAISALABAD</p>
    </div>
""", unsafe_allow_html=True)

# Navigation
col1, col2, col3, col4 = st.columns(4)
with col1: st.button("🏠 Home", use_container_width=True)
with col2: st.button("🛌 Rooms", use_container_width=True)
with col3: st.button("🍴 Dining", use_container_width=True)
with col4: st.button("📞 Contact", use_container_width=True)

st.divider()

# Rooms Section
st.header("💎 Signature Suites & Rooms")
rooms_df = run_query("SELECT TypeName, BasePrice, Description FROM Room_Types")

if rooms_df is not None and not rooms_df.empty:
    for index, row in rooms_df.iterrows():
        img_col, txt_col = st.columns([1, 2])
        
        with img_col:
            # FIXED: Using reliable SVG placeholders with dynamic text
            room_name_encoded = row['TypeName'].replace(' ', '+')
            image_url = f"https://placehold.co/600x400/001f3f/d4af37?text={room_name_encoded}"
            st.image(image_url, use_container_width=True)
            
        with txt_col:
            st.markdown(f"""
                <div class="room-info">
                    <h3>{row['TypeName']}</h3>
                    <p>{row['Description']}</p>
                    <p class="price-tag">PKR {row['BasePrice']:,.0f} <span style='font-size: 1rem; color: #777;'>/ Per Night</span></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Form to capture Inquiry including Full Name
            with st.expander(f"Reserve {row['TypeName']}"):
                guest_name = st.text_input("Your Full Name", key=f"name_{index}")
                phone = st.text_input("Mobile Number", key=f"phone_{index}", placeholder="e.g. 03001234567")
                
                if st.button("Confirm Booking Inquiry", key=f"btn_{index}"):
                    if guest_name and phone:
                        # Updated SQL logic to include FullName
                        insert_query = "INSERT INTO Booking_Inquiries (ServiceName, GuestPhone, FullName) VALUES (?, ?, ?)"
                        success = run_query(insert_query, (row['TypeName'], phone, guest_name), is_select=False)
                        
                        if success:
                            st.balloons()
                            st.success(f"Zabardast {guest_name}! We have received your inquiry for {row['TypeName']}. Our staff will call you on {phone} shortly.")
                        else:
                            st.error("Technical issue with database sync. Please try again.")
                    else:
                        st.warning("Please enter both your Full Name and Mobile Number.")

st.divider()

# Services Section
st.header("✨ Five-Star Amenities")
s_col1, s_col2 = st.columns(2)

with s_col1:
    st.subheader("🍴 Fine Dining")
    # FIXED: Only selecting OutletName to avoid the 'Location' column error
    rests = run_query("SELECT OutletName FROM Restaurant_Outlets")
    if rests is not None:
        for _, r in rests.iterrows():
            st.markdown(f"⭐ **{r['OutletName']}**")

with s_col2:
    st.subheader("💆 Spa & Wellness")
    spas = run_query("SELECT ServiceName, Price FROM Spa_Services")
    if spas is not None:
        for _, s in spas.iterrows():
            st.markdown(f"✨ **{s['ServiceName']}** - PKR {s['Price']:,.0f}")