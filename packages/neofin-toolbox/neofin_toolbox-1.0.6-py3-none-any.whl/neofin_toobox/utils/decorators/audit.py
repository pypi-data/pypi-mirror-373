from datetime import datetime, timezone, timedelta
from functools import wraps

from neofin_toobox.repositories.audit_repository import AuditRepository


def save(**kwargs_dec):
    def save_decorator(f):
        @wraps(f)
        def wrapper_save(*args, **kwargs):
            print('------- {} - audit ------'.format(f.__name__))
            try:
                app = kwargs_dec.get('app')

                json_body = app.current_request.json_body or {}
                pk = json_body.get(kwargs_dec.get('entity_pk'))

                due_date = ''
                if not pk:
                    if 'first_due_date' in json_body:
                        due_date = int(json_body.get('first_due_date'))
                    elif 'due_date' in json_body:
                        due_date = int(json_body.get('due_date'))
                    if len(str(due_date)) > 10:
                        due_date = int(due_date / 1000)
                    customer_document = ''.join(d for d in json_body.get('customer_document', '') if d.isdigit())
                    user_id = app.current_request.context.get('authorizer', {}).get('claims', {}).get(
                        'cognito:username')
                    pk = '{}#{}#{}'.format(user_id, customer_document, str(due_date))

                now = datetime.now(tz=timezone(timedelta(hours=-3))).isoformat(timespec='seconds')

                to_save = {
                    'resource': '{}#{}'.format(kwargs_dec.get('entity'), pk),
                    'date': '{}#{}#{}'.format(now, f.__name__, app.current_request.method),
                    'username': app.current_request.context.get('authorizer', {}).get('claims', {}).get(
                        'cognito:username'),
                    'request_json': json_body,
                    'request_dict': app.current_request.to_dict()
                }

                audit_repository = AuditRepository()
                audit_repository.put_item(to_save)

            except Exception as e:
                print(('save_audit', 'exception', f.__name__, e))
                return f(*args, **kwargs)
            else:
                return f(*args, **kwargs)

        return wrapper_save

    return save_decorator