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
    user_type = forms.ChoiceField((('P', 'Producer'), ('R', 'Retailer')), label="Account Type")
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


class ProducerAddDrinkForm(forms.Form):
    name = forms.CharField(label='Drink Name', max_length=100)
    abv = forms.DecimalField(label='ABV', min_value=0)

class BeerForm(ProducerAddDrinkForm):
    type = forms.CharField(label="Beer Type", max_length=100)
    ibu = forms.DecimalField(label="IBU", min_value=0)

class WineForm(ProducerAddDrinkForm):
    type = forms.CharField(label="Wine Type", max_length=100)
    year = forms.DateField(label="Year", input_formats=["%Y", '%y'])

class LiquorForm(ProducerAddDrinkForm):
    type = forms.CharField(label="Liquor Type", max_length=100)
    flavor = forms.CharField(label="Liquor Flavor", max_length=100)

class RetailerAddStockForm(forms.Form):


    def __init__(self, choices, *args, **kwargs):
        super(RetailerAddStockForm, self).__init__(*args, **kwargs)
        self.fields['d_id'] = forms.ChoiceField(label="Drink", choices=choices)
        self.fields['quantity'] = forms.IntegerField(label="Quantity", min_value=0)



class SearchDrinkForm(forms.Form):
    search_string = forms.CharField(label='Search For Drinks', max_length=30)

