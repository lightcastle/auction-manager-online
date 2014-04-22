from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login, logout as django_logout
from manager.models.auction_item import AuctionItem
from manager.models.invoice import Invoice
from manager.models.auction_item import AuctionItem
from manager.forms import InvoiceForm, TableInvoiceDetailForm
import datetime
from django.contrib import messages
from collections import OrderedDict


def create(request):
    ''' creates a new invoice for the current year's auction.
    '''
    if request.POST:
        form = InvoiceForm(request.POST)
        if form.is_valid():
            new_invoice = form.save()
            if form.cleaned_data['items']:
                print form.cleaned_data['items'].id
                item = AuctionItem.objects.get(id=form.cleaned_data['items'].id)
                new_invoice.items.add(item)
                new_invoice.total_amount = item.selling_price
                new_invoice.save()
#                new_invoice.add_item_value(item)
            messages.add_message(request, messages.SUCCESS, 'New Invoice Saved')
            return redirect('invoice_list')
        else:
            context = {'form': form}
#            return redirect('add_item')
            return render(request, 'invoice/add.html', context)
    else:
        form = InvoiceForm()
        context = {'form': form,
                   }
        return render(request, 'invoice/add.html', context)
    return redirect('invoice_list')


def update(request, id):
    ''' Updates an auction item record
    '''
    invoice = get_object_or_404(Invoice, id=id)

    if request.POST:
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            if form.cleaned_data['items']:
                item = AuctionItem.objects.get(id=form.cleaned_data['items'].id)
                invoice.items.add(item)
                messages.add_message(request, messages.SUCCESS, 'Item added to invoice.')
            elif form.cleaned_data['remove_items']:
                item = AuctionItem.objects.get(id=form.cleaned_data['remove_items'].id)
                invoice.items.remove(item)
                messages.add_message(request, messages.SUCCESS, 'Item removed from invoice.')
            invoice.set_total()
            form.save()
            messages.add_message(request, messages.SUCCESS, 'Invoice updated.')
            return redirect('invoice_list')
        else:
            messages.add_message(request, messages.WARNING, 'Something went wrong, likely some kind of form validation.')
            return render(request, 'invoice/update.html', {'form': form})
    else:
        form = InvoiceForm(instance=invoice)
        context = {'invoice': invoice,
                   'form': form,
                   }

    return render(request, 'invoice/update.html', context)



def info(request, id):
    ''' Deletes an invoice
    '''
    invoice = get_object_or_404(Invoice, id=id)
    return render(request, 'invoice/info.html', {'invoice': invoice})


def list(request):
    ''' Get a list of all auction items for the current year's auction.
    '''
    invoices = Invoice.objects.filter(year=lambda: datetime.datetime.now().year)
    context = {'invoices': invoices,
               }
    return render(request, 'invoice/invoice_list.html', context)

def confirm_delete(request, id):
    return redirect('home')


def delete(request, id):
    invoice = get_object_or_404(Invoice, id=id)
    invoice.delete()
    return redirect('invoice_list')


def table_list(request):
    invoices = Invoice.objects.filter(bill_to__isnull=False).order_by('bill_to__table_assignment')
    context = {'invoices': invoices}
    return render(request, 'invoice/invoice_list.html', context)

def table_invoices_detail(request):
    invoices = Invoice.objects.filter(bill_to__isnull=False).order_by('bill_to__table_assignment')
    context = {'invoices': invoices}
    return render(request, 'invoice/table_invoices_detail.html', context)

def table_invoice_detail(request):
    if request.POST:
        form = TableInvoiceDetailForm(request.POST)
        if form.is_valid():
            invoices = Invoice.objects.filter(bill_to__isnull=False).filter(bill_to__table_assignment=form.cleaned_data['table_assignment'])
            context = {'invoices': invoices,
                       'form': form}
    else:
        form = TableInvoiceDetailForm()
#        invoices = Invoice.objects.filter(bill_to__isnull=False).order_by('bill_to__table_assignment')
#        invoices = Invoice.objects.filter(bill_to__table_assignment=id)
        context = {'form': form}
    return render(request, 'invoice/table_invoice_detail.html', context)
