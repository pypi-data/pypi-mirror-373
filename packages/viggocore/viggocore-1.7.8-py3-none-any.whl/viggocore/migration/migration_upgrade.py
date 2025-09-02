from datetime import datetime
from alembic.script import ScriptDirectory
from alembic import util
from alembic.runtime.environment import EnvironmentContext
from alembic.runtime import migration
import flask_migrate
from flask.globals import current_app


def criar_tabela_alembic_version_history(manager):
    manager.driver.transaction_manager.session.execute(
    """
        CREATE TABLE IF NOT EXISTS alembic_version_history (
            id bpchar(32) NOT NULL,
            active bool NULL,
            created_at timestamp NULL,
            created_by bpchar(32) NULL,
            updated_at timestamp NULL,
            updated_by bpchar(32) NULL,
            tag varchar(1000) NULL,
            ordem SERIAL PRIMARY KEY,
            titulo varchar(200) NOT NULL,
            anterior_id varchar(50) NULL,
            atual_id varchar(50) NOT NULL,
            data_criacao timestamp NOT NULL,
            data_execucao timestamp NOT NULL,
            tipo varchar(50) NOT NULL DEFAULT 'UPGRADE'
        );
    """)  # noqa


# alteração de upgrade
def dbupgrade(directory=None, revision='head', sql=False, tag=None,
              x_arg=None):
    """Upgrade to a later version"""
    config = flask_migrate.current_app.extensions['migrate']\
        .migrate.get_config(directory, x_arg=x_arg)
    # realiza o upgrade
    upgrade(config, revision, sql=sql, tag=tag)


def upgrade(config, revision, sql=False, tag=None):
    """Upgrade to a later version.

    :param config: a :class:`.Config` instance.

    :param revision: string revision target or range for --sql mode

    :param sql: if True, use ``--sql`` mode

    :param tag: an arbitrary "tag" that can be intercepted by custom
    ``env.py`` scripts via the :meth:`.EnvironmentContext.get_tag_argument`
    method.

    """
    # cria a tabela alembic_version_history caso não exista
    manager = current_app.api_handler.api().alembic_version_historys()
    criar_tabela_alembic_version_history(manager)

    # variável responsável por armazenar as informações que serão usadas
    # para preencher o histórico no banco
    histories = []
    script = ScriptDirectory.from_config(config)

    starting_rev = None
    if ":" in revision:
        if not sql:
            raise util.CommandError("Range revision not allowed")
        starting_rev, revision = revision.split(":", 2)

    def upgrade(rev, context):
        response, histories_aux = _upgrade_revs(script, revision, rev)
        histories.extend(histories_aux)
        return response

    with EnvironmentContext(
        config,
        script,
        fn=upgrade,
        as_sql=sql,
        starting_rev=starting_rev,
        destination_rev=revision,
        tag=tag,
    ):
        script.run_env()

    # preenche a tabela de histórico das migrações
    for history in histories:
        manager.create(**history)


def _upgrade_revs(script, destination, current_rev):
    with script._catch_revision_errors(
        ancestor="Destination %(end)s is not a valid upgrade "
        "target from current head(s)",
        end=destination,
    ):
        # executa os upgrades
        revs = script.revision_map.iterate_revisions(
            destination, current_rev, implicit_base=True
        )
        revs = list(revs)
        resposta = []
        histories = []

        for script_aux in reversed(list(revs)):
            resposta.append(migration.MigrationStep.upgrade_from_script(
                script.revision_map, script_aux
            ))
            histories.append({
                'titulo': script_aux.doc,
                'anterior_id': script_aux.down_revision,
                'atual_id': script_aux.revision,
                'data_criacao': datetime.strptime(
                    script_aux.longdoc.split('Date: ')[-1],
                    '%Y-%m-%d %H:%M:%S.%f'),
                'data_execucao': datetime.now(),
                'tipo': 'UPGRADE'
            })

        return (resposta, histories)
