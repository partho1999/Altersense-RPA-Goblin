import re
from datetime import datetime
import os

# import purchase_order


def get_datetime(filename):
    pattern = r"_(\d{8}_\d{6})"
    date_format = "%Y%m%d_%H%M%S"
    match = re.search(pattern, filename)

    if match:
        timestamp = match.group(1)
        datetime_object = datetime.strptime(timestamp, date_format)
        return [timestamp, datetime_object]
    else:
        return "Timestamp not found in the filename."


def main(pdf_list):
    # pdf_list = os.listdir('E:/AlterSense/RPA Docs/INCTL/H&M/Docs of hm')
    # pdf_list = purchase_order.pdf_list
    purchase_order_list = []
    country_breakdown_list = []

    po_dict_list = []
    cb_dict_list = []

    for file in pdf_list:
        if "PurchaseOrder" in file:
            purchase_order_list.append(file)
        if "TotalCountryBreakdown" in file:
            country_breakdown_list.append(file)

    for purchase_order in purchase_order_list:
        po_no = purchase_order.split("_")[0]
        unique_id = get_datetime(purchase_order)[0]
        datetime_object = get_datetime(purchase_order)[1]
        file_name = purchase_order
        po_dict_list.append(
            {
                "po_no": po_no,
                "unique_id": unique_id,
                "file_name": file_name,
                "date_time": datetime_object,
            }
        )

    for country_breakdown in country_breakdown_list:
        po_no = country_breakdown.split("_")[0]
        unique_id = get_datetime(country_breakdown)[0]
        datetime_object = get_datetime(country_breakdown)[1]
        file_name = country_breakdown
        cb_dict_list.append(
            {
                "po_no": po_no,
                "unique_id": unique_id,
                "file_name": file_name,
                "date_time": datetime_object,
            }
        )

    # print(po_dict_list)

    # Group dictionaries by po_no
    po_groups = {}
    for d in po_dict_list:
        po_no = d["po_no"]
        if po_no not in po_groups:
            po_groups[po_no] = []
        po_groups[po_no].append(d)

    # Select the latest datetime for each po_no
    final_result = []
    valid_po_list = []
    for po_no, dicts in po_groups.items():
        latest_dict = max(dicts, key=lambda x: x["date_time"])
        valid_po_list.append(latest_dict["file_name"])
        final_result.append(latest_dict)

    # Print the final result
    # for d in final_result:
    #     print(d)

    # print(valid_po_list)

    # Group dictionaries by country breakdown
    cb_groups = {}
    for d in cb_dict_list:
        po_no = d["po_no"]
        if po_no not in cb_groups:
            cb_groups[po_no] = []
        cb_groups[po_no].append(d)

    # Select the latest datetime for each po_no
    final_result = []
    valid_cb_list = []
    for po_no, dicts in cb_groups.items():
        latest_dict = max(dicts, key=lambda x: x["date_time"])
        valid_cb_list.append(latest_dict["file_name"])
        final_result.append(latest_dict)

    # Print the final result
    # for d in final_result:
    #     print(d)

    return [valid_po_list, valid_cb_list]


# pdf_list = os.listdir('E:/AlterSense/RPA Docs/INCTL/H&M/Docs of hm')
# main(pdf_list)
