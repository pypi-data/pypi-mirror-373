import sys
import os
import unittest

# Añadir la carpeta raíz al sys.path, Esto para pruebas antes de lanzamiento primera versión
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dian_utils.verifier import (
    calculate_verification_digit,
    is_valid_nit,
    check_verification_digit
)

class TestVerifierFunctions(unittest.TestCase):

    def test_calculate_verification_digit(self):
        self.assertEqual(calculate_verification_digit(900974092), 1)
        self.assertEqual(calculate_verification_digit(900241770), 1)
        self.assertEqual(calculate_verification_digit(901873571), 8)
        # print(calculate_verification_digit(830092517))

    def test_is_valid_nit(self):
        self.assertTrue(is_valid_nit(900123456))
        self.assertFalse(is_valid_nit(123456789))
        self.assertFalse(is_valid_nit("ABC123456"))
        self.assertFalse(is_valid_nit(999999999))
        self.assertFalse(is_valid_nit(888888888))
        self.assertFalse(is_valid_nit(000000000))
        self.assertFalse(is_valid_nit(1234))

    def test_check_verification_digit(self):
        self.assertTrue(check_verification_digit(900974092, 1))
        self.assertTrue(check_verification_digit(900123456, 8))
        self.assertTrue(check_verification_digit(830092517, 0))
        self.assertFalse(check_verification_digit(800197268, 3))  # DV incorrecto
        self.assertFalse(check_verification_digit("ABC123456", 5))  # NIT inválido
        self.assertFalse(check_verification_digit(900241770, 4))

if __name__ == '__main__':
    unittest.main()
