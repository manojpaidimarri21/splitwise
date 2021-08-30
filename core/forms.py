# import form class from django
from django import forms
  
# import GeeksModel from models.py
from .models import Group,Event,settlement
  
# create a ModelForm
class GroupForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Group
        exclude = ['groupAdmin']


# create a ModelForm
class GroupFormAddMember(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Group
        exclude = ['groupAdmin','groupName']

# create a ModelForm
class EventForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = Event
        exclude = ['created_by']

# create a ModelForm
class settlementForm(forms.ModelForm):
    # specify the name of model to use
    class Meta:
        model = settlement
        fields = ['amount']