from rest_framework.reverse import reverse


def resolve_profile(request):
    user = request.user
    return {
        "image": user.profile.profile_image.url if user.profile.profile_image else None,
        "endpoint": reverse("wbcore:authentication:userprofile-detail", args=[user.id], request=request),
    }
