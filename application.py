from flask import Flask, request, jsonify
import pandas as pd

global jungong_type
global gyoyang_type
global origin_data
global data
global jungong
global gyoyang
global condition
global condition_list

origin_data=pd.read_csv('final.csv')
gyoyang=['과학과 기술 영역','예술과체육 영역','사회와경제 영역','인간과철학 영역', '글로벌문화와제2외국어 영역','K-MOOC 영역','외국어로서의한국어 영역',
            '서울권역 e-러닝 영역','필수 교양 교과목(정보영역)','필수 교양 교과목(광운인되기,영어)','필수 교양 교과목(융합적사고와글쓰기)']
jungong=['화학과','경영학부',
    '정보콘텐츠학과','전자바이오물리학과','건축공학과','환경공학과','수학과 ','전기공학과','법학부','로봇학부','소프트웨어학부',
    '전자공학과','컴퓨터정보공학부','스포츠융합과학과','전자융합공학과','전자재료공학과','정보융합학부','전자통신공학과','화학공학과']
condition={'팀플횟수':'group_meeting','과제횟수':'assignment','학점부여':'grade','시험횟수':'test_n','강의력':'lecture_faculty','교수인성':'insung'}
condition_list=[]

application = Flask(__name__)
#https://attention-knizk.run.goorm.io
@application.route("/classChoice",methods=['POST'])
def classChoice():
    req = request.get_json()
    
    class_type = req["action"]["detailParams"]["class"]["value"]	# json파일 읽기
    global data
    global origin_data
    global condition_list
    data = origin_data
    condition_list = []
    #print(data)

    answer = class_type #[1:교양,2:전공]
    if class_type=='1':
        ttext=[]
        for i in range(len(gyoyang)):
            st=str(i+1)+'. '+gyoyang[i]
            ttext.append(st)
        ttext='어떤 교양 영역을 선택하시겠습니까?\n'+'\n'.join(ttext)
    else:
        ttext=[]
        for i in range(len(jungong)):
            st=str(i+1)+'. '+jungong[i]
            ttext.append(st)
        ttext='전공이 무엇입니까?\n'+'\n'.join(ttext)
    # 답변 텍스트 설정
    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": ttext
                        #f"{class_type}을 선택하셨습니다. \n"
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)



@application.route("/gyoyangChoice",methods=['POST'])
def gyoyangChoice():
    req = request.get_json()
    
    gyoyang_type = req["action"]["detailParams"]["gyoyang"]["value"]	# json파일 읽기
    global data
    data = data[data['classification2']==gyoyang[int(gyoyang_type)]]
    # print(data)

    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "교양에 대해 원하는 난이도 또는 학년이 있습니까?"
                    }
                }
            ]
        }
    }
    # print(data)

    # 답변 전송
    return jsonify(res)


@application.route("/jungongChoice",methods=['POST'])
def jungongChoice():
    req = request.get_json()
    
    jungong_type = req["action"]["detailParams"]["jungong"]["value"]	# json파일 읽기
    global data
    data = data[data['classification2']==jungong[int(jungong_type)]]
    # print(data)

    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "전공에 대해 원하는 난이도 또는 학년이 있습니까?"
                    }
                }
            ]
        }
    }

    # 답변 전송
    return jsonify(res)



@application.route("/gradeChoice", methods=["POST"])
def gradeChoice():
    req = request.get_json()
    
    grade_level = req["action"]["detailParams"]["grade"]["value"]	# json파일 읽기
    if int(grade_level) != 0:
        global data
        data = data[data['level']==int(grade_level)]
    # print(data)

    res = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": '당신이 강의를 선택할 때, 중요시하는 조건을 3가지 고르세요.\n조건을 하나씩 3번 입력해주세요\n1. 팀플횟수\n2. 과제횟수\n3. 학점부여\n4. 시험횟수\n5. 강의력\n6. 교수인성'
                    }
                }
            ]
        }
    }
    
    return jsonify(res)



@application.route("/conditionChoice", methods=["POST"])
def conditionChoice():
    req = request.get_json()
    
    condition_index = req["action"]["detailParams"]["condition"]["value"]
    global condition_list
    global condition
    global data
    condition_list.append(list(condition.values())[int(condition_index)])
    
    if len(condition_list) == 3:
        data[condition_list[0]]=data[condition_list[0]]*4
        data[condition_list[1]]=data[condition_list[1]]*2
        data[condition_list[2]]=data[condition_list[2]]*1
        
        data['r_score']=(data['group_meeting']+data['assignment']+data['grade']+data['test_n']+data['lecture_faculty']+data['insung'])*(data['score']/2+data['f_score'])/9
        dic=data.groupby('lecture_code')['r_score'].mean()
        dic = dic.to_dict()
        
        #첫번째 큰값
        max_key1 = max(dic, key=dic.get)
        recommend1=data[data['lecture_code']==max_key1]
        recommend11 = list(recommend1['professor_name'])[0]
        recommend12 = list(recommend1['lecture_name'])[0]
        recommend13 = list(recommend1['extractive'])[0]
        
        #두번쨰 큰값
        max_key2 =sorted(list(dic.keys()))[1]
        print(max_key2)
        recommend2=data[data['lecture_code']==max_key2]
        recommend21 = list(recommend2['professor_name'])[0]
        recommend22 = list(recommend2['lecture_name'])[0]
        recommend23 = list(recommend2['extractive'])[0]
        
        #세번쨰 큰값
        max_key3 =sorted(list(dic.keys()))[2]
        print(max_key3)
        recommend3=data[data['lecture_code']==max_key3]
        recommend31 = list(recommend3['professor_name'])[0]
        recommend32 = list(recommend3['lecture_name'])[0]
        recommend33 = list(recommend3['extractive'])[0]
        
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f'{len(condition_list)}번째 조건으로 {list(condition.keys())[int(condition_index)]}을 선택하셨습니다.'
                        }
                    }, 
                    {
                        "simpleText": {
                            "text": f'첫번째 추천 강의는 {recommend11}교수님의 {recommend12}입니다. \n강의 한줄평 : {recommend13}'
                        }
                    },
                    {
                        "simpleText": {
                            "text": f'두번째 추천 강의는 {recommend21}교수님의 {recommend22}입니다. \n강의 한줄평 : {recommend23}' 
                        }
                    },
                    {
                        "simpleText": {
                            "text": f'세번째 추천 강의는 {recommend31}교수님의 {recommend32}입니다. \n강의 한줄평 : {recommend33}'
                        }
                    }
                ]
            }

            # 여기
        }
    else: #2개 이하일때
        res = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": f'{len(condition_list)}번째 조건으로 {list(condition.keys())[int(condition_index)]}을 선택하셨습니다.'
                        }
                    }
                ]
            }
        }
    
    return jsonify(res)

    

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000, threaded=True)
