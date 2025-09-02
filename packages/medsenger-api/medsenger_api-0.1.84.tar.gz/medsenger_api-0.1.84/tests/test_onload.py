import json
import time

from medsenger_api import AgentApiClient, prepare_file
from unittest import TestCase
from tests.config import *


class TestApi(TestCase):
    grpc_client = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True, True, 'localhost')

    def test_get_records_from_multiple_categories(self):
        for i in range(1):

            S = time.time()
            G = self.grpc_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse")
            print("G time:", time.time() - S)