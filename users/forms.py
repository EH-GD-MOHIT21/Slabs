from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
User = get_user_model()

class SignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=20,required=True)
    last_name = forms.CharField(max_length=20,required=True)
    username = forms.CharField(max_length=20,required=True)
    email = forms.EmailField(required=True)
    profile_image = forms.ImageField()
    country = forms.CharField(max_length=50,required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username',
                  'email', 'profile_image', 'country')

    def signup(self, request):
        user = super(SignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.country = self.cleaned_data['country']
        user.profile_image = self.cleaned_data['profile_image']
        user.save()
        return user