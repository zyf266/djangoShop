from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from exam.models import Exam, ExamRecord, Question, AnswerRecord
from exam.serializers import ExamSerializer, ExamRecordSerializer


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    """考试列表和详情"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class ExamRecordViewSet(viewsets.ModelViewSet):
    """考试记录：开始考试、提交答案、完成考试"""
    queryset = ExamRecord.objects.all()
    serializer_class = ExamRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 只返回当前用户的考试记录
        return ExamRecord.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """开始考试:创建一条考试记录"""
        exam_id = request.data.get("exam_id")
        if not exam_id:
            return Response({"error": "exam_id 不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查考试是否存在（避免传入无效的 exam_id）
        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({"error": "指定的考试不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 检查是否已有未完成的记录
        ongoing_record = ExamRecord.objects.filter(
            user=request.user,
            exam=exam,  # 修正：用 exam 实例（外键字段）过滤，而非 exam_id
            status='ongoing'
        ).first()
        if ongoing_record:
            return Response(ExamRecordSerializer(ongoing_record).data)

        # 创建新考试记录（修正：若 ExamRecord 字段是 exam（外键），直接传 exam 实例）
        record = ExamRecord.objects.create(
            user=request.user,
            exam=exam  # 关键修正：替换 exam_id=exam_id 为 exam=exam
        )

        # 初始化答题记录（修正：Question 查询条件用 exam=exam，而非 exam_id=exam_id）
        questions = Question.objects.filter(exam=exam)
        for question in questions:
            AnswerRecord.objects.create(
                exam_record=record,
                question=question
            )

        return Response(ExamRecordSerializer(record).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def save_answers(self, request, pk=None):
        """保存答案(不提交)"""
        record = self.get_object()

        # 检查考试状态
        if record.status == 'completed':
            return Response({"error": "考试已完成，无法保存答案"}, status=status.HTTP_400_BAD_REQUEST)

        # 获取答案列表，增加格式校验
        answers = request.data.get('answers', [])
        if not isinstance(answers, list):
            return Response({"error": "answers 必须是列表格式"}, status=status.HTTP_400_BAD_REQUEST)

        # 批量保存答案，优化数据库操作
        updated_count = 0
        for ans in answers:
            # 校验每个答案的必填字段
            question_id = ans.get("question_id")
            user_answer = ans.get("user_answer", "").strip()  # 去除首尾空格

            if not question_id:
                continue  # 跳过缺少 question_id 的答案

            try:
                # 只更新当前考试记录的答题记录
                answer_record = AnswerRecord.objects.get(
                    exam_record=record,
                    question_id=question_id
                )
                # 只有当答案变化时才保存，减少数据库写入
                if answer_record.user_answer != user_answer:
                    answer_record.user_answer = user_answer
                    answer_record.save()
                    updated_count += 1
            except AnswerRecord.DoesNotExist:
                # 忽略不存在的答题记录（可能是非法的 question_id）
                continue

        return Response({
            "message": f"成功保存 {updated_count} 条答案",
            "updated_count": updated_count
        })

    @action(detail=True, methods=["post"])
    def finish(self, request, pk=None):
        """完成考试并评分"""
        record = self.get_object()

        # 检查考试状态
        if record.status == 'completed':
            return Response({"error": "考试已完成，无需重复提交"}, status=status.HTTP_400_BAD_REQUEST)

        # 更新考试状态和结束时间
        record.status = 'completed'
        record.end_time = timezone.now()

        # 自动评分逻辑（核心修正：ar.user.answer → ar.user_answer）
        total_score = 0
        answer_records = AnswerRecord.objects.filter(exam_record=record)

        for ar in answer_records:
            # 初始化得分和正确性
            ar.is_correct = False
            ar.score = 0

            # 获取用户答案和正确答案（统一转为小写对比，避免大小写问题）
            user_answer = ar.user_answer.strip().lower() if ar.user_answer else ""
            correct_answer = ar.question.answer.strip().lower() if ar.question.answer else ""

            # 不同题型的评分规则
            if ar.question.question_type == 'multiple':
                # 多选题：按逗号分割后排序对比（确保顺序不影响结果）
                user_answers = sorted([a.strip() for a in user_answer.split(',') if a.strip()])
                correct_answers = sorted([a.strip() for a in correct_answer.split(',') if a.strip()])
                if user_answers == correct_answers:
                    ar.is_correct = True
                    ar.score = ar.question.score
            else:
                # 单选题/判断题：直接对比答案
                if user_answer == correct_answer:
                    ar.is_correct = True
                    ar.score = ar.question.score

            ar.save()
            total_score += ar.score

        # 保存总分
        record.score = total_score
        record.save()

        return Response(ExamRecordSerializer(record).data)


class ExamRecordView(generics.RetrieveAPIView):
    """查看考试结果"""
    queryset = ExamRecord.objects.filter(status='completed')
    serializer_class = ExamRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ExamRecord.objects.filter(user=self.request.user, status='completed')


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
