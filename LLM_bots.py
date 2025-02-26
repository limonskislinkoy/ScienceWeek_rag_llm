import openai


class Llm_bot:
    def __init__(self, url="localhost", port=43678):
        self.llm_client = openai.OpenAI(
            base_url=f"http://{url}:{port}/v1", api_key="lm-studio"
        )

    def create_request_to_llm(self, user_query: str, rag_data="") -> str:
        system_promt = """
        Ты интелектуальный помощник. При формировании ответа на вопрос используй информацию из блока "Проверенная информация",
        если же в этом блоке нет необходимой информации, то предупреди об этом пользователя,
        если ты ТОЧНО уверен, что ты знаешь ответ, то напиши его, но обязательно укажи,
        что эти знания взяты не из базы знаний, но ни в коем случае НЕ ПЫТАЙСЯ ВЫДУМАТЬ ИНФОРМАЦИЮ
        """
        prompt = (
            f"Проверенная информация:{rag_data}\nПользовательский вопрос: {user_query}"
        )
        try:
            response = self.llm_client.chat.completions.create(
                model="mistral-nemo-instruct-2407",
                messages=[
                    {"role": "system", "content": system_promt},
                    {"role": "user", "content": prompt},
                ],
            )
            return str(response.choices[0].message.content)
        except:
            print("System is overloaded or something crashed at llm-server side")
            return "Произошла ошибка, попробуйте еще раз позже!"
