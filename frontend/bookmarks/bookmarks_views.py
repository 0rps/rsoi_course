__author__ = 'orps'

from django.views.decorators.http import require_http_methods

from views_settings import *

from myutils import *

@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def add_bookmark(request, session=None):
	if request.method == 'POST':
		form = forms.BookmarkForm(request.POST)
		if form.is_valid():

			query = "{0}/me?userId={1}".format(sessionServer, session['userId'])
			response = requests.get(query)

			profile = {}
			if response.status_code == 200:
				profile = response.json()
			else:
				logerror("bad request to session")
				return HttpResponseBadRequest()

			parameters = form.json()
			parameters['user_id'] = session['userId']
			parameters['username'] = "{0} {1}".format(profile['name'], profile['last_name'])

			response = requests.post(backendBookmarks + '/addbookmark', parameters)
			if response.status_code == 200:
				result = HttpResponseRedirect(frontendServer + '/bookmarks')
				return result
			else:
				return HttpResponseBadRequest()
	else:
		form = forms.BookmarkForm

	parameters = {'form': form, 'logged': session, 'action_name': 'Create bookmark', 'title_name': 'Bookmark creation'}

	return render(request, 'bookmark_handle_form.html', parameters)

@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def change_bookmark(request, session=None):
	if request.method == 'POST':
		form = forms.BookmarkForm(request.POST)
		if form.is_valid():
			parameters = form.full_json()
			parameters['user_id'] = session['userId']
			response = requests.post(backendBookmarks + '/changebookmark', parameters)
			if response.status_code == 200:
				result = HttpResponseRedirect(frontendServer + '/bookmarks')
				return result
			else:
				return HttpResponseBadRequest()
	else:
		bid = request.GET.get('id')
		if bid is None:
			logerror('id is none')
			return HttpResponseBadRequest()

		response = requests.get("{0}/bookmark?bookmark_id={1}".format(backendBookmarks, bid))
		if response.status_code != 200:
			logerror("wrong query to bookback")
			return HttpResponseBadRequest()

		response = response.json()

		if int(response['user_id']) != int(session['userId']):
			logerror('Forbidden')
			return HttpResponseForbidden()

		data = {'title': response['title'],
				'description': response['description'],
				'is_public': bool(response['is_public']),
				'bookmark_id': int(bid)}
		form = forms.BookmarkForm(initial=data)
		form.fields['title'].widget.attrs['readonly'] = True

	parameters = {'form': form, 'logged': session, 'action_name': 'Save bookmark', 'title_name': 'Change bookmark'}

	return render(request, 'bookmark_handle_form.html', parameters)


@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def remove_bookmark(request, session=None):
	if request.method != 'POST':
		logerror("is not POST method")
		return HttpResponseForbidden()

	param = request.POST

	curUrl = param.get('pageurl')
	id = param.get('id')

	loginfo("params: id = {0} currentPageUrl = {1}".format(id, curUrl))

	if id is None:
		logerror("some of parameters is None")
		return HttpResponseBadRequest()

	query = "{0}/removebookmark?bookmark_id={1}&user_id={2}".format(backendBookmarks, id, session['userId'])
	response = requests.delete(query)
	if response.status_code != 200:
		logerror("request to backend bookmarks failed")
		return HttpResponseServerError()

	if curUrl:
		loginfo("redirect to curPageUrl")
		return HttpResponseRedirect(curUrl)

	url = "{0}/bookmarks?page={1}".format(frontendServer, 1)
	loginfo('redirect to 1 page')
	return HttpResponseRedirect(url)


@require_http_methods(['GET'])
@printRequest
@sessionWrapper
@authorizationRequired
def get_bookmark(request, session=None):
	get = request.GET

	bookmark_id = get.get('bookmark_id')
	if bookmark_id is None:
		return HttpResponseBadRequest()

	query = "{0}/bookmark?bookmark_id={1}".format(backendBookmarks, bookmark_id)
	responce = requests.get(query)
	if responce.status_code != 200:
		logerror("There is no bookmark")
		return HttpResponseBadRequest()

	responce = responce.json()
	if responce['user_id'] != session['userId'] and bool(responce['is_public'] is False):
		logerror("there is no access to private bookmark of other user")
		return HttpResponseForbidden()

	parameters = {'logged': session, 'bookmark': responce}
	return render(request, 'bookmark.html', parameters)

