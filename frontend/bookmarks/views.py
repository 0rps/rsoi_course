from views_settings import printRequest, sessionWrapper, render

@printRequest
@sessionWrapper
def index(request, session=None):
	return render(request, "base.html", {'logged': session})


