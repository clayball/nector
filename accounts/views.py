from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.template.context_processors import csrf
from forms import MyRegistrationForm

# Docs: https://docs.djangoproject.com/en/1.11/topics/auth/default/

def index(request):
    '''Renders main accounts page.'''
    return render_to_response('accounts.html')


def login(request):
    '''Renders login page.'''
    c = {}

    if request.user.is_authenticated():
        return loggedin(request)

    if 'next' in request.GET:
        c['next'] = request.GET['next']

    c.update(csrf(request))
    return render_to_response('login.html', c)


def auth_view(request):
    '''Authenticates user/password combo.
       Renders new page onsuccess or onfailure.'''

    # Get info to redirect to previous page.
    next_redirect = ''
    if 'next' in request.POST:
        next_redirect = request.POST['next']

    # Get inputted form info.
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')

    # Authenticate user.
    user = auth.authenticate(username=username, password=password)

    if user is not None:
        auth.login(request, user)

        # Handle redirection to previous page
        # once the user signs in.
        if next_redirect:
            return HttpResponseRedirect(next_redirect)

        # No previous page to redirect to.
        else:
            return HttpResponseRedirect('/accounts/loggedin')
    else:
        return HttpResponseRedirect('/accounts/invalid')


def loggedin(request):
    '''Renders loggedin page.'''
    return render_to_response('loggedin.html',
                                {'user':request.user.username})


def invalid_login(request):
    '''Renders invalid login page.'''
    return render_to_response('invalid_login.html')


def logout(request):
    '''Logs the user out.
       Renders logout page.'''
    auth.logout(request)
    return render_to_response('logout.html')


def register_user(request):
    '''Registers user.
       Renders success page on success,
               register page on failure.'''

    # User is submitting form.
    # Read from form and save
    # form data as new user.
    if request.method == "POST":
        form = MyRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/register_success')
    args = {}
    args.update(csrf(request))
    args['form'] = MyRegistrationForm()
    print args
    return render_to_response('register.html', args)


def register_success(request):
    '''Renders register success page.'''
    return render_to_response('register_success.html')
