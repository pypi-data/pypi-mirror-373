import json
import time

from medsenger_api import AgentApiClient, prepare_file
from unittest import TestCase
from tests.config import *


class TestApi(TestCase):
    grpc_client = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True, True, 'localhost', sentry_dsn=DSN)
    default_client = AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True, False)

    def test_get_categories(self):
        assert self.grpc_client.get_categories() == self.default_client.get_categories()

    def test_get_available_categories(self):
        G = self.grpc_client.get_available_categories(CONTRACT_ID)
        D = self.default_client.get_available_categories(CONTRACT_ID)

        for a, b in zip(G, D):
            if a != b:
                print("a: ", a)
                print("b: ", b)

        assert G == D



    def test_get_records(self):

        S = time.time()
        G = self.grpc_client.get_records(CONTRACT_ID, "systolic_pressure")
        print("G time:", time.time() - S)

        S = time.time()
        D = self.default_client.get_records(CONTRACT_ID, "systolic_pressure")
        print("D time:", time.time() - S)

        for a, b in zip(G['values'], D['values']):
            if a != b:
                print("a: ", a)
                print("b: ", b)

        assert G == D

    def test_get_records_with_group(self):
        S = time.time()
        G = self.grpc_client.get_records(CONTRACT_ID, "systolic_pressure,pulse", limit=3, group=True)
        print("G time:", time.time() - S)

        S = time.time()
        D = self.default_client.get_records(CONTRACT_ID, "systolic_pressure,pulse", limit=3, group=True)
        print("D time:", time.time() - S)

        print(G, '\n\n', D)

        assert G == D

    def test_get_records_from_multiple_categories(self):
        S = time.time()
        G = self.grpc_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", limit=20)
        print("G time:", time.time() - S)

        S = time.time()
        D = self.default_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", limit=20)
        print("D time:", time.time() - S)

        print("records count:", len(D))

        assert G == D

    def test_get_records_from_multiple_categroies_with_offset(self):
        S = time.time()
        G = self.grpc_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", offset=100, limit=100)
        print("G time:", time.time() - S)

        S = time.time()
        D = self.default_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", offset=100, limit=100)
        print("D time:", time.time() - S)


        print(type(G), type(D))

        for a, b in zip(G, D):
            if a != b:
                print("a: ", a)
                print("b: ", b)

        assert G == D

    def test_get_records_from_multiple_categories_with_time(self):
        T = int(time.time() - 2 * 30 * 24 * 60 * 60)
        F = int(time.time() - 3 * 30 * 24 * 60 * 60)

        S = time.time()
        G = self.grpc_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", time_from=F, time_to=T)
        print("G time:", time.time() - S)

        S = time.time()
        D = self.default_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", time_from=F, time_to=T)
        print("D time:", time.time() - S)


        print(type(G), type(D))

        if D and G:
            for a, b in zip(G, D):
                if a != b:
                    print("a: ", a)
                    print("b: ", b)

        assert G == D

    def test_multiple_get_records(self):
        T = int(time.time() - 2 * 30 * 24 * 60 * 60)
        F = int(time.time() - 3 * 30 * 24 * 60 * 60)

        query_1 = dict(contract_id=CONTRACT_ID, category_name="systolic_pressure,diastolic_pressure,pulse")
        query_2 = dict(contract_id=CONTRACT_ID, category_name="pulse")

        G = self.grpc_client.get_multiple_records([query_1, query_2])

        print(G)

    def test_count_records(self):
        S = time.time()
        G = self.grpc_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", return_count=True)
        print("G time:", time.time() - S)

        S = time.time()
        D = self.default_client.get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure,pulse", return_count=True)
        print("D time:", time.time() - S)

        assert G == D

    def test_get_single_record(self):
        record = self.default_client.add_record(CONTRACT_ID, "pulse", 60, return_id=True)

        D = self.default_client.get_record_by_id(CONTRACT_ID, record[0])
        G = self.grpc_client.get_record_by_id(CONTRACT_ID, record[0])

        print(D, G)

        assert D == G

    def test_get_single_record_404(self):
        record = self.default_client.add_record(CONTRACT_ID, "pulse", 60, return_id=True)

        D = self.default_client.get_record_by_id(CONTRACT_ID, record[0] + 1)
        G = self.grpc_client.get_record_by_id(CONTRACT_ID, record[0] + 1)

        print(D, G)

        assert D == G