from datetime import datetime


def get_log_lines():
    if f'log_lines' not in globals():
        globals().update({'log_lines': []})
    log_lines = globals()['log_lines']
    return log_lines


def append_to_log_lines(level: str, value: str):
    log_lines = get_log_lines()
    log_lines_depth = 10000
    log_lines_to_remove_after_the_depth_is_reached = 1000
    log_lines.append({"datetime": datetime.now().strftime("%Y-%m-%h %H:%M:%S"), "level": level, "value": value})
    if len(log_lines) > log_lines_depth:
        log_lines = log_lines[log_lines_to_remove_after_the_depth_is_reached:]


def log_debug(value: str = "") -> None:
    if __debug__:
        append_to_log_lines("[dbug]", value)
        print(value)


def log_info(value: str = "") -> None:
    append_to_log_lines("[info]", value)
    print(value)


def log(value: str = "") -> None:
    log_info(value)


def log_warning(value: str) -> None:
    append_to_log_lines("[warn]", value)
    print(value)


def log_error(value: str) -> None:
    append_to_log_lines("[errr]", value)
    print(value)


def log_fatal(value: str, raise_exception: bool = True) -> None:
    append_to_log_lines("[fatl]", value)
    print(value)
    if raise_exception:
        raise Exception(f"[FATAL ERROR] {value}")


def log_ok(value: str) -> None:
    log(f'      //   __          ')
    log(f'     //   /  \\   ||  //')
    log(f'    //   ||  ||  || // ')
    log(f'\\\\ //    ||  ||  ||<<  {value}')
    log(f' \\V/     ||  ||  || \\\\ ')
    log(f'  V       \\__/   ||  \\\\ ')


def log_w(value: str) -> None:
    log(f'\\\\               //  !!!!!!')
    log(f' \\\\             //    !!!! ')
    log(f'  \\\\           //      !!  ')
    log(f'   \\\\   /^\\   //             {value}')
    log(f'    \\\\ // \\\\ //       !!!! ')
    log(f'     \\V/   \\V/        !!!!')


def get_html_log() -> str:
    result = '<!DOCTYPE html><html><head><style>\n'
    result += 'span.info {color: #000000}\n'
    result += 'span.warn {color: #FF5500}\n'
    result += 'span.errr {color: #FF0000}\n'
    result += 'span.fatl {color: #990099}\n'
    result += '</style></head>\n'
    result += '<body onload="window.scrollTo(0,document.body.scrollHeight)">\n'
    result += '<pre>'
    log_lines = get_log_lines()
    for line in log_lines:
        # result += f"{line['level']} - {line['datetime']} - {line['value']}<br/>\n"
        line_level = line["level"]
        line_value = line["value"]
        result += f'<span class="{line_level[1:-1]}">{line_level}    {line_value}</span>\n'
    result += '</pre>\n'
    result += '</body></html>'
    return result


def clear_log_lines() -> None:
    """
    Vymaze vsechny zaznamy z logu
    :return:
    """
    log_lines = get_log_lines()
    log_lines.clear()
