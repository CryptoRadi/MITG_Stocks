import streamlit as st
import pandas as pd

# Set Streamlit page configuration
st.set_page_config(page_title="MITG Stocks Dashboard",
                   page_icon=":bar_chart:",
                   layout="centered"
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
        usecols='B, D, E, H, J, S, N, Q'
    )
    return df_int


if uploaded_file:
    df = get_data_from_excel(uploaded_file)

    df = df.rename(columns={'Tot stk un': 'Quantity', 'Num': 'BOX of'})

    # Fill NA/NaN values in 'SLoc' with an empty string or drop them
    df['SLoc'] = df['SLoc'].fillna('')

    df = df[df["SLoc"].str.contains("4000|4006|40A0")]

    # Convert the datetime column to just date (without time)
    df['Expr Date'] = pd.to_datetime(df['Expr Date']).dt.date

    # Create a new column with '%' symbol for display
    df['ShelfLife'] = df['ShelfLife%'].apply(lambda x: f"{x:.2f}%")

    # Sort the DataFrame by the 'shelflife' column in-place
    df.sort_values(by='ShelfLife', inplace=True, ascending=False)

    # Filter rows where 'Quantity' is an integer and not equal to 0
    df = df[(df['Quantity'].astype(int) == df['Quantity'])
            & (df['Quantity'] != 0)]

    df['Quantity'] = df['Quantity'].astype(int)

    # ---- MAINPAGE ----
    st.title(":bar_chart: Stocks Dashboard")

    st.markdown("##")

    st.caption('''
        *Only showing _SLoc_: 4000 | 4006 | 40A0

        *MOH Shelflife invoicing requirement: >= 70%
        ''')

    st.markdown("##")

    if not df.empty:
        cfn = st.selectbox(
            "Filter CFN:",
            options=df['CFN'].unique(),
            index=None,
            placeholder="Select CFN..."
        )

        # st.subheader(f"CFN: {cfn}")

        # Retrieve and display the value from column Q for the selected CFN without decimals
        uom_values = df.loc[df['CFN'] == cfn, 'BOX of'].values
        if len(uom_values) > 0:
            uom_value = int(uom_values[0])
            st.subheader(f"UOM: :orange[{uom_value}]")

            # Define filtered_df before using it in calculations
            filtered_df = df[df['CFN'] == cfn]

            # Calculate and display the total quantity
            total_qty = filtered_df.loc[filtered_df['SLoc']
                                        != '40A0', 'Quantity'].sum().astype(int)
            total_qty_ea = filtered_df.loc[filtered_df['SLoc']
                                           == '40A0', 'Quantity'].sum().astype(int)

            # Total QTY: (BOX * uom_value) + EA
            total_qty_combined = (total_qty * uom_value) + total_qty_ea
            st.subheader(f"Total QTY: :green[{total_qty_combined}] EA")

            st.markdown("""---""")

            # Filter MOH rows where 'ShelfLife%' is greater than or equal to 70%
            filtered_df_moh = df[(df['CFN'] == cfn) & (df['ShelfLife%'] >= 70)]

            # Total Qty ALL
            total_qty_moh = filtered_df_moh.loc[filtered_df_moh['SLoc'] !=
                                                '40A0', 'Quantity'].sum().astype(int)
            total_qty_ea_moh = filtered_df_moh.loc[filtered_df_moh['SLoc']
                                                   == '40A0', 'Quantity'].sum().astype(int)

            cpad1, pad2 = st.columns((20, 15))
            with cpad1:
                st.subheader("Total Quantity:")
                st.subheader(f"Box: {total_qty}")
                st.subheader(f"EA: {total_qty_ea}")

            with pad2:
                st.subheader("Total Quantity (MOH):")
                st.subheader(f"Box: {total_qty_moh}")
                st.subheader(f"EA: {total_qty_ea_moh}")

            st.markdown("""---""")

            TABLE_WIDTH = "100%"

            # Centering the table and adjusting its width with CSS
            st.write(
                f"""
                <style>
                .my-table {{
                    margin: 0 auto;
                    text-align: center;
                    width: {TABLE_WIDTH};
                    color: WhiteSmoke;
                }}
                .my-table th {{
                    text-align: center;
                    color: Peru;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
            st.write(
                pd.DataFrame(filtered_df[['Plant Name', 'SLoc', 'Quantity', 'BOX of', 'Batch', 'ShelfLife', 'Expr Date']]).to_html(
                    classes=["my-table"], index=False),
                unsafe_allow_html=True
            )
        else:
            st.subheader(":green[Select CFN to Start.]")
    else:
        st.write("No data available in the uploaded file.")
