from django.http import HttpResponseRedirect

def redir(request):
    return HttpResponseRedirect('autologbackend/')
