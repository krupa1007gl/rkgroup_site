import json
import logging

from django.http import JsonResponse
from django.shortcuts import render

from .models import Lead
from .services import update_lead_status

logger = logging.getLogger(__name__)


def leads_list_view(request):
    leads = Lead.objects.all()
    return render(request, 'main/leads_list.html', {'leads': leads})


def update_lead_status_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    lead_id = data.get('lead_id')
    new_status = data.get('status')

    if not lead_id or new_status not in Lead.Status.values:
        return JsonResponse({'error': 'Missing or invalid parameters'}, status=400)

    try:
        lead = Lead.objects.get(pk=lead_id)
    except Lead.DoesNotExist:
        return JsonResponse({'error': 'Lead not found'}, status=404)

    update_lead_status(lead, new_status, changed_by=request.user)
    return JsonResponse({'success': True, 'status': lead.status})
