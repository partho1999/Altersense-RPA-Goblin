from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from ..forms.forms import PurchaseForm
import os
from django.shortcuts import render
from apps.commercial.models import PurchaseFile
from project_settings.settings import BASE_DIR
from services.purchase_order import clear_dir
from services.purchase_order.purchase_order import po
from apps.commercial.models import (
    PurchaseOrder,
    ActivityLog,
    PurchaseOrderBooking
)
import uuid
from services.booking_bot.booking_run import main as booking_run
# import View
from django.views import View
from django.shortcuts import redirect
import json
from apps.commercial.services import (
    get_all_purchase_orders_data,
    updatePurchaseOrderBookingStatus,
    get_purchase_orders_data_by_status,
    get_booking_config
)
from datetime import datetime
from apps.commercial.schema import (ServiceStatus)
from django.forms.models import model_to_dict


# Create your views here.
def commercial_home(request):
    return render(request, 'commercial/commercial_home.html')


def po_extraction(request):
    return render(request, 'commercial/po_extraction.html')


class Booking(View):
    def get(self, request):
        data = get_all_purchase_orders_data()

        # print("#" * 50)
        # print("data--->", data)
        # print("#" * 50)

        json_data = []
        for po in data:
            full_p = po.get('purchaseorderbooking', {'status': None})
            po_status = full_p.get('status', None)
            # print("#" * 50)
            # print("po_status--->", po_status)
            # print("#" * 50)

            if po_status == 'pending':
                json_data.append(po)

            if po_status == 'rejected':
                json_data.append(po)

            if po_status is None:
                json_data.append(po)

        # print("#" * 50)
        # print("json_data--->", json_data)
        # print("#" * 50)

        return render(request, 'commercial/booking.html', {'json_data': json.dumps(json_data)})

    def post(self, request):
        try:
            data = json.loads(request.body)
            # print("#" * 50)
            # print("Booking post---data->", data)
            # print("#" * 50)
            response_data = []
            for key in data:
                # print("key--->", key)
                # print("value--->", data[key])
                # create PurchaseOrderBooking
                purchase_order_booking_obj = PurchaseOrderBooking.objects.filter(
                    purchase_order__id=key)

                # print("#" * 50)
                # print("purchase_order_booking_obj--->",
                #       purchase_order_booking_obj)
                # print("#" * 50)

                if purchase_order_booking_obj.exists():
                    purchase_order_booking_obj.update(
                        summary_marks=data[key]['summary_marks'] if 'summary_marks' in data[key] else '',
                        summary_desc=data[key]['summary_desc'] if 'summary_desc' in data[key] else '',
                        no_of_pcs_in_pack=data[key]['no_of_pcs_in_pack'] if 'no_of_pcs_in_pack' in data[key] else '',
                        status=ServiceStatus.PENDING.value
                    )
                    response_data.append(purchase_order_booking_obj.first())

                else:
                    purchase_order_obj = PurchaseOrder.objects.get(id=key)
                    purchaseOrderBooking_obj = PurchaseOrderBooking(
                        purchase_order_id=key,
                        summary_marks=data[key]['summary_marks'] if 'summary_marks' in data[key] else '',
                        summary_desc=data[key]['summary_desc'] if 'summary_desc' in data[key] else '',
                        no_of_pcs_in_pack=data[key]['no_of_pcs_in_pack'] if 'no_of_pcs_in_pack' in data[key] else '',
                        status=ServiceStatus.PENDING.value,
                        request_id=purchase_order_obj.request_id
                    )

                    purchaseOrderBooking_obj.save()

            json_data = data = get_all_purchase_orders_data()
            json_data = json.dumps(json_data)
            return JsonResponse({'status': 'success', 'message': 'Booking run completed successfully!', 'data': data, 'response_data': json_data})
        except Exception as e:
            print(f'Error executing booking run: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error executing booking run!', 'error': str(e)})


def po_booking(request):
    return render(request, 'commercial/booking.html')


class StartBooking(View):

    def get(self, request):

        purchaseOrderBookings = PurchaseOrderBooking.objects.filter(
            status=ServiceStatus.RUNING.value).values('id', 'request_id')
        purchaseOrderBookings = [{
            'id': po_booking['id'],
            'request_id': po_booking['request_id']
        } for po_booking in purchaseOrderBookings]

        # return JsonResponse({'status': 'success', 'message': 'Purchase Order Bookings fetched successfully!', 'data': purchaseOrderBookings})

        return render(request, 'commercial/running_services_activity_logs.html', {'purchaseOrderBookings': purchaseOrderBookings})

    def post(self, request):
        try:
            po_data = get_purchase_orders_data_by_status(
                ServiceStatus.PENDING.value)

            # print("#" * 50)
            # print("po_data--->", po_data)
            # print("#" * 50)

            for po in po_data:
                print("#" * 50)
                print(f'po--->', po)
                print("#" * 50)

                # po_rows = po.items()
                # for index, po in po_rows:
                #     print("#" * 50)
                #     print(f'po--->', po)
                #     print("#" * 50)

                username = os.environ.get('BOOKING_SERVICE_USERNAME')
                password = os.environ.get('BOOKING_SERVICE_PASSWORD')
                request_id = po['purchaseorderbooking']['request_id']

                updatePurchaseOrderBookingStatus(
                    po['purchaseorderbooking']['id'],
                    ServiceStatus.RUNING.value
                )
                print("#" * 50)
                print("Starting booking run for PO: ", po['po_no'])
                print("#" * 50)
                start_time = datetime.now()

                booking_run(po, request_id, username, password)

                updatePurchaseOrderBookingStatus(
                    po['purchaseorderbooking']['id'],
                    ServiceStatus.COMPLETED.value
                )
                print("#" * 50)
                print("Booking run completed for PO: ", po['po_no'])
                print("#" * 50)
                end_time = datetime.now()
                print("#" * 50)

                print(f"Time taken for booking run: {end_time - start_time}")

            return JsonResponse({'status': 'success', 'message': 'Booking run completed successfully!'})

        except Exception as e:
            updatePurchaseOrderBookingStatus(
                po['purchaseorderbooking']['id'],
                ServiceStatus.REJECTED.value
            )
            print(f'Error executing booking run: {e}')
            return JsonResponse({'status': 'error', 'message': 'Error executing booking run!', 'error': str(e)})


