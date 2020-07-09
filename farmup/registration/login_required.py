def is_loggedin(request):
    try:
        if request.session['email'] is not None:
            return True
    except:
        return False