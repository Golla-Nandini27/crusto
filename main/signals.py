from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added
from .models import Profile


@receiver(social_account_added)
def save_profile_picture(request, sociallogin, **kwargs):

    user = sociallogin.user

    picture = sociallogin.account.extra_data.get("picture")

    profile, created = Profile.objects.get_or_create(user=user)

    profile.image = picture

    profile.save()