@require_http_methods(['GET'])
@printRequest
@sessionWrapper
@authorizationRequired
def get_user_bookmarks(request, session=None):
	get = request.GET

	page = get.get('page')
	user_id = get.get('user_id')

	if page is None:
		page = 1

	if int(user_id) == int(session['userId']):
		query = "{0}/bookmarks?page={1}".format(frontendServer, page)
		return HttpResponseRedirect(query)

	query = "{0}/bookmarks?bookmarks_user_id={1}&user_id={2}&page={3}&per_page={4}"
	query = query.format(backendBookmarks, user_id, session['userId'], page, 5)
	loginfo(query)
	response = requests.get(query)
	if response.status_code != 200:
		loginfo("status code is {0}".format(response.status_code))
		logerror("request to bookmarks backend failed")
		return HttpResponseServerError()

	response = response.json()

	page = int(response['cur_page'])
	total = int(response['pages'])

	if page > 1:
		loginfo("there is prev page")
		prev_page = {'num': page-1, 'url': "{0}/userbookmarks?page={1}&user_id={2}".format(frontendServer, page-1, user_id)}
	else:
		loginfo("there is no prev page")
		prev_page = None

	if page < total:
		loginfo("there is next page")
		next_page = {'num': page+1, 'url': "{0}/userbookmarks?page={1}&user_id={2}".format(frontendServer, page+1, user_id)}
	else:
		loginfo("there is no next page")
		next_page = None

	page_number = page
	profile = get_profile(user_id)

	bookmarks = response['objects']

	return render(request, "user_bookmarks.html", {'logged': session,
												  'profile': profile,
											  'bookmarks': bookmarks,
											  'pageNumber': page_number,
											  'prevPage': prev_page,
											  'nextPage': next_page})


@printRequest
@sessionWrapper
@authorizationRequired
def search_bookmarks(request, session=None):
	get = request.GET

	text = get.get('search_text')
	page = get.get('page')
	if page is None:
		page = 1

	parms = {'search_text': text, 'page':page, 'per_page':5}

	query = "{0}/search".format(backendBookmarks)
	response = requests.get(query, params=parms)
	if response.status_code != 200:
		logerror("error in query to backbook")
		return HttpResponseBadRequest()

	response = response.json()

	page = int(response['cur_page'])
	total = int(response['pages'])

	if page > 1:
		loginfo("there is prev page")
		prev_page = {'num': page-1, 'url': "{0}/search?search_text={1}&page={1}".format(frontendServer, text, page-1)}
	else:
		loginfo("there is no prev page")
		prev_page = None

	if page < total:
		loginfo("there is next page")
		next_page = {'num': page-1, 'url': "{0}/search?search_text={1}&page={1}".format(frontendServer, text, page+1)}
	else:
		loginfo("there is no next page")
		next_page = None

	page_number = page

	profiles = {}
	bookmarks = response['objects']
	for book in bookmarks:
		user_id = book['user_id']
		if user_id not in profiles:
			profiles[user_id] = get_profile(user_id)
		book['profile'] = profiles[user_id]

	return render(request, "search.html", {'logged': session,
												   'text': text,
											  'bookmarks': bookmarks,
											  'pageNumber': page_number,
											  'prevPage': prev_page,
											  'nextPage': next_page})


@printRequest
@sessionWrapper
@authorizationRequired
def get_my_bookmarks(request, session=None):

	if request.method != 'GET':
		return HttpResponseForbidden()

	page = request.GET.get('page')

	if page is None:
		page = 1

	query = "{0}/bookmarks?bookmarks_user_id={1}&user_id={1}&page={2}&per_page={3}"
	query = query.format(backendBookmarks, session['userId'], page, 5)
	loginfo(query)
	response = requests.get(query)
	if response.status_code != 200:
		loginfo("status code is {0}".format(response.status_code))
		logerror("request to bookmarks backend failed")
		return HttpResponseServerError()

	response = response.json()

	page = int(response['cur_page'])
	total = int(response['pages'])

	if page > 1:
		loginfo("there is prev page")
		prev_page = {'num': page-1, 'url': "{0}/bookmarks?page={1}".format(frontendServer, page-1)}
	else:
		loginfo("there is no prev page")
		prev_page = None

	if page < total:
		loginfo("there is next page")
		next_page = {'num': page+1, 'url': "{0}/bookmarks?page={1}".format(frontendServer, page+1)}
	else:
		loginfo("there is no next page")
		next_page = None

	page_number = page

	bookmarks = response['objects']

	cur_url = "{0}/bookmarks?page={1}".format(frontendServer, page_number)

	return render(request, "bookmarks.html", {'logged': session,
											  'curPageUrl': cur_url,
											  'bookmarks': bookmarks,
											  'pageNumber': page_number,
											  'prevPage': prev_page,
											  'nextPage': next_page})