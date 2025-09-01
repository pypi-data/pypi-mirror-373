# validator_service/validator.py

from dataclasses import field
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from datetime import datetime, date
import re
import json
import uuid
from django.db import connection

class ValidatorService:
    @staticmethod
    def validate(data, rules, custom_messages=None):
        errors = {}

        for field, rule in rules.items():
            value = data.get(field)
            rules_list = rule.split('|')

            # Check if field should be skipped
            has_required_rule = 'required' in rules_list
            has_required_without_rule = any(rule.startswith('required_without') for rule in rules_list)
            
            if field not in data and not has_required_rule and not has_required_without_rule:
                continue  # Skip this field completely

            # Check if the field is an array and handle accordingly
            # Check if the field is an array and handle accordingly
            if 'array' in rules_list:
                if 'nullable' in rules_list and field not in data:
                    continue

                if not isinstance(value, list):
                    ValidatorService._add_error(errors, field, 'array', {'_attribute': field})
                    continue

                # --- Array length constraints (so "min:1" works) ---
                # min:N
                min_rule = next((x for x in rules_list if x.startswith('min:')), None)
                if min_rule:
                    try:
                        min_val = int(min_rule.split(':')[1])
                        if len(value) < min_val:
                            ValidatorService._add_error(
                                errors, field, 'min_array', {'_attribute': field, 'min': min_val}
                            )
                    except ValueError:
                        pass

                # max:N (optional, supported by your error types)
                max_rule = next((x for x in rules_list if x.startswith('max:')), None)
                if max_rule:
                    try:
                        max_val = int(max_rule.split(':')[1])
                        if len(value) > max_val:
                            ValidatorService._add_error(
                                errors, field, 'max_array', {'_attribute': field, 'max': max_val}
                            )
                    except ValueError:
                        pass

                # size:N (optional)
                size_rule = next((x for x in rules_list if x.startswith('size:')), None)
                if size_rule:
                    try:
                        size_val = int(size_rule.split(':')[1])
                        if len(value) != size_val:
                            ValidatorService._add_error(
                                errors, field, 'size_array', {'_attribute': field, '_size': size_val}
                            )
                    except ValueError:
                        pass

                # Validate each item in the array
                for index, item in enumerate(value):
                    item_rules = ValidatorService._get_item_rules(field, rules_list)
                    item_errors = ValidatorService.validate_item(item, item_rules, data, field_name=field)
                    if item_errors:
                        errors[field] = errors.get(field, [])
                        errors[field].extend(item_errors)
                continue  # Move to the next field after processing the array


            # Check required directly
            if 'required' in rules_list and (field not in data or ValidatorService._is_empty(value)):
                ValidatorService._add_error(errors, field, 'required', {'_attribute': field})
                continue  

            # Only skip if field is not in data AND doesn't have required_without rule
            has_required_without_rule = any(rule.startswith('required_without') for rule in rules_list)
            if field not in data and not has_required_without_rule:
                continue  

            for r in rules_list:
                # Skip logic
                if ValidatorService._should_skip_field(value, rules_list):
                    continue

                if r == 'required':
                    if ValidatorService._is_empty(value):
                        ValidatorService._add_error(errors, field, 'required', {'_attribute': field})

                elif r == 'nullable':
                    continue

                elif r.startswith('required_without'):
                    other_field = r.split(':')[1]
                    if ValidatorService._is_empty(value) and ValidatorService._is_empty(data.get(other_field)):
                        custom_message = custom_messages.get(f'{field}.required_without', f'{field} is required if {other_field} is missing.') if custom_messages else None
                        ValidatorService._add_error(errors, field, 'required_without', {'_attribute': field, 'other_field': other_field, 'message': custom_message})

                elif r == 'accepted':
                    if value not in ['yes', 'on', '1', 1, True]:
                        ValidatorService._add_error(
                            errors, field, 'accepted', {'_attribute': field}
                        )
                elif r == 'active_url':
                    try:
                        URLValidator()(value)
                    except ValidationError:
                        ValidatorService._add_error(
                            errors, field, 'active_url', {'_attribute': field}
                        )
                elif r.startswith('after:'):
                    try:
                        input_date = datetime.strptime(value, '%Y-%m-%d').date()
                        after_date = datetime.strptime(r.split(':')[1], '%Y-%m-%d').date()
                        if input_date <= after_date:
                            ValidatorService._add_error(
                                errors, field, 'after', {'_attribute': field, 'date': r.split(':')[1]}
                            )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'after', {'_attribute': field, 'date': r.split(':')[1]}
                        )
                elif r.startswith('after_or_equal:'):
                    ref_field = r.split(':')[1]
                    try:
                        if ref_field in data:
                            ref_value = data.get(ref_field)
                            if value and ref_value:
                                input_date = datetime.strptime(value, '%Y-%m-%d').date()
                                ref_date = datetime.strptime(ref_value, '%Y-%m-%d').date()
                                if input_date < ref_date:
                                    ValidatorService._add_error(
                                        errors, field, 'after_or_equal', {'_attribute': field, 'date': ref_field}
                                    )
                        
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'after_or_equal', {'_attribute': field, 'date': ref_field}
                        )
                        
                elif r == 'alpha':
                    if not re.match(r'^[a-zA-Z]+$', value):
                        ValidatorService._add_error(
                            errors, field, 'alpha', {'_attribute': field}
                        )
                elif r == 'alpha_dash':
                    if not re.match(r'^[a-zA-Z0-9_-]+$', value):
                        ValidatorService._add_error(
                            errors, field, 'alpha_dash', {'_attribute': field}
                        )
                elif r == 'alpha_num':
                    if not re.match(r'^[a-zA-Z0-9]+$', value):
                        ValidatorService._add_error(
                            errors, field, 'alpha_num', {'_attribute': field}
                        )
                elif r == 'array':
                    if not isinstance(value, list):
                        ValidatorService._add_error(
                            errors, field, 'array', {'_attribute': field}
                        )
                    elif 'min:1' in rules_list and len(value) < 1:
                        ValidatorService._add_error(
                            errors, field, 'min_array', {'_attribute': field, '_min': 1}
                        )
                elif r.startswith('before:'):
                    try:
                        input_date = datetime.strptime(value, '%Y-%m-%d').date()
                        before_date = datetime.strptime(r.split(':')[1], '%Y-%m-%d').date()
                        if input_date >= before_date:
                            ValidatorService._add_error(
                                errors, field, 'before', {'_attribute': field, 'date': r.split(':')[1]}
                            )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'before', {'_attribute': field, 'date': r.split(':')[1]}
                        )
                elif r.startswith('before_or_equal:'):
                    try:
                        input_date = datetime.strptime(value, '%Y-%m-%d').date()
                        before_date = datetime.strptime(r.split(':')[1], '%Y-%m-%d').date()
                        if input_date > before_date:
                            ValidatorService._add_error(
                                errors, field, 'before_or_equal', {'_attribute': field, 'date': r.split(':')[1]}
                            )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'before_or_equal', {'_attribute': field, 'date': r.split(':')[1]}
                        )
                elif r.startswith('between:'):
                    min_val, max_val = map(int, r.split(':')[1].split(','))
                    if isinstance(value, (int, float)):
                        if not (min_val <= value <= max_val):
                            ValidatorService._add_error(
                                errors, field, 'between_numeric', {'_attribute': field, 'min': min_val, 'max': max_val}
                            )
                    elif isinstance(value, str):
                        if not (min_val <= len(value) <= max_val):
                            ValidatorService._add_error(
                                errors, field, 'between_string', {'_attribute': field, 'min': min_val, 'max': max_val}
                            )
                    elif isinstance(value, list):
                        if not (min_val <= len(value) <= max_val):
                            ValidatorService._add_error(
                                errors, field, 'between_array', {'_attribute': field, 'min': min_val, 'max': max_val}
                            )
                elif r == 'boolean':
                    if value not in [True, False, 1, 0, '1', '0']:
                        ValidatorService._add_error(
                            errors, field, 'boolean', {'_attribute': field}
                        )
                elif r == 'confirmed':
                    if value != data.get(f'{field}_confirmation'):
                        ValidatorService._add_error(
                            errors, field, 'confirmed', {'_attribute': field}
                        )
                elif r == 'date':
                    try:
                        datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        ValidatorService._add_error(
                            errors, field, 'date', {'_attribute': field}
                        )
                elif r.startswith('date_equals:'):
                    try:
                        input_date = datetime.strptime(value, '%Y-%m-%d').date()
                        equals_date = datetime.strptime(r.split(':')[1], '%Y-%m-%d').date()
                        if input_date != equals_date:
                            ValidatorService._add_error(
                                errors, field, 'date_equals', {'_attribute': field, 'date': r.split(':')[1]}
                            )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'date_equals', {'_attribute': field, 'date': r.split(':')[1]}
                        )
                elif r.startswith('date_format:'):
                    if value is None:
                        # Only add the 'required' error if the field is not already marked as required
                        if 'required' not in rules_list:
                            ValidatorService._add_error(
                                errors, field, 'required', {'_attribute': field}
                            )
                    else:
                        try:
                            datetime.strptime(value, r.split(':')[1])
                        except ValueError:
                            ValidatorService._add_error(
                                errors, field, 'date_format', {'_attribute': field, 'format': r.split(':')[1]}
                            )
                elif r.startswith('different:'):
                    if value == data.get(r.split(':')[1]):
                        ValidatorService._add_error(
                            errors, field, 'different', {'_attribute': field, '_other': r.split(':')[1]}
                        )
                elif r.startswith('digits:'):
                    if not (value.isdigit() and len(value) == int(r.split(':')[1])):
                        ValidatorService._add_error(
                            errors, field, 'digits', {'_attribute': field, '_digits': r.split(':')[1]}
                        )
                elif r.startswith('digits_between:'):
                    min_digits, max_digits = map(int, r.split(':')[1].split(','))
                    if not (value.isdigit() and min_digits <= len(value) <= max_digits):
                        ValidatorService._add_error(
                            errors, field, 'digits_between', {'_attribute': field, 'min': min_digits, 'max': max_digits}
                        )
                elif r == 'email':
                    if value:
                        if not ValidatorService._is_valid_email(value):
                            ValidatorService._add_error(
                                errors, field, 'email_error', {'_attribute': field}
                            )
                elif r.startswith('ends_with:'):
                    if not any(value.endswith(suffix) for suffix in r.split(':')[1].split(',')):
                        ValidatorService._add_error(
                            errors, field, 'ends_with', {'_attribute': field, '_values': r.split(':')[1]}
                        )
                elif r.startswith('exists:'):
                    try:
                        parts = r.split(":", 1)[1].split(',')
                        if len(parts) != 2:
                            ValidatorService._add_error(
                                errors, field, 'exists', {'_attribute': field}
                            )
                            continue

                        table_name, column = parts
                        if ValidatorService._is_empty(value):
                            continue

                        if not ValidatorService.table_exists(table_name):
                            ValidatorService._add_error(
                                errors, field, 'exists', {'_attribute': field, '_values': "Table Not Found"}
                            )
                            continue

                        if not ValidatorService.record_exists(table_name, column, value):
                            ValidatorService._add_error(
                                errors, field, 'exists', {'_attribute': field}
                            )

                    except ValueError as e:
                        ValidatorService._add_error(
                            errors, field, 'exists', {'_attribute': field, '_error': str(e)}
                        )

                elif r == 'file':
                    if not hasattr(value, 'file'):
                        ValidatorService._add_error(
                            errors, field, 'file', {'_attribute': field}
                        )
                elif r == 'filled':
                    if not value:
                        ValidatorService._add_error(
                            errors, field, 'filled', {'_attribute': field}
                        )
                elif r.startswith('gt:'):
                    try:
                        if isinstance(value, (int, float)):
                            if value <= float(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'gt_numeric', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, str):
                            if len(value) <= int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'gt_string', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, list):
                            if len(value) <= int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'gt_array', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'gt', {'_attribute': field, '_value': r.split(':')[1]}
                        )
                elif r.startswith('gte:'):
                    try:
                        if isinstance(value, (int, float)):
                            if value < float(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'gte_numeric', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, str):
                            if len(value) < int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'gte_string', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, list):
                            if len(value) < int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'gte_array', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'gte', {'_attribute': field, '_value': r.split(':')[1]}
                        )
                elif r == 'image':
                    if not hasattr(value, 'image'):
                        ValidatorService._add_error(
                            errors, field, 'image', {'_attribute': field}
                        )
                elif r.startswith('in:'):
                    if value not in r.split(':')[1].split(','):
                        ValidatorService._add_error(
                            errors, field, 'in', {'_attribute': field, '_values': r.split(':')[1]}
                        )
                elif r.startswith('in_array:'):
                    if value not in data.get(r.split(':')[1], []):
                        ValidatorService._add_error(
                            errors, field, 'in_array', {'_attribute': field, '_other': r.split(':')[1]}
                        )
                elif r == 'integer':
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'integer', {'_attribute': field}
                        )
                elif r == 'ip':
                    try:
                        from ipaddress import ip_address
                        ip_address(value)
                    except ValueError:
                        ValidatorService._add_error(
                            errors, field, 'ip', {'_attribute': field}
                        )
                elif r == 'ipv4':
                    try:
                        from ipaddress import IPv4Address
                        IPv4Address(value)
                    except ValueError:
                        ValidatorService._add_error(
                            errors, field, 'ipv4', {'_attribute': field}
                        )
                elif r == 'ipv6':
                    try:
                        from ipaddress import IPv6Address
                        IPv6Address(value)
                    except ValueError:
                        ValidatorService._add_error(
                            errors, field, 'ipv6', {'_attribute': field}
                        )
                elif r == 'json':
                    try:
                        json.loads(value)
                    except json.JSONDecodeError:
                        ValidatorService._add_error(
                            errors, field, 'json', {'_attribute': field}
                        )
                elif r.startswith('lt:'):
                    try:
                        if isinstance(value, (int, float)):
                            if value >= float(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'lt_numeric', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, str):
                            if len(value) >= int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'lt_string', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, list):
                            if len(value) >= int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'lt_array', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'lt', {'_attribute': field, '_value': r.split(':')[1]}
                        )
                elif r.startswith('lte:'):
                    try:
                        if isinstance(value, (int, float)):
                            if value > float(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'lte_numeric', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, str):
                            if len(value) > int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'lte_string', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                        elif isinstance(value, list):
                            if len(value) > int(r.split(':')[1]):
                                ValidatorService._add_error(
                                    errors, field, 'lte_array', {'_attribute': field, '_value': r.split(':')[1]}
                                )
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'lte', {'_attribute': field, '_value': r.split(':')[1]}
                        )
                elif r.startswith('max:'):
                    max_val = int(r.split(':')[1])
                    if isinstance(value, (int, float)):
                        if value > max_val:
                            ValidatorService._add_error(
                                errors, field, 'max_numeric', {'_attribute': field, 'max': max_val}
                            )
                    elif isinstance(value, str):
                        if len(value) > max_val:
                            ValidatorService._add_error(
                                errors, field, 'max_string', {'_attribute': field, 'max': max_val}
                            )
                    elif isinstance(value, list):
                        if len(value) > max_val:
                            ValidatorService._add_error(
                                errors, field, 'max_array', {'_attribute': field, 'max': max_val}
                            )
                elif r.startswith('min:'):
                    min_val = int(r.split(':')[1])
                    if isinstance(value, (int, float)):
                        if value < min_val:
                            ValidatorService._add_error(
                                errors, field, 'min_numeric', {'_attribute': field, 'min': min_val}
                            )
                    elif isinstance(value, str):
                        if len(value) < min_val:
                            ValidatorService._add_error(
                                errors, field, 'min_string', {'_attribute': field, 'min': min_val}
                            )
                    elif isinstance(value, list):
                        if len(value) < min_val:
                            ValidatorService._add_error(
                                errors, field, 'min_array', {'_attribute': field, 'min': min_val}
                            )
                elif r.startswith('mimes:'):
                    if not hasattr(value, 'file'):
                        ValidatorService._add_error(
                            errors, field, 'mimes', {'_attribute': field, '_values': r.split(':')[1]}
                        )
                elif r.startswith('mimetypes:'):
                    if not hasattr(value, 'file'):
                        ValidatorService._add_error(
                            errors, field, 'mimetypes', {'_attribute': field, '_values': r.split(':')[1]}
                        )
                elif r == 'not_in':
                    if value in r.split(':')[1].split(','):
                        ValidatorService._add_error(
                            errors, field, 'not_in', {'_attribute': field, '_values': r.split(':')[1]}
                        )
                elif r == 'not_regex':
                    if re.match(r.split(':')[1], value):
                        ValidatorService._add_error(
                            errors, field, 'not_regex', {'_attribute': field}
                        )
                elif r == 'numeric':
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        ValidatorService._add_error(
                            errors, field, 'numeric', {'_attribute': field}
                        )
                elif r == 'password':
                    # Implement password validation logic here
                    pass
                elif r == 'present':
                    if field not in data:
                        ValidatorService._add_error(
                            errors, field, 'present', {'_attribute': field}
                        )
                elif r == 'regex':
                    if not re.match(r.split(':')[1], value):
                        ValidatorService._add_error(
                            errors, field, 'regex', {'_attribute': field}
                        )
                elif r == 'required_if':
                    # Implement required_if logic here
                    pass
                elif r == 'required_unless':
                    # Implement required_unless logic here
                    pass
                elif r == 'required_with':
                    # Implement required_with logic here
                    pass
                elif r == 'required_with_all':
                    # Implement required_with_all logic here
                    pass
                elif r == 'required_without':
                    # Implement required_without logic here
                    pass
                elif r == 'required_without_all':
                    # Implement required_without_all logic here
                    pass
                elif r == 'same':
                    if value != data.get(r.split(':')[1]):
                        ValidatorService._add_error(
                            errors, field, 'same', {'_attribute': field, '_other': r.split(':')[1]}
                        )
                elif r.startswith('size:'):
                    size_val = int(r.split(':')[1])
                    if isinstance(value, (int, float)):
                        if value != size_val:
                            ValidatorService._add_error(
                                errors, field, 'size_numeric', {'_attribute': field, '_size': size_val}
                            )
                    elif isinstance(value, str):
                        if len(value) != size_val:
                            ValidatorService._add_error(
                                errors, field, 'size_string', {'_attribute': field, '_size': size_val}
                            )
                    elif isinstance(value, list):
                        if len(value) != size_val:
                            ValidatorService._add_error(
                                errors, field, 'size_array', {'_attribute': field, '_size': size_val}
                            )
                elif r.startswith('starts_with:'):
                    if not any(value.startswith(prefix) for prefix in r.split(':')[1].split(',')):
                        ValidatorService._add_error(
                            errors, field, 'starts_with', {'_attribute': field, '_values': r.split(':')[1]}
                        )
                elif r == 'string':
                    if not isinstance(value, str):
                        ValidatorService._add_error(
                            errors, field, 'string', {'_attribute': field}
                        )
                elif r == 'timezone':
                    try:
                        from pytz import timezone
                        timezone(value)
                    except Exception:
                        ValidatorService._add_error(
                            errors, field, 'timezone', {'_attribute': field}
                        )
                elif r.startswith('unique:'):
                    try:
                        # Parse the unique rule (e.g., 'unique:users,email,1')
                        parts = r.split(":")[1].split(',')
                        if len(parts) < 2:
                            ValidatorService._add_error(
                                errors, field, 'invalid_rule', {'_attribute': field}
                            )
                            continue

                        table_name, column = parts[0], parts[1]
                        exclude_id = parts[2] if len(parts) > 2 else None

                        if not ValidatorService.table_exists(table_name):
                            ValidatorService._add_error(
                                errors, field, 'unique', {'_attribute': field, '_values': "Table Not Found"}
                            )
                            continue

                        if ValidatorService.record_exists(table_name, column, value, exclude_id):
                            ValidatorService._add_error(
                                errors, field, 'unique', {'_attribute': field}
                            )
                    except ValueError as e:
                        ValidatorService._add_error(
                            errors, field, 'unique', {'_attribute': field}
                        )
                elif r == 'uploaded':
                    if not hasattr(value, 'file'):
                        ValidatorService._add_error(
                            errors, field, 'uploaded', {'_attribute': field}
                        )
                elif r == 'url':
                    try:
                        URLValidator()(value)
                    except ValidationError:
                        ValidatorService._add_error(
                            errors, field, 'url', {'_attribute': field}
                        )
                elif r == 'uuid':
                    try:
                        uuid.UUID(value)
                    except ValueError:
                        ValidatorService._add_error(
                            errors, field, 'uuid', {'_attribute': field}
                        )

        if errors:
            for field in errors:
                required_error = next((err for err in errors[field] if err['error_type'] == 'required'), None)
                if required_error:
                    errors[field] = [required_error]
                else:
                    errors[field] = errors[field][:1]
            return errors
        return None

    @staticmethod
    def _should_skip_field(value, rules_list):
        # Do NOT skip when any conditional-required rules are present
        if (
            'required' in rules_list
            or any(r.startswith(prefix) for r in rules_list for prefix in (
                'required_without', 'required_with', 'required_if',
                'required_unless', 'required_with_all', 'required_without_all'
            ))
        ):
            return False
        if 'nullable' in rules_list and ValidatorService._is_empty(value):
            return True
        if ValidatorService._is_empty(value):
            return True
        return False


    @staticmethod
    def _is_empty(value):
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == '':
            return True
        if isinstance(value, (list, tuple, dict)) and len(value) == 0:
            return True
        return False


    @staticmethod
    def _add_error(errors, field, error_type, tokens):
        if field not in errors:
            errors[field] = []
        errors[field].append({
            'error_type': error_type,
            'tokens': tokens
        })

    @staticmethod
    def get_model_class(model_name):
        from django.apps import apps
        return apps.get_model(model_name)
    
    @staticmethod
    def table_exists(table_name):
        """Check if the table exists in the database."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s)", [table_name])
            return cursor.fetchone()[0]
        
    @staticmethod
    def record_exists(table_name, column, value, exclude_id=None):
        """
        Check if a record exists in the database.

        :param table_name: The name of the table.
        :param column: The column to check.
        :param value: The value to check.
        :param exclude_id: The ID to exclude (useful for update scenarios).
        :return: True if the record exists, False otherwise.
        """
        if value is None or value == '':
            return False

        with connection.cursor() as cursor:
            query = f"SELECT COUNT(*) FROM {table_name} WHERE {column} = %s"
            params = [value]

            if exclude_id:
                query += f" AND id != %s"
                params.append(exclude_id)

            cursor.execute(query, params)
            return cursor.fetchone()[0] > 0
        
    @staticmethod
    def _get_item_rules(field, rules_list):
        """
        Accept rules like: '<field>.*.<rule>'
        e.g. 'coverages.*.exists:vendor_product,id'
        """
        item_rules = []
        prefix = f"{field}.*."
        for token in rules_list:
            if token.startswith(prefix):
                item_rules.append(token[len(prefix):])  # keep only '<rule>'
        return item_rules

    @staticmethod
    def validate_item(item, rules, data, field_name=None):
        errors = []
        for r in rules:
            if r.startswith('exists:'):
                try:
                    parts = r.split(":", 1)[1].split(',')
                    if len(parts) != 2:
                        errors.append({'error_type': 'exists', 'tokens': {'_attribute': field_name}})
                        continue

                    table_name, column = parts
                    # If item is a dict, take item[column]; otherwise use the item itself
                    item_value = item.get(column) if isinstance(item, dict) else item

                    if item_value is None or item_value == '':
                        errors.append({'error_type': 'exists', 'tokens': {'_attribute': field_name}})
                        continue

                    if not ValidatorService.table_exists(table_name):
                        errors.append({'error_type': 'exists', 'tokens': {'_attribute': "Table Not Found"}})
                        continue

                    if not ValidatorService.record_exists(table_name, column, item_value):
                        errors.append({'error_type': 'exists', 'tokens': {'_attribute': field_name}})

                except ValueError as e:
                    errors.append({'error_type': 'invalid_rule', 'tokens': {'message': str(e)}})
        return errors
    

    @staticmethod
    def _is_valid_email(email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(email_regex, email) is not None