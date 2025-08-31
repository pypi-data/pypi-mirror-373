import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

from q1x.core import option

# -------------------------------
# 1. 常量定义
# -------------------------------
VIX_THRESHOLD_LOW = 0.05
VIX_THRESHOLD_HIGH = 0.05
HISTORICAL_QUANTILE_LOW = 0.2
HISTORICAL_QUANTILE_HIGH = 0.8
RISK_FREE_RATE = 0.02


# -------------------------------
# 2. 获取数据（保持原样）
# -------------------------------
def fetch_risk_data(trade_date: str):
    try:
        print(f"📡 正在获取 {trade_date} 风险数据...")
        data_list = option.option_risk_indicator_sse(date=trade_date)
        if not data_list:
            print("❌ 未获取到风险数据")
            return None

        # 转为 DataFrame
        records = []
        for item in data_list:
            records.append({
                'TRADE_DATE': item.trade_date,
                'SECURITY_ID': item.security_id,
                'CONTRACT_ID': item.contract_id,
                'CONTRACT_SYMBOL': item.contract_symbol,
                'DELTA_VALUE': item.delta,
                'THETA_VALUE': item.theta,
                'GAMMA_VALUE': item.gamma,
                'VEGA_VALUE': item.vega,
                'RHO_VALUE': item.rho,
                'IMPLC_VOLATLTY': item.implc_volatility,
            })
        df = pd.DataFrame(records)
        print(f"✅ 成功获取 {len(df)} 条风险数据")
        return df
    except Exception as e:
        print(f"❌ 获取风险数据失败: {e}")
        return None


def fetch_price_data(symbol: str, end_month: str):
    try:
        print(f"💰 正在获取 {symbol} {end_month} 价格数据...")
        data_list = option.option_finance_board(symbol=symbol, end_month=f'20{end_month}')
        if not data_list:
            print("❌ 未获取到价格数据")
            return None

        # 转为 DataFrame
        records = []
        for item in data_list:
            records.append({
                'CONTRACT_ID': item.contract_id,
                'PRICE': item.price,
                'CHANGE_RATE': item.change_rate,
                'PREV_SETTLE': item.prev_settle,
                'STRIKE': item.strike_price,
                'QUANTITY': item.quantity,
                'DATE': item.date,
            })
        df = pd.DataFrame(records)
        print(f"✅ 成功获取 {len(df)} 条价格数据")
        return df
    except Exception as e:
        print(f"❌ 获取价格数据失败: {e}")
        return None


# -------------------------------
# 3. 计算“第四个星期三”函数
# -------------------------------
def get_fourth_wednesday(year: int, month: int) -> date:
    first_day = datetime(year, month, 1)
    weekday_of_first = first_day.weekday()
    first_wednesday = 1 + (2 - weekday_of_first) % 7
    fourth_wednesday_day = first_wednesday + 21
    return datetime(year, month, fourth_wednesday_day).date()


def calc_expire_date(yy_mm: str) -> date | None:
    try:
        year = 2000 + int(yy_mm[:2])
        month = int(yy_mm[2:4])
        return get_fourth_wednesday(year, month)
    except Exception as e:
        print(f"❌ 计算到期日失败 {yy_mm}: {e}")
        return None


