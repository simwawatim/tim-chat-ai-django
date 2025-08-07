from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .serializers import GeminiPromptSerializer
from .gemini_client import ask_gemini
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def register(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if not username or not email or not password:
        return Response({'error': 'Username, Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already taken'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password, email=email)
    return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)



@api_view(['POST'])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=user.username, password=password)
    if user is not None:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'message': 'Login successful', 'token': token.key})
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_details(request):
    user = request.user
    return Response({
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    })


@api_view(['POST'])
def gemini_chat(request):
    serializer = GeminiPromptSerializer(data=request.data)
    if serializer.is_valid():
        prompt = serializer.validated_data['prompt']

        history = request.session.get('chat_history', [])

        # Add user's message to history
        history.append({"role": "user", "text": prompt})

        result = ask_gemini(prompt)
        history.append({"role": "bot", "text": result})
        request.session['chat_history'] = history
        request.session.modified = True

        return Response({
            'response': result,
            'history': history,
        }, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def chat_history(request):

    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    if request.method == 'GET':
        return Response({'history': request.session['chat_history']}, status=status.HTTP_200_OK)

    if request.method == 'POST':
        new_history = request.data.get('history')
        if not isinstance(new_history, list):
            return Response({'error': 'Invalid history format'}, status=status.HTTP_400_BAD_REQUEST)

        # Update session history
        request.session['chat_history'] = new_history
        request.session.modified = True

        return Response({'message': 'Chat history updated'}, status=status.HTTP_200_OK)
