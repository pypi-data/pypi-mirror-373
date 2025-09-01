from pyqqq.brokerage.ebest.oauth import EBestAuth
from pyqqq.brokerage.ebest.tr_client import (
    EBestTRClient,
    EBestTRWebsocketClient,
    EBestTRWebsocketKeepConnectionStatus,
)
from pyqqq.utils.limiter import CallLimiter
from pyqqq.utils.market_schedule import get_market_schedule
from typing import AsyncGenerator
import asyncio
import datetime as dtm
import json
import websockets


class EBestDomesticStock:
    """
    LS(구 이베스트투자)증권 국내주식 API
    """

    def __init__(self, auth: EBestAuth, corp_data: dict = None):
        self.auth = auth
        self.corp_data = corp_data
        self.tr_client = EBestTRClient(auth)

    def _tr_request(self, *args, **kwargs):
        return self.tr_client.request(*args, **kwargs)

    def get_asset_list(self, market_type: str = "0") -> list:
        """
        ([주식]기타) 주식종목조회 API용 (t8436)

        Args:
            market_type (str): 시장유형 (0:전체 1:코스피 2:코스닥)

        Returns:
            dict:

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output (list): 주식 종목 리스트

                - hname (str): 종목명
                - shcode (str): 단축코드
                - expcode (str): 확장코드
                - etfgubun (str): ETF구분 (0:일반 1:ETF 2:ETN)
                - uplmtprice (float): 상한가
                - dnlmtprice (float): 하한가
                - jnilclose (float): 전일종가
                - memedan (float): 주문수량단위
                - recprice (int): 기준가
                - gubun (str): 구분 (1:코스피 2:코스닥)
                - bu12gubun (str): 12월결산월
                - spac_gubun (str): 기업인수목적회사여부 (Y:기업인수목적회사)
                - filler (str): filler
        """

        CallLimiter().wait_limit_rate(2, scope="ebest/t8436")

        assert market_type in ["0", "1", "2"], "Invalid market type"

        tr_code = "t8436"
        req_body = {f"{tr_code}InBlock": {"gubun": market_type}}

        res_body, _ = self._tr_request("/stock/etc", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output": res_body.get("t8436OutBlock", []),
        }

        return result

    def get_price(self, asset_code: str, exchgubun: str = "K") -> dict:
        """
        ([주식]시세) 주식현재가(시세)조회 (t1102)

        Args:
            asset_code (str): 종목 코드
            exchgubun (str): 거래소 코드 (K:KRX N:NXT U:통합)

        Returns:
            dict: 종목의 현재가 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output (list): 종목의 현재가 정보
        """
        assert len(asset_code) == 6, "Invalid asset code"
        assert exchgubun in ["K", "N", "U"], "Invalid exchange code"

        CallLimiter().wait_limit_rate(3, scope="ebest/t1102")

        tr_code = "t1102"
        req_body = {
            f"{tr_code}InBlock": {"shcode": asset_code, "exchgubun": exchgubun},
        }
        res_body, _ = self._tr_request("/stock/market-data", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output": res_body.get("t1102OutBlock", []),
        }

        return result

    def get_stock_time_conclude(
        self,
        asset_code: str,
        cvolume: int,
        start_time: dtm.time,
        end_time: dtm.time,
        cts_time: str = "",
        tr_cont_key: str = "",
    ) -> dict:
        """
        ([주식]시세) 주식시간대별체결조회 (t1301)

        Args:
            asset_code (str): 종목 코드
            cvolume (int): 특이거래량
            start_time (dtm.time): 시작시간 - 장시작시간 이후
            end_time (dtm.time): 종료시간 - 장종료시간 이전
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 주식 시간대별 체결 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output (list): 주식 시간대별 체결 정보
        """

        CallLimiter().wait_limit_rate(2, scope="ebest/t1301")

        assert len(asset_code) == 6, "Invalid asset code"

        tr_code = "t1301"
        tr_cont = "Y" if cts_time else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": asset_code,
                "cvolume": cvolume,
                "starttime": start_time.strftime("%H%M"),
                "endtime": end_time.strftime("%H%M"),
                "cts_time": cts_time,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/market-data",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output": res_body.get("t1301OutBlock", []),
        }

        return result

    def get_stock_minute_prices(
        self,
        shcode: str,
        gubun: str,
        cnt=900,
        cts_time: str = "",
        tr_cont_key: str = "",
        exchgubun: str = "K",
    ):
        """
        ([주식]시세) 주식분별주가조회 (t1302)

        Args:
            shcode (str): 종목 코드
            gubun (str): 주기구분 (0:30초 1:1분 2:3분 3:5분 4:10분 5:30분 6:60분)
            cnt (int): 조회건수 - 최대 900
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력
            exchgubun (str): 거래소 코드 (K:KRX N:NXT U:통합)

        Returns:
            dict: 주식 분별 주가 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속 조회를 위한 cts_time 필드를 포함
            - output2 (list): 주식 분별 주가 정보
        """

        CallLimiter().wait_limit_rate(1, scope="ebest/t1302")

        assert len(shcode) == 6, "Invalid asset code"
        assert gubun in ["0", "1", "2", "3", "4", "5", "6"], "Invalid gubun"
        assert exchgubun in ["K", "N", "U"], "Invalid exchange code"

        tr_code = "t1302"
        tr_cont = "Y" if cts_time else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": shcode,
                "gubun": gubun,
                "cnt": cnt,
                "time": cts_time,
                "exchgubun": exchgubun,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/market-data",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("t1302OutBlock", {}),
            "output2": res_body.get("t1302OutBlock1", []),
        }

        return result

    def get_period_profit(
        self,
        start_date: dtm.date,
        end_date: dtm.date,
        term_type: str = "1",
        tr_cont_key: str = "",
    ):
        """
        ([주식]계좌) 주식계좌 기간별 수익률 상세 (FOCCQ33600)

        Args:
            start_date (dtm.date): 시작일자
            end_date (dtm.date): 종료일자
            term_type (str): 기간구분 (1:일 2:주 3:월)

        Returns:
            dict: 주식 계좌 기간별 수익률 상세 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 조회 정보
                - RecCnt (int): 레코드갯수
                - AcntNo (str): 계좌번호
                - QrySrtDt (str): 조회시작일자
                - QryEndDt (str): 조회종료일자
                - TermTp (str): 기간구분

            - output2 (dict): 계좌 거래 정보
                - RecCnt (int): 레코드갯수
                - AcntNo (str): 계좌번호
                - BnsctrAmt (int): 매매약정금액
                - MnyinAmt (int): 입금금액
                - MnyoutAmt (int): 출금금액
                - InvstAvrbalPramt (int): 투자원금평잔금액
                - InvstPlAmt (int): 투자손익금액
                - InvstErnrat (float): 투자수익률

            - output3 (list): 기간별 수익률 상세 정보
                - BaseDt (str): 기준일자
                - FdEvalAmt (int): 기초평가금액
                - EotEvalAmt (int): 기말평가금액
                - InvstAvrbalPramt (int): 투자원금평잔금액
                - BnsctrAmt (int): 매매약정금액
                - MnyinSecinAmt (int): 입금고액
                - MnyoutSecoutAmt (int): 출금고액
                - EvalPnlAmt (int): 평가손익금액
                - TermErnrat (float): 기간수익률
                - Idx (float): 지수
        """
        tr_code = "FOCCQ33600"
        tr_cont = "Y" if tr_cont_key else "N"

        assert term_type in ["1", "2", "3"], "Invalid term_type"

        CallLimiter().wait_limit_rate(1, scope=f"ebest/{tr_code}")

        req_body = {
            f"{tr_code}InBlock1": {
                "QrySrtDt": start_date.strftime("%Y%m%d"),
                "QryEndDt": end_date.strftime("%Y%m%d"),
                "TermTp": term_type,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/accno",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        output1 = res_body.get(f"{tr_code}OutBlock1", {})
        output2 = res_body.get(f"{tr_code}OutBlock2", {})
        output3 = res_body.get(f"{tr_code}OutBlock3", [])

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": output1,
            "output2": output2,
            "output3": output3,
        }

        return result

    def get_stock_tick_data_today_yesterday(
        self,
        daygb: int,
        timegb: int,
        shcode: str,
        endtime: dtm.time,
        cts_time: str = "",
        tr_cont_key: str = "",
        exchgubun: str = "K",
    ):
        """
        ([주식]시세) 주일당일전일분틱조회 (t1310)

        Args:
            daygb (int): 일자구분 (0:당일 1:전일)
            timegb (int): 시간구분 (0:분 1:틱)
            shcode (str): 종목 코드
            endtime (dtm.time): 종료시간 outblock.chetime <= endtime 인 데이터 조회됨
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력
            exchgubun (str): 거래소 코드 (K:KRX N:NXT U:통합)

        Returns:
            dict: 응답 데이터

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속 조회를 위한 cts_time 필드를 포함
            - output2 (list): 분틱 정보
        """
        CallLimiter().wait_limit_rate(1, scope="ebest/t1310")

        assert daygb in [0, 1], "Invalid daygb"
        assert timegb in [0, 1], "Invalid timegb"
        assert len(shcode) >= 6, "Invalid asset code"
        assert isinstance(endtime, dtm.time), "Invalid endtime"
        assert exchgubun in ["K", "N", "U"], "Invalid exchange code"

        tr_code = "t1310"
        req_body = {
            f"{tr_code}InBlock": {
                "daygb": str(daygb),
                "timegb": str(timegb),
                "shcode": shcode,
                "endtime": endtime.strftime("%H%M"),
                "cts_time": cts_time,
                "exchgubun": exchgubun,
            }
        }

        tr_cont = "Y" if cts_time else "N"

        res_body, res_header = self._tr_request(
            "/stock/market-data",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("t1310OutBlock", {}),
            "output2": res_body.get("t1310OutBlock1", []),
        }

        return result

    def get_stock_chart_dwmy(
        self,
        shcode: str,
        gubun: str,
        edate: dtm.date,
        sdate: dtm.date = None,
        qrycnt: int = 500,
        cts_date: str = "",
        comp_yn: bool = False,
        sujung_yn: bool = True,
        tr_cont_key: str = "",
    ):
        """
        ([주식]차트) API전용주식챠트(일주월년) (t8410)

        Args:
            shcode (str): 종목 코드
            gubun (str): 주기구분 (d:일 w:주 m:월 y:년)
            edate (dtm.date): 종료일자 - 처음조회기준일(LE) 처음 조회일 경우 이 값 기준으로 조회
            sdate (dtm.date): 시작일자 - 기본값(None)인 경우 edate 기준으로  qrycnt 만큼 조회. 조회구간을 설정하여 필터링하고 싶은 경우 입력.
            qrycnt (int): 요청건수 (최대-압축:2000비압축:500)
            cts_date (str): 연속일자 - 연속조회시 OutBlock의 동일필드 입력
            comp_yn (bool): 압축여부 (True:압축 False:비압축)
            sujung_yn (bool): 수정주가적용여부 (True:수정주가적용 False:비적용)
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 주식 차트 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 전일/당일 시세 정보
                - shcode (str): 단축코드
                - jisiga (int): 전일시가
                - jihigh (int): 전일고가
                - jilow (int): 전일저가
                - jiclose (int): 전일종가
                - jivolume (int): 전일거래량
                - disiga (int): 당일시가
                - dihigh (int): 당일고가
                - dilow (int): 당일저가
                - diclose (int): 당일종가
                - highend (int): 상한가
                - lowend (int): 하한가
                - cts_date (str): 연속일자
                - s_time (str): 장시작시간 (HHMMSS)
                - e_time (str): 장종료시간 (HHMMSS)
                - dshmin (int): 동시호가처리시간 (MM:분)
                - rec_count (int): 레코드카운트
                - svi_uplmtprice (float): 정적VI상한가
                - svi_dnlmtprice (float): 정적VI하한가
            - output2 (list): 주기별 시세 정보
                - date (str): 날짜
                - open (int): 시가
                - high (int): 고가
                - low (int): 저가
                - close (int): 종가
                - jdiff_vol (int): 거래량
                - value (int): 거래대금
                - jongchk (str): 수정구분
                - rate (float): 수정비율
                - pricechk (int): 수정가반영항목
                - ratevalue (int): 수정비율반영거래대금
                - sign (str): 종가등락구분 (1:상한 2:상승 3:보합 4:하한 5:하락 주식일만사용)
        """

        CallLimiter().wait_limit_rate(1, scope="ebest/t8410")

        assert len(shcode) == 6, "Invalid asset code"
        assert gubun.lower() in ["d", "w", "m", "y"], "Invalid gubun"

        tr_code = "t8410"
        tr_cont = "Y" if cts_date else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": shcode,
                "gubun": {"d": "2", "w": "3", "m": "4", "y": "5"}[gubun.lower()],
                "qrycnt": qrycnt,
                "sdate": sdate.strftime("%Y%m%d") if sdate else "",
                "edate": edate.strftime("%Y%m%d"),
                "cts_date": cts_date,
                "comp_yn": "Y" if comp_yn else "N",
                "sujung": "Y" if sujung_yn else "N",
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/chart",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("t8410OutBlock", {}),
            "output2": res_body.get("t8410OutBlock1", []),
        }

        return result

    def get_stock_chart_minutes(
        self,
        shcode: str,
        ncnt: int,
        qrycnt: int,
        nday: int,
        edate: dtm.date,
        sdate: dtm.date = None,
        cts_date: str = "",
        cts_time: str = "",
        comp_yn: bool = False,
        tr_cont_key: str = "",
    ) -> dict:
        """
        ([주식]차트) 주식분별주가조회 (t8412)

        Args:
            shcode (str): 종목 코드
            ncnt (int): 단위(n분)
            qrycnt (int): 요청건수 (최대-압축:2000비압축:500)
            nday (int): 조회영업일수(0:미사용 1>=사용)
            edate (dtm.date): 종료일자 - 처음조회기준일(LE) 처음 조회일 경우 이 값 기준으로 조회
            sdate (dtm.date): 시작일자 - 기본값(None)인 경우 edate 기준으로  qrycnt 만큼 조회. 조회구간을 설정하여 필터링하고 싶은 경우 입력.
            cts_date (str): 연속일자 - 연속조회시 OutBlock의 동일필드 입력
            cts_time (str): 연속시간 - 연속조회시 OutBlock의 동일필드 입력
            comp_yn (bool): 압축여부 (True:압축 False:비압축)
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 주식 차트 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 전일/당일 시세 정보
            - output2 (list): 단위 별 주식 차트 정보
        """

        CallLimiter().wait_limit_rate(1, scope="ebest/t8412")

        tr_code = "t8412"
        tr_cont = "Y" if cts_date else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "shcode": shcode,
                "ncnt": ncnt,
                "qrycnt": qrycnt,
                "nday": str(nday),
                "sdate": sdate.strftime("%Y%m%d") if sdate else "",
                "edate": edate.strftime("%Y%m%d"),
                "cts_date": cts_date,
                "cts_time": cts_time,
                "comp_yn": "Y" if comp_yn else "N",
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/chart",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("t8412OutBlock", {}),
            "output2": res_body.get("t8412OutBlock1", []),
        }

        return result

    def get_account_deposit_orderable_total_evaluation(self) -> dict:
        """
        ([주식]계좌) 현물계좌예수금 주문가능금액 총평가 조회 (CSPAQ12200)

        Returns:
            dict: 주문가능금액 총평가 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 계좌기본정보
            - output2 (dict): 주문가능금액 총평가 정보
        """

        CallLimiter().wait_limit_rate(1, scope="ebest/CSPAQ12200")

        tr_code = "CSPAQ12200"
        req_body = {f"{tr_code}InBlock1": {"BalCreTp": "0"}}

        res_body, _ = self._tr_request("/stock/accno", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("CSPAQ12200OutBlock1", {}),
            "output2": res_body.get("CSPAQ12200OutBlock2", {}),
        }

        return result

    def get_account_orderable_quantity(
        self,
        bns_tp_code: int,
        isu_no: str,
        ord_prc: int,
    ) -> dict:
        """
        ([주식]계좌) 현물계좌증거금률별주문가능수량조회 (CSPBQ00200)

        Args:
            bns_tp_code (int): 매매구분 (1:매도 2:매수)
            isu_no (str): 종목번호
            ord_prc (int): 주문가격

        Returns:
            dict: 주문가능수량 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 요청 정보
            - output2 (dict): 계좌 및 증거금률 별 주문가능수량 정보
        """

        CallLimiter().wait_limit_rate(1, scope="ebest/CSPBQ00200")

        assert bns_tp_code in [1, 2], "Invalid bns_tp_code"
        assert len(isu_no) == 6 or (len(isu_no) == 7 and isu_no[0] == "A"), "Invalid isu_no"

        tr_code = "CSPBQ00200"
        req_body = {
            f"{tr_code}InBlock1": {
                "BnsTpCode": str(bns_tp_code),
                "IsuNo": "A" + isu_no if len(isu_no) == 6 else isu_no,
                "OrdPrc": ord_prc,
            }
        }

        res_body, _ = self._tr_request("/stock/accno", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("CSPBQ00200OutBlock1", {}),
            "output2": res_body.get("CSPBQ00200OutBlock2", {}),
        }

        return result

    def get_stock_balance(
        self,
        prcgb: int = 1,
        chegb: int = 0,
        dangb: int = 0,
        charge: int = 0,
        cts_expcode: str = "",
        tr_cont_key: str = "",
    ):
        """
        ([주식]계좌) 주식잔고2조회 (t0424)

        Args:
            prcgb (int): 단가구분 (1:평균단가, 2:BEP단가)
            chegb (int): 체결구분 (0:결제기준잔고, 2:체결기준(잔고가 0이 아닌 종목만 조회)
            dangb (int): 단일가구분 (0:정규장, 1:시장외단일가)
            charge (int): 수수료구분 (0:제비용미포함, 1:제비용포함)
            cts_expcode (str): 연속종목코드 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 주식 잔고 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 계좌 정보
            - output2 (list): 종목 별 잔고 정보
        """

        CallLimiter().wait_limit_rate(1, scope="ebest/t0424")

        assert prcgb in [1, 2], "Invalid prcgb"
        assert chegb in [0, 2], "Invalid chegb"
        assert dangb in [0, 1], "Invalid dangb"
        assert charge in [0, 1], "Invalid charge"

        tr_code = "t0424"
        tr_cont = "Y" if cts_expcode else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "prcgb": str(prcgb),
                "chegb": str(chegb),
                "dangb": str(dangb),
                "charge": str(charge),
                "cts_expcode": cts_expcode,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/accno",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get("t0424OutBlock", []),
            "output2": res_body.get("t0424OutBlock1", []),
        }

        return result

    def get_today_pnl_and_trades(
        self,
        tr_cont: str = "N",
        tr_cont_key: str = "",
        cts_medosu: str = "",
        cts_expcode: str = "",
        cts_price: str = "",
        cts_middiv: str = "",
    ) -> dict:
        """
        ([주식]계좌) 주식당일실현손익/체결내역조회 (t0150)

        Args:
            tr_cont (str): 연속조회여부
            tr_cont_key (str): 연속조회키
            cts_medosu (str): 연속매도수구분 - 연속조회시 OutBlock의 동일필드 입력
            cts_expcode (str): 연속종목코드 - 연속조회시 OutBlock의 동일필드 입력
            cts_price (str): 연속가격 - 연속조회시 OutBlock의 동일필드 입력
            cts_middiv (str): 연속미체결구분 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 주식 당일 실현손익/체결 내역 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 당일 실현손익 정보
            - output2 (list): 종목별 정보
        """
        CallLimiter().wait_limit_rate(2, scope="ebest/t0150")

        tr_code = "t0150"
        req_body = {
            f"{tr_code}InBlock": {
                "cts_medosu": cts_medosu,
                "cts_expcode": cts_expcode,
                "cts_price": cts_price,
                "cts_middiv": cts_middiv,
            }
        }
        res_body, res_header = self._tr_request(
            "/stock/accno",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("t0150OutBlock", {}),
            "output2": res_body.get("t0150OutBlock1", []),
        }

        return result

    def get_deposit_order_list(
        self,
        isu_no: str = "",
        ord_mkt_code: str = "00",
        bns_tp_code: str = "0",
        exec_yn: str = "0",
        ord_dt: str = None,
        srt_ord_no2: str = "999999999",
        bkseq_tp_code: str = "0",
        ord_ptn_code: str = "00",
    ) -> dict:
        """
        ([주식]계좌) 현물계좌 주문체결내역 조회(API) (CSPAQ13700)
        """
        CallLimiter().wait_limit_rate(1, scope="ebest/CSPAQ13700")

        tr_code = "CSPAQ13700"
        if ord_dt is None:
            ord_dt = dtm.date.today().strftime("%Y%m%d")

        req_body = {
            f"{tr_code}InBlock1": {
                "IsuNo": isu_no,
                "OrdMktCode": ord_mkt_code,
                "BnsTpCode": bns_tp_code,
                "ExecYn": exec_yn,
                "OrdDt": ord_dt,
                "SrtOrdNo2": int(srt_ord_no2),
                "BkseqTpCode": bkseq_tp_code,
                "OrdPtnCode": ord_ptn_code,
            }
        }

        res_body, res_header = self._tr_request("/stock/accno", tr_code, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("CSPAQ13700OutBlock1", {}),
            "output2": res_body.get("CSPAQ13700OutBlock2", {}),
            "output3": res_body.get("CSPAQ13700OutBlock3", {}),
        }

        return result

    def get_order_list(
        self,
        chegb: int = 0,
        medosu: int = 0,
        sortgb: int = 2,
        expcode: str = "",
        cts_ordno: str = "",
        tr_cont_key: str = "",
    ) -> dict:
        """
        ([주식]계좌) 주식체결/미체결 (t0425)

        Args:
            chegb (int): 체결구분 (0:전체, 1:체결, 2:미체결)
            medosu (int): 매도수구분 (0:전체, 1:매도, 2:매수)
            sortgb (int): 정렬기준 (1:주문번호 역순, 2:주문번호 순)
            expcode (str): 종목코드. 전체조회 시 입력값 없음
            cts_ordno (str): 연속주문번호 - 연속조회시 OutBlock의 동일필드 입력
            tr_cont_key (str): 연속조회키 - 연속조회시 이전 응답 헤더의 동일필드 입력

        Returns:
            dict: 주식 체결/미체결 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 총 주문/체결 정보
            - output2 (list): 주문 별 정보
        """
        CallLimiter().wait_limit_rate(1, scope="ebest/t0425")

        tr_code = "t0425"
        tr_cont = "Y" if cts_ordno else "N"

        req_body = {
            f"{tr_code}InBlock": {
                "chegb": str(chegb),
                "medosu": str(medosu),
                "sortgb": str(sortgb),
                "expcode": expcode,
                "cts_ordno": cts_ordno,
            }
        }

        res_body, res_header = self._tr_request(
            "/stock/accno",
            tr_code,
            tr_cont=tr_cont,
            tr_cont_key=tr_cont_key,
            body=req_body,
        )

        res_body.update(
            {
                "tr_cont": res_header.get("tr_cont", ""),
                "tr_cont_key": res_header.get("tr_cont_key", ""),
            }
        )

        if "t0425OutBlock" not in res_body:
            res_body["t0425OutBlock"] = {
                "tqty": 0,
                "tcheqty": 0,
                "tordrem": 0,
                "cmss": 0,
                "tamt": 0,
                "tmdamt": 0,
                "tmsamt": 0,
                "tax": 0,
                "cts_ordno": "",
            }

        if "t0425OutBlock1" not in res_body:
            res_body["t0425OutBlock1"] = []

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body["t0425OutBlock"],
            "output2": res_body["t0425OutBlock1"],
        }

        return result

    def create_order(
        self,
        isu_no: str,
        ord_qty: int,
        ord_prc: int,
        bns_tp_code: int,
        ord_prc_ptn_code: str,
        mgntrn_code: str = "000",
        load_dt: dtm.date = None,
        ord_cndi_tp_code: int = "0",
    ) -> dict:
        """
        ([주식]주문) 현물주문 (CSPAT00601)

        Args:
            isu_no (str): 종목번호

                | 주식/ETF: (종목코드) or A+종목코드
                | ELW: J+종목코드
                | ETN: Q+종목코드

            ord_qty (int): 주문수량
            ord_prc (int): 주문가격
            bns_tp_code (int): 매매구분 (1:매도 2:매수)
            ord_prc_ptn_code (str): 호가유형코드

                | '00: 지정가
                | '03': 시장가
                | '05': 조건부지정가
                | '06': 최유리지정가
                | '07': 최우선지정가
                | '61': 장개시전시간외종가
                | '81': 시간외단일가매매
                | '82': 시간외종가

            mgntrn_code (str): 신용거래코드

                | '000': 보통
                | '003': 유통/자기융자신규
                | '005': 유통대주신규
                | '007': 자기대주신규
                | '101': 유통융자상환
                | '103': 자기융자상환
                | '105': 유통대주상환
                | '107': 자기대주상환
                | '180': 유통대주주문취소

            load_dt (dtm.date): 대출일
            ord_cndi_tp_code (int): 주문조건구분 (0:없음 1:IOC 2:FOK)

        Returns:
            dict: 주문 결과

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 주문 결과
            - output2 (dict): 주문 결과
        """
        CallLimiter().wait_limit_rate(10, scope="ebest/CSPAT00601")

        tr_cd = "CSPAT00601"
        req_body = {
            f"{tr_cd}InBlock1": {
                "IsuNo": isu_no,
                "OrdQty": ord_qty,
                "OrdPrc": ord_prc,
                "BnsTpCode": str(bns_tp_code),
                "OrdprcPtnCode": ord_prc_ptn_code,
                "MgntrnCode": mgntrn_code,
                "LoanDt": load_dt.strftime("%Y%m%d") if load_dt else "",
                "OrdCndiTpCode": str(ord_cndi_tp_code),
            }
        }

        res_body, _ = self._tr_request("/stock/order", tr_cd, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get(f"{tr_cd}OutBlock1", {}),
            "output2": res_body.get(f"{tr_cd}OutBlock2", {}),
        }

        return result

    def update_order(
        self,
        org_ord_no: str,
        isu_no: str,
        ord_qty: int,
        ord_prc_ptn_code: str,
        ord_cndi_tp_code: int = 0,
        ord_prc: int = 0,
    ) -> dict:
        """
        ([주식]주문) 현물정정주문 (CSPAT00701)

        Args:
            org_ord_no (str): 원주문번호
            isu_no (str): 종목번호
            ord_qty (int): 주문수량
            ord_prc_ptn_code (str): 호가유형코드

                | '00: 지정가
                | '03': 시장가
                | '05': 조건부지정가
                | '06': 최유리지정가
                | '07': 최우선지정가
                | '61': 장개시전시간외종가
                | '81': 시간외단일가매매
                | '82': 시간외종가

            ord_cndi_tp_code (int): 주문조건구분 (0:없음 1:IOC 2:FOK)
            ord_prc (int): 주문가격

        Returns:
            dict: 주문 결과

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 원 주문 정보
            - output2 (dict): 정정 주문 정보
        """

        CallLimiter().wait_limit_rate(3, scope="ebest/CSPAT00701")

        tr_cd = "CSPAT00701"
        req_body = {
            f"{tr_cd}InBlock1": {
                "OrgOrdNo": int(org_ord_no),
                "IsuNo": isu_no,
                "OrdQty": ord_qty,
                "OrdprcPtnCode": ord_prc_ptn_code,
                "OrdCndiTpCode": str(ord_cndi_tp_code),
                "OrdPrc": ord_prc,
            }
        }

        res_body, _ = self._tr_request("/stock/order", tr_cd, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get(f"{tr_cd}OutBlock1", {}),
            "output2": res_body.get(f"{tr_cd}OutBlock2", {}),
        }

        return result

    def cancel_order(self, org_ord_no: str, isu_no: str, ord_qty: int) -> dict:
        """
        ([주식]주문) 현물취소주문 (CSPAT00801)

        Args:
            org_ord_no (str): 원주문번호
            isu_no (str): 종목번호
            ord_qty (int): 주문수량

        Returns:
            dict: 주문 결과

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - output1 (dict): 원 주문 정보
            - output2 (dict): 취소 주문 정보

        """
        CallLimiter().wait_limit_rate(3, scope="ebest/CSPAT00801")

        tr_cd = "CSPAT00801"
        req_body = {
            f"{tr_cd}InBlock1": {
                "OrgOrdNo": int(org_ord_no),
                "IsuNo": isu_no,
                "OrdQty": ord_qty,
            }
        }

        res_body, _ = self._tr_request("/stock/order", tr_cd, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "output1": res_body.get(f"{tr_cd}OutBlock1", []),
            "output2": res_body.get(f"{tr_cd}OutBlock2", []),
        }

        return result

    def get_management_stocks(self, gubun: str, jongchk: str, cts_shcode: str = "", tr_cont_key: str = ""):
        """
        ([주식]시세) 관리/불성실/투자유의조회 (t1404)

        Args:
            gubun (str): 구분 (0:전체 1:코스피 2:코스닥)
            jongchk (str): 종목체크 (1:관리 2:불성실공시 3:투자유의 4.투자환기)
            cts_shcode (str): 연속종목코드 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 관리/불성실/투자유의 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속조회정보
            - output2 (list): 종목 별 정보
        """
        tr_cd = "t1404"
        req_body = {
            f"{tr_cd}InBlock": {
                "gubun": gubun,
                "jongchk": jongchk,
                "cts_shcode": cts_shcode,
            }
        }

        tr_cont = "Y" if cts_shcode else "N"

        res_body, _ = self._tr_request("/stock/market-data", tr_cd, tr_cont, tr_cont_key, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_body.get("tr_cont", ""),
            "tr_cont_key": res_body.get("tr_cont_key", ""),
            "output1": res_body.get("t1404OutBlock", {}),
            "output2": res_body.get("t1404OutBlock1", []),
        }

        return result

    def get_alert_stocks(self, gubun: str, jongchk: str, cts_shcode: str = "", tr_cont_key=""):
        """
        ([주식]시세) 투자경고/매매정지/정리매매조회 (t1405)

         Args:
            gubun (str): 구분 (0:전체 1:코스피 2:코스닥)
            jongchk (str): 종목체크 (1:투자경고 2:매매정지 3:정리매매 4:투자주의 5:투자위험 6:위험예고 7:단기과열지정 8:이상급등종목 9:상장주식수부족)
            cts_shcode (str): 연속종목코드 - 연속조회시 OutBlock의 동일필드 입력

        Returns:
            dict: 투자경고/매매정지/정리매매 정보

            - rsp_cd (str): 응답코드
            - rsp_msg (str): 응답메시지
            - tr_cont (str): 연속조회여부
            - tr_cont_key (str): 연속조회키
            - output1 (dict): 연속조회정보
            - output2 (list): 종목 별 정보

        """
        tr_cd = "t1405"
        req_body = {
            f"{tr_cd}InBlock": {
                "gubun": gubun,
                "jongchk": jongchk,
                "cts_shcode": cts_shcode,
            }
        }
        tr_cont = "Y" if cts_shcode else "N"
        res_body, res_header = self._tr_request("/stock/market-data", tr_cd, tr_cont, tr_cont_key, body=req_body)

        result = {
            "rsp_cd": res_body["rsp_cd"],
            "rsp_msg": res_body["rsp_msg"],
            "tr_cont": res_header.get("tr_cont", ""),
            "tr_cont_key": res_header.get("tr_cont_key", ""),
            "output1": res_body.get("t1405OutBlock", {}),
            "output2": res_body.get("t1405OutBlock1", []),
        }

        return result

    async def listen_trade_event(
        self,
        market: str,
        asset_codes: list[str],
        stop_event: asyncio.Event = None,
    ) -> AsyncGenerator:
        """
        체결 이벤트를 수신합니다.
        장/전후 시간외 종가 거래에 대한 체결 이벤트를 포함합니다.

        Args:
            market (str): 시장 (1:코스피 2:코스닥)
            asset_codes (list[str]): 종목 코드 리스트
        """

        assert market in ["1", "2"], "Invalid market"
        assert isinstance(asset_codes, list), "Invalid asset_codes"
        assert len(asset_codes) > 0, "Invalid asset_codes"

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            now = dtm.datetime.now()
            today = now.date()
            market_schedule = get_market_schedule(today)

            if market_schedule.full_day_closed:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            open_time = dtm.datetime.combine(today, market_schedule.open_time)
            close_time = dtm.datetime.combine(today, market_schedule.close_time)
            # 장전 시강외종가 거래 시작 시간
            pre_market_open_time = open_time - dtm.timedelta(minutes=30)
            # 장후 시간외종가 거래 종료 시간
            after_market_close_time = close_time + dtm.timedelta(minutes=30)
            time_margin = dtm.timedelta(minutes=5)

            if now < pre_market_open_time - time_margin:
                return EBestTRWebsocketKeepConnectionStatus.WAIT

            if now > after_market_close_time + time_margin:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            for asset_code in asset_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "3",
                            },
                            "body": {
                                "tr_cd": "S3_" if market == "1" else "K3_",
                                "tr_key": asset_code,
                            },
                        }
                    )
                )

                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        async for data in client.listen():
            yield data

    async def listen_after_market_single_price_trade_event(
        self,
        market: str,
        asset_codes: list[str],
        stop_event: asyncio.Event = None,
    ):
        """
        시간외단일가 체결 이벤트를 수신합니다.
        장 종료 30분 후부터 2시간 동안 시간외단일가 거래가 이루어집니다. (일반적으로 16:00~18:00)

        Args:
            market (str): 시장 (1:코스피 2:코스닥)
            asset_codes (list[str]): 종목 코드 리스트
        """

        assert market in ["1", "2"], "Invalid market"
        assert isinstance(asset_codes, list), "Invalid asset_codes"
        assert len(asset_codes) > 0, "Invalid asset_codes"

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            now = dtm.datetime.now()
            today = now.date()
            market_schedule = get_market_schedule(today)

            if market_schedule.full_day_closed:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            close_time = dtm.datetime.combine(today, market_schedule.close_time)

            # 장후 시간외 단일가 거래 시작 시간
            after_market_open_time = close_time + dtm.timedelta(minutes=30)
            # 장후 시간외 단일가 거래 종료 시간
            after_market_close_time = close_time + dtm.timedelta(hours=2, minutes=30)
            time_margin = dtm.timedelta(minutes=5)

            if now < after_market_open_time - time_margin:
                return EBestTRWebsocketKeepConnectionStatus.WAIT

            if now > after_market_close_time + time_margin:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            for asset_code in asset_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "3",
                            },
                            "body": {
                                "tr_cd": "DS3" if market == "1" else "DK3",
                                "tr_key": asset_code,
                            },
                        }
                    )
                )
                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        async for data in client.listen():
            yield data

    async def listen_orderbook_event(
        self,
        market: str,
        asset_codes: list[str],
        stop_event: asyncio.Event = None,
    ) -> AsyncGenerator:
        """
        호가잔량 이벤트를 수신합니다.

        Args:
            market (str): 시장 (1:코스피 2:코스닥)
            asset_codes (list[str]): 종목 코드 리스트
        """

        assert market in ["1", "2"], "Invalid market"
        assert isinstance(asset_codes, list), "Invalid asset_codes"
        assert len(asset_codes) > 0, "Invalid asset_codes"

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            now = dtm.datetime.now()
            today = now.date()
            market_schedule = get_market_schedule(today)

            if market_schedule.full_day_closed:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            open_time = dtm.datetime.combine(today, market_schedule.open_time)
            close_time = dtm.datetime.combine(today, market_schedule.close_time)
            # 장전 시강외종가 거래 시작 시간
            pre_market_open_time = open_time - dtm.timedelta(minutes=30)
            # 장후 시간외종가 거래 종료 시간
            after_market_close_time = close_time + dtm.timedelta(minutes=30)
            time_margin = dtm.timedelta(minutes=5)

            if now < pre_market_open_time - time_margin:
                return EBestTRWebsocketKeepConnectionStatus.WAIT

            if now > after_market_close_time + time_margin:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            for asset_code in asset_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "3",
                            },
                            "body": {
                                "tr_cd": "H1_" if market == "1" else "HA_",
                                "tr_key": asset_code,
                            },
                        }
                    )
                )

                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        async for data in client.listen():
            yield data

    async def listen_order_event(self, stop_event: asyncio.Event) -> AsyncGenerator:
        """
        주식 주문 이벤트를 실시간으로 수신하고 처리하는 비동기 제너레이터 함수입니다.

        이 함수는 지정된 이벤트를 사용하여 웹소켓 연결을 통해 주문 이벤트를 실시간으로 수신합니다.
        수신된 이벤트 데이터는 이벤트 유형에 따라 매핑된 값과 함께 반환됩니다.
        이 함수는 비동기적으로 동작하며, 이벤트 데이터는 제너레이터를 통해 소비할 수 있습니다.

        Args:
            stop_event (asyncio.Event): 이벤트 리스닝을 중지하기 위한 asyncio 이벤트.

        Yields:
            dict: 주문에 관한 상세 정보를 포함하는 사전형 데이터. 각 키는 다음과 같습니다:
                - event_type (string): 이벤트 유형 - accepted:접수, executed:체결, updated:정정, canceled:취소, denied:거부.
                - accno (string): Push 키.
                - accno1 (string): 계좌번호 1.
                - accno2 (string): 계좌번호 2.
                - acntnm (string): 계좌명.
                - admbrchno (string): 관리지점번호
                - agrgbrnno (string): 집계 지점 번호.
                - avrpchsprc (string): 평균매입가 - 실서버 데이터 미제공 필드
                - avrpchsprc (string): 평균 매입 가격.
                - basketno (string): 바스켓번호
                - bnstp (string): 매매구분 - 1:매도, 2:매수
                - bpno (string): 지점 번호.
                - brwmgmyn (string): 차입구분
                - cmsnamtexecamt (string): 수수료 체결 금액.
                - comid (string): COM ID.
                - compid (string): 이용사 번호.
                - compress (string): 압축 구분.
                - cont (string): 연속 구분.
                - contkey (string): 연속 키.
                - crdayruseexecval (string): 금일 재사용 체결 금액.
                - crdtexecamt (string): 신용 체결 금액.
                - crdtpldgruseamt (string): 신용담보재사용금
                - crdtuseamt (string): 사용신용담보재사용금
                - csgnmnymgn (string): 위탁증거금현금
                - csgnsubstmgn (string): 위탁증거금대용
                - cvrgordtp (string): 반대매매주문구분 - 0:일반 1:자동반대매매 2:지점반대매매 3:예비주문에대한 본주문
                - cvrgseqno (string): 반대매매일련번호
                - deposit (string): 예수금
                - dummy (string): DUMMY
                - encrypt (string): 암호 구분.
                - etfhogagb (string): 호가유형코드 - 0:없음 1:IOC 2:FOK 00:지정가 03:시장가 05:조건부지정가 06:최유리지정가 07:최우선지정가 09:자사주 10:매입인도(일반) 13:시장가 (IOC) 16:최유리지정가 (IOC) 18:사용안함 20:지정가(임의) 23:시장가(임의) 26:최유리지정가 (FOK) 41:부분충족(프리보드) 42:전량충족(프리보드) 51:장중대량 52:장중바스켓 61:장개시전시간외 62:사용안함 63:경매매 66:장전시간외경쟁대량 67:장개시전시간외대량 68:장개시전시간외바스켓 69:장개시전시간외자사주 71:신고대량전장시가 72:사용안함 73:신고대량종가 76:장중경쟁대량 77:장중대량 78:장중바스켓 79:사용안함 80:매입인도(당일) 81:시간외종가 82:시간외단일가 87:시간외대량 88:바스켓주문 89:시간외자사주 91:자사주스톡옵션 A1:stop order
                - eventid (string): I/F이벤트ID
                - execno (string): 체결 번호.
                - execprc (string): 체결 가격.
                - exectime (string): 체결 시각.
                - filler (string): 예비영역
                - fillter1 (string): 예비영역
                - flctqty (string): 변동수량
                - frgrunqno (string): 외국인 고유 번호.
                - funckey (string): 기능 키
                - futaccno (string): 선물계좌번호
                - futmarketgb (string): 선물상품구분
                - futsmkttp (string): 선물 시장 구분.
                - gmhogagb (string): 공매도호가구분 - 0:일반, 1:차입주식매도, 2:기타공매도
                - gmhogayn (string): 공매도가능여부 - 0:일반, 1:공매도
                - groupid (string): 그룹ID
                - grpId (string): 그룹 ID.
                - gubun (string): 헤더 구분.
                - hname (string): 종목명
                - hogagb (string): 주문조건 - 0:없음 1:IOC 2:FOK
                - ifid (string): I/F 일련 번호.
                - ifinfo (string): I/F 정보
                - Isunm (string): 종목명.
                - Isuno (string): 종목 번호.
                - itemno (string): 아이템번호
                - lang (string): 언어 구분
                - len (string): 헤더 길이.
                - lineseq (string): 라인 일련 번호.
                - Loandt (string): 대출일.
                - lpgb (string): 유동성공급자구분 - 0:해당없음, 1:유동성공급자
                - lptp (string): 유동성 공급자 구분.
                - marketgb (string): 시장 구분 - 00:비상장 10:코스피 11:채권 19:장외시장 20:코스닥 23:코넥스 30:프리보드 61:동경거래소 62:JASDAQ
                - mbrno (string): 회원사번호
                - mdfycnfprc (string): 정정 확인 가격.
                - mdfycnfqty (string): 정정 확인 수량.
                - media (string): 접속 매체.
                - mgempno (string): 관리사원번호
                - mgmtbrnno (string): 관리 지점 번호.
                - mgntrncode (string): 신용거래코드 - [신규] 000:보통 001:유통융자신규 003:자기융자신규 005:유통대주신규 007:자기대주신규 080:예탁주식담보융자신규 082:예탁채권담보융자신규 [상환] 101:유통융자상환 103:자기융자상환 105:유통대주상환 107:자기대주상환 111:유통융자전액상환 113:자기융자전액상환 180:예탁주식담보융자상환 182:예탁채권담보융자상환 188:담보대출전액상환
                - mnymgnrat (string): 현금 증거금률.
                - mnyordamt (string): 현금주문금액
                - msgcode (string): 메세지 코드
                - mtordseqno (string): 복수주문일련번호
                - nmcpysndno (string): 비회원사송신번호
                - offset (string): 공통 시작 지점.
                - opdrtnno (string): 운용 지시 번호.
                - ordablemny (string): 주문가능현금
                - ordableruseqty (string): 재사용가능수량(매도) - 실서버 데이터 미제공 필드
                - ordablesubstamt (string): 주문가능대용
                - ordablesubstamt (string): 주문 가능 대용.
                - ordacntno (string): 주문 계좌 번호.
                - ordamt (string): 주문금액
                - ordchegb (string): 주문 체결 구분 - 01:주문 02:정정 03:취소 11:체결 12:정정확인 13:취소확인 14:거부 A1:접수중 AC:접수완료
                - ordcmsnamt (string): 수수료주문금액
                - ordgb (string): 주문 구분 - 01:현금매도 02:현금매수 03:신용매도 04:신용매수 05:저축매도 06:저축매수 07:상품매도(대차) 09:상품매도 10:상품매수 11:선물대용매도(일반) 12:선물대용매도(반대) 13:현금매도(프) 14:현금매수(프) 15:현금매수(유가) 16:현금매수(정리) 17:상품매도(대차.프) 19:상품매도(프) 20:상품매수(프) 30:장외매매
                - ordmktcode (string): 주문 시장 코드.
                - ordno (string): 주문번호
                - ordordcancelqty (string): 원주문취소수량
                - ordprc (string): 주문 가격.
                - ordprcptncode (string): 호가 유형 코드 - 00:지정가 03:시장가 05:조건부지정가 06:최유리지정가 07:최우선지정가 09:자사주 10:매입인도(일반) 13:시장가 (IOC) 16:최유리지정가 (IOC) 18:사용안함 20:지정가(임의) 23:시장가(임의) 26:최유리지정가 (FOK) 41:부분충족(프리보드) 42:전량충족(프리보드) 51:장중대량 52:장중바스켓 61:장개시전시간외 62:사용안함 63:경매매 66:장전시간외경쟁대량 67:장개시전시간외대량 68:장개시전시간외바스켓 69:장개시전시간외자사주 71:신고대량전장시가 72:사용안함 73:신고대량종가 76:장중경쟁대량 77:장중대량 78:장중바스켓 79:사용안함 80:매입인도(당일) 81:시간외종가 82:시간외단일가 87:시간외대량 88:바스켓주문 89:시간외자사주 91:자사주스톡옵션 A1:stop order
                - ordprice (string): 주문 가격
                - ordptncode (string): 주문 유형 코드 - 00 해당없음 01:현금매도 02:현금매수 03신용매도 04:신용매수
                - ordqty (string): 주문수량
                - ordruseqty (string): 재사용주문수량
                - ordseqno (string): 주문회차
                - ordsubstamt (string): 주문대용금액
                - ordtm (string): 주문시각
                - ordtrdptncode (string):  주문 거래 유형 코드 - 00:위탁 01:신용 04:선물대용
                - ordtrxptncode (string): 주문 처리 유형 코드
                - orduserId (string): 주문자 ID.
                - ordxctptncode (string): 주문 체결 유형 코드 - 01:주문 02:정정 03:취소 11:체결 12:정정확인 13:취소확인 14:거부
                - orgordcancqty (string): 원주문 취소 수량.
                - orgordmdfyqty (string): 원주문 정정 수량
                - orgordundrqty (string): 원주문 미체결 수량
                - outgu (string): 메세지출력구분
                - pcbpno (string): 처리 지점 번호.
                - pchsamt (string): 매입금액 - 실서버 데이터 미제공 필드
                - pgmtype (string): 프로그램호가구분 - 00:일반 01:지수차익 02:지수비차익 03:주식차익 04:ETF차익(비차익제외) 05:ETF설정(비차익제외) 06:ETF차익(비차익) 07:ETF설정(비차익) 08:DR차익 09:ELW LP헷지 10:ETF LP헷지 11:주식옵션 LP헷지 12:장외파생상품헷지
                - prdayruseexecval (string): 전일 재사용 체결 금액.
                - prntordno (string): 모주문번호
                - procgb (string): 처리구분
                - proctm (string): 처리 시각.
                - prtno (string): 포트폴리오번호
                - prvip (string): 사설 IP.
                - pubip (string): 공인 IP.
                - regmktcode (string): 등록 시장 코드.
                - reqcnt (string): 요청 레코드 개수.
                - rjtqty (string): 거부 수량.
                - rsvordno (string): 예약주문번호
                - ruseableamt (string): 재사용 가능 금액.
                - ruseordamt (string): 재사용주문금액
                - secbalqty (string): 잔고수량 - 실서버 데이터 미제공 필드
                - secbalqtyd2 (string): 잔고수량(D2) - 실서버 데이터 미제공 필드
                - sellableqty (string): 매도주문가능수량 - 실서버 데이터 미제공 필드
                - seq (string): 전문 일련 번호.
                - shtcode (string): 단축종목번호.
                - shtnIsuno (string): 단축 종목 번호.
                - singb (string): 신용구분 - 000:보통, 001:유통융자신규, 003:자기융자신규, 005:유통대주신규, 007:자기대주신규, 011:미사용, 070:매도대금담보융자신규, 080:예탁주식담보융자신규, 082:예탁채권담보융자신규, 101:유통융자상환, 103:자기융자상환, 105:유통대주상환, 107:자기대주상환, 111:유통융자전액상환, 113:자기융자전액상환, 170:매도대금담보융자상환, 180:예탁주식담보융자상환, 182:예탁채권담보융자상환, 188:담보대출전액상환, 201:유통융자현금상환, 203:자기융자현금상환, 205:유통대주현물상환, 207:자기대주현물상환, 280:예탁주식담보융자현금상환, 282:예탁채권담보융자현금상환, 301:유통융자현금상환취소, 303:자기융자현금상환취소, 305:유통대주현물상환취소, 307:자기대주현물상환취소
                - spareordno (string): 예비주문번호
                - spareordqty (string): 예비주문수량
                - spotordableqty (string): 실물가능수량 - 실서버 데이터 미제공 필드
                - spotordqty (string): 실물주문수량
                - strtgcode (string): 전략코드
                - substamt (string): 대용금
                - termno (string): 단말번호
                - tongsingb (string): 통신매체구분
                - trchno (string): 트렌치 번호.
                - trcode (string): TR 코드. SONAT000: 신규 주문, SONAT001: 정정 주문, SONAT002: 취소 주문, SONAS100: 체결 확인.
                - trid (string): TR 추적 ID.
                - trsrc (string): 조회 발원지.
                - trtzxLevytp (string): 거래세 징수 구분.
                - unercsellordqty (string): 미체결매도주문수량 - 실서버 데이터 미제공 필드
                - user (string): 조작자 ID.
                - userid (string): 사용자 ID.
                - varhdlen (string): 가변 헤더 길이.
                - varlen (string): 가변 시스템 길이.
                - varmsglen (string): 가변 메시지 길이.


        Examples:
            >>> async for order_event in listen_order_event(stop_event):
            >>>    print(order_event)
            {'event_type': 'accepted', 'trchno': '0', 'spareordqty': '0', 'trcode': 'SONAT000', 'userid': '<your-user-id>', 'dummy': '', 'len': '1053', 'loandt': '00000000', 'orgordmdfyqty': '0', 'avrpchsprc': '.00', 'cont': 'N', 'hname': 'TIGER 미국S&P500', 'pgmtype': '0', 'compress': '0', 'ordprice': '18015', 'procgb': '0', 'unercsellordqty': '0', 'ruseableamt': '0', 'ordgb': '02', 'gubun': 'B', 'trid': 'C000152253562059', 'flctqty': '0', 'varmsglen': '0', 'ordno': '150151', 'passwd': '********', 'singb': '000', 'gmhogayn': '0', 'ordruseqty': '0', 'deposit': '1015853', 'trsrc': 'Z', 'gmhogagb': '0', 'reqcnt': ' ', 'accno1': '<your-acc-no>', 'strtgcode': '', 'ordchegb': '01', 'ordtm': '152253562', 'orduserid': '<your-user-id>', 'ordseqno': '0', 'ordablesubstamt': '1139350', 'pchsamt': '0', 'encrypt': '0', 'accno2': '', 'shtcode': 'A360750', 'contkey': '', 'brwmgmyn': '0', 'seq': '000000103', 'mtordseqno': '0', 'lineseq': '1300076459', 'tongsingb': '51', 'varlen': '50', 'lpgb': '0', 'rsvordno': '0', 'spotordqty': '0', 'cvrgseqno': '0', 'filler': '', 'hogagb': '0', 'secbalqty': '0', 'expcode': 'KR7360750004', 'prntordno': '150151', 'ordablemny': '961813', 'pubip': 'D180A4DE36E6', 'prvip': 'D180A4DE36E6', 'funckey': 'C', 'accno': '<your-acc-no>', 'compreq': '0', 'orgordundrqty': '0', 'ruseordamt': '0', 'crdtpldgruseamt': ' ', 'ordordcancelqty': '0', 'ordamt': '18015', 'spareordno': '0', 'termno': '', 'etfhogagb': '00', 'bpno': '202', 'substamt': '1139350', 'mgempno': '999999202', 'csgnsubstmgn': '0', 'offset': '212', 'sellableqty': '0', 'groupid': '', 'varhdlen': '0', 'mnyordamt': '18015', 'itemno': '0', 'prtno': '0', 'marketgb': '10', 'ifinfo': '', 'ordableruseqty': '0', 'crdtuseamt': '0', 'ordcmsnamt': '0', 'secbalqtyd2': '0', 'eventid': '', 'csgnmnymgn': '54040', 'pcbpno': '000', 'orgordno': '0', 'basketno': '0', 'ifid': '000', 'media': 'HT', 'filler1': '', 'mbrno': '63', 'proctm': '152253562', 'ordsubstamt': '0', 'lang': 'K', 'spotordableqty': '0', 'cvrgordtp': '0', 'ordqty': '1', 'outgu': '', 'msgcode': '0040', 'futaccno': '00000000000000000000', 'futmarketgb': '0', 'admbrchno': '202', 'comid': '063', 'bnstp': '2', 'user': '<your-user-id>', 'nmcpysndno': '0'}
            {'event_type': 'executed', 'grpId': 'A4000000000000000000', 'trchno': '0', 'trtzxLevytp': '1', 'ordtrxptncode': '0', 'acntnm': '<your-name>', 'trcode': 'SONAS100', 'userid': '<your-user-id>', 'agrgbrnno': '202', 'regmktcode': '10', 'len': '1294', 'opdrtnno': '', 'orgordmdfyqty': '0', 'avrpchsprc': '0', 'exectime': '153022964', 'cont': 'N', 'mnymgnrat': '1.000', 'mdfycnfqty': '0', 'orgordcancqty': '0', 'compress': '0', 'execprc': '18020', 'mdfycnfprc': '0', 'unercsellordqty': '0', 'cmsnamtexecamt': '0', 'ruseableamt': '0', 'gubun': 'B', 'trid': 'C000152305251008', 'flctqty': '1', 'execno': '36110', 'lptp': '0', 'varmsglen': '0', 'ordno': '150162', 'futsmkttp': '', 'crdtexecamt': '0', 'deposit': '1015853', 'frgrunqno': '000000', 'crdayruseexecval': '0', 'trsrc': 'Z', 'ordacntno': '<your-acc-no>', 'reqcnt': ' ', 'shtnIsuno': 'A360750', 'accno1': '<your-acc-no>', 'strtgcode': '', 'ordseqno': '0', 'Isunm': 'TIGER 미국S&P500', 'ordablesubstamt': '1139350', 'encrypt': '0', 'Isuno': 'KR7360750004', 'accno2': '', 'contkey': '', 'Loandt': '00000000', 'seq': '000000112', 'lineseq': '1300076856', 'varlen': '50', 'orduserId': '<your-user-id>', 'mgmtbrnno': '202', 'rjtqty': '0', 'ordprcptncode': '03', 'stdIsuno': 'KR7360750004', 'pchsant': '0', 'filler': '', 'secbalqty': '0', 'ordxctptncode': '11', 'canccnfqty': '0', 'ordablemny': '961808', 'pubip': 'D180A4DE36E6', 'prvip': 'D180A4DE36E6', 'funckey': 'C', 'accno': '<your-acc-no>', 'compreq': '0', 'crdtpldgruseamt': '0', 'ordamt': '0', 'termno': '', 'crdtpldgexecamt': '0', 'ordcndi': '0', 'rmndLoanamt': '0', 'bpno': '202', 'substamt': '1139350', 'mgempno': '999999202', 'csgnsubstmgn': '0', 'offset': '212', 'rcptexectime': '153022954', 'sellableqty': '0', 'spotexecqty': '0', 'varhdlen': '0', 'substmgnrat': '.0000000', 'ordavrexecprc': '18020', 'itemno': '0', 'mgntrncode': '000', 'nsavtrdqty': '0', 'ifinfo': '', 'ordableruseqty': '0', 'ptflno': '0', 'secbalqtyd2': '0', 'brwmgmtYn': '0', 'eventid': '', 'csgnmnymgn': '54045', 'pcbpno': '000', 'orgordno': '0', 'ifid': '000', 'media': 'HT', 'mtiordseqno': '0', 'filler1': '', 'orgordunercqty': '0', 'mbrnmbrno': '0', 'futsLnkbrnno': '', 'commdacode': '51', 'stslexecqty': '0', 'proctm': '153022964', 'bfstdIsuno': 'KR7360750004', 'futsLnkacntno': '', 'lang': 'K', 'unercqty': '0', 'execqty': '1', 'adduptp': '51', 'bskno': '0', 'spotordableqty': '0', 'ubstexecamt': '0', 'cvrgordtp': '0', 'ordqty': '1', 'mnyexecamt': '18020', 'outgu': '', 'msgcode': '9999', 'ordtrdptncode': '00', 'ordmktcode': '10', 'ordptncode': '02', 'prdayruseexecval': '0', 'comid': '063', 'bnstp': '2', 'user': '<your-user-id>', 'ordprc': '0'}

        Note:
            이 함수는 비동기 I/O를 사용하므로 async for 문을 사용하여 이벤트를 소비해야 합니다.
        """

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            tr_codes = [f"SC{i}" for i in range(5)]
            for tr_code in tr_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "1",
                            },
                            "body": {
                                "tr_cd": tr_code,
                            },
                        }
                    )
                )

                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        event_type_map = {
            "SC0": "accepted",
            "SC1": "executed",
            "SC2": "updated",
            "SC3": "cancelled",
            "SC5": "denied",
        }

        async for data in client.listen():
            new_data = {
                "event_type": event_type_map[data["header"]["tr_cd"]],
                **data["body"],
            }

            yield new_data

    async def listen_upper_under_limit_enter_event(
        self,
        stop_event: asyncio.Event = None,
    ) -> AsyncGenerator:
        """
        상 하한가 진입 이벤트를 실시간으로 수신하고 처리하는 비동기 제너레이터 함수입니다.
        이 함수는 비동기적으로 동작하며, 이벤트 데이터는 제너레이터를 통해 소비할 수 있습니다.

        Args:
            stop_event (asyncio.Event): 이벤트 리스닝을 중지하기 위한 asyncio 이벤트.

        Yields:
            dict: 상한가 진입에 관한 상세 정보를 포함하는 사전형 데이터. 각 키는 다음과 같습니다:
                - sijanggubun (string): 거래소. 1:코스피 2:코스닥
                - hname (string): 종목명
                - shcode (string): 단축코드
                - price (string): 현재가
                - change (string): 전일대비 가격변화
                - sign (string): 전일대비 구분. 1:상한가
                - drate (string): 등락율
                - volume (string): 누적거래량
                - volincrate (string): 거래증가율
                - totofferrem (string): 매도호가총수량
                - totbidrem (string): 매수호가총수량
                - updnlmtstime (string): 상한가/하한가최종진입시간
                - updnlmtdaycnt (string): 상한가/하한가연속일수
                - jnilvolume (string): 전일거래량
                - gwangubun (string): 관리종목구분
                - undergubun (string): 이상급등구분
                - tgubun (string): 투자유의구분
                - wgubun (string): 우선주구분
                - dishonest (string): 불성실공시구분
                - jkrate (string): 증거금률

        """

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            now = dtm.datetime.now()
            today = now.date()
            market_schedule = get_market_schedule(today)

            if market_schedule.full_day_closed:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            open_time = dtm.datetime.combine(today, market_schedule.open_time)
            close_time = dtm.datetime.combine(today, market_schedule.close_time)
            # 장전 시간외종가 거래 시작 시간
            pre_market_open_time = open_time - dtm.timedelta(minutes=30)
            # 장후 시간외종가 거래 종료 시간
            after_market_close_time = close_time + dtm.timedelta(minutes=30)
            time_margin = dtm.timedelta(minutes=5)

            if now < pre_market_open_time - time_margin:
                return EBestTRWebsocketKeepConnectionStatus.WAIT

            if now > after_market_close_time + time_margin:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            for asset_code in asset_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "3",
                            },
                            "body": {
                                "tr_cd": "SHI",
                            },
                        }
                    )
                )

                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        async for data in client.listen():
            yield data

    async def listen_upper_under_limit_release_event(
        self,
        stop_event: asyncio.Event = None,
    ) -> AsyncGenerator:
        """
        상 하한가 이탈 이벤트를 실시간으로 수신하고 처리하는 비동기 제너레이터 함수입니다.
        이 함수는 비동기적으로 동작하며, 이벤트 데이터는 제너레이터를 통해 소비할 수 있습니다.

        Args:
            stop_event (asyncio.Event): 이벤트 리스닝을 중지하기 위한 asyncio 이벤트.

        Yields:
            dict: 상한가 진입에 관한 상세 정보를 포함하는 사전형 데이터. 각 키는 다음과 같습니다:
                - sijanggubun (string): 거래소. 1:코스피 2:코스닥
                - hname (string): 종목명
                - shcode (string): 단축코드
                - price (string): 현재가
                - change (string): 전일대비 가격변화
                - sign (string): 전일대비 구분. 1:상한가
                - drate (string): 등락율
                - volume (string): 누적거래량
                - volincrate (string): 거래증가율
                - totofferrem (string): 매도호가총수량
                - totbidrem (string): 매수호가총수량
                - updnlmtstime (string): 상한가/하한가최종진입시간
                - updnlmtdaycnt (string): 상한가/하한가연속일수
                - jnilvolume (string): 전일거래량
                - gwangubun (string): 관리종목구분
                - undergubun (string): 이상급등구분
                - tgubun (string): 투자유의구분
                - wgubun (string): 우선주구분
                - dishonest (string): 불성실공시구분
                - jkrate (string): 증거금률

        """

        def __on_ask_keep_connection() -> EBestTRWebsocketKeepConnectionStatus:
            now = dtm.datetime.now()
            today = now.date()
            market_schedule = get_market_schedule(today)

            if market_schedule.full_day_closed:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            open_time = dtm.datetime.combine(today, market_schedule.open_time)
            close_time = dtm.datetime.combine(today, market_schedule.close_time)
            # 장전 시간외종가 거래 시작 시간
            pre_market_open_time = open_time - dtm.timedelta(minutes=30)
            # 장후 시간외종가 거래 종료 시간
            after_market_close_time = close_time + dtm.timedelta(minutes=30)
            time_margin = dtm.timedelta(minutes=5)

            if now < pre_market_open_time - time_margin:
                return EBestTRWebsocketKeepConnectionStatus.WAIT

            if now > after_market_close_time + time_margin:
                return EBestTRWebsocketKeepConnectionStatus.CLOSE

            return EBestTRWebsocketKeepConnectionStatus.KEEP

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            for asset_code in asset_codes:
                await ws.send(
                    json.dumps(
                        {
                            "header": {
                                "token": self.auth.get_token(),
                                "tr_type": "3",
                            },
                            "body": {
                                "tr_cd": "SHO",
                            },
                        }
                    )
                )

                await asyncio.sleep(0.01)

        client = EBestTRWebsocketClient(
            self.auth,
            on_connect=__on_connect,
            on_ask_keep_connection=__on_ask_keep_connection,
            stop_event=stop_event,
        )

        async for data in client.listen():
            yield data
