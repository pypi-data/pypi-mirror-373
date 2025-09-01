class Process:
    def __init__(self):
        self.query_info = None
        self.error_info = None

    def data_process(self, q_data, e_data):
        fields = {
            'query': q_data.query,
            'res_headers': q_data.res_headers,
            'res_cookies': q_data.res_cookies,
            'response': q_data.response,
            'status_code': q_data.status_code,
            'res_type': q_data.res_type
        }
        self.query_info = {k: v for k, v in fields.items() if v}

        if e_data:
            self.error_info = dict(msg_dict=e_data.msg_dict)