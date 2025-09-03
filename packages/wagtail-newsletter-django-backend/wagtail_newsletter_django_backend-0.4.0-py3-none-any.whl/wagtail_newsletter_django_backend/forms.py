from collections.abc import Collection, Iterable
from typing import cast, override
from django import forms
from . import models

class ManageForm(forms.ModelForm):
    '''
    Form for managing subscriptions.

    This must be constructed with the relevant instance.  If the instance is
    changed after the fact, the segments will not be correct.
    '''
    instance: models.Subscriber
    audience_segments: forms.ModelMultipleChoiceField = forms.ModelMultipleChoiceField(
        label='Categories',
        queryset=None,  # pyright: ignore[reportArgumentType]
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    
    class Meta:
        model: type[models.Subscriber] = models.Subscriber
        fields: Collection[str] = ('email_name', 'audience_segments')
    
    def __init__(self, *args, **kwargs):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
        
        # Filter audience_segments to only show those belonging to this subscriber's audience
        if self.instance:
            cast(
                 forms.ModelMultipleChoiceField,
                 self.fields['audience_segments'],
             ).queryset = models.AudienceSegment.objects.filter(
                audience=self.instance.audience
            )
    
    @override
    def save(self, commit: bool = True) -> models.Subscriber:
        # Save the subscriber instance first
        subscriber = cast(models.Subscriber, super().save(commit=commit))
        
        if commit:
            # Clear existing subscriptions and create new ones based on selected segments
            _ = models.Subscription.objects.filter(subscriber=subscriber).delete()
            
            for segment in cast(Iterable[models.AudienceSegment], self.cleaned_data['audience_segments']):
                _ = models.Subscription.objects.create(
                    subscriber=subscriber,
                    audience_segment=segment
                )
        
        return subscriber

class SignupForm(forms.ModelForm):
    '''
    Form for creating subscriptions.
    '''
    instance: models.Subscriber
    audience: forms.ModelChoiceField = forms.ModelChoiceField(
        queryset=models.Audience.objects.all(),
        widget=forms.HiddenInput(),
    )
    audience_segments: forms.ModelMultipleChoiceField = forms.ModelMultipleChoiceField(
        label='Categories',
        queryset=None,  # pyright: ignore[reportArgumentType]
        widget=forms.CheckboxSelectMultiple(),
        required=False,
    )
    
    class Meta:
        model: type[models.Subscriber] = models.Subscriber
        fields: Collection[str] = ('email_name', 'email_address', 'audience', 'audience_segments')
    
    def __init__(self, *args, audience: models.Audience, **kwargs):  # pyright: ignore[reportUnknownParameterType, reportMissingParameterType]
        super().__init__(*args, **kwargs)  # pyright: ignore[reportUnknownArgumentType]
        # Filter audience_segments to only show those belonging to this subscriber's audience
        cast(
            forms.ModelMultipleChoiceField,
            self.fields['audience_segments'],
        ).queryset = audience.audience_segment_set.all()

    @override
    def save(self, commit: bool = True) -> models.Subscriber:
        # Save the subscriber instance first
        subscriber = cast(models.Subscriber, super().save(commit=commit))
        
        if commit:
            # Clear existing subscriptions and create new ones based on selected segments
            _ = models.Subscription.objects.filter(subscriber=subscriber).delete()
            
            for segment in cast(Iterable[models.AudienceSegment], self.cleaned_data['audience_segments']):
                _ = models.Subscription.objects.create(
                    subscriber=subscriber,
                    audience_segment=segment
                )
        
        return subscriber
