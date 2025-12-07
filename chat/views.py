"""Chat views for Gemini AI integration."""

import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from chat.services import generate_chat_response


def chat_home(request):
    """Render the chat interface."""
    return render(request, 'chat_interface.html')


@require_POST
@csrf_exempt
def chat_api(request):
    """Handle chat API requests."""
    try:
        data = json.loads(request.body)
        user_prompt = data.get('prompt', '')
        chat_history = data.get('history', [])
        
        if not user_prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)

        ai_response = generate_chat_response(user_prompt, chat_history)

        return JsonResponse({'response': ai_response, 'role': 'model'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"Gemini error: {e}")
        return JsonResponse({'error': f'An AI service error occurred: {str(e)}'}, status=500)
