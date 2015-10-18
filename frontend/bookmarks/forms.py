__author__ = 'orps'
from django import forms
from django.utils.safestring import mark_safe

import json

class RegisterForm(forms.Form):
	name = forms.CharField(label=mark_safe('<br>Your name<br>'), max_length=32)
	last_name = forms.CharField(label=mark_safe('<br>Your surname<br>'), max_length=32)
	email = forms.EmailField(label=mark_safe('<br>Email<br>'))
	password = forms.CharField(label=mark_safe('<br>Password<br>'), max_length=32, widget=forms.PasswordInput)

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
	title = forms.CharField(label=mark_safe('<br>Bookmark title<br>'), max_length=None)
	description = forms.CharField(label=mark_safe('<br>Your description<br>'), max_length=None, widget=forms.Textarea)
	is_public = forms.BooleanField(label=mark_safe('<br>Is public<br>'), required=False)
	bookmark_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

	def json(self):
		data = self.cleaned_data

		result = {'title': data['title'],
				  'description': data['description'],
				  'is_public': data['is_public'] }


		return result

	def full_json(self):
		result = self.json()
		data = self.cleaned_data
		result['bookmark_id'] = data['bookmark_id']

		return result

class SigninForm(forms.Form):
	email = forms.EmailField(label=mark_safe('<br>Your email<br>'))
	password = forms.CharField(label=mark_safe('<br>Your password<br>'), max_length=32, widget=forms.PasswordInput)

	def json(self):
		data = self.cleaned_data
		result = {"email": data['email'], 'password': data['password']}

		return result