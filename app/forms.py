from django import forms
from decimal import Decimal

class LoginForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)	

class SupplierForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)
	confirm_pass = forms.CharField(label='Confirm Password', max_length=100, widget=forms.PasswordInput)
	org_name = forms.CharField(label='Organization name', max_length=100)
	email = forms.EmailField(label='Email')
	phone_number = forms.IntegerField(label='Phone Number')
	address = forms.CharField(label='Location', max_length=300)
	user_type = forms.ChoiceField((('P','Producer'), ('R','Retailer')), label="Account Type")
	business_type = forms.CharField(label='Business Type', max_length=45)

class CustomerForm(forms.Form):
	username = forms.CharField(label='Username', max_length=30)
	password = forms.CharField(label='Password', max_length=100, widget=forms.PasswordInput)
	confirm_pass = forms.CharField(label='Confirm Password', max_length=100, widget=forms.PasswordInput)
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
	serving_size = forms.DecimalField(label="Serving Size", max_digits=2, min_value=Decimal('0.01'))
	cooking_time = forms.DecimalField(label="Cooking Time", max_digits=3, min_value=Decimal('0.01'))
	cuisine_type = forms.CharField(label="Cuisine Type", max_length=20)
	price = forms.DecimalField(label="Price", decimal_places=2, min_value=Decimal('0.01'))
	ingredient_count = forms.CharField(label="Ingredient Count", widget = forms.HiddenInput())
	src = forms.CharField(label="Image Source", max_length=500)

	def __init__(self, *args, **kwargs):
		extra_fields = kwargs.pop('extra', 0)

		# check if extra_fields exist. if they don't exist assign 0 to them
		if not extra_fields:
				extra_fields = 0;
		super(RecipeForm, self).__init__(*args, **kwargs)
		self.fields['ingredient_count'].initial = extra_fields

		for index in range(int(extra_fields)):
			# generate extra fields in the number specified via extra_fields
			self.fields['ingredient_{index}'.format(index=index)] = forms.CharField()
			self.fields['quantity_{index}'.format(index=index)] = forms.IntegerField()

class OrderHistoryForm(forms.Form):
	title = forms.CharField(label = 'Title', max_length=50)
	

