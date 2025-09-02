import json
import time
import grpc
from .utils import *
from .protocol import records_pb2_grpc as pb2_grpc
from .protocol import records_pb2 as pb2
from .certificates import CERTTIFICATE


class RecordsClient(object):
    def __get_method__(self, method, stub):
        if method == 'GetCategoryList':
            return stub.GetCategoryList
        elif method == 'GetCategoryListForUser':
            return stub.GetCategoryListForUser
        elif method == 'GetRecordById':
            return stub.GetRecordById
        elif method == 'GetRecords':
            return stub.GetRecords
        elif method == 'CountRecords':
            return stub.CountRecords
        elif method == 'GetMultipleRecords':
            return stub.GetMultipleRecords
        else:
            return None

    def __create_connection__(self):
        if self.channel:
            if self.__debug:
                print("Closing GRPC connection")

            self.channel.close()

        if self.__debug:
            print("Connecting to GRPC...")

        credentials = grpc.ssl_channel_credentials(root_certificates=CERTTIFICATE)

        # instantiate a channel
        self.channel = grpc.secure_channel(
            '{}:{}'.format(self.host, self.server_port), credentials, options=[
                ('grpc.max_send_message_length', 50 * 1024 * 1024),
                ('grpc.max_receive_message_length', 50 * 1024 * 1024),
                ('grpc.keepalive_time_ms', 10000),
                ('grpc.keepalive_timeout_ms', 5000),
                ('grpc.keepalive_permit_without_calls', True),
                ('grpc.http2.max_pings_without_data', 0),
                ('grpc.http2.min_time_between_pings_ms', 10000),
                ('grpc.http2.min_ping_interval_without_data_ms', 5000)
            ])

        # bind the client and the server
        self.stub = pb2_grpc.RecordsStub(self.channel)

        if self.__debug:
            print("Connected to GRPC")

    def reconnect(self):
        self.__create_connection__()

    def __connect_if_should(self):
        if not self.channel:
            self.__create_connection__()

    def __close_connection__(self):
        self.channel.close()

    def __init__(self, debug=False, host=None, api_key=None, locale=None):
        if not host:
            host = "medsenger.ru"

        self.host = host
        self.server_port = 50051
        self.__categories_by_id = {}
        self.__categories_by_name = {}

        self.__debug = debug
        self.channel = None
        self.api_key = api_key
        self.locale = locale

    def __find_category_by_id(self, id):
        if not self.__categories_by_id or id not in self.__categories_by_id:
            print("Loading categories")
            self.get_categories()

        categories = self.__categories_by_id.get(id)

        if not categories:
            return None

        if self.locale:
            result = [category for category in categories if category.locale == self.locale]
            if result:
                return result[0]

        return categories[0]

    def __find_category_by_name(self, name):
        if not self.__categories_by_name or name not in self.__categories_by_name:
            print("Loading categories")
            self.get_categories()

        categories = self.__categories_by_name.get(name)

        if not categories:
            return None

        if self.locale:
            result = [category for category in categories if category.locale == self.locale]
            if result:
                return result[0]

        return categories[0]

    def __find_ids_for_categories(self, category_names):
        if not self.__categories_by_name:
            print("Loading categories")
            self.get_categories()

        result = set()

        for name in category_names:
            for category in self.__categories_by_name[name]:
                result.add(category.id)

        return list(result)

    def __present_category(self, category):
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "unit": category.unit,
            "type": category.type,
            "default_representation": category.default_representation,
            "is_legacy": category.is_legacy,
            "doctor_can_add": category.doctor_can_add,
            "doctor_can_replace": category.doctor_can_replace,
            "subcategory": category.subcategory if category.subcategory else None,
            "locale": category.locale if category.locale else None
        }

    def __present_file(self, file):
        return {
            "id": file.id,
            "name": file.name,
            "type": file.type,
        }

    def __convert_value(self, value, category):
        if category.type == 'integer':
            return int(float(value.replace(',', '.')))
        if category.type == 'float':
            return round(float(value.replace(',', '.')), 3)
        return value

    def __present_record(self, record, with_category=False):
        category = self.__find_category_by_id(record.category_id)

        presentation = {
            "id": record.id,
            "value": self.__convert_value(record.value, category),
            "timestamp": record.created_at,
            "uploaded": record.updated_at,
            "source": {
                "id": record.source.id if record.source.id else None,
                "name": record.source.name
            },
            "group": record.group if record.group else None,
            "params": json.loads(record.params),
            "additions": json.loads(record.additions),
            "attached_files": [self.__present_file(file) for file in record.attached_files],
        }

        if with_category:
            presentation['category_info'] = self.__present_category(category)

        return presentation

    def __make_request(self, method, *args, timeout=20, tries=3):
        self.__connect_if_should()

        if self.__debug:
            print(gts(), " GRPC request to {} with params {} and locale {}".format(method, args, self.locale))

        exception = None
        for i in range(tries):
            try:
                F = self.__get_method__(method, self.stub)

                if F:
                    return F(*args, timeout=timeout, metadata=[('authorization', self.api_key)])
                else:
                    raise Exception("Wrong method")
            except grpc.RpcError as e:
                print("Exception in GRPC request: ", e)

                if e.code() == grpc.StatusCode.NOT_FOUND:
                    return None
                else:
                    exception = e

                    time.sleep(tries)

                    self.__create_connection__()

                    if self.__debug:
                        print("Retrying request... {}".format(i + 1))

        print("Request failed!")
        raise GrpcConnectionError("GRPC request error to {} with params {}: {}".format(method, args, exception))

    @safe
    def get_categories(self):
        request = pb2.Empty()

        result = self.__make_request('GetCategoryList', request)

        categories = []

        for category in result.categories:
            if category.id not in self.__categories_by_id:
                self.__categories_by_id[category.id] = []
            if category.name not in self.__categories_by_name:
                self.__categories_by_name[category.name] = []

            self.__categories_by_id[category.id].append(category)
            self.__categories_by_name[category.name].append(category)

            categories.append(self.__present_category(category))

        if self.locale:
            categories = [category for category in categories if category['locale'] == self.locale]

        return categories

    @safe
    def get_categories_for_user(self, user_id):
        request = pb2.User(id=user_id)

        result = self.__make_request('GetCategoryListForUser', request)

        categories = []
        for category in result.categories:
            if self.locale and category.locale != self.locale:
                continue
            categories.append(self.__present_category(category))
        return categories

    @safe
    def get_record_by_id(self, record_id):
        request = pb2.RecordRequest(id=record_id)

        record = self.__make_request('GetRecordById', request)

        if record:
            return self.__present_record(record)
        else:
            return None

    def __prepare_record_query(self, user_id, category_name, time_from, time_to, offset, limit, group,
                               inner_list=False):
        category_names = category_name.split(',')
        category_ids = self.__find_ids_for_categories(category_names)

        if category_names and not category_ids:
            if self.__debug:
                print("Category search failed:", category_names, self.__categories_by_name.keys())

            return None, 0

        if time_from is not None:
            time_from = int(time_from)

        if time_to is not None:
            time_to = int(time_to)

        if offset is not None:
            offset = int(offset)

        if limit is not None:
            limit = int(limit)

        return pb2.RecordQuery(user_id=user_id, category_ids=category_ids, from_timestamp=time_from,
                               to_timestamp=time_to, offset=offset, limit=limit, with_group=group)

    def __present_record_query_answer(self, answer, category_name, full_list=False):
        records = None
        if full_list:
            if answer.records:
                records = [self.__present_record(record, with_category=True) for record in answer.records]
        else:
            if answer.records:
                records = {
                    "category": self.__present_category(self.__find_category_by_name(category_name)),
                    "values": [self.__present_record(record, with_category=False) for record in answer.records]
                }

        return records, answer.count

    def __aggregate_records(self, method, user_id, category_name, time_from=0, time_to=int(time.time()),
                            offset=0,
                            limit=None, group=False, inner_list=False):
        full_list = not category_name or ',' in category_name or inner_list

        request = self.__prepare_record_query(user_id, category_name, time_from, time_to, offset, limit, group)
        result = self.__make_request(method, request)

        return self.__present_record_query_answer(result, category_name, full_list)

    def get_records(self, user_id, category_name, time_from=0, time_to=int(time.time()), offset=0,
                    limit=None, group=False, inner_list=False):

        records, count = self.__aggregate_records('GetRecords', user_id, category_name, time_from,
                                                  time_to,
                                                  offset, limit, group, inner_list)
        return records

    def get_multiple_records(self, queries):
        prepared_queries = [self.__prepare_record_query(**query) for query in queries]
        request = pb2.MultiRecordQuery(queries=prepared_queries)

        result = self.__make_request('GetMultipleRecords', request)
        answers = []
        for i in range(len(queries)):
            category_name = queries[i]['category_name']
            full_list = not category_name or ',' in category_name or queries[i]['inner_list']
            answers.append(self.__present_record_query_answer(result.answers[i], category_name, full_list)[0])

        return answers

    def count_records(self, user_id, category_name, time_from=0, time_to=int(time.time()), offset=0,
                      limit=None, group=False, inner_list=False):

        records, count = self.__aggregate_records('CountRecords', user_id, category_name, time_from,
                                                  time_to,
                                                  offset, limit, group, inner_list)

        return {"count": count}
