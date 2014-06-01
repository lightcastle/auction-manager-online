from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login, logout as django_logout
from manager.models.invoice import Invoice
from manager.models.attendee import Attendee
from manager.models.auction_item import AuctionItem
from manager.forms import AuctionItemForm, ItemSearchForm, YearForm
import datetime
from django.core.exceptions import ObjectDoesNotExist
from exceptions import AttributeError
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required
def create(request):
    ''' creates a new auction item for the current year's auction.
    '''
    if request.POST:
        form = AuctionItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.add_message(request, messages.SUCCESS, 'Auction Item created')
            return redirect('item_list')
        else:
            context = {'form': form}
            return render(request, 'auction_item/add.html', context)
    else:
        form = AuctionItemForm()
        context = {'form': form,
                   }
        return render(request, 'auction_item/add.html', context)
    return redirect('item_list')

@login_required
def update(request, id):
    ''' Updates an auction item record
    '''
    item = get_object_or_404(AuctionItem, id=id)

    if request.POST:
        form = AuctionItemForm(request.POST, instance=item)
        if form.is_valid():
            if form.cleaned_data['winning_bid_number']:
                invoice = Invoice.objects.get(attendee=Attendee.objects.get(bid_number=form.cleaned_data['winning_bid_number']))
                invoice.items.add(item)
                form.save()
                messages.add_message(request, messages.SUCCESS, 'Auction Item updated')
            return redirect('item_list')
        else:
            return redirect('item_info', id)
    else:
        form = AuctionItemForm(instance=item)
        context = {'auction_item': item,
                   'form': form,
                   }

    return render(request, 'auction_item/update.html', context)



@login_required
def info(request, id):
    ''' Get item's info
    '''
    item = AuctionItem.objects.get(id=id)
    return render(request, 'auction_item/info.html', {'item': item})


@login_required
def item_search(request):
    """
    Search for Item by item number
    """
    context = {}
    if request.POST:
        form = ItemSearchForm(request.POST)
        if form.is_valid():
            try:
                item = AuctionItem.objects.get(item_number=form.cleaned_data['item_number'])
                context['item'] = item
                context['form'] = form
            except Exception as e:
                context['error'] = e
        else:
            return render(request, 'quction_item/item_search.html', context)
    else:
        form = ItemSearchForm()
        context['form'] = form

    return render(request, 'auction_item/item_search.html', context)



@login_required
def unsold_item_list(request):
    ''' Get a list of all unsold auction items for the current year's auction.
    '''
    items = AuctionItem.objects.filter(year=lambda: datetime.datetime.now().year, winning_bid_number__isnull=True)
    context = {'auction_items': items,
               }
    return render(request, 'auction_item/item_list.html', context)

@login_required
def past_items(request):
    ''' Get a list of all auction items for the a past year's auction.
    '''
    context = {}
    if request.POST:
        form = YearForm(request.POST)
        if form.is_valid():
            items = AuctionItem.objects.filter(year=form.cleaned_data['year'])
            context['auction_items'] = items
            context['year'] = form.cleaned_data['year']
        else:
            context['errors'] = form.errors
            context['form'] = form
        return render(request, 'auction_item/item_list.html', context)
    else:
        form = YearForm()
        context['form'] = form
    return render(request, 'auction_item/item_list.html', context)





@login_required
def list(request):
    ''' Get a list of all auction items for the current year's auction.
    '''
    items = AuctionItem.objects.filter(year=lambda: datetime.datetime.now().year)
    context = {'auction_items': items,
               }
    return render(request, 'auction_item/item_list.html', context)


@login_required
def confirm_delete(request, id):
    return redirect('home')


@login_required
def delete(request, id):
    item = AuctionItem.objects.get(id=id)
    item.delete()
    return redirect('item_list')

