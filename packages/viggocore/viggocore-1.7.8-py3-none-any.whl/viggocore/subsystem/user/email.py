import enum
import os
from sparkpost import SparkPost
from viggocore.common import exception


_HTML_EMAIL_USER_CREATED_TEMPLATE = """
    <div style="width: 100%; text-align: center">
        <h1>{app_name}</h1>
        <h2>CONFIRMAR E CRIAR SENHA</h2>
    </div>

    <p>Você acaba de ser cadastrado no portal da {app_name}.</p>
    <p><strong>Domínio:</strong> {domain_name}</p>
    <p><strong>Usuário:</strong> {username}</p>
    <p>Para ter acesso ao sistema você deve clicar no link abaixo
        para confirmar esse email e criar uma senha.</p>

    <div style="width: 100%; text-align: center">
        <a href="{reset_url}">Clique aqui para CONFIRMAR o
            email e CRIAR uma senha.</a>
    </div>
"""

_HTML_EMAIL_FORGOT_PASSWORD_TEMPLATE = """
    <div style="width: 100%; text-align: center">
        <h1>{app_name}</h1>
        <h2>Recuperar SENHA</h2>
    </div>

    # <p>Você acaba de ser cadastrado no portal da {app_name}.</p>
    # <p>Para ter acesso ao sistema você deve clicar no link abaixo
    #     para confirmar esse email e criar uma senha.</p>

    <div style="width: 100%; text-align: center">
        <a href="{reset_url}">Clique aqui para RECUPERAR a senha.</a>
    </div>
"""

_HTML_EMAIL_FORGOT_PASSWORD_ALTERNATIVE_TEMPLATE = '''
    <div style="width: 100%; text-align: center">
        <h1>{app_name}</h1>
        <h2>NOVAS CREDENCIAIS DE ACESSO</h2>
    </div>

    <p>Você solicitou a restauração de senha, então foi gerada uma nova senha aleatória no sistema e aqui está ela.</p>

    <p><strong>Senha:</strong> {password}</p>
'''  # noqa 501

_HTML_EMAIL_ACTIVATE_ACCOUNT_TEMPLATE = """
    <div style="width: 100%; text-align: center">
        <h1>{app_name}</h1>
        <h2>Ativar Conta</h2>
    </div>

    <p>Você acaba de ser cadastrado no portal da {app_name}.</p>
    <p><strong>Domínio:</strong> {domain_name}</p>
    <p><strong>Usuário:</strong> {username}</p>
    <p>Para ter acesso ao sistema você deve clicar no link abaixo
        para o cadastro.</p>

    <div style="width: 100%; text-align: center">
        <a href="{activate_url}">Clique aqui para ATIVAR a conta.</a>
    </div>
"""


class TypeEmail(enum.Enum):
    USER_CREATED = {'id': 1,
                    'template': _HTML_EMAIL_USER_CREATED_TEMPLATE,
                    'action': 'new'}
    FORGOT_PASSWORD = {'id': 2,
                       'template': _HTML_EMAIL_FORGOT_PASSWORD_TEMPLATE,
                       'action': 'recovery'}
    UPDATED_PASSWORD = {'id': 3, 'template': None}
    ACTIVATE_ACCOUNT = {'id': 4,
                        'template': _HTML_EMAIL_ACTIVATE_ACCOUNT_TEMPLATE}
    FORGOT_PASSWORLD_ALTERNATE = {
        'id': 5,
        'template': _HTML_EMAIL_FORGOT_PASSWORD_ALTERNATIVE_TEMPLATE
    }

    @staticmethod
    def value_of(value):
        return TypeEmail.__members__.get(value, None)

    @property
    def template(self):
        return self.value.get('template', None)


def get_html_reset_password(app_name, base_url, type_email,
                            token_id, domain, user):
    action = type_email.value.get('action')

    url = '{}/auth/reset/{}/{}?action={}'.format(base_url,
                                                 token_id,
                                                 domain.name,
                                                 action)

    return type_email.template.format(app_name=app_name,
                                      reset_url=url,
                                      domain_name=domain.name,
                                      username=user.name)


def get_html_activate_account(app_name, base_url, template,
                              token_id, user, domain):

    url = '{}/landing/activate/{}/{}/{}'.format(base_url,
                                                token_id,
                                                domain.id,
                                                user.id)

    return template.format(app_name=app_name, activate_url=url,
                           username=user.name, domain_name=domain.name)


def _get_variables():
    default_app_name = "VIGGOCORE"
    default_email_use_sandbox = False
    default_base_url = 'http://objetorelacional.com.br'
    default_noreply_email = 'noreply@objetorelacional.com.br'
    default_email_subject = 'VIGGOCORE - CONFIRMAR email e CRIAR senha'

    app_name = os.environ.get(
        'VIGGOCORE_APP_NAME', default_app_name)
    noreply_email = os.environ.get(
        'VIGGOCORE_NOREPLY_EMAIL', default_noreply_email)
    base_url = os.environ.get('VIGGOCORE_BASE_URL', default_base_url)
    email_subject = os.environ.get(
        'VIGGOCORE_EMAIL_SUBJECT', default_email_subject)
    email_use_sandbox = os.environ.get(
        'VIGGOCORE_EMAIL_USE_SANDBOX',
        default_email_use_sandbox) == 'True'

    return (app_name, base_url, noreply_email, email_subject,
            email_use_sandbox)


def send_email(type_email, token_id, user, domain, alternate_pass=None):
    try:
        sparkpost = SparkPost()
        (app_name, base_url, noreply_email, email_subject,
         email_use_sandbox) = _get_variables()

        if type_email in [TypeEmail.USER_CREATED, TypeEmail.FORGOT_PASSWORD]:
            html = get_html_reset_password(
                app_name, base_url, type_email, token_id, domain, user)
        elif type_email is TypeEmail.ACTIVATE_ACCOUNT:
            html = get_html_activate_account(app_name, base_url,
                                             type_email.template,
                                             token_id, user, domain)
        elif type_email is TypeEmail.UPDATED_PASSWORD:
            return None
        elif type_email is TypeEmail.FORGOT_PASSWORLD_ALTERNATE:
            html = type_email.template \
                .format(app_name=app_name, password=alternate_pass)
        else:
            raise exception.BadRequest()

        sparkpost.transmissions.send(
            use_sandbox=email_use_sandbox,
            recipients=[user.email],
            html=html,
            from_email=noreply_email,
            subject=email_subject
        )
    except Exception:
        # TODO(fdoliveira): do something here!
        pass
