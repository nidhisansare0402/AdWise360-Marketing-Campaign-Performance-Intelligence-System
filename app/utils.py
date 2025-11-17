def safe_div(a,b):
    return a/b if b else 0

def format_number(n):
    try:
        return f"{int(n):,}"
    except:
        return n
