"""Module providing a function printing python version."""
import streamlit as st
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(page_title="Sales Dashboard",
                   page_icon=":bar_chart:",
                   layout="wide"
                   )

# Allow the user to upload an XLSX file
uploaded_file = st.file_uploader('Choose a XLSX file', type='xlsx')

# Function to read data from the uploaded Excel file
CACHE_KEY = "data_" + str(uploaded_file)


@st.cache_data(ttl=3600)
def get_data_from_excel(file):
    """Reads data from excel file and return DataFrame """
    df_int = pd.read_excel(
        file,
        engine='openpyxl',
        sheet_name='Sheet1',
        usecols='D, E, J, S'
    )
    return df_int


if uploaded_file:
    df = get_data_from_excel(uploaded_file)

    df = df.rename(columns={'Tot stk un': 'Quantity'})

    df = df[df["SLoc"].str.contains(
        "4000|4006|40A0"
    )]

    # Filter rows where 'ShelfLife%' is greater than or equal to '0' & 'X'
    # df = df[(df['ShelfLife%'] == 0) | (df['ShelfLife%'] > 60)]

    # Format the 'ShelfLife%' column values as percentages with two decimal places
    df['ShelfLife%'] = df['ShelfLife%'].apply(lambda x: f"{x * 1:.2f}%")

    # Sort the DataFrame by the 'SLoc' column in-place
    df.sort_values(by='ShelfLife%', inplace=True, ascending=False)

    # Filter rows where 'Quantity' is an integer and not equal to 0
    df = df[(df['Quantity'].astype(int) == df['Quantity'])
            & (df['Quantity'] != 0)]

    # ---- MAINPAGE ----
    st.title(":bar_chart: Stocks Dashboard")

    st.markdown("##")

    st.caption(
        ':red[Only showing _SLoc_]:  :green[4000 | 4006 | 40A0]')

    st.markdown("##")

    cfn = st.selectbox(
        "Filter CFN:",
        options=df['CFN'].unique(),
        index=None,
        placeholder="Select CFN..."
    )

    filtered_df = df[df['CFN'] == cfn]

    total_qty = filtered_df.loc[df['SLoc'] !=
                                '40A0', 'Quantity'].sum().astype(int)
    total_qty_ea = filtered_df.loc[df['SLoc']
                                   == '40A0', 'Quantity'].sum().astype(int)

    cpad1, col, pad2 = st.columns((10, 10, 10))
    with cpad1:
        st.subheader("Total Quantity:")
        st.subheader(f"Box: {total_qty}")
        st.subheader(f"EA: {total_qty_ea}")

    st.markdown("""---""")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )
