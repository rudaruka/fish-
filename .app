# main.py
import random
import time
import sys

coin = 0

물고기종류 = [
    "누치", "정어리", "붕어", "빙어", "북어", "전갱이", "꽁치", "은어", "노래미", "고등어",
    "메기", "잉어", "쥐치", "볼락", "열기", "줄돔", "삼치", "병어", "향어", "우럭",
    "송어", "해파리", "꼴뚜기", "넙치", "광어", "농어", "가물치", "방어", "바다송어",
    "해마", "연어", "쭈꾸미", "아귀", "한치", "오징어", "참치", "홍어", "랍스터",
    "가오리", "상어", "문어", "발광오징어", "킹크랩", "전복"
]

# 가격 맵 (유지보수 쉬움)
price_map = {
    # 10~50 예시 (원래 코드 기준 값들)
    "멸치": 10, "복어": 10,
    "누치": 15, "정어리": 15,
    "붕어": 20, "빙어": 20, "북어": 20, "전갱이": 20, "꽁치": 20,
    "은어": 25,
    "노래미": 30, "고등어": 30, "메기": 30, "잉어": 30,
    "쥐치": 35, "볼락": 35, "열기": 35, "줄돔": 35, "향어": 35,
    "삼치": 40, "병어": 40,
    "우럭": 45, "송어": 45, "연어": 45,
    "해파리": 50,
    "꼴뚜기": 60, "넙치": 60,
    "광어": 70, "농어": 70, "가물치": 70,
    "방어": 75, "바다송어": 75, "해마": 75,
    "쭈꾸미": 80,
    "아귀": 85, "한치": 85,
    "오징어": 90,
    "참치": 95, "홍어": 95,
    "랍스터": 110, "가오리": 110,
    "상어": 120, "문어": 120, "발광오징어": 120, "킹크랩": 120, "전복": 120
}

인벤토리 = []

def normalize(s: str) -> str:
    """입력 정규화: 양쪽 공백 제거, 소문자화"""
    return s.strip()

def ask(prompt: str) -> str:
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        print("\n입력이 중단되었습니다. 게임을 종료합니다.")
        sys.exit(0)

def fish_once():
    fish = random.choice(물고기종류)
    print(f"뽑힌 물고기: {fish}")
    인벤토리.append(fish)
    time.sleep(0.3)

def sell_fish(fish_name: str) -> int:
    """인벤토리에서 한 개 제거하고 가격을 반환. 재고 없으면 0 반환."""
    if fish_name not in 인벤토리:
        return 0
    price = price_map.get(fish_name, 0)
    인벤토리.remove(fish_name)
    return price

def yes_answer(s: str) -> bool:
    """여러 형태의 '예' 응답을 허용"""
    s = s.strip().lower()
    return s in ("예", "네", "y", "yes", "ㅇㅇ", "응")

def main():
    global coin
    print("=== 낚시 게임 ===")
    print("입장하려면 !입장 을 입력해주세요")
    시작 = ask("!입장 입력: ")

    if normalize(시작) != "!입장":
        print("게임을 시작하지 않았습니다. 프로그램을 종료합니다.")
        return

    print("입장합니다!")
    time.sleep(0.5)

    while True:
        print("\n===== 로비 =====")
        print("1. 낚시터로 가기")
        print("2. 상점으로 가기")
        print("3. 인벤토리 확인")
        print("4. 코인 확인")
        print("5. 게임 종료")
        선택 = normalize(ask("번호를 선택하세요: "))

        if 선택 == "1":
            print("\n낚시터에 도착했습니다!")
            time.sleep(0.5)
            시도횟수 = normalize(ask("몇 번 도전하시겠습니까? [1/2]: "))
            if 시도횟수 not in ("1", "2"):
                print("잘못 입력했습니다. 1 또는 2를 입력해주세요.")
                continue
            fish_once()
            if 시도횟수 == "2":
                fish_once()

        elif 선택 == "2":
            if not 인벤토리:
                print("인벤토리에 물고기가 없습니다. 낚시터로 가세요!")
                continue

            print("\n상점에 도착했습니다!")
            time.sleep(0.5)
            방문횟수 = 0

            while True:
                방문횟수 += 1
                if 방문횟수 == 1:
                    print("\n상인: 어떤 물고기를 팔건가?")
                else:
                    print("\n상인: 또 어떤 물고기를 팔건가?")

                time.sleep(0.2)
                print("인벤토리:", 인벤토리)
                물고기1 = normalize(ask("판매할 물고기 이름 입력: "))

                if 물고기1 not in 인벤토리:
                    print("인벤토리에 없는 물고기입니다!")
                    다시 = normalize(ask("다시 시도하시겠습니까? [예/아니요]: "))
                    if yes_answer(다시):
                        continue
                    else:
                        print("상점을 나갑니다. 로비로 돌아갑니다.")
                        break

                price = price_map.get(물고기1, 0)
                coin += sell_fish(물고기1)
                print(f"{물고기1}을(를) 팔았습니다! 가격: {price} 코인입니다.")
                print(f"현재 코인: {coin} 코인")

                if not 인벤토리:
                    print("더 이상 팔 물고기가 없습니다. 상점을 나갑니다.")
                    time.sleep(0.3)
                    break

                다시팔기 = normalize(ask("다른 물건을 팔겠습니까? [예/아니요]: "))
                if not yes_answer(다시팔기):
                    print("상점을 나갑니다. 로비로 돌아갑니다!")
                    time.sleep(0.3)
                    break

        elif 선택 == "3":
            if 인벤토리:
                print("\n현재 인벤토리:", 인벤토리)
            else:
                print("\n인벤토리가 비어 있습니다.")

        elif 선택 == "4":
            print(f"\n현재 코인: {coin} 코인")

        elif 선택 == "5":
            print("\n게임을 종료하시겠습니까?")
            대답1 = normalize(ask("[네/아니요]: "))
            if yes_answer(대답1):
                print("낚시터를 종료합니다! 안녕히 가세요!!")
                time.sleep(0.5)
                break
            else:
                print("다시 낚시터로 가봅시다!")
                time.sleep(0.4)

        else:
            print("잘못된 입력입니다. 1~5번 중 선택해주세요.")
            time.sleep(0.4)

if __name__ == "__main__":
    main()
