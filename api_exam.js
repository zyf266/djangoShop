import request from "../utils/request.js";

export  function getExamList(){
    return request({
        url:'exam/exams/',
        method:'get'
    });
}

export function startExam(examId){
    return request({
        url:'exam/records/',
        method:'post',
        data:{exam_id:examId}
    });
}

export function getExamRecord(recordId){
    return request({
        url:`exam/records/${recordId}/`,
        method:'get'
    })
}
export const saveAnswers = (recordId, answers) => {
  // 将 recordId 拼接在 URL 路径中
  // 请求体是 answers 数组
  return request.post(`exam/records/${recordId}/save_answers/`, answers);
};

export const finishExam = (recordId) => {
  return request.post(`exam/records/${recordId}/finish/`);
};

export function getExamResult(recordId){
    return request({
        url:`exam/results/${recordId}/`,
        method:'get'
    });
}
