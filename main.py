# import os
# import queue
# import time
# from threading import Thread

# from debug import inspect_queue

# NUM_WORKERS = 3
# POISON_PILL = object()
# POLL_INTERVAL = 0.1
# LOG_PATH = "app.log"

# def reader(path, q, running_flag) -> None:
#     try:
#         with open(path, 'r', encoding='utf-8') as file:
#             file.seek(0, 2)
#             while running_flag:
#                 line = file.readline()
#                 if not line:
#                     # Ждем новые данные
#                     time.sleep(POLL_INTERVAL)  
#                     continue

#                 q.put(line.rstrip("\n"))
#                 print(inspect_queue(q))

#     except FileNotFoundError:
#         print("Файл не найден!")
#     except UnicodeDecodeError:
#         print("Ошибка кодировки! Попробуйте другую кодировку.")

# def worker(worker_id, q, stats, running_flag):
#     while running_flag:
#         item = q.get()
#         if item is POISON_PILL:   
#             q.task_done()
#             break
#         else:
#             if "ERROR" in item: 
#                 print(f"[ALERT] Ошибка: {item}")
#             else:
#                 print(f"[INFO] {item}")
#             q.task_done()
# def main():
#     running_flag = True
#     q = queue.Queue()
#     stats = {"total": 0, "errors": 0}
#     try:
#         reader_thread = Thread(target=reader, args=(LOG_PATH, q, running_flag), daemon=True)
#         reader_thread.start()
           
#     except KeyboardInterrupt:
#         print("\nПолучен сигнал Ctrl+C")
#         running_flag = False
        
#     finally:
#         # Код очистки (выполняется ВСЕГДА)
#         print("Выполняем очистку...")
#         reader_thread.join()
#         # Закрываем ресурсы, останавливаем потоки и т.д.
    
# if __name__ == "__main__": 
#     main()
#     print("Программа завершена корректно")

import os
import queue
import time
from threading import Thread

from debug import inspect_queue

NUM_WORKERS = 3
POISON_PILL = object()
POLL_INTERVAL = 0.1
LOG_PATH = "app.log"

def reader(path, q, running_flag) -> None:
    try:
        with open(path, 'r', encoding='utf-8') as file:
            file.seek(0, 2)
            while running_flag[0]:  
                line = file.readline()
                if not line:
                    time.sleep(POLL_INTERVAL)  
                    continue

                q.put(line.rstrip("\n"))
                # print(inspect_queue(q))  # Убрал для чистоты вывода

    except FileNotFoundError:
        print("Файл не найден!")
    except UnicodeDecodeError:
        print("Ошибка кодировки! Попробуйте другую кодировку.")

def worker(worker_id, q, stats, running_flag):
    while running_flag[0]: 
        try:
            item = q.get(timeout=1.0)  
            if item is POISON_PILL:   
                q.task_done()
                break
            else:
                if "ERROR" in item: 
                    print(f"[ALERT Worker-{worker_id}] Ошибка: {item}")
                    stats["errors"] += 1
                else:
                    print(f"[INFO Worker-{worker_id}] {item}")
                stats["total"] += 1
                q.task_done()
        except queue.Empty:
            continue  

def main():
    running_flag = [True] 
    q = queue.Queue()
    stats = {"total": 0, "errors": 0}

    workers = []
    for i in range(NUM_WORKERS):
        w = Thread(target=worker, args=(i, q, stats, running_flag), daemon=True)
        w.start()
        workers.append(w)
    
    reader_thread = Thread(target=reader, args=(LOG_PATH, q, running_flag), daemon=True)
    reader_thread.start()
    
    print("Система запущена. Нажмите Ctrl+C для остановки")
    
    try:
        while running_flag[0]:
            time.sleep(0.5)  
            
    except KeyboardInterrupt:
        print("\nПолучен сигнал Ctrl+C")
        running_flag[0] = False  
        
    finally:
        print("Выполняем очистку...")
        
        # Отправляем POISON_PILL каждому воркеру
        for _ in range(NUM_WORKERS):
            q.put(POISON_PILL)
        
        time.sleep(1)
        
        print(f"Финальная статистика: Всего {stats['total']} сообщений, ошибок {stats['errors']}")
        print("Программа завершена корректно")

if __name__ == "__main__": 
    main()