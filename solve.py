flag = False
#table = [list(map(int, input().split())) for i in range(9)]


def is_promising(row, col, table):
    promising = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    for i in range(0, 9):
        if table[row][i] in promising:
            promising.remove(table[row][i])
        if table[i][col] in promising:
            promising.remove(table[i][col])

    for cur_row in range(row - row % 3, row - row % 3 + 3):
        for cur_col in range(col - col % 3, col - col % 3 + 3):
            if table[cur_row][cur_col] in promising:
                promising.remove(table[cur_row][cur_col])
    return promising


def check_finish(table):
    for row in table:
        if 0 in row:
            return False
    return True


def recursive(i, j, table):
    global flag
    if flag:
        return table
    if check_finish(table):
        for i in table:
            print(*i)
        flag = True
        return table
    while table[i][j] != 0 and j < 9 and i < 9:
        if j == 8:
            i += 1
            j = 0
        else:
            j += 1

    promising = is_promising(i, j, table)
    for n in promising:
        table[i][j] = n
        recursive(i + 1, 0, table) if j == 8 else recursive(i, j + 1, table)
        if flag:
            return table
        table[i][j] = 0