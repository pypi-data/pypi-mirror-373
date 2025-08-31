from unittest import TestCase
from unittest.mock import MagicMock, patch
from eaasy.extensions import validate_email_address, validate_phone_number
from eaasy.extensions.helper import verify_oidc


class TestHelper(TestCase):
    def test_validating_email_address_raises_exception_when_address_is_not_valid(self):
        # Act & Assert
        with self.assertRaises(Exception) as context:
            validate_email_address('invalid_email')
        
        self.assertEqual(context.exception.args[0]['status_code'], 400)
        self.assertEqual(
            context.exception.args[0]['message'], "'invalid_email' is not a valid email address")
        self.assertEqual(context.exception.args[0]['data']['email'], 'invalid_email')

    def test_validating_email_address_returns_true_when_address_is_valid(self):
        # Act
        result = validate_email_address('user@email.com')

        # Assert
        self.assertIsNone(result)

    def test_validating_phone_number_raises_exception_when_number_is_not_valid(self):
        # Act & Assert
        with self.assertRaises(Exception) as context:
            validate_phone_number('invalid_phone')
        
        self.assertEqual(context.exception.args[0]['status_code'], 400)
        self.assertEqual(
            context.exception.args[0]['message'], "'invalid_phone' is not a valid phone number")
        self.assertEqual(context.exception.args[0]['data']['phone'], 'invalid_phone')

    def test_validating_phone_number_returns_true_when_phone_is_valid(self):
        # Act
        result = validate_phone_number('1234567890')

        # Assert
        self.assertIsNone(result)

    def __get_mock_oidc(self) -> tuple[MagicMock, list]:
        unauthorized = [0]  # Use a list to hold the count
        oidc = MagicMock()

        # Mock accept_token to behave like a decorator
        def mock_accept_token(*args, **kwargs):
            def decorator(f):
                unauthorized[0] += 1
                return f
            return decorator

        oidc.accept_token = MagicMock(side_effect=mock_accept_token)
        return oidc, unauthorized

    def test_verifying_oidc_decorator_is_not_executed_when_oidc_is_null(self):
        # Arrange
        oidc, unauthorized = self.__get_mock_oidc()
        
        @verify_oidc(None)
        def test_func():
            return 'ok'

        # Act
        result = test_func()

        # Assert
        self.assertEqual('ok', result)
        oidc.accept_token.assert_not_called()
        self.assertEqual(unauthorized[0], 0)

    @patch('eaasy.extensions.helper.assert_is_instance', return_value=None)
    def test_verifying_oidc_decorator_is_executed_when_oidc_is_not_null(self, *_):
        # Arrange
        oidc, unauthorized = self.__get_mock_oidc()
        
        @verify_oidc(oidc)
        def test_func():
            return 'ok'

        # Act
        result = test_func()

        # Assert
        self.assertEqual('ok', result)
        oidc.accept_token.assert_called_once()
        self.assertEqual(unauthorized[0], 1)
