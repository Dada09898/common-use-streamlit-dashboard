import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------------------
# Initialize session state
# -------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'premium' not in st.session_state:
    st.session_state['premium'] = False

# -------------------------------
# User database (temporary in memory)
# -------------------------------
if 'users' not in st.session_state:
    st.session_state['users'] = {}  # username -> dict(name,email,mobile,password)

# -------------------------------
# Function to send email notification
# -------------------------------
def send_registration_email(to_email, name, username):
    try:
        # Gmail credentials (replace with your email & app password)
        sender_email = "yourgmail@gmail.com"
        sender_password = "your_app_password"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = "New Account Registered - Dashboard"

        body = f"""
        Hello {name},

        Your account has been successfully created!

        Username: {username}
        Email: {to_email}

        You can now login to the Dashboard.

        Regards,
        Dashboard Team
        """
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.warning(f"Email could not be sent: {e}")
        return False

# -------------------------------
# Sidebar: Login or Create Account
# -------------------------------
st.sidebar.title("🔐 Login / Create Account")
mode = st.sidebar.radio("Select Mode:", ["Login", "Create Account"])

if mode == "Create Account":
    name = st.sidebar.text_input("Full Name")
    email = st.sidebar.text_input("Email")
    mobile = st.sidebar.text_input("Mobile Number")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Create Account"):
        if username in st.session_state['users']:
            st.sidebar.error("Username already exists!")
        elif name and email and mobile and username and password:
            st.session_state['users'][username] = {
                "name": name, "email": email, "mobile": mobile, "password": password
            }
            send_registration_email(email, name, username)
            st.sidebar.success("✅ Account created! You can now login.")
        else:
            st.sidebar.error("Please fill all fields")

elif mode == "Login":
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = st.session_state['users'].get(username)
        if user and user['password'] == password:
            st.session_state['logged_in'] = True
            st.session_state['username'] = username
            st.sidebar.success(f"✅ Welcome {user['name']}!")
        else:
            st.sidebar.error("❌ Invalid username or password")

