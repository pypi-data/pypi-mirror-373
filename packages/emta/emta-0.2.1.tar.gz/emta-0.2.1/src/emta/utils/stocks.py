def get_market_code(code: str) -> str:
    code = code.strip()

    # A股
    if code.startswith(("600", "601", "603", "605", "688")):
        return "HA"
    elif code.startswith(("000", "001", "002", "003", "300", "301")):
        return "SA"
    elif code.startswith("8") or code.startswith("4"):  # 北交所/新三板
        return "BJ"

    # 港股
    if code.isdigit() and len(code) <= 5:
        return "HK" + code.zfill(5)

    # 美股（简单规则，默认全字母为美股）
    if code.isalpha():
        return "US:" + code.upper()

    return "UNKNOWN"


if __name__ == "__main__":
    print(get_market_code("600519"))  # SH600519
    print(get_market_code("000001"))  # SZ000001
    print(get_market_code("00700"))  # HK00700
    print(get_market_code("AAPL"))  # US:AAPL
