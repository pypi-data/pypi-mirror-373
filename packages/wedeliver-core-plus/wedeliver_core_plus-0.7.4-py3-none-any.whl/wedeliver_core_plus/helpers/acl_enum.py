

class Permission():
    # the below should be unique for each permission
    admin_permission = "admin_permission" # TODO this is will be removed later, we added to test the admin role
    # invoice
    invoice_create = "invoice_create"
    invoice_reviewer = "invoice_reviewer"

    #report
    report_create = "report_create"
    report_reviewer = "report_reviewer"



class OpsRole():
    permission = [Permission.invoice_create]

class FinanceRole():
    permission = [Permission.invoice_reviewer]


class adminRole():
    #this to add all the above permissions into the adminRole as a list of permissions
    def props(cls):
        return [i for i in cls.__dict__.keys() if i[:1] != '_']

    permission = props(Permission)




print(adminRole.permission)
#TODO
# 1
#  need to add the roles to the database later