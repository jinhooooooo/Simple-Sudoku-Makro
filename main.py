from selenium import webdriver
import solve
import os
import json
from time import time
from selenium.webdriver import ActionChains


def log_filter(log_):
    return (
        # is an actual response
        log_["method"] == "Network.responseReceived"
        # and json
        and "json" in log_["params"]["response"]["mimeType"]
        and log_["params"]["response"]["url"] == f"https://sudoku.com/api/level/{level_api}"
    )


def get_canvas():
    return driver.find_element_by_id("game")


def get_blanks():
    return [(row, col) for row in range(9) for col in range(9) if table[row][col] == 0]


def get_mission():
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

    for log in filter(log_filter, logs):
        resp_url = log["params"]["response"]["url"]
        request_id = log["params"]["requestId"]
        print(f"Caught {resp_url}")
        res_body = json.loads(driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})["body"])
        return list(res_body["mission"])


def select_level():
    print("난이도 쉬움: 0, 보통: 1, 어려움: 2, 전문가: 3, 이블: 4 종료: 5")
    while True:
        select_num = input()
        if select_num == "0":
            level = "swium"
            level_api = "easy"
            break
        elif select_num == "1":
            level = "botong"
            level_api = "medium"
            break
        elif select_num == "2":
            level = "eolyeoum"
            level_api = "hard"
            break
        elif select_num == "3":
            level = "jeonmunga"
            level_api = "expert"
            break
        elif select_num == "4":
            level = "evil"
            level_api = "evil"
            break
        elif select_num == "5":
            exit(0)
        else:
            print("잘못된 입력입니다.")
    return level, level_api


def run_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
    )
    driver = webdriver.Chrome(f"{os.getcwd()}/chromedriver", options=chrome_options)
    driver.get(f"https://sudoku.com/ko/{level}/")
    driver.execute_script("window.scrollTo(0, 20);")
    return driver


def init_table():
    table_str = get_mission()
    table = [[0] * 9 for _ in range(9)]
    row, col = 0, 0
    for num in table_str:
        table[row][col] = int(num)
        col += 1
        if col == 9:
            row += 1
            col = 0
    return table


def init_canvas_btn_position(canvas):
    canvas_dimension = canvas.size
    height = canvas_dimension['height']
    width = canvas_dimension['width']
    cell_width_offset = (width // 9) // 2
    cell_height_offset = (height // 9) // 2
    return [((height // 9) * row + cell_height_offset,
                      (width // 9) * col + cell_width_offset)
                     for row in range(9) for col in range(9) if table[row][col] == 0]


def click_ans(res, canvas, driver, btn_positions, blanks):
    for btn_pos, blank_pos in zip(btn_positions, blanks):
        btn_y, btn_x = btn_pos
        y, x = blank_pos
        ActionChains(driver).\
            move_to_element_with_offset(canvas, xoffset=btn_x, yoffset=btn_y).\
            click().\
            perform()
        answer_num = res[y][x]
        driver.find_element_by_css_selector(f"#numpad > div:nth-child({answer_num})").click()


if __name__ == "__main__":
    level, level_api = select_level()

    print("드라이버 시작 중...")
    driver = run_driver()

    print("스도쿠 데이터 초기화 중...")
    table = init_table()
    canvas = get_canvas()
    btn_position = init_canvas_btn_position(canvas)
    blanks = get_blanks()

    print("풀이 중...")
    start = time()
    res = solve.recursive(0, 0, table)
    print(f"풀이 시간: {time() - start:.2f}")

    print("답 작성 중...")
    click_ans(res, canvas, driver, btn_position, blanks)
    print("답안이 작성되었습니다.")
