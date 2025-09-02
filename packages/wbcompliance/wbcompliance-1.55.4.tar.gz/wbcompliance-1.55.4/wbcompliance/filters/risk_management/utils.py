def get_default_handler(field, request, view, **kwargs):
    if not request.user.is_superuser and (profile := request.user.profile):
        return profile.id
