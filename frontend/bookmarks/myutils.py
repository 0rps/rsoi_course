__author__ = 'orps'

from views_settings import *


def is_subscribed(subscriber_id, owner_id):
	loginfo("is subscribed request")
	query = "{0}/issubscribed".format(backendNews)
	params = {'owner': owner_id, 'subscriber': subscriber_id}
	response = requests.get(query, params=params)
	if response.status_code == 200:
		return bool(response.json()['subscribed'])
	logerror("issubscribed request is failed")
	return False


def get_profile(user_id):
	loginfo("profile request: " + str(user_id))
	query = "{0}/me?userId={1}".format(sessionServer, user_id)
	response = requests.get(query)
	profile = {}
	if response.status_code == 200:
		profile = response.json()
		profile['full_name'] = "{0} {1}".format(profile['name'], profile['last_name'])
		profile['user_id'] = int(user_id)
		return profile
	else:
		logerror("bad request to session")
		return None

def remove_bookmark_from_news(bookmark_id):
	data = {'bookmark_id': bookmark_id}
	query = "{0}/remove".format(backendNews)
	response = requests.delete(query, params=data)
	return response.status_code == 200

def add_bookmark_to_news(params):
	data = {}
	data['user_id'] = params['user_id']
	data['bookmark_id'] = params['id']
	data['title'] = params['title']

	query = "{0}/add".format(backendNews)
	response = requests.post(query, data)
	return response.status_code == 200



