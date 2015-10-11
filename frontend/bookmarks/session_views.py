__author__ = 'orps'

from views_settings import *

@printRequest
@sessionWrapper
@authorizationRequired
def me(request, session=None):

	query = "{0}/me?userId={1}".format(sessionServer, session['userId'])

	response = requests.get(query)
	profile = {}
	if response.status_code == 200:
		profile = response.json()
	else:
		logerror("bad request to session")
	return render(request, "profile.html", {'logged': session, 'profile': profile})


@printRequest
@sessionWrapper
def login(request, session=None):
	if session is not None:
		return HttpResponseRedirect(frontendServer + "/index")

	if request.method == 'POST':
		form = forms.SigninForm(request.POST)
		if form.is_valid():
			response = requests.post(sessionServer + '/login', form.json())
			if response.status_code == 200:
				answer = response.json()

				id = answer['id']
				token = answer['token']

				result = HttpResponseRedirect(frontendServer + '/index')
				result.set_cookie('id', id)
				result.set_cookie('token', token)

				return result
	else:
		form = forms.SigninForm()
	return render(request, 'login.html', {'form': form, 'logged': session})


@printRequest
@sessionWrapper
def register(request, session=None):
	if session is not None:
		return HttpResponseRedirect(frontendServer + "/index")

	if request.method == 'POST':
		form = forms.RegisterForm(request.POST)
		if form.is_valid():
			response = requests.put(sessionServer + '/register', params=form.json())
			if response.status_code == 200:
				return HttpResponseRedirect(frontendServer + '/login')
			else:
				return render(request, 'registration.html', {'form': form, 'logged': session, 'tryagain': 1})

	else:
		form = forms.RegisterForm()
	return render(request, 'registration.html', {'form': form, 'logged': session})


@printRequest
@sessionWrapper
@authorizationRequired
def logout(request, session=None):

	response = requests.delete(url=sessionServer+"/logout?id={0}&token={1}".format(session['id'], session['token']))
	if response.status_code == 200:
		result = HttpResponseRedirect("{0}/index".format(frontendServer))
		result.delete_cookie('id')
		result.delete_cookie('token')

		return result

	return HttpResponseRedirect("{0}/login".format(frontendServer))