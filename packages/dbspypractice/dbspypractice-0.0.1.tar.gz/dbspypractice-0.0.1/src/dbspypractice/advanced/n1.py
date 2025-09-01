import time
question = """
[질문 1]
콤마(,)로 구분된 수들 중 최빈값을 구하세요. (빈도가 같은 경우는 큰 수를 출력하세요.)
모든 수는 1이상 9이하의 정수입니다.

문자열을 입력받고, 숫자1개를 출력하는 함수를 작성하세요.

[입력]
3,1,2,1,2,3,1,2,3,4,3

[출력]
3
"""

sample1_input = "3,1,2,1,2,3,1,2,3,4,3"
sample1_output = 3


sample2_input = "1,5,1,5,1,5"
sample2_output = 5

sample3_input = "1"
sample3_output = 1

sample4_input = "1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,1,2,3,4,5,6,1,2,3,4,5,1,2,3,4,1,2,3,1,2,1"
sample4_output = 1


def __run_test__(user_f, input, output):
    try:
        user_output = user_f(input)
        if user_output == output:
            print("PASS")
        else:
            print("FAIL")
            print("* DEBUG INFO *")
            print("input:", input)
            print("output should be:", output)
            print("but, user output:", user_output)
            print("**************")
            
    except Exception as e:
        print("ERROR:", e)



def run(user_f):
    input = [sample1_input, sample2_input, sample3_input, sample4_input]
    output = [sample1_output, sample2_output, sample3_output, sample4_output]
    print(f'*** 총 {len(input)}개의 테스트 케이스를 확인합니다. ***')
    start_time = time.time()
    for i,o, idx in zip(input, output, range(1, len(input)+1)):
        print(f'TC [{idx}]: ', end='')
        __run_test__(user_f, i, o)
    end_time = time.time()
    print(f'{(end_time-start_time)* 1000} ms')

    