
def is_employee(user):
    return  hasattr(user, 'employee')

def is_client(user):
    return hasattr(user, 'client')