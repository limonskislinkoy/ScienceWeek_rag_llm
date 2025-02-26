from LLM_bots import Llm_bot
from vector_storage import VecStorage


class LoadBalancer:
    def __init__(self, llm_bot: Llm_bot, vec_storage: VecStorage):
        # NOTE: WorkInProgress

        self.llm_bot = llm_bot
        self.vec_storage = vec_storage

    def test_request(self, request: str) -> str:
        rag_info = str(self.vec_storage.get_best_results(request, count=3))
        print(rag_info)
        answer = self.llm_bot.create_request_to_llm(request, rag_info)
        return answer

    def test_load_file(self, file_path: str) -> None:
        self.vec_storage.add_text_file(file_path)
