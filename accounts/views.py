from django.shortcuts import render,redirect
from . forms import signup_form,signin_form
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout

# Create your views here.
def signup(request):


        if request.method == "POST":

            form = signup_form(request.POST,request.FILES)

            if form.is_valid():

                user = User.objects.create_user(username=form.cleaned_data[ "username" ],password=form.cleaned_data["password"],email=form.cleaned_data["email"])
                profile = form.save(
                     commit=False
                )

                profile.user = user

                profile.save()

        else:

            form = signup_form()
            print(form.errors)

        return render(request,"authentication/signup.html", {"form":form})


def signin(request):

    if request.method == "POST":
         form=signin_form(request.POST)
         if form.is_valid():
              username=form.cleaned_data["username"]
              password=form.cleaned_data["password"]

              user = authenticate(request,username=username,password=password)
              if user is not None:
                   login(request,user)
                   return redirect("dashboard")

              else:
                   redirect("signin")
                   print(form.errors)
    else:
         form=signin_form()

    return render(request,"authentication/signin.html",{"form":form})

def dashboard(request):
     
     return render(request,"user/dashboard.html")


         