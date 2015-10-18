__author__ = 'orps'

from views_settings import *
from myutils import *


@printRequest
@sessionWrapper
@authorizationRequired
def get_news(request, session=None):
	user_id = int(session['userId'])
	page = request.GET.get('page')
	if page is None:
		page = 1

	query = "{0}/news".format(backendNews)
	data = {}
	data['user_id'] = user_id
	data['per_page'] = 5
	data['page'] = page
	response = requests.get(query, params=data)
	if response.status_code != 200:
		logerror("news error")
		return HttpResponseServerError()

	response = response.json()

	page = int(response['page'])
	total = int(response['count'])

	if page > 1:
		loginfo("there is prev page")
		prev_page = {'num': page-1, 'url': "{0}/news?page={1}".format(frontendServer, page-1)}
	else:
		loginfo("there is no prev page")
		prev_page = None

	if page < total:
		loginfo("there is next page")
		next_page = {'num': page+1, 'url': "{0}/news?page={1}".format(frontendServer, page+1)}
	else:
		loginfo("there is no next page")
		next_page = None

	profiles = {}
	bookmarks = response['objects']
	for book in bookmarks:
		user_id = book['owner_id']
		if user_id not in profiles:
			profiles[user_id] = get_profile(user_id)
		book['profile'] = profiles[user_id]

	return render(request, "newsline.html", {'logged': session,
											  'bookmarks': bookmarks,
											  'pageNumber': page,
											  'prevPage': prev_page,
											  'nextPage': next_page})

	return render()


@printRequest
@sessionWrapper
@authorizationRequired
def subscribe(request, session=None):
	owner_id = request.GET.get('user_id')
	user_id = session['userId']

	if False == is_subscribed(user_id, owner_id):
		params = {'owner': owner_id, 'subscriber': user_id}
		query = "{0}/subscribe".format(backendNews)
		response = requests.get(query, params=params)
		if response.status_code == 200:
			return HttpResponseRedirect("{0}/user?user_id={1}".format(frontendServer, owner_id))
		else:
			return HttpResponseBadRequest()

	return HttpResponseRedirect("{0}/user?user_id={1}".format(frontendServer, owner_id))


@printRequest
@sessionWrapper
@authorizationRequired
def unsubscribe(request, session=None):
	owner_id = request.GET.get('user_id')
	user_id = session['userId']

	if is_subscribed(user_id, owner_id):
		params = {'owner': owner_id, 'subscriber': user_id}
		query = "{0}/unsubscribe".format(backendNews)
		response = requests.get(query, params=params)
		if response.status_code == 200:
			return HttpResponseRedirect("{0}/user?user_id={1}".format(frontendServer, owner_id))
		else:
			return HttpResponseBadRequest()

	return HttpResponseRedirect("{0}/user?user_id={1}".format(frontendServer, owner_id))



@printRequest
@sessionWrapper
@authorizationRequired
def get_news_owners(request, session=None):
	user_id = int(session['userId'])
	query = "{0}/newsownerslist?user_id={1}".format(backendNews, user_id)
	responce = requests.get(query)
	if responce.status_code != 200:
		logerror("query to news backend failed")
		return HttpResponseServerError()

	users = responce.json()
	data = [get_profile(x) for x in users]

	return render(request, "subscribe_line.html", {'logged': session, 'profiles': data})

