

import uuid
from ..forms.forms import InvoiceForm
from django.shortcuts import render, redirect
import os
from services.invoice_extractor_bot.main_app.main_functions import extract_pdf_data
from django.http import JsonResponse
from apps.commercial.models import InvoiceFile, Invoice
from services.purchase_order import clear_dir
from project_settings.settings import BASE_DIR
from services.fcr_bot.run_fcr import main as run_fcr_main
from apps.commercial.models import ActivityLog
import json
from apps.commercial.schema import ServiceStatus, ActivityLogSchema
from apps.commercial.services import create_bot_activity_log, update_invoice_status_by_id

# def invoice_extractor(request):
#     if request.method == 'GET':
#         pdf_dir = './media/pdfs'
#         all_invoice_data = extract_pdf_data(pdf_dir)
#         print('#'*50)
#         print(all_invoice_data)
#         print('#'*50)
#         return JsonResponse({'data': all_invoice_data})


def invoice_extractor(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                dir_path = os.path.join(BASE_DIR, 'media/invoice_data')
                clear_dir.main(dir_path)
                # print(p1.returncode)
                files = request.FILES.getlist('file')
                # print("files--->", files)

                for a_file in files:
                    purchase_file = InvoiceFile(file=a_file)
                    purchase_file.save()

                    # messages.success(request, 'Purchase Orders uploaded successfully!')
            except Exception as e:
                print(f'Error executing subprocess: {e}')
            try:

                invoice_files_path = os.path.join(BASE_DIR, 'media/invoice_data')
                all_invoice_data = extract_pdf_data(invoice_files_path)
                # Invoice.objects.bulk_create(all_invoice_data)
                for invoice in all_invoice_data:
                    Invoice.objects.create(**invoice)

                # return JsonResponse({'data': all_invoice_data})
                return redirect('show_all_invoice')
            except Exception as e:
                print(f'Error executing purchase order {str(e)}')
                return JsonResponse({'Error': f'Error executing purchase order,Error message : {str(e)}'})

    else:

        form = InvoiceForm()

    return render(request, 'core/purchase_order.html', {'form': form, 'title': 'Extract Invoice Data'})


def show_all_invoice(request):
    invoices = Invoice.objects.all()
    return render(request, 'commercial/show_all_invoice.html', {'invoices': invoices})


def start_invoice_bot(request):
    if request.method == 'POST':
        json_data = json.loads(request.body)
        invoice_id = json_data.get('invoice_id')
        print("#"*50)
        print("invoice_id: ", invoice_id)
        print("json_data>>>>>", json_data)
        print("#"*50)
        invoice = Invoice.objects.get(id=invoice_id)
        if not invoice:
            return JsonResponse({'message': 'Invoice not found!'})
        username = os.environ.get('BOOKING_SERVICE_USERNAME')
        password = os.environ.get('BOOKING_SERVICE_PASSWORD')

        # configs = get_booking_config()
        # print('**********Configs***********: ')
        # print(configs)
        # fcr_data = configs['fcr']
        # fcr_template = fcr_data['header_tab']['fcr_template']
        # additional_desc =  fcr_data['marks&numbers_tab']['modified_description']
        # delivery_party = fcr_data['parties_tab']['delivery_party']
        # print("fcr_data: ", fcr_data)
        # print("fcr_template: ", fcr_template)
        # print("additional_desc: ", additional_desc)
        # print("delivery_party: ", delivery_party)
        # print('**********Configs***********: ')

        # try:
        create_bot_activity_log(ActivityLogSchema(
            activity_type='FCR', activity='Invoice bot started', request_id=invoice.request_id))

        update_invoice_status_by_id(invoice_id, ServiceStatus.RUNING.value)

        run_fcr_main(invoice, invoice.request_id, username, password)

        update_invoice_status_by_id(invoice_id, ServiceStatus.COMPLETED.value)

        return JsonResponse({'message': 'Invoice bot started successfully!'})

        # except Exception as e:

        #     update_invoice_status_by_id(invoice_id, ServiceStatus.REJECTED.value)

        #     print(f'Error Invoice Starting : {e}')

        #     create_bot_activity_log(ActivityLogSchema(
        #         activity_type='FCR', activity=f'Error creating activity log: {e}', request_id=invoice.request_id))

        #     return JsonResponse({'message': 'Error starting invoice bot!, Error message: ' + str(e)})

    return JsonResponse({'message': 'Invalid request!'})


def get_invoice_activity_logs(request, request_id):
    activity_logs = ActivityLog.objects.filter(request_id=request_id)
    return render(request, 'commercial/invoice_activity_logs.html', {'activity_logs': activity_logs})
