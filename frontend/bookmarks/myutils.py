__author__ = 'orps'

from views_settings import *

def get_profile(user_id):
	loginfo("profile request: " + str(user_id))
	query = "{0}/me?userId={1}".format(sessionServer, user_id)
	response = requests.get(query)
	profile = {}
	if response.status_code == 200:
		profile = response.json()
		profile['full_name'] = "{0} {1}".format(profile['name'], profile['last_name'])
		return profile
	else:
		logerror("bad request to session")
		return None