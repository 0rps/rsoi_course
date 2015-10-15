__author__ = 'orps'
from django import forms
from django.utils.safestring import mark_safe

import json

class RegisterForm(forms.Form):
	name = forms.CharField(label=mark_safe('<br>Your name<br>'), max_length=32)
	last_name = forms.CharField(label=mark_safe('<br>Your surname<br>'), max_length=32)
	email = forms.EmailField(label=mark_safe('<br>Email<br>'))
	password = forms.CharField(label=mark_safe('<br>Password<br>'), max_length=32)

	def json(self):
		data = self.cleaned_data
		result = {
			'email': data['email'],
			'password': data['password'],
			'last_name': data['last_name'],
			'name': data['name']
		}

		return result


class BookmarkForm(forms.Form):
	title = forms.CharField(label=mark_safe('<br>Bookmark title<br>'),max_length=None)
	description = forms.CharField(label=mark_safe('<br>Your description<br>'), max_length=None)
	is_public = forms.BooleanField(label=mark_safe('<br>Is public<br>'))
	#password = forms.CharField(label=mark_safe('<br>Password<br>'), max_length=32)

	def json(self):
		data = self.cleaned_data
		#	result = {
		#		'email': data['email'],
		#		'password': data['password'],
		#		'last_name': data['last_name'],
		#	'name': data['name']
		#}

		return None


class SigninForm(forms.Form):
	email = forms.EmailField(label=mark_safe('<br>Your email<br>'))
	password = forms.CharField(label=mark_safe('<br>Your password<br>'), max_length=32)

	def json(self):
		data = self.cleaned_data
		result = {"email": data['email'], 'password': data['password']}

		return result