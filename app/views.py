from django.contrib.auth import get_user_model
from django.contrib.auth.backends import UserModel
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic.base import View
from .forms import SignUpForm
from django.contrib.auth.models import User

UserModel = get_user_model()
from .forms import SignUpForm


class Signup(View):
    def get(self,request):
        return render(request,'signup.html')
    def post(self,request):
        form = SignUpForm(request.POST)
        print(form.errors.as_data())
        if form.is_valid():
            print('1')
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('authenticate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            print(message)
            email.send()
            print(to_email)
            print(email)
            return render(request,'confirm.html')

        else:
            form = SignUpForm()
            return render(request, 'signup.html', {'form': form})


def activate(request,uidb64, token):
    print('hi')
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        print('1')
        user = UserModel._default_manager.get(pk=uid)
        print('2')
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request,'confirm1.html')
    else:
        return HttpResponse('Activation link is invalid!')


class email(View):
    def post(self,request):
        em=request.POST.get('email')
        try:
            User.objects.get(email=em)
            return HttpResponse("Done")
        except:
            return None