# -------------------------------
# 4. 提取并合并数据（保持原样）
# -------------------------------
def extract_and_merge_data(risk_df, price_df_dict, trade_date_str: str):
    df_300 = risk_df[risk_df['CONTRACT_ID'].str.startswith('510300')].copy()
    if df_300.empty:
        print("❌ 未找到 300ETF 期权数据")
        return None

    df_300['TYPE'] = df_300['CONTRACT_ID'].str.extract(r'([CP])')[0]
    df_300['EXPIRE_YYMM'] = df_300['CONTRACT_ID'].str.extract(r'[CP](\d{4})')[0]

    if df_300['EXPIRE_YYMM'].isnull().any():
        before = len(df_300)
        df_300 = df_300.dropna(subset=['EXPIRE_YYMM']).copy()
        print(f"⚠️ 过滤了 {before - len(df_300)} 条无法提取年月的合约")

    df_300['EXPIRE_DATE_DT'] = df_300['EXPIRE_YYMM'].apply(calc_expire_date)

    if df_300['EXPIRE_DATE_DT'].isnull().any():
        before = len(df_300)
        df_300 = df_300.dropna(subset=['EXPIRE_DATE_DT']).copy()
        print(f"⚠️ 过滤了 {before - len(df_300)} 条计算到期日失败的合约")

    current_date = datetime.strptime(trade_date_str, "%Y%m%d").date()
    df_300['T_DAYS'] = (pd.to_datetime(df_300['EXPIRE_DATE_DT']) - pd.to_datetime(current_date)).dt.days
    df_300['T_YEARS'] = df_300['T_DAYS'] / 365.0

    iv_col = [col for col in df_300.columns if 'IMPLC' in col]
    if not iv_col:
        print("❌ 未找到隐含波动率列")
        return None
    df_300.rename(columns={iv_col[0]: 'IMPLC_VOLATLTY'}, inplace=True)

    numeric_cols = ['DELTA_VALUE', 'THETA_VALUE', 'GAMMA_VALUE', 'VEGA_VALUE', 'RHO_VALUE', 'IMPLC_VOLATLTY']
    for col in numeric_cols:
        df_300[col] = pd.to_numeric(df_300[col], errors='coerce')

    df_300 = df_300[(df_300['IMPLC_VOLATLTY'] > 0.01) & (df_300['IMPLC_VOLATLTY'] < 1.0)].copy()
    print(f"✅ 提取 300ETF 期权: {len(df_300)} 条，已计算真实剩余时间")

    prices, strikes = [], []
    for _, row in df_300.iterrows():
        contract_id = row['CONTRACT_ID']
        yymm = row['EXPIRE_YYMM']
        price = np.nan
        strike = np.nan
        if yymm in price_df_dict:
            price_df = price_df_dict[yymm]
            price_row = price_df[price_df['CONTRACT_ID'] == contract_id]
            if not price_row.empty:
                price = price_row['PRICE'].iloc[0]
                strike = price_row['STRIKE'].iloc[0]
        prices.append(price)
        strikes.append(strike)

    df_300['PRICE'] = prices
    df_300['STRIKE'] = strikes

    df_300 = df_300.dropna(subset=['PRICE', 'STRIKE']).copy()

    if df_300.empty:
        print("❌ 合并后数据为空")
        return None

    print(f"📊 行权价范围: {df_300['STRIKE'].min():.3f} ~ {df_300['STRIKE'].max():.3f} 元")
    print(f"📊 当前300ETF价格应在: {df_300['STRIKE'].median():.3f} 元附近")

    if df_300['STRIKE'].nunique() == 1:
        print("❌ 警告：所有行权价相同！可能是数据错误！")
    else:
        print("✅ 行权价分布正常")

    #print("\n📋 示例数据:")
    #print(df_300[['CONTRACT_ID', 'STRIKE', 'TYPE', 'PRICE', 'T_DAYS', 'IMPLC_VOLATLTY']].head(8).to_string(index=False))

    print(f"✅ 数据合并完成，最终有效合约: {len(df_300)} 条")
    print(f"📊 合约类型分布: \n{df_300['TYPE'].value_counts()}")
    if len(df_300[df_300['TYPE'] == 'P']) == 0:
        print("❌ 警告：未找到 Put 合约！无法计算真实 VIX！")
        return None
    return df_300


