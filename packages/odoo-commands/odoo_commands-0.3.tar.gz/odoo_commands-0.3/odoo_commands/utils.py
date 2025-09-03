import odoo

SUPERUSER_ID = 1


def create_env(database, user_id=SUPERUSER_ID, context=None):
    cr = odoo.registry(database).cursor()
    return odoo.api.Environment(cr, user_id, context or {})
