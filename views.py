from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import datetime
from django.contrib.auth.models import User
import json
from .models import SGPTSlot

@csrf_exempt
def sync_booking(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            date_str = data.get('date')
            time_str = data.get('time')

            if not email or not date_str or not time_str:
                return JsonResponse({'error': 'Missing fields'}, status=400)

            user = User.objects.get(email=email)
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            time = datetime.strptime(time_str, "%H:%M").time()

            slot, created = SGPTSlot.objects.get_or_create(
                user=user,
                date=date,
                time=time
            )

            return JsonResponse({'status': 'created' if created else 'exists'}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
