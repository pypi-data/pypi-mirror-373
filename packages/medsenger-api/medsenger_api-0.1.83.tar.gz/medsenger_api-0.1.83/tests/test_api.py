from medsenger_api import AgentApiClient, prepare_file
from unittest import TestCase
from tests.config import *

class TestApi(TestCase):

    def create_client(self):
        return AgentApiClient(API_KEY, MAIN_HOST, AGENT_ID, True)

    def test_patient_info(self):
        print(self.create_client().get_patient_info(CONTRACT_ID))

    def test_get_categories(self):
        print(self.create_client().get_categories())

    def test_get_available_categories(self):
        print(self.create_client().get_available_categories(CONTRACT_ID))

    def test_get_records(self):
        print(self.create_client().get_records(CONTRACT_ID, "systolic_pressure"))

    def test_get_records_from_multiple_categroies(self):
        records = self.create_client().get_records(CONTRACT_ID, "systolic_pressure,diastolic_pressure", inner_list=True, group=False)

        for record in records:
            print(record['category_info']['name'], record.get('group'))

    def test_send_message_with_attachments(self):
        client = self.create_client()
        client.send_message(contract_id=CONTRACT_ID, text='', attachments=[prepare_file('.gitignore')], send_from='patient')

    def test_outdate_message(self):
        client = self.create_client()
        messsage = client.send_message(contract_id=CONTRACT_ID, text='', attachments=[prepare_file('.gitignore')],
                            send_from='patient')

        client.outdate_message(CONTRACT_ID, messsage['id'])



    def test_add_record_with_file(self):
        client = self.create_client()

        result = client.add_record(CONTRACT_ID, 'systolic_pressure', value=120, files=[prepare_file('test_api.py')])
        print(result)

    def test_get_file(self):
        client = self.create_client()

        result = client.get_file(CONTRACT_ID, 4)

        print(result)

    def test_clinics_info(self):
        client = self.create_client()

        print(client.get_clinics_info())

    def test_add_record_with_id_returns_ids(self):
        client = self.create_client()

        result = client.add_record(CONTRACT_ID, 'systolic_pressure', value=120, return_id=True)

        print(result)

        id = result[0]

        print(client.get_record_by_id(CONTRACT_ID, id))

    def test_delete_record(self):
        client = self.create_client()

        result = client.add_record(CONTRACT_ID, 'systolic_pressure', value=120, return_id=True)
        id = result[0]
        client.delete_record(CONTRACT_ID, id)

        assert client.get_record_by_id(CONTRACT_ID, id) == None

    def test_get_messsages(self):
        client = self.create_client()

        print(client.get_messages(CONTRACT_ID))

    def test_set_classifier(self):
        client = self.create_client()

        client.set_classifier(CONTRACT_ID, "unstandart")

    def test_set_contract_param(self):
        client = self.create_client()

        client.set_contract_param(CONTRACT_ID, "param", "value")

    def test_remove_contract_param(self):
        client = self.create_client()

        client.set_contract_param(CONTRACT_ID, "param", "")

