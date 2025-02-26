import LLM_bots
import load_balancer
import vector_storage
import message_bot


if __name__ == "__main__":
    error_flag = False
    try:
        llmbot = LLM_bots.Llm_bot(url="localhost", port=1234)
    except:
        error_flag = True
        print("Ошибка подключения к LLM")
    try:
        database = vector_storage.VecStorage(url="localhost", server_port=6333)
    except:
        error_flag = True
        print("Ошибка инициализации Qdrant (скорее всего не запущен сервер)")

    if not error_flag:
        load_dispatcher = load_balancer.LoadBalancer(
            llm_bot=llmbot, vec_storage=database
        )
        msg_bot = message_bot.initialize_and_run(load_dispatcher)
