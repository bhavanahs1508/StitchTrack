import streamlit as st
from supabase import create_client
from datetime import date
import calendar

# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="StitchTrack",
    page_icon="🧵",
    layout="wide"
)

# ---------------- SUPABASE CONNECTION ----------------

SUPABASE_URL = "https://rmpjwshhwcgneesjqayr.supabase.co"
SUPABASE_KEY = "sb_publishable_3yIox6O_4CX3_yNf7MXd1g_4YpDqdCV"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- APP SETTINGS ----------------

st.title("🧵 StitchTrack")
st.caption("Track Every Stitch. Know Every Rupee.")

RATE = 1.30

# ---------------- DAILY WORK ENTRY ----------------

st.subheader("📅 Daily Work Entry")

selected_date = st.date_input(
    "Select Date",
    value=date.today()
)

date_string = selected_date.strftime("%Y-%m-%d")
day_name = selected_date.strftime("%A")

st.write(f"**Day:** {day_name}")

# ---------------- GET EXISTING RECORD ----------------

response = (
    supabase
    .table("work_records")
    .select("*")
    .eq("work_date", date_string)
    .execute()
)

existing = response.data[0] if response.data else None

if existing:
    current_status = existing["status"]
    current_pieces = existing["pieces"] or 0
else:
    current_status = "Working"
    current_pieces = 0

# ---------------- STATUS ----------------

status = st.radio(
    "Status",
    ["Working", "Holiday"],
    index=0 if current_status == "Working" else 1,
    horizontal=True
)

# ---------------- WORKING ----------------

if status == "Working":

    pieces = st.number_input(
        "Number of Pieces",
        min_value=0,
        value=int(current_pieces),
        step=1
    )

    amount = pieces * RATE

    st.info(f"💰 Amount: ₹{amount:.2f}")

# ---------------- HOLIDAY ----------------

else:

    pieces = 0
    amount = 0

    st.info("🏖️ Holiday — No amount will be counted.")

# ---------------- SAVE ENTRY ----------------

if st.button("💾 Save Entry", use_container_width=True):

    record = {
        "work_date": date_string,
        "status": status,
        "pieces": pieces,
        "rate": RATE,
        "amount": amount
    }

    if existing:

        # Update existing record
        supabase \
            .table("work_records") \
            .update(record) \
            .eq("work_date", date_string) \
            .execute()

        st.success("✅ Entry updated successfully!")

    else:

        # Create new record
        supabase \
            .table("work_records") \
            .insert(record) \
            .execute()

        st.success("✅ Entry saved successfully!")

# ---------------- MONTHLY SUMMARY ----------------

st.divider()

st.subheader("📊 Monthly Summary")

selected_month = st.selectbox(
    "Select Month",
    range(1, 13),
    index=date.today().month - 1,
    format_func=lambda x: calendar.month_name[x]
)

selected_year = st.number_input(
    "Year",
    min_value=2020,
    max_value=2100,
    value=date.today().year
)

month_text = f"{selected_year}-{selected_month:02d}"

# Get all records for selected month
response = (
    supabase
    .table("work_records")
    .select("*")
    .gte("work_date", f"{month_text}-01")
    .lt(
        "work_date",
        f"{selected_year}-{selected_month + 1:02d}-01"
        if selected_month < 12
        else f"{selected_year + 1}-01-01"
    )
    .order("work_date")
    .execute()
)

records = response.data

# ---------------- CALCULATE SUMMARY ----------------

working_days = sum(
    1 for record in records
    if record["status"] == "Working"
)

holidays = sum(
    1 for record in records
    if record["status"] == "Holiday"
)

total_pieces = sum(
    record["pieces"] or 0
    for record in records
)

total_amount = sum(
    float(record["amount"] or 0)
    for record in records
)

# ---------------- SUMMARY DISPLAY ----------------

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "🧵 Total Pieces",
    total_pieces
)

col2.metric(
    "📅 Working Days",
    working_days
)

col3.metric(
    "🏖️ Holidays",
    holidays
)

col4.metric(
    "💰 Total Earnings",
    f"₹{total_amount:.2f}"
)

# ---------------- MONTHLY RECORDS ----------------

st.divider()

st.subheader("📋 Monthly Records")

if records:

    for record in records:

        record_id = record["id"]
        work_date = record["work_date"]
        status = record["status"]
        pieces = record["pieces"] or 0
        rate = float(record["rate"] or RATE)
        amount = float(record["amount"] or 0)

        display_date = date.fromisoformat(work_date)

        with st.expander(
            f"📅 {display_date.strftime('%d-%m-%Y')} — "
            f"{display_date.strftime('%A')}"
        ):

            col1, col2, col3 = st.columns(3)

            col1.write(f"**Status:** {status}")
            col2.write(f"**Pieces:** {pieces}")
            col3.write(f"**Amount:** ₹{amount:.2f}")

else:

    st.info("No records found for this month.")

# ---------------- RATE ----------------

st.divider()

st.caption(
    f"💰 Current rate: ₹{RATE:.2f} per piece"
)