# -------------------------------
# ✅ 修复版 _compute_variance（仅修复 KeyError 和 K0 逻辑）
# -------------------------------
def _compute_variance(df_term, T, r):
    if T <= 1 / 365:
        return np.nan

    discount = np.exp(-r * T)
    df = df_term.copy()
    df.rename(columns={'STRIKE': 'K'}, inplace=True)

    # ✅ 1. 按 K 升序排序
    # ✅ 让 Put 在 Call 前（或 Call 在 Put 前），确保与 Go 一致
    # ✅ 正确：先按 K 升序，再按 TYPE 稳定排序（Put 在 Call 前）
    #df = df.sort_values(['K', 'TYPE'], key=lambda x: x.map({'P': 0, 'C': 1})).reset_index(drop=True)
    df = df.sort_values(by=['K', 'TYPE'], ascending=[True, False]).reset_index(drop=True)

    # ✅ 2. 提取 Call 和 Put 价格
    calls = df[df['TYPE'] == 'C'].set_index('K')['PRICE']
    puts = df[df['TYPE'] == 'P'].set_index('K')['PRICE']

    # ✅ 3. 对齐 C - P
    common_k = calls.index.intersection(puts.index)
    if len(common_k) < 2:
        F = df['K'].median()  # 保底
    else:
        c_prices = calls.reindex(common_k)
        p_prices = puts.reindex(common_k)
        c_minus_p = c_prices - p_prices

        # 找 C-P 符号变化点
        cp_vals = c_minus_p.values
        k_vals = common_k.values
        cross = None
        for i in range(len(cp_vals) - 1):
            if cp_vals[i] * cp_vals[i + 1] <= 0:
                cross = i
                break

        if cross is None:
            F = k_vals[np.argmin(np.abs(cp_vals))]
        else:
            k1, k2 = k_vals[cross], k_vals[cross + 1]
            c1, c2 = cp_vals[cross], cp_vals[cross + 1]
            if c2 != c1:
                w = -c1 / (c2 - c1)
                F = k1 + w * (k2 - k1)
            else:
                F = (k1 + k2) / 2
    print(f"🔍 远期价格 F ≈ {F:.4f}")

    # ✅ 4. 截断行权价范围（现在 F 是 float，不会报错）
    df = df[(df['K'] >= 0.7 * F) & (df['K'] <= 1.3 * F)].copy()
    df = df.sort_values('K').reset_index(drop=True)

    # ✅ 5. 找 K0
    K0 = 0.0
    for k in df['K']:
        if k <= F:
            K0 = k
        else:
            break
    if K0 == 0.0:
        K0 = df['K'].iloc[0] if len(df) > 0 else df_term['K'].median()

    # ✅ 6. 计算 sum_
    sum_ = 0.0
    n = len(df)
    print(f"\n🔍 开始计算 sum_ (T={T:.4f}, discount={discount:.6f})")
    for i, row in df.iterrows():
        K = row['K']
        Q = row['PRICE'] * discount
        if Q <= 0:
            continue

        if n == 1:
            dk = 0.0
        elif i == 0:
            dk = df.iloc[1]['K'] - K
        elif i == n - 1:
            dk = K - df.iloc[n-2]['K']
        else:
            dk = (df.iloc[i+1]['K'] - df.iloc[i-1]['K']) / 2

        weight = dk / (K ** 2)
        contrib = weight * Q
        print(f"  K={K:5.3f} | P={row['PRICE']:6.4f} | Q={Q:7.5f} | dk={dk:6.4f} | w={weight:8.6f} | → {contrib:8.6f}")
        sum_ += contrib

    print(f"📈 T={T:.4f}, F={F:.4f}, K0={K0:.4f}, sum={sum_:.6f}")
    variance = (2 / T) * sum_ - ((F / K0 - 1) ** 2) / T
    return max(variance, 1e-6)

