import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date
import pandas as pd

# HTTP 客户端配置
DEFAULT_TIMEOUT = 10  # seconds

# ==================== 1. 期权行情数据：option_finance_board ====================

class OptionFinanceBoardData:
    def __init__(self, date: str, contract_id: str, price: float, change_rate: float,
                 prev_settle: float, strike_price: float, quantity: int):
        self.date = date
        self.contract_id = contract_id
        self.price = price
        self.change_rate = change_rate
        self.prev_settle = prev_settle
        self.strike_price = strike_price
        self.quantity = quantity


def option_finance_board(symbol: str, end_month: str) -> List[OptionFinanceBoardData]:
    """
    期权行情数据（与 Go 版完全一致的逻辑）
    """
    # 取最后两位
    end_month = end_month[-2:]

    # 构建 URL
    payload = {"select": "contractid,last,chg_rate,presetpx,exepx"}
    symbol_map = {
        "华夏上证50ETF期权": f"http://yunhq.sse.com.cn:32041/v1/sho/list/tstyle/510050_{end_month}",
        "华泰柏瑞沪深300ETF期权": f"http://yunhq.sse.com.cn:32041/v1/sho/list/tstyle/510300_{end_month}",
        "南方中证500ETF期权": f"http://yunhq.sse.com.cn:32041/v1/sho/list/tstyle/510500_{end_month}",
        "华夏科创50ETF期权": f"http://yunhq.sse.com.cn:32041/v1/sho/list/tstyle/588000_{end_month}",
        "易方达科创50ETF期权": f"http://yunhq.sse.com.cn:32041/v1/sho/list/tstyle/588080_{end_month}",
    }

    if symbol not in symbol_map:
        raise ValueError(f"不支持的 symbol: {symbol}")

    option_url = symbol_map[symbol]

    try:
        print(f"📡 正在获取 {symbol} {end_month} 价格数据（直连SSE）...")
        resp = requests.get(option_url, params=payload, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()

        body = resp.content
        result: Dict[str, Any] = json.loads(body)

        data: List[OptionFinanceBoardData] = []
        timestamp = f"{result['date']}{result['time']:06d}"

        for item in result.get("list", []):
            if len(item) < 5:
                continue
            try:
                price = float(item[1]) if item[1] not in (None, '') else 0.0
                chg_rate = float(item[2]) if item[2] not in (None, '') else 0.0
                prev_settle = float(item[3]) if item[3] not in (None, '') else 0.0
                strike = float(item[4]) if item[4] not in (None, '') else 0.0
            except (ValueError, TypeError):
                continue

            data.append(OptionFinanceBoardData(
                date=timestamp,
                contract_id=str(item[0]),
                price=price,
                change_rate=chg_rate,
                prev_settle=prev_settle,
                strike_price=strike,
                quantity=result["total"],
            ))
        print(f"✅ 成功获取 {len(data)} 条价格数据")
        return data
    except Exception as e:
        print(f"❌ 获取价格数据失败: {e}")
        return []


# ==================== 2. 风险指标：option_risk_indicator_sse ====================

class RiskIndicator:
    def __init__(self, trade_date: datetime, security_id: str, contract_id: str,
                 contract_symbol: str, delta: float, theta: float, gamma: float,
                 vega: float, rho: float, implc_volatility: float):
        self.trade_date = trade_date
        self.security_id = security_id
        self.contract_id = contract_id
        self.contract_symbol = contract_symbol
        self.delta = delta
        self.theta = theta
        self.gamma = gamma
        self.vega = vega
        self.rho = rho
        self.implc_volatility = implc_volatility


def option_risk_indicator_sse(date: str) -> List[RiskIndicator]:
    """
    获取上交所风险指标（与 Go 版完全一致的逻辑）
    """
    risk_url = "http://query.sse.com.cn/commonQuery.do"
    params = {
        "isPagination": "false",
        "trade_date": date,
        "sqlId": "SSE_ZQPZ_YSP_GGQQZSXT_YSHQ_QQFXZB_DATE_L",
        "contractSymbol": "",
    }
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Host": "query.sse.com.cn",
        "Pragma": "no-cache",
        "Referer": "http://www.sse.com.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36"
    }

    try:
        print(f"📡 正在从 SSE 获取 {date} 风险数据...")
        resp = requests.get(risk_url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()

        result = resp.json()
        indicators: List[RiskIndicator] = []

        for item in result.get("result", []):
            try:
                # 解析日期
                trade_date = datetime.strptime(item["TRADE_DATE"], "%Y-%m-%d").date()
                # 转换浮点数
                delta = float(item["DELTA_VALUE"]) if item["DELTA_VALUE"] else 0.0
                theta = float(item["THETA_VALUE"]) if item["THETA_VALUE"] else 0.0
                gamma = float(item["GAMMA_VALUE"]) if item["GAMMA_VALUE"] else 0.0
                vega = float(item["VEGA_VALUE"]) if item["VEGA_VALUE"] else 0.0
                rho = float(item["RHO_VALUE"]) if item["RHO_VALUE"] else 0.0
                iv = float(item["IMPLC_VOLATLTY"]) if item["IMPLC_VOLATLTY"] else 0.0
            except (ValueError, KeyError):
                continue

            indicators.append(RiskIndicator(
                trade_date=trade_date,
                security_id=item["SECURITY_ID"],
                contract_id=item["CONTRACT_ID"],
                contract_symbol=item["CONTRACT_SYMBOL"],
                delta=delta,
                theta=theta,
                gamma=gamma,
                vega=vega,
                rho=rho,
                implc_volatility=iv,
            ))
        print(f"✅ 成功获取 {len(indicators)} 条风险数据")
        return indicators
    except Exception as e:
        print(f"❌ 获取风险数据失败: {e}")
        return []


# ------------------------------- 3. 其他辅助函数（保持与 Go 一致） -------------------------------

def get_fourth_wednesday(year: int, month: int) -> date:
    first_day = datetime(year, month, 1)
    weekday_of_first = first_day.weekday()
    first_wednesday = 1 + (3 - weekday_of_first + 7) % 7  # 周三=3
    fourth_wednesday_day = first_wednesday + 21
    return datetime(year, month, fourth_wednesday_day).date()


def calc_expire_date(yy_mm: str) -> Optional[date]:
    try:
        year = 2000 + int(yy_mm[:2])
        month = int(yy_mm[2:4])
        return get_fourth_wednesday(year, month)
    except Exception as e:
        print(f"❌ 计算到期日失败 {yy_mm}: {e}")
        return None