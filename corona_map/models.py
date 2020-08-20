from django.db import models

# 수녕- 전국 현황 데이터 모델
'''
확진자 수 : decidecnt
격리해제 수 : clearcnt
검사진행 수 : examcnt
사망자 수 : deathcnt
'''
class NationStatus(models.Model):
    # 확진자 수
    decidecnt = models.IntegerField
    # 격리해제 수
    clearcnt = models.IntegerField
    # 검사진행 수
    examcnt = models.IntegerField
    # 사망자 수
    deathcnt = models.IntegerField