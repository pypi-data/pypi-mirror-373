from app.core.celery import celery_app
from main import main

@celery_app.task(bind=True)
def paper_assistant(task, keyword, search_paper_num):
    """
        celery异步任务
    """
    data = main(task, keyword, search_paper_num)
    return data
