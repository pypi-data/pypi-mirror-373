import time

from medsenger_api import AgentApiClient, prepare_file
from unittest import TestCase
from tests.config import *

class TestReplace(TestCase):

    def create_client(self):
        return AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True, True, 'localhost')

    def test_single_record_replace(self):
        client = self.create_client()
        initial = client.get_records(CONTRACT_ID, "swimming_freestyle_50")
        print("initial:", len(initial['values']))

        client.add_record(CONTRACT_ID, "swimming_freestyle_50", 10)
        client.add_record(CONTRACT_ID, "swimming_freestyle_50", 15)
        print("adding two records:", len(client.get_records(CONTRACT_ID, "swimming_freestyle_50")['values']))
        client.add_record(CONTRACT_ID, "swimming_freestyle_50", 25, replace=True)
        print("after replace:", len(client.get_records(CONTRACT_ID, "swimming_freestyle_50")['values']) )

    def test_single_record_replace_with_classifier(self):
        client = self.create_client()
        initial = client.get_records(CONTRACT_ID, "swimming_freestyle_50")
        print("initial:", len(initial['values']))

        client.add_record(CONTRACT_ID, "swimming_freestyle_50", 10)
        client.add_record(CONTRACT_ID, "swimming_freestyle_50", 15, params={'record_classifier': 'A'})
        print("adding two records:", len(client.get_records(CONTRACT_ID, "swimming_freestyle_50")['values']))
        client.add_record(CONTRACT_ID, "swimming_freestyle_50", 25, params={'record_classifier': 'A'}, replace=True)
        time.sleep(1)
        print("after replace:", len(client.get_records(CONTRACT_ID, "swimming_freestyle_50")['values']) )

