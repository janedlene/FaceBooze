from django import forms
from decimal import Decimal

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)	
class SearchDrinkForm(forms.Form):
	search_string = forms.CharField(label='Search For Drinks', max_length=30)
class ConsumerForm(forms.Form):
	name = forms.CharField(label='Name', max_length=30)
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)
	confirm_password = forms.CharField(label='Confirm Password', max_length=100, widget=forms.PasswordInput)	
	

