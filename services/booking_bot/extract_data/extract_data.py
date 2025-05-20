import pandas as pd
import os


# Check path validity
def check_path(root_dir):
    if os.path.exists(root_dir):
        # print(f"The path '{root_dir}' exists.")
        return True
    else:
        print(f"The path '{root_dir}' does not exist.")
        exit()


def get_data():
    # excel_path = input('Enter excel path: ')
    # check_path(excel_path)
    po_no = input("Purchase Order No: ")
    country_name = input("Enter Country Name: ")
    df = pd.read_excel(
        r'C:\Users\Salman\Desktop\mails\Exp_Issue_Template.xlsx'
    )
    # C:\Users\Salman\Documents\Altersense\RPA\Projects\h&m booking bot\extract_data\data.xlsx

    try:
        # Filter the DataFrame based on the conditions
        filtered_row = df[
            (df["PO NO"] == po_no) & (df["COUNTRY NAME"] == country_name.upper())
        ]

        # Check if any rows meet the conditions
        if not filtered_row.empty:
            # Extract 'ORDER NO' and 'COUNTRY ISO' values from the filtered row
            order_number = filtered_row["ORDER NO"].iloc[
                0
            ]  # Assuming there's only one row
            item = filtered_row["ITEM"].iloc[0]
            gender = filtered_row["GENDER"].iloc[0]
            country_iso = filtered_row["COUNTRY ISO"].iloc[0]
            delivery_time = (
                filtered_row["DELIVERY TIME"].dt.strftime("%Y-%m-%d").iloc[0]
            )
        else:
            print("No matching row found.")

        data = {
            "ORDER NO": order_number,
            "ITEM": item,
            "GENDER": gender,
            "COUNTRY ISO": country_iso,
            "DELIVERY DATE": delivery_time,
            "SUMMARY DESCRIPTION": f'100% BCI COTTON KNITTED\nORDER # {po_no}\nINV # 22 DATE:-09-2022\nCONT.NO:INCTL/H&M/021/2021\nDATE : 14-06-2021\nEXP.NO: 1471-0-2022\nDATE :-08-2022',
        }
        return data

    except KeyError as e:
        print("Error:", "- One or more columns are missing in the DataFrame.")
    except IndexError:
        print("No matching row found.")
    # except Exception as e:
    #     print("An unexpected error occurred:")
