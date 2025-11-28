import request from "../utils/request.js";
import {useCookies} from "vue3-cookies";


//用户登录
export function userLogin(data){
    return request({
        url:'exam/token/',//后端登录接口地址
        method:'POST',
        data:data  //传递用户名和密码
    });
}
//用户退出
export function userLogout(){
    const {cookies} =useCookies();
    cookies.remove('user_token');
}
