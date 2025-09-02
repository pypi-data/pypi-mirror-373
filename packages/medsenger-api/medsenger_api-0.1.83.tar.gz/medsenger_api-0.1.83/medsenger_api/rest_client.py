from copy import copy
import requests
from datetime import datetime


class RestApiClient:
    def __init__(self, api_key, host="https://medsenger.ru", agent_id=None, debug=False, locale=None):
        self.host = host
        self.api_key = api_key
        self.debug = debug
        self.agent_id = agent_id
        self.locale = locale

    def __gts__(self):
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S - ")

    def __send_request__(self, page, json_params):
        target = self.host + page
        try:
            if self.debug:
                if len(str(json_params)) > 400:
                    print(self.__gts__(), "Sending request to {} with params {}".format(target, str(json_params)[:200]))
                else:
                    print(self.__gts__(), "Sending request to {} with params {}".format(target, json_params))

            result = requests.post(target, json=json_params)

            if result.status_code != 200:
                raise Exception('status code - {}'.format(result.status_code))

            if self.debug:
                if len(result.text) > 400:
                    print(self.__gts__(), "Result - {}...".format(result.text[:200]))
                else:
                    print(self.__gts__(), "Result - {}".format(result.text))

            try:
                return result.json()
            except:
                return result.text
        except Exception as e:
            print(self.__gts__(), "Error in {} - {}".format(target, e))
            return None

    def get_categories(self):
        data = {
            "api_key": self.api_key,
        }

        return self.__send_request__('/api/agents/records/categories', data) or []

    def get_available_categories(self, contract_id):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
        }

        return self.__send_request__('/api/agents/records/available_categories', data) or []

    def get_patient_info(self, contract_id):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
        }

        return self.__send_request__('/api/agents/patient/info', data) or {
            'name': '',
            'sex': '',
            'birthday': ''
        }

    def get_clinics_info(self):
        data = {
            "api_key": self.api_key,
        }

        return self.__send_request__('/api/agents/clinics', data) or []

    def get_records(self, contract_id, category_name=None, time_from=None, time_to=None, limit=None, offset=None,
                    group=False, return_count=False, inner_list=False):

        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
        }

        if self.locale:
            data["locale"] = self.locale

        if category_name:
            data["category_name"] = category_name

        full_list = not category_name or ',' in category_name or inner_list

        if limit:
            data['limit'] = limit
        if offset:
            data['offset'] = offset
        if time_from:
            data['from'] = time_from
        if time_to:
            data['to'] = time_to
        if group:
            if full_list:
                data['same_group'] = True
            else:
                data['last_group'] = True
        if return_count:
            data['return_count'] = True

        if full_list:
            url = "/api/agents/records/get/all"
        else:
            url = "/api/agents/records/get"

        return self.__send_request__(url, data) or None

    def get_record_by_id(self, contract_id, record_id):

        data = {
            "contract_id": contract_id,
            "record_id": record_id,
            "api_key": self.api_key,
        }

        return self.__send_request__("/api/agents/records/get", data) or None

    def add_hooks(self, contract_id, names):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "categories": names
        }

        return self.__send_request__("/api/agents/hooks/add", data)

    def remove_hooks(self, contract_id, names):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "categories": names
        }

        return self.__send_request__("/api/agents/hooks/remove", data)

    def send_addition(self, contract_id, record_id, addition):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "record_id": record_id,
            "addition": addition,
        }

        return self.__send_request__('/api/agents/records/addition', data)

    def add_record(self, contract_id, category_name, value, record_time=None, params=None, files=None, return_id=False,
                   replace=False):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "category_name": category_name,
            "value": value,
            "replace": replace
        }

        if params:
            data['params'] = params

        if record_time:
            data['time'] = record_time

        if files:
            data['files'] = files

        if return_id:
            data['return_id'] = True

        return self.__send_request__('/api/agents/records/add', data)

    def delete_record(self, contract_id, record_id):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "record_id": record_id,
        }

        return self.__send_request__('/api/agents/records/delete', data)

    def set_classifier(self, contract_id, code):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "code": code,
        }

        return self.__send_request__('/api/agents/classifier', data)

    def add_records(self, contract_id, values, record_time=None, params={}, return_id=False):
        data = {"contract_id": contract_id, "api_key": self.api_key, 'values': []}

        for record in values:
            category_name = None
            value = None
            record_params = copy(params)
            current_record_time = record_time
            files = []
            custom_params = {}
            should_replace = False

            if isinstance(record, (list, tuple)):
                if len(record) == 2:
                    category_name, value = record
                else:
                    category_name, value, custom_params = record

            elif isinstance(record, dict):
                category_name = record['category_name']
                value = record['value']
                custom_params = record.get('params', {})
                files = record.get('files', [])
                should_replace = record.get('replace', False)

            if "record_time" in custom_params:
                current_record_time = custom_params['record_time']
                del custom_params['record_time']

            record_params.update(custom_params)

            data['values'].append(
                {"category_name": category_name, "value": value, "params": record_params, "files": files,
                 "time": current_record_time, "replace": should_replace})

        if return_id:
            data['return_id'] = True

        return self.__send_request__('/api/agents/records/add', data)

    def send_message(self, contract_id, text, action_link=None, action_name=None, action_onetime=True,
                     only_doctor=False,
                     only_patient=False, action_deadline=None, is_urgent=False, need_answer=False,
                     attachments=None, action_big=True, send_from=None, forward_to_doctor=True, action_type='action'):
        message = {
            "text": text,
            "forward_to_doctor": forward_to_doctor
        }

        if action_link:
            message['action_link'] = action_link

        if send_from:
            message['send_from'] = send_from

        if action_name:
            message['action_name'] = action_name

        if action_onetime:
            message['action_onetime'] = action_onetime

        if action_big:
            message['action_big'] = action_big

        if action_type:
            message['action_type'] = action_type

        if only_doctor:
            message['only_doctor'] = only_doctor

        if need_answer:
            message['need_answer'] = need_answer

        if only_patient:
            message['only_patient'] = only_patient

        if action_deadline:
            message['action_deadline'] = action_deadline

        if is_urgent:
            message['is_urgent'] = is_urgent

        if attachments:
            message['attachments'] = []

            for attachment in attachments:
                if isinstance(attachment, (list, tuple)):
                    message['attachments'].append({
                        "name": attachment[0],
                        "type": attachment[1],
                        "base64": attachment[2],
                    })
                elif isinstance(attachment, (dict)):
                    message['attachments'].append(attachment)

        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "message": message
        }

        return self.__send_request__('/api/agents/message', data)

    def outdate_message(self, contract_id, message_id):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "message_id": message_id,
        }

        return self.__send_request__('/api/agents/message/outdate', data)

    def finish_task(self, contract_id, task_id):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "task_id": task_id,
        }

        return self.__send_request__('/api/agents/tasks/done', data)

    def delete_task(self, contract_id, task_id):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "task_id": task_id,
        }

        return self.__send_request__('/api/agents/tasks/delete', data)

    def add_task(self, contract_id, text, target_number=1, date=None, important=False, action_link=None):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "text": text,
            "number": target_number,
            "important": important
        }

        if date:
            data['date'] = date

        if action_link:
            data['action_link'] = action_link

        return self.__send_request__('/api/agents/tasks/add', data)

    def request_payment(self, contract_id, inv_id, amount, title):
        data = {
            "api_key": self.api_key,
            "title": title,
            "inv_id": inv_id,
            "sum": amount,
            "contract_id": contract_id
        }

        return self.__send_request__('/api/agents/payments/request', data)

    def get_payments(self, contract_id):
        data = {
            "api_key": self.api_key,
            "contract_id": contract_id
        }

        return self.__send_request__('/api/agents/payments', data).get('payments')

    def send_order(self, contract_id, order, receiver_id=None, params=None):
        data = {
            "contract_id": contract_id,
            "api_key": self.api_key,
            "order": order,
        }

        if receiver_id:
            data['receiver_id'] = receiver_id

        if params:
            data['params'] = params

        return self.__send_request__('/api/agents/order', data)

    def get_agent_token(self, contract_id):
        data = {
            "api_key": self.api_key,
            "contract_id": contract_id
        }

        return self.__send_request__('/api/agents/token', data)

    def get_file(self, contract_id, file_id):
        data = {
            "api_key": self.api_key,
            "file_id": file_id,
            "contract_id": contract_id
        }

        return self.__send_request__('/api/agents/records/file', data)

    def get_attachment(self, attachment_id):
        data = {
            "api_key": self.api_key,
            "attachment_id": attachment_id
        }

        return self.__send_request__('/api/agents/attachment', data)

    def get_image(self, image_id, size):
        data = {
            "api_key": self.api_key,
            "attachment_id": image_id,
            "size": size
        }

        return self.__send_request__('/api/agents/image', data)

    def get_messages(self, contract_id, from_id=0):
        data = {
            "api_key": self.api_key,
            "from_id": from_id,
            "contract_id": contract_id
        }

        answer = self.__send_request__('/api/agents/messages', data)

        if answer and isinstance(answer, dict):
            return answer.get('messages')
        return []

    def update_cache(self, contract_id):
        data = {
            "api_key": self.api_key,
            "contract_id": contract_id
        }

        return self.__send_request__('/api/agents/cache', data)

    def set_info_materials(self, contract_id, materials):
        data = {
            "api_key": self.api_key,
            "contract_id": contract_id,
            "info_materials": materials
        }

        return self.__send_request__('/api/agents/info_materials/set', data)

    def set_contract_param(self, contract_id, name, value):
        data = {
            "api_key": self.api_key,
            "contract_id": contract_id,
            "name": name,
            "value": value
        }

        return self.__send_request__('/api/agents/set_contract_param', data)

    def notify_admin(self, message, channel="it"):
        data = {
            "api_key": self.api_key,
            "message": message,
            "channel": channel
        }

        return self.__send_request__('/api/agents/notify_admin', data)
