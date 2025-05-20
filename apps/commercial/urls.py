from django.contrib import admin
from django.urls import path, include
from .views import views as po_views
from .views import invoice_views

urlpatterns = [
    path('', po_views.commercial_home, name='commercial-home'),
    path('po-extraction-v2', po_views.po_extraction, name='po_extraction_v2'),
    path('booking', po_views.Booking.as_view(), name='booking'),
    path('start-booking', po_views.StartBooking.as_view(), name='start_booking'),
    path('automation-report', po_views.commercial_automation_report,
         name='commercial-automation-report'),
    path('po-extraction-report', po_views.po_extraction_report,
         name='po-extraction-report'),
    path('booking-report', po_views.booking_report, name='booking-report'),
    path('fcr-report', po_views.fcr_report, name='fcr-report'),
    path('invoice-report', po_views.invoice_report, name='invoice-report'),
    path('exp-issuance-report', po_views.exp_issuance_report,
         name='exp-issuance-report'),


    path('delete-activity-log/<str:request_id>',
         po_views.delete_activity_log, name='delete_activity_logs'),


    path('purchase-orders', po_views.show_po_for_logs, name='purchase_orders'),
    path('activity-log/<str:request_id>',
         po_views.getActivityLog, name='get_activity_logs'),
    path('activity-log-json/<str:request_id>',
         po_views.getActivityLogJson, name='get_activity_log_json'),


    path("po-extraction", po_views.purchase_order, name="po_extraction"),
    path("get-all-purchase-orders/", po_views.get_all_purchase_orders,
         name="get_all_purchase_orders"),

    # Invoice Extractor

    path('invoice-extractor', invoice_views.invoice_extractor,
         name='invoice_extractor'),
    path('show-all-invoice', invoice_views.show_all_invoice,
         name='show_all_invoice'),

    path('start-invoice-bot', invoice_views.start_invoice_bot,
         name='start_invoice_bot'),

     path('get-invoice-activity-logs/<str:request_id>',invoice_views.get_invoice_activity_logs,name='get_invoice_activity_logs')



]
