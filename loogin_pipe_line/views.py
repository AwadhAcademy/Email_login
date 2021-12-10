from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from email_loogin import settings
from django.core.mail import EmailMessage, send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import authenticate, login, logout
from . tokens import generate_token

from django.contrib.auth import authenticate, login, logout
# Create your views here.
def home(request):
    return render(request,'loogin_pipe_line/home.html')
# Create your views here.
def signup(request):
    #collecting Data From froent end html form

    if request.method =="POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        # Checkng Some credentials for new form for overwite protection 
        
        if pass1 !=pass2:
            message_data=f"{username} pasword does not match"
            messages.error(request, message_data)
            return redirect('signup')
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email Already Registered!!")
            return redirect('signup')
        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Please try some other username.")
            return redirect('signup')
        # after all credentials creating non Active User 
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()
        messages.success(request, "Your Account has been created succesfully!! Please check your email to confirm your email address in order to activate your account.")
        
        # Welcome Message for Email
        
        subject = "Welcome to Python- Django Login!!"
        message = "Hello " + myuser.first_name + "!! \n" + "Welcome to coreblaze!! \nThank you for visiting our website\n. We have also sent you a confirmation email, please confirm your email address. \n\nThanking You\nAyush Gupta"        
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        # Email Address Confirmation Email
        current_site = get_current_site(request)
        email_subject = "Confirm your Email @ coreblaze - Django Login!!"
        message2 = render_to_string('email_confirmation.html',{
            
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
        email_subject,
        message2,
        settings.EMAIL_HOST_USER,
        [myuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('home')


    return render(request,'loogin_pipe_line/signup.html')
# Create your views here.
def activate(request,uidb64,token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError,ValueError,OverflowError,User.DoesNotExist):
        myuser = None

    if myuser is not None and generate_token.check_token(myuser,token):
        myuser.is_active = True
        # user.profile.signup_confirmation = True
        myuser.save()
        login(request,myuser)
        messages.success(request, "Your Account has been activated!!")
        return redirect('signin')
    else:
        return render(request,'activation_failed.html')

def signin(request):
    if request.method== 'POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass1')
        user=authenticate(username=username, password=pass1)
        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request,'loogin_pipe_line/home.html',{'Fname':fname})
        else:
            message_data=f"{username} invalid credanciles"
            messages.error(request,message_data)
            return redirect("signin")
    return render(request,'loogin_pipe_line/signin.html')


def signout(request):
    logout(request)
    messages.success(request, "signout Successfully!!")
    return redirect('home')