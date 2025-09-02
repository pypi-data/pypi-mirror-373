def valida_cpf_cnpj(cpf_cnpj):
    if len(cpf_cnpj) == 11:
        return valida_cpf(cpf_cnpj)
    elif len(cpf_cnpj) == 14:
        return valida_cnpj(cpf_cnpj)
    else:
        return False


def valida_cpf(cpf):
    cpf = cpf.replace('.', '').replace('-', '')
    digitos_verificadores = cpf[9:]
    cpf = cpf[:9]

    try:
        dig_1 = int(cpf[0]) * 1
        dig_2 = int(cpf[1]) * 2
        dig_3 = int(cpf[2]) * 3
        dig_4 = int(cpf[3]) * 4
        dig_5 = int(cpf[4]) * 5
        dig_6 = int(cpf[5]) * 6
        dig_7 = int(cpf[6]) * 7
        dig_8 = int(cpf[7]) * 8
        dig_9 = int(cpf[8]) * 9
    except IndexError:
        return False

    dig_1_ao_9_somados = (
        dig_1 + dig_2 + dig_3 + dig_4 + dig_5 + dig_6 + dig_7 + dig_8 + dig_9)

    dig_10 = dig_1_ao_9_somados % 11

    if dig_10 > 9:
        dig_10 = 0

    cpf += str(dig_10)

    dig_1 = int(cpf[0]) * 0
    dig_2 = int(cpf[1]) * 1
    dig_3 = int(cpf[2]) * 2
    dig_4 = int(cpf[3]) * 3
    dig_5 = int(cpf[4]) * 4
    dig_6 = int(cpf[5]) * 5
    dig_7 = int(cpf[6]) * 6
    dig_8 = int(cpf[7]) * 7
    dig_9 = int(cpf[8]) * 8
    dig_10 = int(cpf[9]) * 9

    dig_1_ao_10_somados = (
        dig_1 + dig_2 + dig_3 + dig_4 + dig_5 + dig_6 + dig_7 + dig_8 + dig_9 +
        dig_10)

    dig_11 = dig_1_ao_10_somados % 11

    if dig_11 > 9:
        dig_11 = 0

    cpf_validado = cpf + str(dig_11)

    return digitos_verificadores == cpf_validado[9:]


def valida_cnpj(cnpj):
    cnpj = cnpj.replace('.', '').replace('/', '').replace('-', '')
    digitos_verificadores = cnpj[12:]
    cnpj = cnpj[:12]

    try:
        dig_1 = int(cnpj[0]) * 6
        dig_2 = int(cnpj[1]) * 7
        dig_3 = int(cnpj[2]) * 8
        dig_4 = int(cnpj[3]) * 9
        dig_5 = int(cnpj[4]) * 2
        dig_6 = int(cnpj[5]) * 3
        dig_7 = int(cnpj[6]) * 4
        dig_8 = int(cnpj[7]) * 5
        dig_9 = int(cnpj[8]) * 6
        dig_10 = int(cnpj[9]) * 7
        dig_11 = int(cnpj[10]) * 8
        dig_12 = int(cnpj[11]) * 9
    except IndexError:
        return False

    dig_1_ao_12_somados = (
        dig_1 + dig_2 + dig_3 + dig_4 + dig_5 + dig_6 + dig_7 + dig_8 + dig_9 +
        dig_10 + dig_11 + dig_12)

    dig_13 = dig_1_ao_12_somados % 11

    if dig_13 > 9:
        dig_13 = 0

    cnpj += str(dig_13)

    dig_1 = int(cnpj[0]) * 5
    dig_2 = int(cnpj[1]) * 6
    dig_3 = int(cnpj[2]) * 7
    dig_4 = int(cnpj[3]) * 8
    dig_5 = int(cnpj[4]) * 9
    dig_6 = int(cnpj[5]) * 2
    dig_7 = int(cnpj[6]) * 3
    dig_8 = int(cnpj[7]) * 4
    dig_9 = int(cnpj[8]) * 5
    dig_10 = int(cnpj[9]) * 6
    dig_11 = int(cnpj[10]) * 7
    dig_12 = int(cnpj[11]) * 8
    dig_13 = int(cnpj[12]) * 9

    dig_1_ao_13_somados = (
        dig_1 + dig_2 + dig_3 + dig_4 + dig_5 + dig_6 + dig_7 + dig_8 + dig_9 +
        dig_10 + dig_11 + dig_12 + dig_13)

    dig_14 = dig_1_ao_13_somados % 11

    if dig_14 > 9:
        dig_14 = 0

    cnpj_validado = cnpj + str(dig_14)

    return digitos_verificadores == cnpj_validado[12:]
