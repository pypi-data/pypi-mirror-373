import json

from mtkresearch.llm.prompt import MRPromptV3


class TestMRPromptV3:
    prompt = MRPromptV3(
    )
    functions = [
        {
            'name': 'get_current_weather',
            'description': 'Get the current_weather',
            'parameters': {
                'type': 'object',
                'properties': {
                    'location': {
                        'type': 'string',
                        'description': 'The city and state, e.g. San Francisco, CA'
                    },
                    'unit': {
                        'type': 'string',
                        'enum': ['celsius', 'fahrenheit']
                    }
                },
                'required': ['location']
            }
        }
    ]

    def test_chat_case1(self): # sys + query
        conversations = [
            {
                "role": "system",
                "content": "SYS"
            },
            {
                "role": "user",
                "content": "QUERY1"
            }
        ]
        result = self.prompt.get_prompt(conversations, add_bos_token=True, training=True)
        assert result == (
            '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nSYS<|eot_id|>'
            '<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>'
            '<|start_header_id|>assistant<|end_header_id|>\n\n'
        )

    def test_chat_case2(self): # sys + query + response
        conversations = [
            {
                "role": "system",
                "content": "SYS"
            },
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "content": "RESPONSE1"
            },
        ]
        result = self.prompt.get_prompt(conversations, add_bos_token=True, training=True)
        assert result == (
            '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nSYS<|eot_id|>'
            '<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>'
            '<|start_header_id|>assistant<|end_header_id|>\n\nRESPONSE1<|eot_id|>'   
        )

    def test_chat_case3(self): # query + response + query
        conversations = [
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "content": "RESPONSE1"
            },
            {
                "role": "user",
                "content": "QUERY2"
            }
        ]
        result = self.prompt.get_prompt(conversations, add_bos_token=True, training=True)
        assert result == (
            '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful AI assistant.<|eot_id|>'
            '<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>'
            '<|start_header_id|>assistant<|end_header_id|>\n\nRESPONSE1<|eot_id|>'
            '<|start_header_id|>user<|end_header_id|>\n\nQUERY2<|eot_id|>'
            '<|start_header_id|>assistant<|end_header_id|>\n\n'
        )

    def test_func_case1(self): # sys + query + f_call

        conversations = [
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "reason": "REASON",
                "tool_calls": [
                    {
                        'id': 'call_8jLWqlXaY3OisD24IHJLwD3G',
                        'type': 'function',
                        'function': {
                            'arguments': "{\"location\": \"Boston, MA\"}",
                            'name': 'get_current_weather'
                        }
                    }]
            },
        ]
        result = self.prompt.get_prompt(conversations, self.functions, add_bos_token=True, training=True)
        assert result == (            
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCustomized Functions: [{'name': 'get_current_weather', 'description': 'Get the current_weather', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string', "
            "'description': 'The city and state, e.g. San Francisco, CA'}, 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}}, 'required': ['location']}}]\n\n---\n"
            "You are a helpful assistant.<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|use_tool|>[get_current_weather(location='Boston, MA')]<|eot_id|>"
        )

    def test_func_case2(self): # sys + query + f_call + f_response
        conversations = [
            {
                "role": "system",
                "content": "SYS"
            },
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        'id': 'call_8jLWqlXaY3OisD24IHJLwD3G',
                        'type': 'function',
                        'function': {
                            'arguments': "{\"location\": \"Boston, MA\"}",
                            'name': 'get_current_weather'
                        }
                    }]
            },
            {
                "role": "tool",
                "tool_call_id": "call_8jLWqlXaY3OisD24IHJLwD3G",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22 celsius\"}"
            },
        ]
        result = self.prompt.get_prompt(conversations, self.functions, add_bos_token=True, training=True)
        assert result == (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCustomized Functions: [{'name': 'get_current_weather', 'description': 'Get the current_weather', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string', "
            "'description': 'The city and state, e.g. San Francisco, CA'}, 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}}, 'required': ['location']}}]\n\n---\n"
            "SYS<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|python_tag|>[get_current_weather(location='Boston, MA')]<|eom_id|>"
            "<|start_header_id|>ipython<|end_header_id|>\n\n[{'temperature': '22 celsius'}]<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

    def test_func_case3(self): # sys + query + f_call + f_response + response + query
        conversations = [
            {
                "role": "system",
                "content": "SYS"
            },
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        'id': 'call_8jLWqlXaY3OisD24IHJLwD3G',
                        'type': 'function',
                        'function': {
                            'arguments': "{\"location\": \"Boston, MA\"}",
                            'name': 'get_current_weather'
                        }
                    }]
            },
            {
                "role": "tool",
                "tool_call_id": "call_8jLWqlXaY3OisD24IHJLwD3G",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22 celsius\"}"
            },
            {
                "role": "assistant",
                "content": "RESP1"
            }
        ]
        result = self.prompt.get_prompt(conversations, self.functions, add_bos_token=True, training=True)
        assert result == (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCustomized Functions: [{'name': 'get_current_weather', 'description': 'Get the current_weather', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string', "
            "'description': 'The city and state, e.g. San Francisco, CA'}, 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}}, 'required': ['location']}}]\n\n---\n"
            "SYS<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|python_tag|>[get_current_weather(location='Boston, MA')]<|eom_id|>"
            "<|start_header_id|>ipython<|end_header_id|>\n\n[{'temperature': '22 celsius'}]<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|answer|>RESP1<|eot_id|>"
        )

    def test_func_case4(self): # sys + query + response + query + f_call
        conversations = [
            {
                "role": "system",
                "content": "SYS"
            },
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "content": "RESP1"
            },
            {
                "role": "user",
                "content": "QUERY2"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        'id': 'call_8jLWqlXaY3OisD24IHJLwD3G',
                        'type': 'function',
                        'function': {
                            'arguments': "{\"location\": \"Boston, MA\"}",
                            'name': 'get_current_weather'
                        }
                    }]
            },
        ]
        result = self.prompt.get_prompt(conversations, self.functions, add_bos_token=True, training=True)
        assert result == (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCustomized Functions: [{'name': 'get_current_weather', 'description': 'Get the current_weather', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string', "
            "'description': 'The city and state, e.g. San Francisco, CA'}, 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}}, 'required': ['location']}}]\n\n---\n"
            "SYS<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\nRESP1<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nQUERY2<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|use_tool|>[get_current_weather(location='Boston, MA')]<|eot_id|>"
        )

    def test_func_case5(self): # query + f_call(2)
        conversations = [
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        'type': 'function',
                        'function': {
                            'arguments': "{\"location\": \"Boston, MA\"}",
                            'name': 'get_current_weather'
                        }
                    },
                    {
                        'type': 'function',
                        'function': {
                            'arguments': "{\"location\": \"Taipei, Taiwan\"}",
                            'name': 'get_current_weather'
                        }
                    }]
            },
        ]
        result = self.prompt.get_prompt(conversations, self.functions, add_bos_token=True, training=True)
        assert result == (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCustomized Functions: [{'name': 'get_current_weather', 'description': 'Get the current_weather', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string', "
            "'description': 'The city and state, e.g. San Francisco, CA'}, 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}}, 'required': ['location']}}]\n\n---\n"
            "You are a helpful AI assistant.<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|use_tool|>[get_current_weather(location='Boston, MA'),get_current_weather(location='Taipei, Taiwan')]<|eot_id|>"
        )

    def test_func_case6(self): # query + f_call(2) + f_response(2)
        conversations = [
            {
                "role": "user",
                "content": "QUERY1"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        'type': 'function',
                        'id': 'ID1',
                        'function': {
                            'arguments': "{\"location\": \"Boston, MA\"}",
                            'name': 'get_current_weather'
                        }
                    },
                    {
                        'type': 'function',
                        'id': 'ID2',
                        'function': {
                            'arguments': "{\"location\": \"Taipei, Taiwan\"}",
                            'name': 'get_current_weather'
                        }
                    }]
            },
            {
                "role": "tool",
                "tool_call_id": "ID1",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22 celsius\"}"
            },
            {
                "role": "tool",
                "tool_call_id": "ID2",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"31 celsius\"}"
            },
        ]
        result = self.prompt.get_prompt(conversations, self.functions, add_bos_token=True, training=True)
        assert result == (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCustomized Functions: [{'name': 'get_current_weather', 'description': 'Get the current_weather', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string', "
            "'description': 'The city and state, e.g. San Francisco, CA'}, 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}}, 'required': ['location']}}]\n\n---\n"
            "You are a helpful AI assistant.<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\nQUERY1<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|python_tag|>[get_current_weather(location='Boston, MA'),get_current_weather(location='Taipei, Taiwan')]<|eom_id|>"
            "<|start_header_id|>ipython<|end_header_id|>\n\n[{'temperature': '22 celsius'}, {'temperature': '31 celsius'}]<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

    def test_func_tc(self): # sys + query + f_call + f_response + response + query
        conversations = [
            {
                "role": "system",
                "content": "系統"
            },
            {
                "role": "user",
                "content": "問1"
            },
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        'id': 'call_8jLWqlXaY3OisD24IHJLwD3G',
                        'type': 'function',
                        'function': {
                            'arguments': "{\"location\": \"波士頓\"}",
                            'name': 'get_current_weather'
                        }
                    }]
            },
            {
                "role": "tool",
                "tool_call_id": "call_8jLWqlXaY3OisD24IHJLwD3G",
                "name": "get_current_weather",
                "content": "{\"temperature\": \"22 度c\"}"
            },
            {
                "role": "assistant",
                "content": "答1"
            },
            {
                "role": "user",
                "content": "問2"
            },
        ]
        result = self.prompt.get_prompt(conversations, self.functions, add_bos_token=True, training=True)
        assert result == (
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nCustomized Functions: [{'name': 'get_current_weather', 'description': 'Get the current_weather', 'parameters': {'type': 'object', 'properties': {'location': {'type': 'string', "
            "'description': 'The city and state, e.g. San Francisco, CA'}, 'unit': {'type': 'string', 'enum': ['celsius', 'fahrenheit']}}, 'required': ['location']}}]\n\n---\n"
            "系統<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n問1<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n<|python_tag|>[get_current_weather(location='波士頓')]<|eom_id|>"
            "<|start_header_id|>ipython<|end_header_id|>\n\n[{'temperature': '22 度c'}]<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n答1<|eot_id|>"
            "<|start_header_id|>user<|end_header_id|>\n\n問2<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\n"
        )

    def test_parse_generated_str(self):
        generated_str = '<|answer|>RESP1<|eot_id|>'
        assert self.prompt.parse_generated_str(generated_str) == {
            'role': 'assistant',
            'content': 'RESP1'
        }

        generated_str = "<|use_tool|>[get_ans(determine=True),get_current_weather(location='Taipei, Taiwan')]<|eot_id|>"
        conv = self.prompt.parse_generated_str(generated_str)
        
        print(conv)
        assert conv['role'] == 'assistant'
        assert conv['tool_calls'][0]['type'] == 'function'
        assert conv['tool_calls'][0]['function']['name'] == 'get_ans'
        print(conv['tool_calls'][0]['function']['arguments'])
        assert json.loads(conv['tool_calls'][0]['function']['arguments']) == {'determine': True}
        assert conv['tool_calls'][1]['type'] == 'function'
        assert conv['tool_calls'][1]['function']['name'] == 'get_current_weather'
        assert json.loads(conv['tool_calls'][1]['function']['arguments']) == {"location": "Taipei, Taiwan"}

    def test_parse_generated_str_case2(self):
        generated_str = "<|use_tool|>[get.ans(determine=True)]<|eot_id|>"
        conv = self.prompt.parse_generated_str(generated_str)
        
        print(conv)
        assert conv['role'] == 'assistant'
        assert conv['tool_calls'][0]['type'] == 'function'
        assert conv['tool_calls'][0]['function']['name'] == 'get.ans'
        print(conv['tool_calls'][0]['function']['arguments'])
        assert json.loads(conv['tool_calls'][0]['function']['arguments']) == {'determine': True}

    def test_parse_generated_str_case3(self):
        generated_str = "<|use_tool|>[get  ans(determine=True), get.ans(determine=True)]<|eot_id|>"
        conv = self.prompt.parse_generated_str(generated_str)
        
        print(conv)
        assert conv['tool_calls'][0]['function']['name'] == 'get  ans'
        assert conv['tool_calls'][1]['function']['name'] == 'get.ans'

    def test_chat_with_image_case1(self): # sys + query_with_image
        conversations = [
            {
                "role": "system",
                "content": "SYS"
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "ABC"
                    },
                    {
                        "type": "image",
                        "image_path": "./tests/test_img.png",
                    },
                    {
                        "type": "bbox",
                        "width": 1024,
                        "height": 768,
                        "coords": [[0, 0, 512, 384]]
                    }
                ]
            }
        ]
        result, pixel_values = self.prompt.get_prompt(conversations, add_bos_token=True, training=True)
        expected_patch_size = 1
        assert pixel_values.size(0) == expected_patch_size
    
        image_content_token_num = 256 * (1 + expected_patch_size)
        image_content_str = ''.join(['<|img|>'] * image_content_token_num)
        assert result == (
            '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nSYS<|eot_id|>'
            f"<|start_header_id|>user<|end_header_id|>\n\nABC<|start_img|>{image_content_str}<|end_img|>\n"
            "<|start_bbox|>[[0, 0, 500, 500]]<|end_bbox|><|eot_id|>"
            '<|start_header_id|>assistant<|end_header_id|>\n\n'
        )

    def test_chat_with_image_case2(self): # sys + query + response_with_bbox
        conversations = [
            {
                "role": "system",
                "content": "SYS"
            },
            {
                "role": "user",
                "content": 'query'
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "ABC"
                    },
                    {
                        "type": "bbox",
                        "width": 1024,
                        "height": 768,
                        "coords": [[0, 0, 512, 384]]
                    }
                ]
            }
        ]
        result = self.prompt.get_prompt(conversations, add_bos_token=True, training=True)
        assert result == (
            '<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nSYS<|eot_id|>'
            f"<|start_header_id|>user<|end_header_id|>\n\nquery<|eot_id|>"
            "<|start_header_id|>assistant<|end_header_id|>\n\nABC<|start_bbox|>[[0, 0, 500, 500]]<|end_bbox|><|eot_id|>"
        )
