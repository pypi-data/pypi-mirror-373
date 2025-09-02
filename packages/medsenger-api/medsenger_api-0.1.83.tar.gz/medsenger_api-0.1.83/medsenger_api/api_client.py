import time
from .utils import gts
from .grpc_client import RecordsClient
from .rest_client import RestApiClient

try:
    import sentry_sdk
except:
    pass


class AgentApiClient:
    def __init__(self, api_key, host="https://medsenger.ru", agent_id=None, debug=False, use_grpc=False,
                 grpc_host=None, sentry_dsn=None, locale=None):

        self.rest_client = RestApiClient(api_key, host, agent_id, debug, locale=locale)
        self.grpc_client = None
        self.user_cache = {}
        self.categories_cache = {}
        self.debug = debug
        self.dsn = sentry_dsn
        self.locale = locale

        self.categories = []
        self.categories_last_request = 0

        if use_grpc:
            self.grpc_client = RecordsClient(host=grpc_host, debug=debug, api_key=api_key, locale=locale)

        if self.dsn:
            sentry_sdk.init(dsn=self.dsn, traces_sample_rate=1.0)

    def set_locale(self, locale):
        self.locale = locale
        self.rest_client.locale = locale
        if self.grpc_client:
            self.grpc_client.locale = locale

    def get_categories(self):
        if self.categories and time.time() - self.categories_last_request < 60:
            return self.categories

        self.categories_last_request = time.time()

        if self.grpc_client:
            try:
                self.categories = self.grpc_client.get_categories()

                for category in self.categories:
                    self.categories_cache[category['name']] = category

                return self.categories
            except Exception as e:
                if self.dsn:
                    sentry_sdk.capture_exception(e)
                print(gts(), "GRPC failed with error:", e)

        self.categories = self.rest_client.get_categories()

        if self.locale:
            self.categories = [category for category in self.categories if category['locale'] == self.locale]

        return self.categories

    def reconnect(self):
        if self.grpc_client:
            self.grpc_client.reconnect()

    def get_available_categories(self, contract_id):
        if self.grpc_client:
            try:
                if contract_id not in self.user_cache:
                    self.get_patient_info(contract_id)

                if contract_id in self.user_cache:
                    return self.grpc_client.get_categories_for_user(self.user_cache[contract_id])

                return []
            except Exception as e:
                if self.dsn:
                    sentry_sdk.capture_exception(e)
                print(gts(), "GRPC failed with error:", e)

        categories = self.rest_client.get_available_categories(contract_id)

        if self.locale:
            categories = [category for category in categories if category['locale'] == self.locale]

        return categories

    def get_patient_info(self, contract_id):
        result = self.rest_client.get_patient_info(contract_id)

        if self.debug:
            print(result)

        if result.get('id'):
            self.user_cache[contract_id] = result.get('id')

        return result

    def get_clinics_info(self):
        return self.rest_client.get_clinics_info()

    def __prepare_query_for_grpc(self, contract_id, category_name=None, time_from=None, time_to=None, limit=None,
                                 offset=None,
                                 group=False, inner_list=False, user_id=None):

        print("Preparing q for gprc request in api client:", (contract_id, category_name, time_from, time_to, limit, offset, group, inner_list, user_id))
        if contract_id not in self.user_cache and not user_id:
            self.get_patient_info(contract_id)

        if not user_id:
            user_id = self.user_cache[contract_id]

        return dict(user_id=user_id, category_name=category_name, time_from=time_from, time_to=time_to, offset=offset, limit=limit, group=group, inner_list=inner_list)

    def get_multiple_records(self, queries):
        if self.grpc_client:
            try:
                prepared_queries = [self.__prepare_query_for_grpc(**query) for query in queries]
                return self.grpc_client.get_multiple_records(prepared_queries)
            except Exception as e:
                if self.dsn:
                    sentry_sdk.capture_exception(e)
                print(gts(), "GRPC for multiple records failed with error:", e)

        return [self.get_records(**query) for query in queries]

    def get_records(self, contract_id, category_name=None, time_from=None, time_to=None, limit=None, offset=None,
                    group=False, return_count=False, inner_list=False, user_id=None):

        if self.grpc_client:
            try:
                if return_count:
                    method = self.grpc_client.count_records
                else:
                    method = self.grpc_client.get_records

                return method(
                    **self.__prepare_query_for_grpc(contract_id, category_name, time_from, time_to, limit, offset, group,
                                                   inner_list, user_id))
            except Exception as e:
                if self.dsn:
                    sentry_sdk.capture_exception(e)
                print(gts(), "GRPC failed with error:", e)

        return self.rest_client.get_records(contract_id, category_name, time_from, time_to, limit, offset, group,
                                            return_count, inner_list)

    def get_record_by_id(self, contract_id, record_id):
        if self.grpc_client:
            try:
                return self.grpc_client.get_record_by_id(record_id)
            except Exception as e:
                if self.dsn:
                    sentry_sdk.capture_exception(e)
                print(gts(), "GRPC failed with error:", e)

        return self.rest_client.get_record_by_id(contract_id, record_id)

    def add_hooks(self, contract_id, names):
        return self.rest_client.add_hooks(contract_id, names)

    def set_classifier(self, contract_id, code):
        return self.rest_client.set_classifier(contract_id, code)

    def remove_hooks(self, contract_id, names):
        return self.rest_client.remove_hooks(contract_id, names)

    def send_addition(self, contract_id, record_id, addition):
        return self.rest_client.send_addition(contract_id, record_id, addition)

    def add_record(self, contract_id, category_name, value, record_time=None, params=None, files=None, return_id=False,
                   replace=False):
        return self.rest_client.add_record(contract_id, category_name, value, record_time, params, files, return_id,
                                           replace)

    def delete_record(self, contract_id, record_id):
        return self.rest_client.delete_record(contract_id, record_id)

    def add_records(self, contract_id, values, record_time=None, params={}, return_id=False):
        return self.rest_client.add_records(contract_id, values, record_time, params, return_id)

    def send_message(self, contract_id, text, action_link=None, action_name=None, action_onetime=True,
                     only_doctor=False,
                     only_patient=False, action_deadline=None, is_urgent=False, need_answer=False,
                     attachments=None, action_big=True, send_from=None, forward_to_doctor=True, action_type='action'):
        return self.rest_client.send_message(contract_id, text, action_link, action_name, action_onetime,
                                             only_doctor,
                                             only_patient, action_deadline, is_urgent, need_answer,
                                             attachments, action_big, send_from, forward_to_doctor, action_type)

    def outdate_message(self, contract_id, message_id):
        return self.rest_client.outdate_message(contract_id, message_id)

    def finish_task(self, contract_id, task_id):
        return self.rest_client.finish_task(contract_id, task_id)

    def delete_task(self, contract_id, task_id):
        return self.rest_client.delete_task(contract_id, task_id)

    def add_task(self, contract_id, text, target_number=1, date=None, important=False, action_link=None):
        return self.rest_client.add_task(contract_id, text, target_number, date, important, action_link)

    def request_payment(self, contract_id, inv_id, amount, title):
        return self.rest_client.request_payment(contract_id, inv_id, amount, title)

    def get_payments(self, contract_id):
        return self.rest_client.get_payments(contract_id)

    def send_order(self, contract_id, order, receiver_id=None, params=None):
        return self.rest_client.send_order(contract_id, order, receiver_id, params)

    def get_agent_token(self, contract_id):
        return self.rest_client.get_agent_token(contract_id)

    def download_file(self, *args, **kwargs):
        return self.get_file(*args, **kwargs)

    def download_attachment(self, *args, **kwargs):
        return self.get_attachment(*args, **kwargs)

    def download_image(self, *args, **kwargs):
        return self.get_image(*args, **kwargs)

    def get_file(self, contract_id, file_id):
        return self.rest_client.get_file(contract_id, file_id)

    def get_attachment(self, attachment_id):
        return self.rest_client.get_attachment(attachment_id)

    def get_image(self, image_id, size):
        return self.rest_client.get_image(image_id, size)

    def update_cache(self, contract_id):
        return self.rest_client.update_cache(contract_id)

    def set_info_materials(self, contract_id, materials):
        return self.rest_client.set_info_materials(contract_id, materials)

    def set_contract_param(self, contract_id, name, value):
        return self.rest_client.set_contract_param(contract_id, name, value)

    def ajax_url(self, action, contract_id, agent_token):
        # TODO fix
        return self.host.replace('8001',
                                 '8000') + "/api/client/agents/{agent_id}/?action={action}&contract_id={contract_id}&agent_token={agent_token}".format(
            agent_id=self.agent_id, action=action, contract_id=contract_id, agent_token=agent_token
        )

    def get_messages(self, contract_id, from_id=0):
        return self.rest_client.get_messages(contract_id, from_id)

    def notify_admin(self, message, channel="it"):
        return self.rest_client.notify_admin(message, channel)
