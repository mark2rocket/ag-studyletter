"""
자동화 스케줄러
- 매주 월요일 오전 9시 자동 발송
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StudyLetterScheduler:
    """논문 요약 자동 발송 스케줄러"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        logger.info("스케줄러가 시작되었습니다.")
    
    def add_weekly_job(self, job_func, schedule_id, keyword, email):
        """
        매주 월요일 오전 9시 작업 추가
        
        Args:
            job_func: 실행할 함수
            schedule_id: 스케줄 ID
            keyword: 검색 키워드
            email: 수신 이메일
        """
        job_id = f"schedule_{schedule_id}"
        
        # 기존 작업이 있으면 제거
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
        
        # 매주 월요일 오전 9시에 실행
        trigger = CronTrigger(
            day_of_week='mon',  # 월요일
            hour=9,             # 오전 9시
            minute=0,
            timezone='Asia/Seoul'
        )
        
        self.scheduler.add_job(
            job_func,
            trigger=trigger,
            args=[schedule_id, keyword, email],
            id=job_id,
            name=f"Weekly digest: {keyword} → {email}",
            replace_existing=True
        )
        
        logger.info(f"자동화 작업 추가됨: {keyword} → {email} (매주 월요일 09:00)")
    
    def remove_job(self, schedule_id):
        """작업 제거"""
        job_id = f"schedule_{schedule_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            logger.info(f"자동화 작업 제거됨: schedule_{schedule_id}")
    
    def get_jobs(self):
        """모든 작업 조회"""
        return self.scheduler.get_jobs()
    
    def shutdown(self):
        """스케줄러 종료"""
        self.scheduler.shutdown()
        logger.info("스케줄러가 종료되었습니다.")


# 전역 스케줄러 인스턴스
_scheduler_instance = None


def get_scheduler():
    """스케줄러 싱글톤 인스턴스 반환"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = StudyLetterScheduler()
    return _scheduler_instance
