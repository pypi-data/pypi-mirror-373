from viggocore.common.subsystem import operation


class Create(operation.Create):

    def pre(self, session, **kwargs):
        validar_user = kwargs.get('validar_user', False)
        if validar_user is True:
            self.manager.valida_user(**kwargs)
        return super().pre(session, **kwargs)
