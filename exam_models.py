from django.db import models
from django.contrib.auth.models import User
import json


class Question(models.Model):
    """题目模型"""
    QUESTION_TYPES = (
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('judge', '判断题'),
    )
    content = models.TextField('题目内容')
    question_type = models.CharField('题型', max_length=10, choices=QUESTION_TYPES)
    options = models.JSONField('选项', help_text="单选题/多选题格式: {'A': '选项1', 'B': '选项2'}, 判断题无需填写")
    answer = models.CharField('答案', max_length=100, help_text="多选题答案用逗号分隔，如'A,B'；判断题用'True'/'False'")
    score = models.PositiveIntegerField('分值', default=5)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return f"{self.get_question_type_display()}: {self.content[:20]}"


class Exam(models.Model):
    """试卷模型"""
    title = models.CharField('考试名称', max_length=200)
    description = models.TextField('考试描述', blank=True)
    questions = models.ManyToManyField(Question, verbose_name='包含题目')
    time_limit = models.PositiveIntegerField('考试时长(分钟)', default=60)
    total_score = models.PositiveIntegerField('总分', default=100)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """自动计算总分（所有题目分数之和）"""
        if self.questions.exists():
            self.total_score = sum(q.score for q in self.questions.all())
        super().save(*args, **kwargs)


class ExamRecord(models.Model):
    """考试记录模型"""
    STATUS_CHOICES = (
        ('ongoing', '进行中'),
        ('completed', '已完成'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='考生')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='试卷')
    start_time = models.DateTimeField('开始时间', auto_now_add=True)
    end_time = models.DateTimeField('结束时间', null=True, blank=True)
    status = models.CharField('状态', max_length=10, choices=STATUS_CHOICES, default='ongoing')
    score = models.PositiveIntegerField('得分', default=0)

    def __str__(self):
        return f"{self.user.username}的{self.exam.title}记录"


class AnswerRecord(models.Model):
    """答题记录模型"""
    exam_record = models.ForeignKey(ExamRecord, on_delete=models.CASCADE, verbose_name='考试记录')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='题目')
    user_answer = models.CharField('用户答案', max_length=100, blank=True)
    is_correct = models.BooleanField('是否正确', default=False)
    score = models.PositiveIntegerField('得分', default=0)

    class Meta:
        unique_together = ('exam_record', 'question')  # 同一考试中同一题目只能有一条记录
