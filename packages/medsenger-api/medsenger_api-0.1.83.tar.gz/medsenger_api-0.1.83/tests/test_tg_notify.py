from medsenger_api import AgentApiClient, prepare_file
from unittest import TestCase
from tests.config import *

class TestPayment(TestCase):

    def create_client(self):
        return AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True)

    def test_admin_notify(self):
        print(self.create_client().notify_admin("hello from medsenger api tests"))

