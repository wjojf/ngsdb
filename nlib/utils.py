from django.urls import resolve, reverse
from django.db.models import Sum, Avg
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.encoding import smart_str

from orders.models import Ordered, Vendor, Item

def build_tabs_dict(request, tabs):
    match = resolve(request.path)
    tab_dict = {}
    for tab,view in tabs.items():
        try:
            view_name, args, kwargs = view
            is_active = match.url_name == view_name
        except ValueError:
            is_active = match.url_name == view
            kwargs = None
            args = []
            view_name = view
        tab_dict[tab] = [reverse(view_name, args=args, kwargs=kwargs), is_active]
    return tab_dict

def sort_items(vendor, filename=None):
    '''
    Stupid utility funciton to sort items from the given vendor
    according to the number of orders. To be used from the shell.
    Probably need to incorporate it to some view.

    `vendor` - vendor instance for which a list of sorted items needs
    to be generated

    `filename` - output file name. Defaults to vendor_name.txt
    '''

    qs = Item.objects.filter(vendor__name=vendor)
    #print qs
    sorted_qs = sorted(qs, key=lambda x: x.ordered_set.all().count())
    sorted_qs.reverse()
    #print sorted_qs
    if not filename:
        filename = vendor + '.txt'
    handle = open(filename, 'w')
    handle.write('Nudler Lab. Items ordered from %s \n' % vendor)
    #tmpl = u'%s \t %d \t %s \t %s \n'
    tmpl = '%s \t %d \t %s\n'
    for item in sorted_qs:
        s = tmpl % (item.cat_no, item.ordered_set.all().count(), item.name)
        try:
            handle.write(s.encode('utf-8'))
        except:
            handle.write('*****ERROR****\n')
    handle.close()


def get_filters(params):
    '''
    Given a dictionary of lookup parameters (usually from query string),
    builds a dictionary that can be used for ORM lookup,
    `lookup_params` and a dictionary to be used in templates
    to render filters `ctx`
    '''

    lookup_params = {}
    ctx = {}
    for k, v in params.items():
        if k.startswith('page'):
            break
        if k.startswith('q'):
            lookup_params['%s__icontains' % smart_str(k[1:])] = v
            ctx['filter'] = '%s contains' % ' '.join(k[1:].split('__'))
        else:
            lookup_params['%s__exact' % smart_str(k)] = v
            ctx['filter'] = ' '.join(k.split('__'))
        ctx['filter_val'] = params[k]
    return lookup_params, ctx

########################################################################
# Utility views and functions used for migrations, one-off tasks, etc
########################################################################

@login_required
def set_status(request):
    msg = []
    msg_str = 'Status set to %s for %d orders.'
    qs = Ordered.pending.all()
    qs.update(status='P')
    messages.info(request, msg_str % ('PENDING', qs.count()))
    qs = Ordered.objects.filter(delivered='True')
    qs.update(status='D')
    messages.info(request, msg_str % ('DELIVERED', qs.count()))
    qs = Ordered.objects.filter(backordered='True')
    qs.update(status='B')
    messages.info(request, msg_str % ('BACKORDERED', qs.count()))
    qs = Ordered.objects.filter(date_ordered__isnull=False, ref_number__isnull=False, delivered=False)
    qs.update(status='O')
    messages.info(request, msg_str % ('ORDERED', qs.count()))
    return HttpResponseRedirect(reverse('orders_view'))

@login_required
def fix_old(request):
    lookup_params = {'ref_number': None, 'delivered': True }
    bad_qs = Ordered.objects.filter(**lookup_params)
    for order in bad_qs:
        order.ref_number = 'fixed'
        order.save(force_update=True)
    messages.info(request, 'Fixed %d records' % bad_qs.count())
    return HttpResponseRedirect(reverse('orders_view'))

@login_required
def update_schema(request):
    success_count = 0
    for order in Ordered.objects.all():
        if order.date_ordered is not None:
            order.eta_date = order.date_ordered + timedelta(days=3)
            if order.date_ordered < (date.today() - timedelta(days=3)):
                order.delivered = True
            order.save(force_update=True)
            success_count += 1
    messages.info(request, 'Successfully updated %d orders' % success_count)
    return HttpResponseRedirect(reverse('home_view'))

@login_required
def add_total(request):
    success_count = 0
    for order in Ordered.objects.all():
        if not order.is_editable():
            order.save(force_update=True)
            success_count += 1
    messages.info(request, 'Successfully updated %d ordered items.' % success_count)
    return HttpResponseRedirect(reverse('home_view'))
