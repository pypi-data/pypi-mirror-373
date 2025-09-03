import logging
from functools import wraps

from chalice import Response

from neofin_toobox.exceptions.decorators.auth_exceptions import MissingUserException, MissingRoleException, \
    PermissionException
from neofin_toobox.repositories.roles_repository import RolesRepository
from neofin_toobox.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


def check(**kwargs_dec):
    def check_decorator(f):
        @wraps(f)
        def wrapper_check(*args, **kwargs):
            logger.info(f'Starting authorization check for function: {f.__name__}')
            try:
                app = kwargs_dec.get('app')

                user_id = app.current_request.context.get('authorizer', {}).get('claims', {}).get('cognito:username')

                if not user_id:
                    logger.error('User ID is missing from request context')
                    raise MissingUserException(message='User ID is missing from request context')

                user_repository = UserRepository()
                roles_repository = RolesRepository()

                logger.info(f'Retrieving user data for user_id: {user_id}')
                user_result = user_repository.get_user_by_id(user_id)

                if not (role_id := user_result.get('role_id')):
                    logger.error('Role ID not found in user data')
                    raise MissingRoleException(message='Role ID not found in user data')

                logger.info(f'Retrieving role permissions for role_id: {role_id}')
                role_result = roles_repository.get_role_by_id(role_id)

                role = role_result.get('perms')
                perm_list = kwargs_dec.get('perm_list')

                logger.debug(f'Checking permissions: {perm_list} against role permissions: {role}')
                for perm in perm_list:
                    entity, action = perm.split('/')
                    if action in role.get(entity, []):
                        logger.info(f'Access granted for permission: {perm}')
                        return f(*args, **kwargs)

                logger.warning(f'Required permissions not found in user role. Required: {perm_list}, Available: {role}')
                raise PermissionException(message='Required permissions not found in user role')

            except (MissingUserException, MissingRoleException, PermissionException) as auth_error:
                logger.error(f'Authorization error in {f.__name__}: {type(auth_error).__name__} - {auth_error}')
                raise auth_error
            except Exception as exc:
                logger.exception(f'Unexpected error in {f.__name__}: {type(exc).__name__} - {str(exc)}')
                raise exc

        return wrapper_check

    return check_decorator