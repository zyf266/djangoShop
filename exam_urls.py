from django.urls import include, path
from rest_framework.routers import DefaultRouter

from exam.views import ExamViewSet, ExamRecordView,ExamRecordViewSet

from exam.views import CustomAuthToken



router=DefaultRouter()
router.register(r'exams',ExamViewSet)
router.register(r'records', ExamRecordViewSet, basename='examrecord')

urlpatterns=[
    path('',include(router.urls)),
    path('results/<int:pk>/',ExamRecordView.as_view(),name='exam-result'),
    path('token/',CustomAuthToken.as_view(),name='api_token_auth'),
  # 1. 保存答案 (对应 finish 方法)
    # 注意：这里我们复用了 'examrecord' 这个 basename
    path('records/<int:pk>/finish/',
         ExamRecordViewSet.as_view({'post': 'finish'}),
         name='examrecord-finish'),

    # 2. 完成考试 (对应 save_answers 方法)
    path('records/<int:pk>/save_answers/',
         ExamRecordViewSet.as_view({'post': 'save_answers'}),
         name='examrecord-save-answers'),
]
