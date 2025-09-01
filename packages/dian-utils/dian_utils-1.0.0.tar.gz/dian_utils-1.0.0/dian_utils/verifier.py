# @author jdperea

def calculate_verification_digit(nit: int) -> int:
    """
    Calcula el dígito de verificación del NIT según la DIAN.
    """
    if not is_valid_nit(nit):
        return False
    factors = [71, 67, 59, 53, 47, 43, 41, 37, 29, 23, 19, 17, 13, 7, 3]
    nit_str = str(nit).rjust(15, '0')
    total = sum(int(nit_str[i]) * factors[i] for i in range(15))
    remainder = total % 11
    return 11 - remainder if remainder > 1 else remainder

def check_verification_digit(nit: int, dv: int) -> bool:
    """
    Verifica si el dígito de verificación proporcionado coincide con el calculado.
    """
    if not is_valid_nit(nit):
        return False
    return calculate_verification_digit(nit) == dv

def is_valid_nit(nit: int) -> bool:
    """
    Valida si el NIT es estructuralmente correcto:
    - Debe tener entre 5 y 15 dígitos.
    - Solo debe contener números.
    """
    nit_str = str(nit)
    if not nit_str.isdigit() or not (5 <= len(nit_str) <= 15):
        return False

    if nit_str in ['999999999', '000000000']:
        return False

    if len(set(nit_str)) == 1:
        return False

    if nit_str in '0123456789':
        return False
    if nit_str in '9876543210':
        return False
    for i in range(len(nit_str) - 1):
        if int(nit_str[i+1]) - int(nit_str[i]) == 1:
            continue
        else:
            break
    else:
        return False

    for i in range(len(nit_str) - 1):
        if int(nit_str[i]) - int(nit_str[i+1]) == 1:
            continue
        else:
            break
    else:
        return False
    return True
