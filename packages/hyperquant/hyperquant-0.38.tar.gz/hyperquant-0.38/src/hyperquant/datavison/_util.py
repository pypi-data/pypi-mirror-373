from datetime import date, datetime


def _to_milliseconds( t):
    """
    支持毫秒时间戳或datetime/date类型，返回毫秒时间戳
    """
    if t is None:
        return None
    if isinstance(t, int):
        return t
    if isinstance(t, float):
        return int(t * 1000)
    if isinstance(t, datetime):
        return int(t.timestamp() * 1000)
    if isinstance(t, date):
        return int(datetime.combine(t, datetime.min.time()).timestamp() * 1000)
    raise ValueError(f"不支持的时间类型: {type(t)}")