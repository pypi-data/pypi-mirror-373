from wbcore.metadata.configs.titles import TitleViewConfig

from wbcrm.models.accounts import Account


class AccountTitleConfig(TitleViewConfig):
    def get_instance_title(self):
        return "Account: {{title}}"

    def get_list_title(self):
        return "Accounts"


class ChildAccountAccountTitleConfig(TitleViewConfig):
    def get_list_title(self):
        account = Account.all_objects.get(id=self.view.kwargs["account_id"])
        return f"{account.title}: Sub Accounts"


class AccountRoleAccountTitleConfig(TitleViewConfig):
    def get_list_title(self):
        account = Account.all_objects.get(id=self.view.kwargs["account_id"])
        return f"Roles for Account {str(account)}"
