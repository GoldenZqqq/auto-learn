import requests
import time
import json
from datetime import datetime
import config
import threading
from concurrent.futures import ThreadPoolExecutor
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64
import urllib3
import random

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class AutoLearner:
    def __init__(self, username, auth_token):
        self.username = username
        self.base_url = config.BASE_URL
        self.token = auth_token
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "authorization": self.token,
            "content-type": "application/json",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Referer": "https://yygfeduuser.bkehs.com/",
            "Origin": "https://yygfeduuser.bkehs.com"
        }

    def get_course_list(self):
        """获取课程列表"""
        url = f"{self.base_url}/course/progress/list"
        params = {
            "pageNum": 1,
            "pageSize": 999,  # 获取所有课程
            "learnStatus": 3  # 只获取未完成的课程
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    courses = result.get('rows', [])
                    print(f"[{self.username}] 获取到 {len(courses)} 个未完成课程")
                    return courses
            return []
        except Exception as e:
            print(f"获取课程列表失败: {e}")
            return []

    def get_course_stats(self, course_id):
        """获取课程学习进度"""
        url = f"{self.base_url}/course/stats/{course_id}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return result.get('data', [])
            return []
        except Exception as e:
            print(f"获取课程进度失败: {e}")
            return []

    def get_course_passages(self, course_id):
        """获取课程章节信息"""
        url = f"{self.base_url}/course/passage/list"
        params = {
            "courseId": course_id,
            "pageSize": 999
        }
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return result.get('rows', [])
            return []
        except Exception as e:
            print(f"获取章节信息失败: {e}")
            return []

    def update_progress(self, course_id, passage_id, media_progress, media_duration, delta_duration):
        """更新学习进度"""
        url = f"{self.base_url}/course/progress/saveOrUpdate"
        data = {
            "courseId": str(course_id),
            "passageId": passage_id,
            "learnFileType": "0",  # 视频类型
            "deltaDuration": delta_duration,  # 使用实际的时间间隔
            "mediaProgress": media_progress,  # 当前进度
            "mediaDuration": media_duration  # 总时长
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data)
            return response.json()
        except Exception as e:
            print(f"更新进度失败: {e}")
            return None

    def process_passage(self, course_id, passage):
        """处理单个章节的学习"""
        passage_id = passage.get('id')
        video_file_list = passage.get('videoFileList', [])
        
        if not video_file_list:
            print(f"章节 {passage_id} 没有视频文件")
            return
        
        for video_file in video_file_list:
            media_duration = float(video_file.get('mediaDuration') or video_file.get('passageDuration', 0))
            if not media_duration:
                print(f"警告: 视频时长为0，跳过该视频")
                continue
                
            current_progress = 0
            total_reported_duration = 0  # 记录已上报的总时长
            
            print(f"开始学习视频: {video_file.get('fileName', '未命名')}")
            print(f"视频总时长: {media_duration:.1f}秒")
            
            while total_reported_duration < media_duration:
                # 计算本次需要上报的时长
                remaining_duration = media_duration - total_reported_duration
                if remaining_duration <= 0:
                    break
                    
                # 确保最后一次上报的时长不会超过总时长
                delta_duration = min(config.PROGRESS_CHUNK_SIZE, remaining_duration)
                total_reported_duration += delta_duration
                current_progress = total_reported_duration
                
                result = self.update_progress(
                    course_id, 
                    passage_id,
                    current_progress,  # 当前进度
                    media_duration,    # 总时长
                    delta_duration     # 本次增加的时长
                )
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                progress_percentage = (total_reported_duration / media_duration) * 100
                
                if result and result.get('code') == 200:
                    print(f"[{current_time}] 进度: {progress_percentage:.1f}% "
                          f"(当前学习时长: {total_reported_duration:.1f}/{media_duration:.1f}秒)")
                else:
                    print(f"[{current_time}] 进度更新失败")
                
                # 随机等待一段时间
                sleep_time = random.uniform(config.MIN_UPDATE_INTERVAL, config.MAX_UPDATE_INTERVAL)
                time.sleep(sleep_time)
            
            print(f"视频学习完成！")

    def process_course(self, course):
        """处理单个课程的学习"""
        course_id = course.get('courseId')
        print(f"\n[{self.username}] 开始学习课程: {course.get('courseName', course_id)}")
        
        # 获取章节信息
        passages = self.get_course_passages(course_id)
        if not passages:
            print(f"[{self.username}] 课程 {course_id} 没有章节信息")
            return False
            
        # 获取当前学习进度
        stats = self.get_course_stats(course_id)
        
        # 处理每个章节
        for passage in passages:
            # 检查章节是否已完成
            passage_stats = [stat for stat in stats if stat.get('passageId') == passage.get('id')]
            if passage_stats:
                passage_stat = passage_stats[0]
                if passage_stat.get('learnedStatus') == '2':
                    print(f"章节 {passage.get('coursePassageName', '未命名')} 已完成，跳过")
                    continue
                elif passage_stat.get('learnedDuration', 0) >= passage_stat.get('mediaDuration', 0):
                    print(f"章节 {passage.get('coursePassageName', '未命名')} 学习时长已满，跳过")
                    continue
            
            self.process_passage(course_id, passage)
        
        # 再次获取进度检查是否全部完成
        final_stats = self.get_course_stats(course_id)
        all_completed = all(stat.get('learnedStatus') == '2' for stat in final_stats)
        
        print(f"[{self.username}] 课程 {course_id} {'全部' if all_completed else '部分'}完成！")
        return all_completed

    def start_learning(self):
        """开始自动学习"""
        print(f"\n[{self.username}] 开始自动学习...")
        
        # 获取所有课程
        courses = self.get_course_list()
        if not courses:
            print(f"[{self.username}] 没有可学习的课程")
            return

        # 依次学习每个课程
        for i, course in enumerate(courses, 1):
            print(f"\n[{self.username}] ===== 开始学习第 {i}/{len(courses)} 门课程 =====")
            self.process_course(course)

        print(f"\n[{self.username}] 所有课程学习完成！")

class LoginManager:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "zh-CN,zh;q=0.9",
            "content-type": "application/json;charset=UTF-8",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "Referer": "https://yygfeduuser.bkehs.com/",
            "Origin": "https://yygfeduuser.bkehs.com"
        }
    
    def get_public_key(self):
        """获取公钥"""
        url = f"{self.base_url}/auth/publicKey"
        try:
            response = requests.get(
                url, 
                headers={
                    **self.headers,
                    "Referer": self.referrer
                },
                verify=False,  # 略 SSL 验证
                allow_redirects=True,
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                if result.get('publicKey'):
                    return result.get('publicKey')
                print(f"获取公钥响应错误: {result}")
            else:
                print(f"获取公钥HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
            return None
        except Exception as e:
            print(f"获取公钥失败: {e}")
            return None

    def encrypt_password(self, password, public_key):
        """使用公钥加密密码"""
        try:
            # 处理可能的格式问题
            public_key = public_key.replace('-----BEGIN PUBLIC KEY-----\n', '')
            public_key = public_key.replace('\n-----END PUBLIC KEY-----', '')
            public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
            
            # 创建 RSA 密钥对象
            rsa_key = RSA.importKey(public_key)
            cipher = PKCS1_v1_5.new(rsa_key)
            
            # 加密密码
            encrypted = cipher.encrypt(password.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"密码加密失败: {e}")
            return None


    def login(self, username, password):
        """登录并获取token"""
        # 1. 获取公钥
        public_key = self.get_public_key()
        if not public_key:
            raise Exception("获取公钥失败")

        # 2. 加密密码
        encrypted_password = self.encrypt_password(password, public_key)
        if not encrypted_password:
            raise Exception("密码加密失败")

        # 3. 登录请求
        login_url = f"{self.base_url}/auth/login"
        login_data = {
            "username": username,
            "password": encrypted_password,
            "code": "",
            "uuid": "",
            "domainName": "",
            "fromType": 0
        }

        try:
            response = requests.post(
                login_url, 
                headers={
                    **self.headers,
                    "Referer": self.referrer,
                    "isToken": "false"  # 添加 isToken 头
                },
                json=login_data,
                verify=False,  # 忽略 SSL 验证
                allow_redirects=True,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return f"Bearer {result['data']['access_token']}"
                else:
                    print(f"登录响应错误: {result}")
                    raise Exception(f"登录失败: {result.get('msg')}")
            else:
                print(f"登录HTTP错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                raise Exception(f"登录请求失败: {response.status_code}")
        except Exception as e:
            print(f"登录失败: {e}")
            return None

def start_user_learning(user_config):
    """为单个用户启动学习进程"""
    username = user_config['username']
    
    # 如果没有token，先进行登录
    if not user_config.get('auth_token'):
        print(f"[{username}] 未配置token，尝试使用账号密码登录...")
        login_manager = LoginManager(config.AUTH_URL)
        try:
            auth_token = login_manager.login(
                username=user_config['username'],
                password=user_config['password']
            )
            if not auth_token:
                print(f"[{username}] 登录失败，跳过该用户")
                return
            user_config['auth_token'] = auth_token
            print(f"[{username}] 登录成功，获取到token")
        except Exception as e:
            print(f"[{username}] 登录过程出错: {e}")
            return

    # 创建学习实例并开始学习
    learner = AutoLearner(username, user_config['auth_token'])
    try:
        learner.start_learning()
    except Exception as e:
        print(f"[{username}] 学习过程发生错误: {e}")

if __name__ == "__main__":
    print("启动多账号自动学习程序...")
    
    # 使用线程池同时处理多个账号
    with ThreadPoolExecutor(max_workers=len(config.USERS)) as executor:
        try:
            # 为每个用户创建一个学习线程
            futures = [executor.submit(start_user_learning, user) for user in config.USERS]
            # 等待所有线程完成
            for future in futures:
                future.result()
        except KeyboardInterrupt:
            print("\n程序已停止") 