def _compute_variance_v1(df_term, T, r):
    if T <= 1 / 365:
        return np.nan

    discount = np.exp(-r * T)
    df = df_term.copy()

    # ✅ 1. 先重命名
    df.rename(columns={'STRIKE': 'K'}, inplace=True)

    # ✅ 2. 按 K 和 TYPE 排序（稳定排序）
    #df = df.sort_values(['K', 'TYPE']).reset_index(drop=True)
    # 修改排序：Put 在前，Call 在后
    # ✅ 让 Put 在 Call 前
    df['TYPE_ORDER'] = df['TYPE'].map({'P': 0, 'C': 1})
    df = df.sort_values(['K', 'TYPE_ORDER']).reset_index(drop=True)
    df.drop('TYPE_ORDER', axis=1, inplace=True)

    # ✅ 3. 提取 Call 和 Put
    calls = df[df['TYPE'] == 'C'].set_index('K')['PRICE']
    puts = df[df['TYPE'] == 'P'].set_index('K')['PRICE']

    # ✅ 4. 对齐 C - P
    c_minus_p = []
    for k in df['K']:
        c = calls.get(k, np.nan)
        p = puts.get(k, np.nan)
        if np.isnan(c) or np.isnan(p):
            c = calls.reindex([k], method='nearest').iloc[0] if not calls.empty else np.nan
            p = puts.reindex([k], method='nearest').iloc[0] if not puts.empty else np.nan
        c_minus_p.append(c - p)
    df['C_MINUS_P'] = c_minus_p

    # ✅ 5. 插值找 F
    df_valid = df.dropna(subset=['C_MINUS_P']).sort_values('K')
    if len(df_valid) < 2:
        F = df['K'].median()
    else:
        cp_vals = df_valid['C_MINUS_P'].values
        k_vals = df_valid['K'].values
        cross = None
        for i in range(len(cp_vals) - 1):
            if cp_vals[i] * cp_vals[i + 1] <= 0:
                cross = i
                break
        if cross is None:
            F = df_valid.iloc[(df_valid['C_MINUS_P']).abs().argsort()[0]]['K']
        else:
            k1, k2 = k_vals[cross], k_vals[cross + 1]
            c1, c2 = cp_vals[cross], cp_vals[cross + 1]
            if c2 != c1:
                w = -c1 / (c2 - c1)
                F = k1 + w * (k2 - k1)
            else:
                F = (k1 + k2) / 2
    print(f"🔍 远期价格 F ≈ {F:.4f}")

    # ✅ 6. 截断行权价范围
    df = df[(df['K'] >= 0.7 * F) & (df['K'] <= 1.3 * F)].copy()
    df = df.sort_values('K').reset_index(drop=True)
    #df = df.sort_values(['K', 'TYPE'], key=lambda x: x.map({'C': 0, 'P': 1})).reset_index(drop=True)

    # ✅ 7. 找 K0：小于等于 F 的最大行权价（显式遍历，更稳）
    K0 = 0.0
    for k in df['K']:
        if k <= F:
            K0 = k
        else:
            break
    if K0 == 0.0:
        K0 = df['K'].iloc[0]  # 保底

    # ✅ 8. 计算加权方差（先贴现）
    sum_ = 0.0
    Ks = df['K'].values
    print(f"\n🔍 开始计算 sum_ (T={T:.4f}, discount={discount:.6f})")
    for i, row in df.iterrows():
        K = row['K']
        Q = row['PRICE'] * discount
        if np.isnan(Q) or Q <= 0:
            continue
        n = len(df)
        if i == 0:
            dk = df.iloc[i + 1]['K'] - K
        elif i == n-1:
            dk = K - df.iloc[n - 2]['K']
        else:
            dk = (df.iloc[i + 1]['K'] - df.iloc[i - 1]['K']) / 2

        weight = dk / (K ** 2)
        contrib = weight * Q
        print(f"  K={K:5.3f} | P={row['PRICE']:6.4f} | Q={Q:7.5f} | dk={dk:6.4f} | w={weight:8.6f} | → {contrib:8.6f}")
        sum_ += contrib
        #print(f"  K={K:5.3f} | P={row['PRICE']:6.4f} | Q={Q:7.5f} | dk={dk:6.4f} | w={weight:8.6f} | → {sum_:8.6f}")

    print(f"📈 T={T:.4f}, F={F:.4f}, K0={K0:.4f}, sum={sum_:.6f}")

    # ✅ 9. 计算方差
    variance = (2 / T) * sum_ - ((F / K0 - 1) ** 2) / T
    return max(variance, 1e-6)


