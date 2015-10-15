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
			response = requests.post(backendBookmarks + '/addbookmark', form.json())
			if response.status_code == 200:
				result = HttpResponseRedirect(frontendServer + '/bookmarks')
				return result
			else:
				return HttpResponseBadRequest()
	else:
		form = forms.BookmarkForm

	return render(request, 'bookmark.html', {'form': form, 'logged': session, 'is_new': True})

@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def changeBookmark(request, session=None):
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
		form = forms.BookmarkForm

	return render(request, 'bookmark.html', {'form': form, 'logged': session, 'is_new': False})


@csrf_exempt
@printRequest
@sessionWrapper
@authorizationRequired
def deleteBookmark(request, session=None):
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

	loginfo("last bookmark")
	query = "{0}/removebookmark?id={1}&user_id={2}".format(backendBookmarks, id, session.user_id)
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
		logerror("page param is None")
		return HttpResponseBadRequest()

	query = "{0}/bookmarks?bookmarks_user_id={1}&user_id={1}&page={2}&per_page={3}"
	query = query.format(backendBookmarks, session['userId'], page, 10)
	loginfo("ololo")
	loginfo(query)
	response = requests.get(query)
	if response.status_code != 200:
		loginfo("status code is {0}".format(response.status_code))
		logerror("request to favorites backend failed")
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