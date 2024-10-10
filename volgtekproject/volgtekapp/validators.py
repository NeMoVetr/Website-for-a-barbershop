import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class PasswordValidator:

    def validate(self, password, user=None):

        if re.search(r'[А-Яа-я]', password):
            raise ValidationError(
                _('Пароль не должен содержать русские буквы.'),
                code='password_has_russian',
            )

        if len(password) < 6:
            raise ValidationError(
                _('Пароль должен содержать не менее 6 символов.'),
                code='password_too_short',
            )

        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Пароль должен содержать хотя бы одну заглавную латинскую букву."),
                code='password_no_upper',
            )

        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _('Пароль должен содержать хотя бы одну строчную латинскую букву'),
                code='password_no_lower',
            )
        if not re.search('[0-9]', password):
            raise ValidationError(
                _('Пароль должен содержать хотя бы одну цифру.'),
                code='password_no_number',
            )
        if not re.search('[!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]', password):
            raise ValidationError(
                _('Пароль должен содержать хотя бы один специальный символ.'),
                code='password_no_special',
            )
        if not re.search(r'\s', password):
            raise ValidationError(
                _('Пароль должен содержать хотя бы один пробел.'),
                code='password_has_spaces',
            )


    def get_help_text(self):
        return _(
            "Ваш пароль должен содержать хотя бы одну заглавную и одну строчную латинскую букву, цифру, специальный символ, пробел и не должен содержать русские буквы."
        )
