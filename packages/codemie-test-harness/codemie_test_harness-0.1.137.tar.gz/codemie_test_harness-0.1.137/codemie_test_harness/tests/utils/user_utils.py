from codemie_test_harness.tests.utils.base_utils import BaseUtils


class UserUtils(BaseUtils):
    def get_about_me(self):
        return self.client.users.about_me()

    def get_user_data(self):
        return self.client.users.get_data()
