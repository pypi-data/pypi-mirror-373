from medsenger_api import AgentApiClient, prepare_file
from unittest import TestCase
from tests.config import *

class TestPayment(TestCase):

    def create_client(self):
        return AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True)

    def test_request_payment(self):
        print(self.create_client().request_payment(CONTRACT_ID, "test_1", 100, "Test payment"))

    def test_get_all_payments(self):
        print(self.create_client().get_payments(CONTRACT_ID))

