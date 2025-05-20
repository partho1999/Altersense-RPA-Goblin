from typing import Any
from django.db import models
from apps.utils.base_model import BaseModel
from django.conf import settings
from services.booking_bot.booking_config import settings as booking_settings
import uuid
from apps.commercial.schema import ServiceStatus


class PurchaseOrder(BaseModel):
    po_no = models.CharField(blank=True, default='', max_length=255, null=True)
    order_no = models.CharField(
        blank=True, default='', max_length=25, null=True)
    item = models.CharField(blank=True, default='', max_length=25, null=True)
    description = models.CharField(
        blank=True, default='', max_length=25, null=True)
    gender = models.CharField(blank=True, default='', max_length=25, null=True)
    country_iso = models.CharField(
        blank=True, default='', max_length=25, null=True)
    country_name = models.CharField(
        blank=True, default='', max_length=25, null=True)
    country_code = models.CharField(
        blank=True, default='', max_length=25, null=True)
    no_of_pcs_per_pack = models.CharField(
        blank=True, default='', max_length=25, null=True)
    quantity_in_pack = models.CharField(
        blank=True, default='', max_length=25, null=True)
    quantity_in_pcs = models.CharField(
        blank=True, default='', max_length=25, null=True)
    quantity = models.CharField(
        blank=True, default='', max_length=25, null=True)
    invoice_average_price = models.CharField(
        blank=True, default='', max_length=25, null=True)
    currency_iso = models.CharField(
        blank=True, default='', max_length=25, null=True)
    currency_name = models.CharField(
        blank=True, default='', max_length=25, null=True)
    currency_code = models.CharField(
        blank=True, default='', max_length=25, null=True)
    value = models.CharField(blank=True, default='', max_length=25, null=True)
    delivery_time = models.CharField(
        blank=True, default='', max_length=25, null=True)
    s_c_no = models.CharField(blank=True, default='', max_length=25, null=True)
    lc_no = models.CharField(blank=True, default='', max_length=25, null=True)
    bin = models.CharField(blank=True, default='', max_length=25, null=True)
    ad_code = models.CharField(
        blank=True, default='', max_length=25, null=True)
    commodity_code = models.CharField(
        blank=True, default='', max_length=25, null=True)
    incoterm = models.CharField(
        blank=True, default='', max_length=25, null=True)
    unit_code = models.CharField(
        blank=True, default='', max_length=25, null=True)
    unit = models.CharField(blank=True, default='', max_length=25, null=True)
    area_code = models.CharField(
        blank=True, default='', max_length=25, null=True)
    invoice_no = models.CharField(
        blank=True, default='', max_length=25, null=True)
    invoice_date = models.CharField(
        blank=True, default='', max_length=25, null=True)
    invoice_amount = models.CharField(
        blank=True, default='', max_length=25, null=True)
    cmt_amount = models.CharField(
        blank=True, default='', max_length=25, null=True)
    freight = models.CharField(
        blank=True, default='', max_length=25, null=True)
    insurance = models.CharField(
        blank=True, default='', max_length=25, null=True)
    other_charges = models.CharField(
        blank=True, default='', max_length=25, null=True)
    carrier_vessel = models.CharField(
        blank=True, default='', max_length=25, null=True)
    dest_port = models.CharField(blank=True, max_length=255)
    trans_doc_type = models.CharField(
        blank=True, default='', max_length=25, null=True)
    trans_doc_no = models.CharField(
        blank=True, default='', max_length=25, null=True)
    trans_doc_date = models.CharField(
        blank=True, default='', max_length=25, null=True)
    ship_port = models.CharField(
        blank=True, default='', max_length=25, null=True)
    sector = models.CharField(blank=True, default='', max_length=25, null=True)
    fob_amount = models.CharField(
        blank=True, default='', max_length=25, null=True)
    signatory_id = models.CharField(
        blank=True, default='', max_length=25, null=True)
    remarks = models.CharField(
        blank=True, default='', max_length=25, null=True)
    bank_ref_no = models.CharField(
        blank=True, default='', max_length=25, null=True)
    exp_serial = models.CharField(
        blank=True, default='', max_length=25, null=True)
    exp_year = models.CharField(
        blank=True, default='', max_length=25, null=True)
    full_exp = models.CharField(
        blank=True, default='', max_length=25, null=True)
    issue_date = models.CharField(
        blank=True, default='', max_length=25, null=True)
    exp_status = models.CharField(
        blank=True, default='', max_length=25, null=True)
    booking_status = models.CharField(
        blank=True, default='', max_length=25, null=True)
    request_id = models.CharField(
        max_length=255, blank=True, null=True, default=None)

    def __str__(self):
        return f"PO No={self.po_no} - Order No={self.order_no} - Item={self.item} - Country iso={self.country_iso}"


class PurchaseFile(BaseModel):
    file = models.FileField(upload_to='purchase_data/')


class InvoiceFile(BaseModel):
    file = models.FileField(upload_to='invoice_data/')


class ActivityLog(BaseModel):
    bot = models.CharField(max_length=255, blank=True, null=True, default=None)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True)
    activity = models.TextField(blank=True, null=True, default=None)
    activity_type = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    activity_time = models.DateTimeField(auto_now_add=True)
    request_id = models.CharField(
        max_length=255, blank=True, null=True, default=None)

    draft = models.TextField(blank=True, null=True, default=None)

    def __str__(self):
        return f"ID={self.id} - Request ID={self.request_id} - Activity={self.activity} - Activity Type={self.activity_type}"


class PurchaseOrderBooking(BaseModel):
    request_id = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE,)
    summary_marks = models.CharField(
        max_length=255, blank=True, null=True, default='')
    summary_desc = models.CharField(
        max_length=255, blank=True, null=True, default='')
    no_of_pcs_in_pack = models.CharField(
        max_length=25, blank=True, null=True, default='')
    status = models.CharField(
        max_length=255, blank=True, null=True, default=ServiceStatus.PENDING.value)


class BookingCredentials(BaseModel):
    username = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    password = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    status = models.CharField(
        max_length=255, blank=True, null=True, default=None)

    def __str__(self) -> str:
        return self.username


class BookingConfig(BaseModel):
    settings = models.JSONField(blank=True, null=True, default=dict)

    @classmethod
    def add_initial_data(cls):
        if cls.objects.count() == 0:
            cls.objects.create(settings=booking_settings)
            print('Initial data added to BookingConfig')
        return cls.objects.first()


# invoice_no
# invoice_date
# exporters_ref
# hs_code
# description
# composition
# quantity
# po_no
# country_iso
# fcr_status
# request_id

class Invoice(BaseModel):
    invoice_no = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    invoice_date = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    exporters_ref = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    hs_code = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    description = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    composition = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    quantity = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    po_no = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    country_iso = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    fcr_status = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    request_id = models.CharField(
        max_length=255, blank=True, null=True, default=None)
    status = models.CharField(
        max_length=255, blank=True, null=True, default=ServiceStatus.PENDING.value)

    def __str__(self) -> str:
        return f"Invoice No={self.invoice_no} - Invoice Date={self.invoice_date} - Quantity={self.quantity} - PO No={self.po_no} - Country ISO={self.country_iso} - FCR Status={self.fcr_status} - Request ID={self.request_id}"
