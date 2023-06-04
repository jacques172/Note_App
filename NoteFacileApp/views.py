
from django.http import JsonResponse
from rest_framework.response import Response #import restframework
from rest_framework.decorators import api_view # import decorators

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


from .serializers import UserSerializer
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password # for hashing the password
from rest_framework import status #for defining HTTP status codes.

from django.http import HttpResponse # add

from django.contrib.sites.shortcuts import get_current_site 
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode   
from django.utils.encoding import force_bytes, force_str  
from django.core.mail import send_mail
from django.conf import settings
from .tokens import account_activation_token 
from django.shortcuts import render, redirect
from .models import Note

@api_view(['GET','POST']) # add the get method
def SignupView(request):
    if request.method == 'POST': #add
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=make_password(serializer.validated_data['password'])
            )
            user.is_active = False  
            user.save()
        
            # Send activation email to user
            current_site = get_current_site(request)
            mail_subject = "L'activation a été envoyée à votre adresse email."
            message = render_to_string('acc_active_email.html'
                                       , {  
                    'user': user,  
                    'domain': current_site.domain,  
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),  
                    'token':account_activation_token.make_token(user),  
                }
                )
            recipient_list = [user.email]
            send_mail(mail_subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
            return render(request, 'signup_success.html')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else: #add the else statement
        return render(request, 'signup.html')

# activate user account
def activate(request, uidb64, token):  
    try:  
        uid = force_str(urlsafe_base64_decode(uidb64))  
        user = User.objects.get(pk=uid)  
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):  
        user = None
    if user is not None and account_activation_token.check_token(user, token):  
        user.is_active = True
        user.save()  
        return render(request, 'activation.html')
    else:  
        return HttpResponse('Lien d\'activation invalide!')
        

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        # ...

        return token


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


# View to handle user login
class LoginView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        # Use serializer_class attribute to get the serializer class
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        return redirect('home')
        # return redirect('home')
    
    def get(self, request, *args, **kwargs):
        # Render the login form
        return render(request, 'login.html')
        # return render(request, 'login.html')

def home(request):
    user = request.user

    if request.method == 'POST':
        content = request.POST.get('content')
        color = request.POST.get('formColorPicker')

        if content and color:
            note = Note(user=user, content=content, color=color)
            note.save()

    notes = Note.objects.filter(user=user)
    return render(request, 'home.html', {'notes': notes})



    
@api_view(['GET']) # add the get decorator
def getRoutes(request):
    routes = [
        'token',
        'token/refresh',
    ]

    return Response(routes) # change jsonresponse to response