# -------------------------------
# ✅ 真实 VIX 计算函数（加插值日志）
# -------------------------------
def calculate_real_vix(df_300, trade_date_str: str, risk_free_rate: float = 0.02):
    current_date = datetime.strptime(trade_date_str, "%Y%m%d").date()
    today = pd.Timestamp(current_date)

    df = df_300.dropna(subset=['EXPIRE_DATE_DT', 'T_YEARS', 'PRICE', 'STRIKE']).copy()
    df = df[(df['IMPLC_VOLATLTY'] > 0.01) & (df['IMPLC_VOLATLTY'] < 1.0)]
    if df.empty:
        print("❌ 数据为空，无法计算 VIX")
        return np.nan

    expirations = sorted(df['EXPIRE_DATE_DT'].unique())
    if len(expirations) < 2:
        print("❌ 不足两个到期日")
        return np.nan

    target_T = 30 / 365.0
    valid_pairs = []
    for i in range(len(expirations) - 1):
        t1 = expirations[i]
        t2 = expirations[i + 1]
        T1 = (pd.Timestamp(t1) - today).days / 365.0
        T2 = (pd.Timestamp(t2) - today).days / 365.0
        if T1 < target_T < T2:
            valid_pairs.append((t1, t2, T1, T2))

    if not valid_pairs:
        print("⚠️ 无满足 T1<30<T2 的组合，使用最近两个")
        t1, t2 = expirations[0], expirations[1]
        T1 = (pd.Timestamp(t1) - today).days / 365.0
        T2 = (pd.Timestamp(t2) - today).days / 365.0
    else:
        t1, t2, T1, T2 = valid_pairs[0]

    print(f"🎯 使用到期日: {t1.strftime('%Y-%m-%d')} ({T1 * 365:.1f}天), {t2.strftime('%Y-%m-%d')} ({T2 * 365:.1f}天)")

    term1 = df[df['EXPIRE_DATE_DT'] == t1].copy()
    term2 = df[df['EXPIRE_DATE_DT'] == t2].copy()
    print(f'T1={T1}, T2={T2}')

    try:
        var1 = _compute_variance(term1, T1, risk_free_rate)
        var2 = _compute_variance(term2, T2, risk_free_rate)
    except Exception as e:
        print(f"❌ 方差计算异常: {e}")
        import traceback
        traceback.print_exc()
        return np.nan

    if np.isnan(var1) or np.isnan(var2) or var1 <= 0 or var2 <= 0:
        print("⚠️ 方差非正，回退")
        return np.nan

    vix_squared = ((T2 - target_T) * var1 + (target_T - T1) * var2) / (T2 - T1)
    vix = np.sqrt(vix_squared) * 100

    # ✅ 添加插值日志
    print(f"📊 插值得到 30 天方差: {vix_squared:.6f} → VIX = {vix:.2f}")
    return max(vix, 5.0)


# -------------------------------
# 6. 主函数（移除保存逻辑）
# -------------------------------
def main():
    trade_date = "20250819"
    print("🚀 开始执行 300ETF 恐慌指数监控...")

    risk_df = fetch_risk_data(trade_date)
    if risk_df is None:
        return

    df_temp = risk_df[risk_df['CONTRACT_ID'].str.startswith('510300')].copy()
    df_temp['EXPIRE_YYMM'] = df_temp['CONTRACT_ID'].str.extract(r'[CP](\d{4})')[0]
    all_yymm = df_temp['EXPIRE_YYMM'].dropna().unique()
    print(f"🔍 发现 {len(all_yymm)} 个到期月份: {sorted(all_yymm)}")

    price_df_dict = {}
    for yymm in all_yymm:
        price_df = fetch_price_data(symbol="华泰柏瑞沪深300ETF期权", end_month=yymm)
        if price_df is not None:
            price_df_dict[yymm] = price_df

    df_300 = extract_and_merge_data(risk_df, price_df_dict, trade_date)
    if df_300 is None or df_300.empty:
        print("❌ 数据合并后为空，程序终止。")
        return

    print("\n🔍 正在计算【真实VIX】（CBOE官方方法）...")
    try:
        vix_value = calculate_real_vix(df_300, trade_date, risk_free_rate=RISK_FREE_RATE)
        if np.isnan(vix_value):
            raise ValueError("VIX 计算结果为 NaN")
        print(f"🎯 真实 A股300ETF恐慌指数（VIX）: {vix_value:.2f}")
    except Exception as e:
        print(f"❌ 真实VIX计算失败: {e}")
        vix_value = df_300['IMPLC_VOLATLTY'].mean() * 100
        print(f"✅ 回退使用平均隐含波动率: {vix_value:.2f}")

    print("\n🎉 全部完成！")


if __name__ == "__main__":
    main()