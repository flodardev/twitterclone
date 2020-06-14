'''
from django import forms
from django.conf import settings

from .models import Tweet
MAX_TWEET_LENGTH = settings.MAX_TWEET_LENGTH

class TweetForm(forms.ModelForm):
    # Could create a new model
    # content = forms.CharField()
    class Meta:
        # Using the default value of the Tweet Model
        model = Tweet
        fields = ['content']

    def clean_content(self):
        content = self.cleaned_data.get("content")
        # print(content)
        if len(content) > MAX_TWEET_LENGTH:
            raise forms.ValidationError("Tweet is too long")
        return content
