def check_mark(func, mark_name):
    marker_option = func.config.getoption("-m")
    has_mark = False
    if marker_option:
        if marker_option == mark_name:
            has_mark = True
        else:
            has_mark = mark_name in marker_option
    return has_mark
