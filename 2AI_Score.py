# ai_score.py

def calculate_ai_score(hist):
    """
    AI Score based on:
    - 6 month return (growth)
    - momentum (20-day trend)
    - volatility penalty
    - moving average trend
    """

    if hist is None or hist.empty or len(hist) < 50:
        return 0

    close = hist["Close"]

    try:
        # 6-month return
        return_6m = (close.iloc[-1] - close.iloc[0]) / close.iloc[0]

        # momentum (short term trend)
        momentum = (close.iloc[-1] - close.iloc[-20]) / close.iloc[-20]

        # volatility (risk penalty)
        volatility = close.pct_change().std()

        # trend signal
        ma20 = close.tail(20).mean()
        ma50 = close.tail(50).mean()
        trend_bonus = 0.12 if ma20 > ma50 else -0.12

        # final AI score formula
        score = (
            (return_6m * 50) +
            (momentum * 30) -
            (volatility * 25) +
            (trend_bonus)
        )

        # normalize to 0–100
        score = max(0, min(100, score * 100))
        return round(score, 2)

    except Exception:
        return 0


def rating(score):
    if score >= 75:
        return "🟢 STRONG BUY"
    elif score >= 55:
        return "🟡 HOLD"
    elif score >= 35:
        return "🟠 WEAK"
    else:
        return "🔴 AVOID"


def color(score):
    if score >= 75:
        return "#22c55e"
    elif score >= 55:
        return "#eab308"
    elif score >= 35:
        return "#f97316"
    else:
        return "#ef4444"
