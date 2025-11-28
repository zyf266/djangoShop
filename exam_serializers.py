from rest_framework import serializers
from exam.models import Question, Exam, AnswerRecord, ExamRecord

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model=Question
        fields = ['id', 'content', 'question_type', 'options', 'answer', 'score']

class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Exam
        fields = ['id', 'title', 'description', 'time_limit', 'total_score',
                  'created_time', 'questions']

class AnswerRecordSerializer(serializers.ModelSerializer):
    question=QuestionSerializer(read_only=True)
    question_id=serializers.IntegerField(write_only=True)
    class Meta:
        model=AnswerRecord
        fields=["id","question","question_id","user_answer","is_correct","score"]

class ExamRecordSerializer(serializers.ModelSerializer):
    exam=ExamSerializer(read_only=True)
    exam_id=serializers.IntegerField(write_only=True)
    # 关键修复：添加 source 指定反向关联的 AnswerRecord 集合
    answer_records=AnswerRecordSerializer(
        source='answerrecord_set',  # 对应 AnswerRecord 模型的 exam_record 外键反向关联名
        many=True,
        read_only=True
    )
    class Meta:
        model=ExamRecord
        fields=["id","exam_id","start_time","end_time","status","score","answer_records","exam"]
        read_only_fields=['start_time','end_time','status','score']