def commercial_automation_report(request):
    return render(request, 'commercial/commercial_automation_report.html')


def po_extraction_report(request):
    po_data = PurchaseOrder.objects.all()
    json_data = serializers.serialize('json', po_data)
    # print("po_data--->", serializers.serialize('json', po_data))
    return render(request, 'commercial/po_extraction_report.html', {'po_data': po_data, 'json_data': json_data})
    # return render(request, 'commercial/po_extraction_report.html')


def booking_report(request):
    return render(request, 'commercial/booking_report.html')


def fcr_report(request):
    return render(request, 'commercial/fcr_report.html')


def invoice_report(request):
    return render(request, 'commercial/invoice_report.html')


def exp_issuance_report(request):
    return render(request, 'commercial/exp_issuance_report.html')


def get_all_purchase_orders(request):
    purchase_orders = PurchaseOrder.objects.all()
    # print(purchase_orders)
    return JsonResponse({'status': 'success', 'message': 'Purchase Orders fetched successfully!', 'data': serializers.serialize('json', purchase_orders)})


def purchase_order(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                dir_path = os.path.join(BASE_DIR, 'media/purchase_data')
                clear_dir.main(dir_path)
                # print(p1.returncode)
                files = request.FILES.getlist('file')
                # print("files--->",files)

                for a_file in files:
                    purchase_file = PurchaseFile(file=a_file)
                    purchase_file.save()

                    # messages.success(request, 'Purchase Orders uploaded successfully!')
            except Exception as e:
                print(f'Error executing subprocess: {e}')
            try:
                request_id = uuid.uuid4().hex

                purchase_order_data = po(request_id)

                # print("purchase_order_data--->", purchase_order_data)
                # print("purchase_order_data--->", purchase_order_data)

                # purchase_order_obj = PurchaseOrder.objects.bulk_create(
                #     [PurchaseOrder(
                #         **po_data,
                #         request_id=request_id
                #     ) for po_data in purchase_order_data])

                # for po_data in purchase_order_data:
                #     purchase_order_obj = PurchaseOrder(
                #         **po_data,
                #         request_id=request_id
                #     )
                #     purchase_order_obj.save()

                # print("purchase_order_obj--->", purchase_order_obj)

                return redirect('booking')

            except Exception as e:
                print(f'Error executing purchase order {e}')

    else:

        form = PurchaseForm()

    return render(request, 'core/purchase_order.html', {'form': form, 'title': 'Extract Purchase Order Data'})


def getActivityLog(request, request_id, *args, **kwargs):
    print("request_id--->", request_id)
    activity_logs = ActivityLog.objects.filter(request_id=request_id)
    activity_logs = serializers.serialize('json', activity_logs)
    purchase_order_booking_obj = PurchaseOrderBooking.objects.filter(
        request_id=request_id)
    purchase_order_booking_obj = serializers.serialize(
        'json', purchase_order_booking_obj)

    return render(request, 'commercial/services_activity_logs.html', {'activity_logs': activity_logs, 'purchase_order_booking': purchase_order_booking_obj, 'request_id': request_id})


def getActivityLogJson(request, request_id, *args, **kwargs):
    print("request_id--->", request_id)
    activity_logs = ActivityLog.objects.filter(request_id=request_id)
    activity_logs = serializers.serialize('json', activity_logs)
    purchase_order_booking_obj = PurchaseOrderBooking.objects.filter(
        request_id=request_id)
    purchase_order_booking_obj = serializers.serialize(
        'json', purchase_order_booking_obj)

    return JsonResponse({'status': 'success', 'message': 'Activity Logs fetched successfully!', 'activity_logs': activity_logs, 'purchase_order_booking': purchase_order_booking_obj, 'request_id': request_id})


def show_po_for_logs(request, *args, **kwargs):
    po_data = get_purchase_orders_data_by_status()
    po_data = json.dumps(po_data)
    return render(request, 'commercial/show_po_for_logs.html', {'po_data': po_data})


def delete_activity_log(request, request_id, *args, **kwargs):
    print("request_id--->", request_id)
    activity_logs = ActivityLog.objects.filter(request_id=request_id)
    activity_logs.delete()
    return JsonResponse({'status': 'success', 'message': 'Activity Logs deleted successfully!'})
