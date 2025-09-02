import os
import requests
from viggocore.common.valida_cpf_cnpj import valida_cpf_cnpj
from viggocore.common import exception
from viggocore.common.subsystem import operation


API_CPF_CONSULTA_PF = 'API_CPF_CONSULTA_PF'
API_CPF_CONSULTA_PJ = 'API_CPF_CONSULTA_PJ'
API_CPF_AUTH = 'API_CPF_CONSULTA_AUTH'


class ConsultaCpfCnpj(operation.List):
    def pre(self, **kwargs):
        # obriga a presença do cpf_cnpj
        self.cpf_cnpj = kwargs.get('cpf_cnpj', None)
        if self.cpf_cnpj is None:
            raise exception.BadRequest('ERRO! cpf_cnpj não informado')

        # remove caracteres especiais
        self.cpf_cnpj = self.cpf_cnpj \
            .replace(' ', '') \
            .replace('-', '') \
            .replace('/', '') \
            .replace('.', '')

        # valida o cpf/cnpj
        self.is_cpf_cnpj_valid = valida_cpf_cnpj(self.cpf_cnpj)
        if self.is_cpf_cnpj_valid is False:
            raise exception.BadRequest(
                'ERRO! o CPF/CNPJ informado não é válido')

        # define se o valor trata um cpf ou um cnpj
        self.is_cpf = len(self.cpf_cnpj) == 11

        return True

    def do(self, session, **kwargs):
        # busca as variáveis necessárias para a requisição
        auth = os.getenv(API_CPF_AUTH, None)
        op_api = API_CPF_CONSULTA_PF if self.is_cpf \
            else API_CPF_CONSULTA_PJ
        api = os.getenv(op_api, None)
        if not all([auth, api]):
            raise exception.BadRequest(
                ' '.join([
                    'É obrigatório preencher as variáveis de ambiente: ',
                    f'"{API_CPF_AUTH}", "{API_CPF_CONSULTA_PF}" e ',
                    f'"{API_CPF_CONSULTA_PJ}".']))

        # monta header
        headers = {
            'Authorization': f'Basic {auth}'
        }

        # monta url
        api_url = api + self.cpf_cnpj

        try:
            # tenta fazera requisição e trata o resultado
            request = requests.get(api_url, headers=headers)
            # caso o resultado seja sucesso, retorna o contaúdo da consulta
            if request.status_code == 200:
                return request.json()

        except Exception:
            # em caso de erro na requisição, dispara uma exceção com erro
            # diferente
            raise exception.BadRequest(
                'ERRO! Ocorreu uma falha na API ao consultar o CPF/CNPJ')

        # caso não seja sucesso e nem erro na requisição, dispara uma exceção
        raise exception.BadRequest(
            'ERRO! Não foi possível consultar o CPF/CNPJ')
