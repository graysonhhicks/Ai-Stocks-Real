def calculate_ai_score(hist):
    close = hist["Close"]

    if len(close) < 50:
        return 0

    return_6m = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]
    momentum = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]
    volatility = close.pct_change().std()

    ma20 = close.tail(20).mean()
    ma50 = close.tail(50).mean()

    trend_bonus = 0.15 if ma20 > ma50 else -0.15

    score = (
        return_6m * 50 +
        momentum * 30 -
        volatility * 20 +
        trend_bonus * 100
    )

    score = max(0, min(100, score * 100))
    return round(score, 2)


def rating(score):
    if score >= 75:
        return "🟢 ELITE"
    elif score >= 55:
        return "🟡 SOLID"
    elif score >= 35:
        return "🟠 RISKY"
    return "🔴 WEAK"
