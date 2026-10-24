def decide(signals):
    score = 0

    if signals.get("whatsapp"):
        score += 40
    if signals.get("telegram"):
        score += 25
    if signals.get("instagram"):
        score += 15
    if signals.get("facebook"):
        score += 10
    if signals.get("snapchat"):
        score += 10

    # internal threshold
    return "YES" if score >= 50 else "NO"
