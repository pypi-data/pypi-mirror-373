import datetime as dtm
from pyqqq.utils.market_schedule import is_full_day_closed


def print_invest_result(dataframe, initial_cash, risk_free_rate=0.02, save_csv=False, csv_path="invest_result.csv"):
    """투자 성과를 분석하고 주요 성과 지표를 계산하여 출력합니다.

    이 함수는 일별 거래 데이터를 기반으로 CAGR, Sharpe Ratio, Maximum Drawdown 등의
    주요 투자 성과 지표를 계산합니다. 휴장일은 자동으로 제외되며, 모든 지표는
    연율화(252 거래일 기준)하여 계산됩니다.

    Args:
        dataframe (pandas.DataFrame): 일별 거래 결과가 담긴 데이터프레임

            - earn_money: 일별 수익 (매매 후 현금 + 보유 주식 가치 기준)
            - account_value: 일별 계좌 가치 없는 경우 earn_money와 initial_cash로 자동 계산
            - datetime.date 타입의 거래일

        initial_cash (float): 초기 투자 금액

        risk_free_rate (float, optional): 무위험 수익률(연율).
            Defaults to 0.02 (2%).
            Sharpe Ratio 계산에 사용됩니다.

        save_csv (bool, optional): 분석 결과를 CSV 파일로 저장할지 여부.
            Defaults to False.

        csv_path (str, optional): CSV 파일 저장 경로.
            Defaults to "invest_result.csv".

    Prints:
        다음 성과 지표들을 계산하여 출력합니다:

        1. CAGR (Compound Annual Growth Rate)
            - 연평균 성장률
            - (최종가치/초기가치)^(252/투자일수) - 1

        2. Sharpe Ratio
            - 무위험 수익률 대비 위험 조정 수익률
            - (초과수익률 평균/초과수익률 표준편차) * sqrt(252)

        3. Maximum Drawdown
            - 고점 대비 최대 하락폭
            - max(1 - 현재가치/누적최대가치)

    Example:

    .. highlight:: python
    .. code-block:: python

        import pandas as pd
        import datetime as dtm

        # 일별 거래 결과 데이터 준비
        data = {
            'earn_money': [1000, 2000, -500, 1500],
            'account_value': [101000, 103000, 102500, 104000]
        }
        dates = [
            dtm.date(2023, 1, 2),
            dtm.date(2023, 1, 3),
            dtm.date(2023, 1, 4),
            dtm.date(2023, 1, 5)
        ]
        df = pd.DataFrame(data, index=dates)

        # 성과 분석 실행
        print_invest_result(
            dataframe=df,
            initial_cash=100000,
            risk_free_rate=0.02,
            save_csv=True,
            csv_path="trading_results.csv"
        )

    Notes:
        - 휴장일은 자동으로 제외됩니다 (is_full_day_closed 함수 사용)
        - 모든 수익률 지표는 252 거래일 기준으로 연율화됩니다
        - account_value가 제공되지 않은 경우, earn_money의 누적합과
          initial_cash를 사용하여 자동 계산됩니다
        - 일별 수익률은 earn_money/account_value로 계산됩니다
        - 무위험 수익률은 일별로 환산되어 계산에 사용됩니다

    Raises:
        KeyError: dataframe에 필수 컬럼 'earn_money'가 없는 경우
    """

    print("====== invest result ======")
    df = dataframe.copy(deep=True)
    df["trading_date"] = ~df.index.to_series().apply(lambda x: is_full_day_closed(dtm.datetime.combine(x, dtm.time(10, 30))))
    df = df.loc[df["trading_date"]]
    if "account_value" not in df.columns:
        df["account_value"] = df["earn_money"].cumsum() + initial_cash
    df["daily_pnl"] = df["earn_money"] / df["account_value"]

    # cagr
    days = len(df)
    cagr = (df["account_value"].iloc[-1] / initial_cash) ** (252 / days) - 1
    print(f"cagr: {cagr * 100:.3f}%")

    # sharpe ratio
    daily_risk_free_rate = (1 + risk_free_rate) ** (1 / 252) - 1
    df["daily_excess_return"] = df["daily_pnl"] - daily_risk_free_rate
    mean_excess_return = df["daily_excess_return"].mean()
    std_excess_return = df["daily_excess_return"].std()
    sharpe_ratio = mean_excess_return / std_excess_return * (252 ** 0.5)
    print(f"sharpe ratio: {sharpe_ratio:.3f}")

    # max drawdown
    df["cummax"] = df["account_value"].cummax()
    df["drawdown"] = 1 - df["account_value"] / df["cummax"]
    max_drawdown = df["drawdown"].max()
    print(f"max drawdown: {max_drawdown*100:.3f}%")
    print("===========================")

    if save_csv:
        df.to_csv(csv_path)
