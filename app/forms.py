from django import forms

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)	

class SupplierForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)
	org_name = forms.CharField(label='Organization name', max_length=100)
	email = forms.EmailField(label='Email')
	phone_number = forms.IntegerField(label='Phone Number')
	website = forms.CharField(label='Website', max_length=100)
	street = forms.CharField(label='Street', max_length=50)
	city = forms.CharField(label='City', max_length=50)
	state = forms.CharField(label='State', max_length=2)
	zip_code = forms.IntegerField(label='Zip Code')

class CustomerForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)
	first_name = forms.CharField(label='First Name', max_length=50)
	last_name = forms.CharField(label='Last Name', max_length=100)
	email = forms.EmailField(label='Email')
	phone_number = forms.IntegerField(label='Phone Number')
	street = forms.CharField(label='Street', max_length=50)
	city = forms.CharField(label='City', max_length=50)
	state = forms.CharField(label='State', max_length=2)
	zip_code = forms.IntegerField(label='Zip Code')


class ReviewForm(forms.Form):
    title = forms.CharField(label='Title', max_length=200)
        body = forms.CharField(label='Body', max_length=65000)
        rating = forms.IntegerField(label='Rating')

class RecipeForm(forms.Form):
	title = forms.CharField(label='Title', max_length=50)
	directions = forms.CharField(label="Directions", max_length=65000)
	serving_size = forms.DecimalField(label="Serving Size", max_digits=2)
	cooking_time = forms.DecimalField(label="Cooking Time", max_digits=3)
	cuisine_type = forms.CharField(label="Cuisine Type", max_length=20)
	price = forms.DecimalField(label="Price", max_digits=3, decimal_places=2)

