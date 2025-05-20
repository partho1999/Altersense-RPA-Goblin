from apps.commercial.models import (
    ActivityLog,
    PurchaseOrder,
    BookingConfig,
    PurchaseOrderBooking,
    Invoice
)
from apps.commercial.schema import (
    ActivityLogSchema,
    ServiceStatus
)
import json


def create_bot_activity_log(data: ActivityLogSchema):
    return ActivityLog.objects.create(**data.dict())


def update_po_status_by_id(po_id, status):
    po = PurchaseOrder.objects.get(id=po_id)
    po.booking_status = status
    po.save()
    return po

def update_invoice_status_by_id(invoice_id, status):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.status = status
    invoice.save()
    return invoice


def save_po_data(po_data, request_id):
    purchase_order_obj = PurchaseOrder(
        **po_data,
        request_id=request_id
    )
    purchase_order_obj.save()

def get_booking_config():
    settings = BookingConfig.objects.first().settings
    return settings


def get_all_purchase_orders_data():
    po_data = PurchaseOrder.objects.all().prefetch_related('purchaseorderbooking_set')
    data = []
    for po in po_data:
        po_dict = {
            'id': po.id,
            'po_no': po.po_no,
            'order_no': po.order_no,
            'item': po.item,
            'gender': po.gender,
            'country_iso': po.country_iso,
            'delivery_time': po.delivery_time,
            'purchaseorderbooking': [
                {
                    'id': po_booking.id,
                    'summary_marks': po_booking.summary_marks,
                    'summary_desc': po_booking.summary_desc,
                    'no_of_pcs_in_pack': po_booking.no_of_pcs_in_pack,
                    'status': po_booking.status,
                    'request_id': po_booking.request_id,
                }
                for po_booking in po.purchaseorderbooking_set.all()
            ]
        }
        po_dict['purchaseorderbooking'] = po_dict['purchaseorderbooking'][0] if po_dict['purchaseorderbooking'] else {}
        data.append(po_dict)
    return data


def get_purchase_orders_data_by_status(status: str = None):
    if status:
        po_data = PurchaseOrder.objects.filter(
            purchaseorderbooking__status=status).prefetch_related('purchaseorderbooking_set')
    else:
        po_data = PurchaseOrder.objects.all().prefetch_related('purchaseorderbooking_set')

    data = []
    for po in po_data:
        po_dict = {
            'id': po.id,
            'po_no': po.po_no,
            'order_no': po.order_no,
            'item': po.item,
            'gender': po.gender,
            'country_iso': po.country_iso,
            'delivery_time': po.delivery_time,
            'request_id': po.request_id,
            'purchaseorderbooking': [
                {
                    'id': po_booking.id,
                    'summary_marks': po_booking.summary_marks,
                    'summary_desc': po_booking.summary_desc,
                    'no_of_pcs_in_pack': po_booking.no_of_pcs_in_pack,
                    'status': po_booking.status,
                    'request_id': po_booking.request_id,
                }
                for po_booking in po.purchaseorderbooking_set.all()
            ]
        }
        po_dict['purchaseorderbooking'] = po_dict['purchaseorderbooking'][0] if po_dict['purchaseorderbooking'] else {}
        data.append(po_dict)
    return data


def updatePurchaseOrderBookingStatus(id, status):
    po_booking = PurchaseOrderBooking.objects.get(id=id)
    po_booking.status = status
    po_booking.save()
    return po_booking
