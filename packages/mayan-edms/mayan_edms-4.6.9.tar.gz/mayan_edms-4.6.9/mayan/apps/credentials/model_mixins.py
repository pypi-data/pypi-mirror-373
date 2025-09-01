from .events import event_credential_used


class StoredCredentialBusinessLogicMixin:
    def get_backend_data(self):
        obj = super().get_backend_data()

        if self.backend_path:
            backend_class = self.get_backend_class()

            if hasattr(backend_class, 'post_processing'):
                obj = backend_class.post_processing(obj=obj)

        if not getattr(self, '_event_ignore_credential_used', False):
            actor = getattr(self, '_event_actor', None)

            if actor or self.pk:
                event_credential_used.commit(actor=actor, target=self)

        return obj