# -------------------------------
# Main Dashboard
# -------------------------------
if st.session_state['logged_in']:
    user_info = st.session_state['users'][st.session_state['username']]
    st.title(f"Welcome, {user_info['name']}! 🚀 Data Analytics Dashboard")

    # -------------------------------
    # Sidebar Navigation
    # -------------------------------
    st.sidebar.title("Navigation")
    menu_option = st.sidebar.radio("Select Page:", [
        "Welcome", "Upload & Explore Data", "Analysis", "Factors & Causes", "Conclusion & Insights", "Premium Features"
    ])

    # -------------------------------
    # File Upload
    # -------------------------------
    uploaded_file = None
    if menu_option in ["Upload & Explore Data", "Analysis", "Factors & Causes"]:
        uploaded_file = st.sidebar.file_uploader(
            "Upload Dataset (CSV, Excel, JSON)", type=["csv", "xlsx", "json"]
        )

    df = None
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(".xlsx"):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".json"):
                df = pd.read_json(uploaded_file)
            st.success("✅ Dataset loaded successfully")
            st.dataframe(df.head(10))
        except Exception as e:
            st.error(f"Error loading file: {e}")

    # -------------------------------
    # Welcome Page
    # -------------------------------
    if menu_option == "Welcome":
        st.subheader("📊 Welcome to the Interactive Data Dashboard")
        st.markdown("""
        This dashboard allows business users and data scientists to:
        - Upload any dataset (CSV, Excel, JSON)
        - Explore Univariate, Bivariate, and Multivariate relationships
        - Analyze Factors & Causes impacting KPIs
        - Generate automatic summary pointers
        - Use Premium features for advanced analytics
        """)

    # -------------------------------
    # Analysis Page
    # -------------------------------
    if menu_option == "Analysis" and df is not None:
        st.subheader("🔹 Data Analysis")
        analysis_type = st.radio("Select Analysis Type:", ["Univariate", "Bivariate", "Multivariate"])
        top_n = st.slider("Top N records to analyze:", min_value=5, max_value=50, value=10)

        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

        # -------------------------
        # Univariate
        # -------------------------
        if analysis_type == "Univariate":
            col = st.selectbox("Select Column:", df.columns)
            chart_type = st.selectbox("Select Graph Type:", ["Bar", "Histogram", "Pie", "Box", "Area", "Treemap", "Radar"])
            data = df.head(top_n)

            if chart_type == "Bar":
                vc = data[col].value_counts().reset_index()
                vc.columns = [col, 'count']
                fig = px.bar(vc, x=col, y='count', color_discrete_sequence=colors)
            elif chart_type == "Histogram":
                fig = px.histogram(data, x=col, color_discrete_sequence=colors)
            elif chart_type == "Pie":
                fig = px.pie(data, names=col)
            elif chart_type == "Box":
                fig = px.box(data, y=col)
            elif chart_type == "Area":
                fig = px.area(data, y=col)
            elif chart_type == "Treemap":
                fig = px.treemap(data, path=[col], values=col)
            elif chart_type == "Radar":
                fig = go.Figure(go.Scatterpolar(r=data[col], theta=data.index[:len(data)], fill='toself'))
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### ✅ Key Insights")
            st.markdown(f"- Column analyzed: {col}")
            st.markdown(f"- Top {top_n} records visualized")

        # -------------------------
        # Bivariate
        # -------------------------
        if analysis_type == "Bivariate":
            x_col = st.selectbox("Select X-axis Column:", df.columns)
            y_col = st.selectbox("Select Y-axis Column:", df.columns)
            chart_type = st.selectbox("Select Graph Type:", ["Scatter", "Line", "Bar", "Area"])
            data = df.head(top_n)

            if chart_type == "Scatter":
                fig = px.scatter(data, x=x_col, y=y_col, color=y_col)
            elif chart_type == "Line":
                fig = px.line(data, x=x_col, y=y_col)
            elif chart_type == "Bar":
                fig = px.bar(data, x=x_col, y=y_col)
            elif chart_type == "Area":
                fig = px.area(data, x=x_col, y=y_col)
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### ✅ Key Insights")
            st.markdown(f"- X-axis: {x_col}, Y-axis: {y_col}")
            st.markdown(f"- Top {top_n} records visualized")

        # -------------------------
        # Multivariate
        # -------------------------
        if analysis_type == "Multivariate":
            cols = st.multiselect("Select 3+ Columns:", df.columns, default=df.columns[:3])
            data = df.head(top_n)
            chart_type = st.selectbox("Select Graph Type:", ["Scatter Matrix", "Heatmap", "Radar", "Treemap", "Area"])

            if len(cols) >= 3:
                if chart_type == "Scatter Matrix":
                    fig = px.scatter_matrix(data[cols])
                elif chart_type == "Heatmap":
                    fig = px.imshow(data[cols].corr(), text_auto=True)
                elif chart_type == "Radar":
                    fig = go.Figure()
                    for i in range(len(data)):
                        fig.add_trace(go.Scatterpolar(r=data[cols].iloc[i], theta=cols, fill='toself', name=f"Row {i}"))
                elif chart_type == "Treemap":
                    fig = px.treemap(data, path=cols, values=cols[0])
                elif chart_type == "Area":
                    fig = px.area(data, y=cols)
                st.plotly_chart(fig, use_container_width=True)

                st.markdown("### ✅ Key Insights")
                st.markdown(f"- Columns analyzed: {', '.join(cols)}")
                st.markdown(f"- Top {top_n} records visualized")
            else:
                st.warning("⚠️ Select at least 3 columns for multivariate analysis")

    # -------------------------
    # Factors & Causes Page
    # -------------------------
    if menu_option == "Factors & Causes" and df is not None:
        st.subheader("⚡ Factors & Causes Analysis")
        top_n = st.slider("Top N entities:", min_value=5, max_value=20, value=10)
        colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

        def plot_top(df_grouped, group_col, top_n, title_prefix):
            df_top = df_grouped.head(top_n).reset_index()
            fig = px.bar(df_top, x=group_col, y=["delivery_delay", "processing_time", "freight_value"],
                         barmode="group", color_discrete_sequence=colors,
                         labels={"value":"Avg Value","variable":"Metric"},
                         title=f"Top {top_n} {title_prefix} by Delay/Processing/Freight")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"### ✅ Key Insights ({title_prefix})")
            st.markdown(f"- Top {top_n} {title_prefix} analyzed by delivery delay, processing time, freight value")

        # Sellers
        sellers = df.groupby("seller_id")[["delivery_delay","processing_time","freight_value"]].mean().sort_values("delivery_delay", ascending=False)
        plot_top(sellers, "seller_id", top_n, "Sellers")

        # Cities
        cities = df.groupby("customer_city")[["delivery_delay","processing_time","freight_value"]].mean().sort_values("delivery_delay", ascending=False)
        plot_top(cities, "customer_city", top_n, "Cities")

        # Products
        products = df.groupby("product_id")[["delivery_delay","processing_time","freight_value"]].mean().sort_values("delivery_delay", ascending=False)
        plot_top(products, "product_id", top_n, "Products")

    # -------------------------
    # Conclusion & Insights
    # -------------------------
    if menu_option == "Conclusion & Insights":
        st.title("📌 Conclusion & Insights")
        st.markdown("""
        ### Key Findings
        * Delivery delays drive negative reviews
        * Fast processing correlates with positive feedback
        * Freight cost alone isn’t a deal‑breaker
        * Top sellers, cities, products impact KPIs
        ### Next Steps
        1. Improve ETA accuracy
        2. Automate low-risk order approvals
        3. Target worst sellers/cities/products first
        4. Monitor KPI trends
        5. Use dashboards for data-driven decisions
        """)

    # -------------------------
    # Premium Features
    # -------------------------
    if menu_option == "Premium Features":
        st.subheader("💎 Premium Analytics")
        activate = st.checkbox("Activate Premium Mode", value=st.session_state['premium'])
        if activate:
            st.session_state['premium'] = True
            st.success("✅ Premium mode activated! Advanced analytics enabled.")
            st.markdown("""
            - Detailed multivariate correlation heatmaps
            - Forecasting with trends
            - Automated executive summary reports
            - Export charts with high resolution
            - Advanced interactive dashboards
            """)
else:
    st.info("ℹ️ Please login or create an account to access the dashboard.")
