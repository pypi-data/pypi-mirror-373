import os
from viggocore.common import exception
from datetime import datetime as datetime1


def get_size(domain_id, **kwargs):  # noqa
    size = 0
    de = kwargs.get('de', None)
    ate = kwargs.get('ate', None)

    try:
        if de is not None:
            de = de.replace(tzinfo=None)
    except Exception:
        raise exception.BadRequest('Não foi possível remover o tzinfo do "de"')

    try:
        if ate is not None:
            ate = ate.replace(tzinfo=None)
    except Exception:
        raise exception.BadRequest('Não foi possível remover o tzinfo do "ate"')

    folderpath = os.environ.get('VIGGOCORE_FILE_DIR_SIZE', '')
    if len(folderpath) == 0:
        raise exception.BadRequest('VIGGOCORE_FILE_DIR_SIZE not found')

    if de is None and ate is None:
        for ele in os.scandir(folderpath):
            if '.' not in ele.name:
                for ele2 in os.scandir(f'{folderpath}/{ele.name}'):
                    if '.' not in ele2.name:
                        for ele3 in os.scandir(f'{folderpath}/{ele.name}/{ele2.name}'):  # noqa
                            if ele3.name == domain_id:
                                for ele4 in os.scandir(f'{folderpath}/{ele.name}/{ele2.name}/{ele3.name}'):  # noqa
                                    for ele5 in os.scandir(f'{folderpath}/{ele.name}/{ele2.name}/{ele3.name}/{ele4.name}'):  # noqa
                                        size += os.path.getsize(ele5)
    else:
        for ele in os.scandir(folderpath):
            if '.' not in ele.name:
                for ele2 in os.scandir(f'{folderpath}/{ele.name}'):
                    if '.' not in ele2.name:
                        for ele3 in os.scandir(f'{folderpath}/{ele.name}/{ele2.name}'):  # noqa
                            if ele3.name == domain_id:
                                for ele4 in os.scandir(f'{folderpath}/{ele.name}/{ele2.name}/{ele3.name}'):  # noqa
                                    for ele5 in os.scandir(f'{folderpath}/{ele.name}/{ele2.name}/{ele3.name}/{ele4.name}'):  # noqa
                                        ti_c = os.path.getctime(ele5)
                                        created_at = datetime1.fromtimestamp(ti_c)  # noqa
                                        validacao = ((de is None or created_at > de) and  # noqa
                                           (ate is None or created_at < ate))  # noqa
                                        print(validacao)
                                        if validacao:
                                            size += os.path.getsize(ele5)
                                        else:
                                            print(created_at)

    response_dict = {}

    # montandos as respostas
    conversoes = ['BYTES', 'KBYTES', 'MEGAS', 'GIGAS', 'TERAS']
    for conversao in conversoes:
        response_dict.update({conversao: size})
        size /= 1024

    return response_dict
