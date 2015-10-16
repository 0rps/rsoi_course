__author__ = 'orps'

from views_settings import *

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

			response = requests.post(backendBookmarks + '/changebookmark', form.json())
			if response.status_code == 200:
				result = HttpResponseRedirect(frontendServer + '/bookmarks')
				return result
			else:
				return HttpResponseBadRequest()
	else:
		#response = request.get("{0}/bookmark?id={1}")

		form = forms.BookmarkForm

	parameters = {'form': form, 'logged': session, 'action_name': 'Change bookmark', 'title_name': 'Change bookmark'}

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