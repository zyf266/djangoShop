import axios  from "axios";
import {useCookies} from 'vue3-cookies';
const {cookies}=useCookies();


const service=axios.create({
    baseURL: "http://127.0.0.1:8000/api",  //后端api地址
    timeout: 5000,
    headers:{
        'Content-Type':'application/json'
    },
      withCredentials: true  // 关键：允许跨域请求携带 Cookie
});
//添加请求拦截器(处理CSRF Token)
service.interceptors.request.use(
    config=>{
        const csrfToken=document.cookie.match(/csrftoken=([^;]+)/)?.[1];
        if (csrfToken){
            config.headers['X-CSRFToken']=csrfToken;
        }
        // 验证 Token 是否能读取到
        const token=cookies.get('user_token');
        console.log('请求携带的 Token:', token); // 开发环境验证
        if (token){
            config.headers['Authorization']=`Token ${token}`;
        }
        return config
    },
    error=>{
        return Promise.reject(error);
    }
);
//响应拦截器:统一处理错误
service.interceptors.response.use(
    (response)=>{
        //成功响应直接返回数据
        return response.data;
    },
    (error)=>{
        //401:未认证（Token无效/过期/未携带)
        if(error.response?.status==401){
            //清除无效Token
            cookies.remove('user_token');
            //跳转到登录页
            window.location.href='/login';
            alert('登录已过期,请重新登录');

        }
        return Promise.reject(error)
    }
)
export default service;
