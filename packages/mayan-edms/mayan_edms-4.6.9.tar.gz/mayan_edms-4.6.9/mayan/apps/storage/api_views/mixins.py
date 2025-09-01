class OwnerPlusFilteredQuerysetAPIViewMixin:
    def filter_queryset(self, queryset):
        user = self.request.user

        if user.is_authenticated:
            queryset_user_owned = queryset.filter(user=self.request.user)
        else:
            queryset_user_owned = queryset.none()

        queryset = super().filter_queryset(queryset=queryset)

        queryset = queryset_user_owned | queryset

        return queryset.distinct()
