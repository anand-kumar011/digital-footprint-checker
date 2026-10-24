def normalize_india(raw):
    if raw is None:
        return None

    # Convert everything safely to string
    n = str(raw).strip()

    # Remove decimal if Excel converted to float
    if "." in n:
        n = n.split(".")[0]

    # Remove spaces
    n = n.replace(" ", "")

    # +91XXXXXXXXXX
    if n.startswith("+91") and len(n) == 13:
        return n

    # 91XXXXXXXXXX
    if n.startswith("91") and len(n) == 12:
        return "+" + n

    # XXXXXXXXXX (10 digit)
    if len(n) == 10 and n.isdigit():
        return "+91" + n

    return None
