from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from decimal import Decimal
from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.brokerage.kis.tr_client import KISTRClient, KISTRWebsocketClient
from typing import AsyncGenerator
import asyncio
import datetime as dtm
import json
import re
import websockets


class KISDomesticStock:
    """
    한국투자증권 국내주식 API
    """

    def __init__(self, auth: KISAuth, corp_data: dict = None):
        self.auth = auth
        self.corp_data = corp_data
        self.tr_client = KISTRClient(auth, corp_data)

    def _tr_request(self, *args, **kwargs):
        return self.tr_client.request(*args, **kwargs)

    def get_price(self, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J"):
        """
        (국내주식시세) 주식현재가 시세[v1_국내주식-008]

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:KRX NX:NXT UN:통합

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 출력

                - iscd_stat_cls_code: 종목상태구분코드 - 00:그외 51:관리종목 52:투자위험 53:투자경고 54:투자주의 55:신용가능 57:증거금 100% 58:거래정지 59:단기과열
                - marg_rate: 증거금비율
                - rprs_mrkt_kor_name: 대표시장한글명
                - new_hgpr_lwpr_cls_code: 신고가저가구분코드 - 조회하는 종목이 신고/신저에 도달했을 경우에만 조회됨
                - bstp_kor_isnm: 업종한글종목명
                - temp_stop_yn: 임시정지여부
                - oprc_rang_cont_yn: 시가범위연장여부
                - clpr_rang_cont_yn: 종가범위연장여부
                - crdt_able_yn: 신용가능여부
                - grmn_rate_cls_code: 보증금비율구분코드 - 한국투자 증거금비율 (marg_rate 참고) 40:20%,30%,40% 50:50% 60:60%
                - elw_pblc_yn: ELW발행여부
                - stck_prpr: 주식현재가
                - prdy_vrss: 전일대비
                - prdy_vrss_sign: 전일대비부호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - prdy_ctrt: 전일대비율
                - acml_tr_pbmn: 누적 거래 대금
                - acml_vol: 누적 거래량
                - prdy_vrss_vol_rate: 전일 대비 거래량 비율 - 주식현재가 일자별 API 응답값 사용
                - stck_oprc: 주식 시가
                - stck_hgpr: 주식 최고가
                - stck_lwpr: 주식 최저가
                - stck_mxpr: 주식 상한가
                - stck_llam: 주식 하한가
                - stck_sdpr: 주식 기준가
                - wghn_avrg_stck_prc: 가중 평균 주식 가격
                - hts_frgn_ehrt: HTS 외국인 소진율
                - frgn_ntby_qty: 외국인 순매수 수량
                - pgtr_ntby_qty: 프로그램매매 순매수 수량
                - pvt_scnd_dmrs_prc: 피벗 2차 디저항 가격 - 직원용 데이터
                - pvt_frst_dmrs_prc: 피벗 1차 디저항 가격 - 직원용 데이터
                - pvt_pont_val: 피벗 포인트 값 - 직원용 데이터
                - pvt_frst_dmsp_prc: 피벗 1차 디지지 가격 - 직원용 데이터
                - pvt_scnd_dmsp_prc: 피벗 2차 디지지 가격 - 직원용 데이터
                - dmrs_val: 디저항 값 - 직원용 데이터
                - dmsp_val: 디지지 값 - 직원용 데이터
                - cpfn: 자본금
                - rstc_wdth_prc: 제한 폭 가격
                - stck_fcam: 주식 액면가
                - stck_sspr: 주식 대용가
                - aspr_unit: 호가단위
                - hts_deal_qty_unit_val: HTS 매매 수량 단위 값
                - lstn_stcn: 상장 주수
                - hts_avls: HTS 시가총액
                - per: PER
                - pbr: PBR
                - stac_month: 결산 월
                - vol_tnrt: 거래량 회전율
                - eps: EPS
                - bps: BPS
                - d250_hgpr: 250일 최고가
                - d250_hgpr_date: 250일 최고가 일자
                - d250_hgpr_vrss_prpr_rate: 250일 최고가 대비 현재가 비율
                - d250_lwpr: 250일 최저가
                - d250_lwpr_date: 250일 최저가 일자
                - d250_lwpr_vrss_prpr_rate: 250일 최저가 대비 현재가 비율
                - stck_dryy_hgpr: 주식 연중 최고가
                - dryy_hgpr_vrss_prpr_rate: 연중 최고가 대비 현재가 비율
                - dryy_hgpr_date: 연중 최고가 일자
                - stck_dryy_lwpr: 주식 연중 최저가
                - dryy_lwpr_vrss_prpr_rate: 연중 최저가 대비 현재가 비율
                - dryy_lwpr_date: 연중 최저가 일자
                - w52_hgpr: 52주일 최고가
                - w52_hgpr_vrss_prpr_ctrt: 52주일 최고가 대비 현재가 대비
                - w52_hgpr_date: 52주일 최고가 일자
                - w52_lwpr: 52주일 최저가
                - w52_lwpr_vrss_prpr_ctrt: 52주일 최저가 대비 현재가 대비
                - w52_lwpr_date: 52주일 최저가 일자
                - whol_loan_rmnd_rate: 전체 융자 잔고 비율
                - ssts_yn: 공매도가능여부
                - stck_shrn_iscd: 주식 단축 종목코드
                - fcam_cnnm: 액면가 통화명
                - cpfn_cnnm: 자본금 통화명 - 외국주권은 억으로 떨어지며, 그 외에는 만으로 표시됨
                - apprch_rate: 접근도
                - frgn_hldn_qty: 외국인 보유 수량
                - vi_cls_code: VI적용구분코드
                - ovtm_vi_cls_code: 시간외단일가VI적용구분코드
                - last_ssts_cntg_qty: 최종 공매도 체결 수량
                - invt_caful_yn: 투자유의여부 - Y/N
                - mrkt_warn_cls_code: 시장경고코드 - 00:없음 01:투자주의 02:투자경고 03:투자위험
                - short_over_yn: 단기과열여부 - Y/N
                - sltr_yn: 정리매매여부 - Y/N
                - mang_issu_cls_code: 관리종목여부 - Y/N

        Raise:
            ValueError: API 에러 발생시
        """

        assert fid_cond_mrkt_div_code in ["J", "NX", "UN"], "fid_cond_mrkt_div_code must be 'J', 'NX' or 'UN'"
        assert len(fid_input_iscd) == 6 or (len(fid_input_iscd) == 7 and fid_input_iscd[0] == "Q")

        path = "/uapi/domestic-stock/v1/quotations/inquire-price"
        tr_id = "FHKST01010100"
        params = {"FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code, "FID_INPUT_ISCD": fid_input_iscd}

        res_body, _ = self._tr_request(path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body["output"]

        decimal_keys = [
            "marg_rate",
            "prdy_ctrt",
            "prdy_vrss_vol_rate",
            "wghn_avrg_stck_prc",
            "hts_frgn_ehrt",
            "per",
            "pbr",
            "vol_tnrt",
            "eps",
            "bps",
            "d250_hgpr_vrss_prpr_rate",
            "d250_lwpr_vrss_prpr_rate",
            "dryy_hgpr_vrss_prpr_rate",
            "dryy_lwpr_vrss_prpr_rate",
            "w52_hgpr_vrss_prpr_ctrt",
            "w52_lwpr_vrss_prpr_ctrt",
            "whol_loan_rmnd_rate",
            "stck_fcam",
        ]

        for k in decimal_keys:
            if k in output and len(output[k]) > 0:
                output[k] = Decimal(output[k])

        int_keys = [
            "stck_prpr",
            "prdy_vrss",
            "prdy_vrss_sign",
            "acml_tr_pbmn",
            "acml_vol",
            "stck_oprc",
            "stck_hgpr",
            "stck_lwpr",
            "stck_mxpr",
            "stck_llam",
            "stck_sdpr",
            "frgn_ntby_qty",
            "pgtr_ntby_qty",
            "pvt_scnd_dmrs_prc",
            "pvt_frst_dmrs_prc",
            "pvt_pont_val",
            "pvt_frst_dmsp_prc",
            "pvt_scnd_dmsp_prc",
            "dmrs_val",
            "dmsp_val",
            "cpfn",
            "rstc_wdth_prc",
            "stck_sspr",
            "aspr_unit",
            "hts_deal_qty_unit_val",
            "lstn_stcn",
            "hts_avls",
            "stac_month",
            "d250_hgpr",
            "d250_lwpr",
            "stck_dryy_hgpr",
            "stck_dryy_lwpr",
            "w52_hgpr",
            "w52_lwpr",
            "frgn_hldn_qty",
            "last_ssts_cntg_qty",
        ]

        for k in int_keys:
            if k in output and len(output[k]) > 0:
                output[k] = int(output[k])

        date_keys = [
            "d250_hgpr_date",
            "d250_lwpr_date",
            "dryy_hgpr_date",
            "dryy_lwpr_date",
            "w52_hgpr_date",
            "w52_lwpr_date",
        ]

        for k in date_keys:
            if k in output and len(output[k]) > 0 and output[k] != "0":  # NXT 종목이 아닌데 지정한 경우 output[k] 값이 0
                output[k] = dtm.datetime.strptime(output[k], "%Y%m%d").date()

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": output}

        return result

    def inquire_ccnl(self, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J", tr_cont: str = ""):
        """
        (국내주식시세) 주식현재가 체결[v1_국내주식-009]

        국내현재가 체결 API 입니다. 종목의 체결 정보를 확인할 수 있습니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN W:ELW NX:Nextrade UN:통합

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부
            - output (list): 출력
                - stck_cntg_hour: 주식 체결 시간
                - stck_prpr: 주식 현재가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - cntg_vol: 체결 거래량
                - tday_rltv: 당일 체결강도 - 체결거래가 발생하는 시점의 체결강도
                - prdy_ctrt: 전일 대비율

        Raise:
            ValueError: API 에러 발생시
        """

        path = "/uapi/domestic-stock/v1/quotations/inquire-ccnl"
        tr_id = "FHKST01010300"
        params = {"FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code, "FID_INPUT_ISCD": fid_input_iscd}

        res_body, res_headers = self._tr_request(path, tr_id, tr_cont, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            decimal_keys = ["tday_rltv", "prdy_ctrt"]
            for k in decimal_keys:
                if k in el and len(el[k]) > 0:
                    el[k] = Decimal(el[k])

            int_keys = ["stck_prpr", "prdy_vrss", "prdy_vrss_sign", "cntg_vol"]
            for k in int_keys:
                if k in el and len(el[k]) > 0:
                    el[k] = int(el[k])

            el["stck_cntg_hour"] = dtm.datetime.strptime(el["stck_cntg_hour"], "%H%M%S").time()

            output.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output": output}

        return result

    def inquire_daily_price(self, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J", fid_period_div_code: str = "D", fid_org_adj_prc: str = "0"):
        """
        (국내주식시세) 주식현재가 일자별[v1_국내주식-010]

        주식현재가 일자별 API입니다. 일/주/월별 주가를 확인할 수 있으며 최근 30일(주,별)로 제한되어 있습니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합
            fid_period_div_code (str): FID 기간구분코드 - D:(일)최근 30거래일 W:(주)최근 30주 M:(월)최근 30개월
            fid_org_adj_prc (str): FID 조정가구분코드 - 0:수정주가 1:원주가

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부
            - output (list): 출력

                - stck_bsop_date: 주식 영업 일자
                - stck_oprc: 주식 시가
                - stck_hgpr: 주식 최고가
                - stck_lwpr: 주식 최저가
                - stck_clpr: 주식 종가
                - acml_vol: 누적 거래량
                - prdy_vrss_vol_rate: 전일 대비 거래량 비율
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - prdy_ctrt: 전일 대비율
                - hts_frgn_ehrt: HTS 외국인 소진율
                - frgn_ntby_qty: 외국인 순매수 수량
                - flng_cls_code: 락 구분 코드

                    | 01:권리락
                    | 02:배당락
                    | 03:분배락
                    | 04:권배락
                    | 05:중간(분기)배당락
                    | 06:권리중간배당락
                    | 07:권리분기배당락

                - acml_prtt_rate: 누적 분할 비율

        Raise:
            ValueError: API 에러 발생시
        """
        url_path = "/uapi/domestic-stock/v1/quotations/inquire-daily-price"
        tr_id = "FHKST01010400"
        params = {"FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code, "FID_INPUT_ISCD": fid_input_iscd, "FID_PERIOD_DIV_CODE": fid_period_div_code, "FID_ORG_ADJ_PRC": fid_org_adj_prc}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            el["stck_bsop_date"] = dtm.datetime.strptime(el["stck_bsop_date"], "%Y%m%d").date()

            int_keys = ["stck_oprc", "stck_hgpr", "stck_lwpr", "stck_clpr", "acml_vol", "prdy_vrss", "frgn_ntby_qty"]
            for k in int_keys:
                if k in el and len(el[k]) > 0:
                    el[k] = int(el[k])

            decimal_keys = ["prdy_vrss_vol_rate", "prdy_vrss_sign", "prdy_ctrt", "hts_frgn_ehrt", "acml_prtt_rate"]
            for k in decimal_keys:
                if k in el and len(el[k]) > 0:
                    el[k] = Decimal(el[k])

            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "tr_cont": res_headers["tr_cont"],
            "output": output,
        }

        return result

    def inquire_asking_price_exp_ccn(self, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J"):
        """
        (국내주식시세) 주식현재가 호가/예상체결[v1_국내주식-011]

        주식현재가 호가 예상체결 API입니다. 매수 매도 호가를 확인하실 수 있습니다. 실시간 데이터를 원하신다면 웹소켓 API를 활용하세요.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output1 (list): 응답상세1

                - aspr_acpt_hour: 호가 접수 시간
                - askp1: 매도호가1
                - askp2: 매도호가2
                - askp3: 매도호가3
                - askp4: 매도호가4
                - askp5: 매도호가5
                - askp6: 매도호가6
                - askp7: 매도호가7
                - askp8: 매도호가8
                - askp9: 매도호가9
                - askp10: 매도호가10
                - bidp1: 매수호가1
                - bidp2: 매수호가2
                - bidp3: 매수호가3
                - bidp4: 매수호가4
                - bidp5: 매수호가5
                - bidp6: 매수호가6
                - bidp7: 매수호가7
                - bidp8: 매수호가8
                - bidp9: 매수호가9
                - bidp10: 매수호가10
                - askp_rsqn1: 매도호가 잔량1
                - askp_rsqn2: 매도호가 잔량2
                - askp_rsqn3: 매도호가 잔량3
                - askp_rsqn4: 매도호가 잔량4
                - askp_rsqn5: 매도호가 잔량5
                - askp_rsqn6: 매도호가 잔량6
                - askp_rsqn7: 매도호가 잔량7
                - askp_rsqn8: 매도호가 잔량8
                - askp_rsqn9: 매도호가 잔량9
                - askp_rsqn10: 매도호가 잔량10
                - bidp_rsqn1: 매수호가 잔량1
                - bidp_rsqn2: 매수호가 잔량2
                - bidp_rsqn3: 매수호가 잔량3
                - bidp_rsqn4: 매수호가 잔량4
                - bidp_rsqn5: 매수호가 잔량5
                - bidp_rsqn6: 매수호가 잔량6
                - bidp_rsqn7: 매수호가 잔량7
                - bidp_rsqn8: 매수호가 잔량8
                - bidp_rsqn9: 매수호가 잔량9
                - bidp_rsqn10: 매수호가 잔량10
                - askp_rsqn_icdc1: 매도호가 잔량 증감1
                - askp_rsqn_icdc2: 매도호가 잔량 증감2
                - askp_rsqn_icdc3: 매도호가 잔량 증감3
                - askp_rsqn_icdc4: 매도호가 잔량 증감4
                - askp_rsqn_icdc5: 매도호가 잔량 증감5
                - askp_rsqn_icdc6: 매도호가 잔량 증감6
                - askp_rsqn_icdc7: 매도호가 잔량 증감7
                - askp_rsqn_icdc8: 매도호가 잔량 증감8
                - askp_rsqn_icdc9: 매도호가 잔량 증감9
                - askp_rsqn_icdc10: 매도호가 잔량 증감10
                - bidp_rsqn_icdc1: 매수호가 잔량 증감1
                - bidp_rsqn_icdc2: 매수호가 잔량 증감2
                - bidp_rsqn_icdc3: 매수호가 잔량 증감3
                - bidp_rsqn_icdc4: 매수호가 잔량 증감4
                - bidp_rsqn_icdc5: 매수호가 잔량 증감5
                - bidp_rsqn_icdc6: 매수호가 잔량 증감6
                - bidp_rsqn_icdc7: 매수호가 잔량 증감7
                - bidp_rsqn_icdc8: 매수호가 잔량 증감8
                - bidp_rsqn_icdc9: 매수호가 잔량 증감9
                - bidp_rsqn_icdc10: 매수호가 잔량 증감10
                - total_askp_rsqn: 총 매도호가 잔량
                - total_bidp_rsqn: 총 매수호가 잔량
                - total_askp_rsqn_icdc: 총 매도호가 잔량 증감
                - total_bidp_rsqn_icdc: 총 매수호가 잔량 증감
                - ovtm_total_askp_icdc: 시간외 총 매도호가 증감
                - ovtm_total_bidp_icdc: 시간외 총 매수호가 증감
                - ovtm_total_askp_rsqn: 시간외 총 매도호가 잔량
                - ovtm_total_bidp_rsqn: 시간외 총 매수호가 잔량
                - ntby_aspr_rsqn: 순매수 호가 잔량
                - new_mkop_cls_code: 신 장운영 구분 코드

                    - '00':장전 예상체결가와 장마감 동시호가
                    - '49':장후 예상체결가
                    - (1)첫 번째 비트: 1:장개시전 2:장중 3:장종료후 4:시간외단일가 7:일반Buy-in 8:당일Buy-in
                    - (2)두 번째 비트: 0:보통 1:종가 2:대량 3:바스켓 7:정리매매 8:Buy-in

            - output2 (list): 응답상세2
                - antc_mkop_cls_code: 예상 장운영 구분 코드 - 311:예상체결시작 112:예상체결종료
                - stck_prpr: 주식 현재가
                - stck_oprc: 주식 시가
                - stck_hgpr: 주식 최고가
                - stck_lwpr: 주식 최저가
                - stck_sdpr: 주식 기준가
                - antc_cnpr: 예상 체결가
                - antc_cntg_vrss_sign: 예상 체결 대비 부호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - antc_cntg_vrss: 예상 체결 대비
                - antc_cntg_prdy_ctrt: 예상 체결 전일 대비율
                - antc_vol: 예상 거래량
                - stck_shrn_iscd: 주식 단축 종목코드
                - vi_cls_code: VI적용구분코드

        Raise:
            ValueError: API 에러 발생시
        """

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn"
        tr_id = "FHKST01010200"
        params = {"FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code, "FID_INPUT_ISCD": fid_input_iscd}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k == "aspr_acpt_hour":
                output1[k] = dtm.datetime.strptime(output1[k], "%H%M%S").time()
            elif k == "new_mkop_cls_code":
                pass
            else:
                output1[k] = int(output1[k])

        output2 = res_body["output2"]
        for k in output2.keys():
            if k in ["antc_mkop_cls_code", "stck_shrn_iscd", "vi_cls_code"]:
                pass
            elif k == "antc_cntg_prdy_ctrt":
                output2[k] = Decimal(output2[k])
            else:
                output2[k] = int(output2[k])

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output1": output1, "output2": output2}

        return result

    def inquire_investor(self, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J"):
        """
        (국내주식시세) 주식현재가 투자자[v1_국내주식-012]

        주식현재가 투자자 API입니다. 개인, 외국인, 기관 등 투자 정보를 확인할 수 있습니다. (30건)

        [유의사항]
        - 외국인은 외국인(외국인투자등록 고유번호가 있는 경우)+기타 외국인을 지칭합니다.
        - 당일 데이터는 장 종료 후 제공됩니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (list): 응답상세

                - stck_bsop_date: 주식 영업 일자
                - stck_clpr: 주식 종가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prsn_ntby_qty: 개인 순매수 수량
                - frgn_ntby_qty: 외국인 순매수 수량
                - orgn_ntby_qty: 기관계 순매수 수량
                - prsn_ntby_tr_pbmn: 개인 순매수 거래 대금
                - frgn_ntby_tr_pbmn: 외국인 순매수 거래 대금
                - orgn_ntby_tr_pbmn: 기관계 순매수 거래 대금
                - prsn_shnu_vol: 개인 매수2 거래량
                - frgn_shnu_vol: 외국인 매수2 거래량
                - orgn_shnu_vol: 기관계 매수2 거래량
                - prsn_shnu_tr_pbmn: 개인 매수2 거래 대금
                - frgn_shnu_tr_pbmn: 외국인 매수2 거래 대금
                - orgn_shnu_tr_pbmn: 기관계 매수2 거래 대금
                - prsn_seln_vol: 개인 매도 거래량
                - frgn_seln_vol: 외국인 매도 거래량
                - orgn_seln_vol: 기관계 매도 거래량
                - prsn_seln_tr_pbmn: 개인 매도 거래 대금
                - frgn_seln_tr_pbmn: 외국인 매도 거래 대금
                - orgn_seln_tr_pbmn: 기관계 매도 거래 대금

        Raise:
            ValueError: API 에러 발생시
        """

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-investor"
        tr_id = "FHKST01010900"
        params = {
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd,
        }

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            el["stck_bsop_date"] = dtm.datetime.strptime(el["stck_bsop_date"], "%Y%m%d").date()

            int_keys = [
                "stck_clpr",
                "prdy_vrss",
                "prdy_vrss_sign",
                "prsn_ntby_qty",
                "frgn_ntby_qty",
                "orgn_ntby_qty",
                "prsn_ntby_tr_pbmn",
                "frgn_ntby_tr_pbmn",
                "orgn_ntby_tr_pbmn",
                "prsn_shnu_vol",
                "frgn_shnu_vol",
                "orgn_shnu_vol",
                "prsn_shnu_tr_pbmn",
                "frgn_shnu_tr_pbmn",
                "orgn_shnu_tr_pbmn",
                "prsn_seln_vol",
                "frgn_seln_vol",
                "orgn_seln_vol",
                "prsn_seln_tr_pbmn",
                "frgn_seln_tr_pbmn",
                "orgn_seln_tr_pbmn",
            ]
            for k in int_keys:
                if k in el and len(el[k]) > 0:
                    el[k] = int(el[k])

            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "tr_cont": res_headers["tr_cont"],
            "output": output,
        }

        return result

    def inquire_daily_itemchartprice(self, fid_input_iscd: str, fid_input_date_1: dtm.date, fid_input_date_2: dtm.date, fid_period_div_code: str, fid_cond_mrkt_div_code: str = "J", fid_org_adj_prc: str = "0"):
        """
        (국내주식시세) 국내주식기간별시세(일/주/월/년)[v1_국내주식-016]

        국내주식기간별시세(일/주/월/년) API입니다.
        실전계좌/모의계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_input_date_1 (datetime.date): FID 입력일자1 - 조회 시작일자 (ex. dtm.date(2024, 1, 01))
            fid_input_date_2 (datetime.date): FID 입력일자2 - 조회 종료일자 (ex. dtm.date(2024, 1, 31))
            fid_period_div_code (str): FID 기간구분코드 - D:일별 W:주별 M:월별 Y:년별
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합
            fid_org_adj_prc (str): FID 조정가구분코드 - 0:수정주가 1:원주가

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부
            - output1 (object): 응답상세1

                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - stck_prdy_clpr: 주식 전일 종가
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - hts_kor_isnm: HTS 한글 종목명
                - stck_prpr: 주식 현재가
                - stck_shrn_iscd: 주식 단축 종목코드
                - prdy_vol: 전일 거래량
                - stck_mxpr: 상한가
                - stck_llam: 하한가
                - stck_oprc: 시가
                - stck_hgpr: 최고가
                - stck_lwpr: 최저가
                - stck_prdy_oprc: 주식 전일 시가
                - stck_prdy_hgpr: 주식 전일 최고가
                - stck_prdy_lwpr: 주식 전일 최저가
                - askp: 매도호가
                - bidp: 매수호가
                - prdy_vrss_vol: 전일 대비 거래량
                - vol_tnrt: 거래량 회전율
                - stck_fcam: 주식 액면가
                - lstn_stcn: 상장 주수
                - cpfn: 자본금
                - hts_avls: 시가총액
                - per: PER
                - eps: EPS
                - pbr: PBR
                - itewhol_loan_rmnd_ratem: 전체 융자 잔고 비율

            - output2: (list): 일별데이터

                - stck_bsop_date: 주식 영업 일자
                - stck_clpr: 주식 종가
                - stck_oprc: 주식 시가
                - stck_hgpr: 주식 최고가
                - stck_lwpr: 주식 최저가
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - flng_cls_code: 락 구분 코드

                    | 00:해당사항없음(락이 발생안한 경우)
                    | 01:권리락
                    | 02:배당락
                    | 03:분배락
                    | 04:권배락
                    | 05:중간(분기)배당락
                    | 06:권리중간배당락
                    | 07:권리분기배당락

                - prtt_rate: 분할 비율 - 기준가/전일 종가
                - mod_yn: 분할변경여부 - 현재 영업일에 체결이 발생하지 않아 시가가 없을경우 Y 로 표시(차트에서 사용)
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_vrss: 전일 대비
                - revl_issu_reas: 재평가사유코드

                    | 00:해당없음
                    | 01:회사분할
                    | 02:자본감소
                    | 03:장기간정지
                    | 04:초과분배
                    | 05:대규모배당
                    | 06:회사분할합병
                    | 07:ETN증권병합/분할
                    | 08:신종증권기세조정
                    | 99:기타

        Raise:
            ValueError: API 에러 발생시
        """

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
        tr_id = "FHKST03010100"
        params = {
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_INPUT_DATE_1": fid_input_date_1.strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": fid_input_date_2.strftime("%Y%m%d"),
            "FID_PERIOD_DIV_CODE": fid_period_div_code,
            "FID_ORG_ADJ_PRC": fid_org_adj_prc,
        }
        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]

        int_keys = [
            "prdy_vrss",
            "prdy_vrss_sign",
            "stck_prdy_clpr",
            "acml_vol",
            "acml_tr_pbmn",
            "stck_prpr",
            "prdy_vol",
            "stck_mxpr",
            "stck_llam",
            "stck_oprc",
            "stck_hgpr",
            "stck_lwpr",
            "stck_prdy_oprc",
            "stck_prdy_hgpr",
            "stck_prdy_lwpr",
            "askp",
            "bidp",
            "prdy_vrss_vol",
            "lstn_stcn",
            "cpfn",
            "hts_avls",
        ]
        for k in int_keys:
            if k in output1 and len(output1[k]) > 0:
                output1[k] = int(output1[k])

        decimal_keys = [
            "prdy_ctrt",
            "vol_tnrt",
            "per",
            "eps",
            "pbr",
            "itewhol_loan_rmnd_ratem name",
            "stck_fcam",
        ]
        for k in decimal_keys:
            if k in output1 and len(output1[k]) > 0:
                output1[k] = Decimal(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "stck_bsop_date":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k in ["mod_yn", "revl_issu_reas"]:
                    pass
                elif k == "prtt_rate":
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])

            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output1": output1, "output2": output2}

        return result

    def inquire_daily_indexchartprice(self, fid_input_iscd: str, fid_input_date_1: dtm.date, fid_input_date_2: dtm.date, fid_period_div_code: str):
        """
        (국내주식시세) 국내주식업종기간별시세(일/주/월/년)[v1_국내주식-021]

        국내주식 업종기간별시세(일/주/월/년) API입니다.
        실전계좌/모의계좌의 경우, 한 번의 호출에 최대 50건까지 확인 가능합니다.

        Args:
            fid_input_iscd (str): 업종상세코드 - 0001:종합 0002:대형주, ... 포탈(FAQ:종목정보 다운로드 - 업종코드 참조)
            fid_input_date_1 (datetime.date): FID 입력일자1 - 조회 시작일자 (ex. dtm.date(2024, 1, 01))
            fid_input_date_2 (datetime.date): FID 입력일자2 - 조회 종료일자 (ex. dtm.date(2024, 1, 31))
            fid_period_div_code (str): FID 기간구분코드 - D:일별 W:주별 M:월별 Y:년별

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output1 (object): 응답상세1

                - BSTP_NMIX_PRDY_VRSS: 업종 지수 전일 대비 - 업종 지수 전일 대비
                - PRDY_VRSS_SIGN: 전일 대비 부호 - 전일 대비 부호
                - BSTP_NMIX_PRDY_CTRT: 업종 지수 전일 대비율 - 업종 지수 전일 대비율
                - PRDY_NMIX: 전일 지수 - 전일 지수
                - ACML_VOL: 누적 거래량 - 누적 거래량
                - ACML_TR_PBMN: 누적 거래 대금 - 누적 거래 대금
                - HTS_KOR_ISNM: HTS 한글 종목명 - HTS 한글 종목명
                - BSTP_NMIX_PRPR: 업종 지수 현재가 - 업종 지수 현재가
                - BSTP_CLS_CODE: 업종 구분 코드 - 업종 구분 코드
                - PRDY_VOL: 전일 거래량 - 전일 거래량
                - BSTP_NMIX_OPRC: 업종 지수 시가 - 업종 지수 시가
                - BSTP_NMIX_HGPR: 업종 지수 최고가 - 업종 지수 최고가
                - BSTP_NMIX_LWPR: 업종 지수 최저가 - 업종 지수 최저가
                - FUTS_PRDY_OPRC: 업종 전일 시가 - 업종 전일 시가
                - FUTS_PRDY_HGPR: 업종 전일 최고가 - 업종 전일 최고가
                - FUTS_PRDY_LWPR: 업종 전일 최저가 - 업종 전일 최저가

            - output2 (list): 응답상세2

                - STCK_BSOP_DATE: 영업 일자 - 영업 일자
                - BSTP_NMIX_PRPR: 업종 지수 현재가 - 업종 지수 현재가
                - BSTP_NMIX_OPRC: 업종 지수 시가 - 업종 지수 시가
                - BSTP_NMIX_HGPR: 업종 지수 최고가 - 업종 지수 최고가
                - BSTP_NMIX_LWPR: 업종 지수 최저가 - 업종 지수 최저가
                - ACML_VOL: 누적 거래량 - 누적 거래량
                - ACML_TR_PBMN: 누적 거래 대금 - 누적 거래 대금
                - MOD_YN: 변경 여부 - 변경 여부

        Raise:
            ValueError: API 에러 발생시

        """
        url_path = "/uapi/domestic-stock/v1/quotations/inquire-daily-indexchartprice"
        tr_id = "FHKUP03500100"
        params = {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": fid_input_iscd, "FID_INPUT_DATE_1": fid_input_date_1.strftime("%Y%m%d"), "FID_INPUT_DATE_2": fid_input_date_2.strftime("%Y%m%d"), "FID_PERIOD_DIV_CODE": fid_period_div_code}
        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        decimal_keys = ["bstp_nmix_prdy_vrss", "bstp_nmix_prdy_ctrt", "prdy_nmix", "bstp_nmix_oprc", "bstp_nmix_prpr", "bstp_nmix_hgpr", "bstp_nmix_lwpr", "futs_prdy_oprc", "futs_prdy_hgpr", "futs_prdy_lwpr"]
        for k in decimal_keys:
            if k in output1 and len(output1[k]) > 0:
                output1[k] = Decimal(output1[k])

        int_keys = ["prdy_vrss_sign", "acml_vol", "acml_tr_pbmn", "prdy_vol"]
        for k in int_keys:
            if k in output1 and len(output1[k]) > 0:
                output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k in ["bstp_nmix_prpr", "bstp_nmix_oprc", "bstp_nmix_hgpr", "bstp_nmix_lwpr"]:
                    el[k] = Decimal(el[k])
                elif k == "stck_bsop_date":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k in ["acml_vol", "acml_tr_pbmn"]:
                    el[k] = int(el[k])

            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output1": output1, "output2": output2}

        return result

    def inquire_time_itemconclusion(self, fid_input_iscd: str, fid_input_hour_1: dtm.time, fid_cond_mrkt_div_code: str = "J", tr_cont: str = ""):
        """
        (국내주식시세) 주식현재가 당일시간대별체결[v1_국내주식-023]

        주식현재가 당일시간대별체결 API입니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_input_hour_1 (datetime.time): FID 입력시간1 - 기준시간 ex)dtm.time(15, 50, 0) 입력 시 15시 50분 기준 이전 체결내역이 조회됨
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합
            tr_cont (str): 연속조회여부

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부
            - output1 (object): 응답상세1 - 기본정보

                - stck_prpr: 주식 현재가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - acml_vol: 누적 거래량
                - prdy_vol: 전일 거래량
                - rprs_mrkt_kor_name: 대표 시장 한글명

            - output2 (list): 응답상세2 - 시간대체결 정보

                - stck_cntg_hour: 주식 체결 시간
                - stck_prpr: 주식 현재가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - askp: 매도호가
                - bidp: 매수호가
                - tday_rltv: 당일 체결강도
                - acml_vol: 누적 거래량
                - cnqn: 체결량

        Raise:
            ValueError: API 에러 발생시
        """

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-time-itemconclusion"
        tr_id = "FHPST01060000"
        params = {"FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code, "FID_INPUT_ISCD": fid_input_iscd, "FID_INPUT_HOUR_1": fid_input_hour_1.strftime("%H%M%S")}

        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k == "rprs_mrkt_kor_name":
                pass
            elif k == "prdy_ctrt":
                output1[k] = Decimal(output1[k])
            else:
                output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "stck_cntg_hour":
                    el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                elif k in ["prdy_ctrt", "tday_rltv"]:
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])

            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output1": output1, "output2": output2}

        return result

    def inquire_time_overtimeconclusion(self, fid_input_iscd: str, tr_cont: str = ""):
        """
        (국내주식시세) 주식현재가 시간외시간별체결[v1_국내주식-025]

        주식현재가 시간외시간별체결 API입니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            tr_cont (str): 연속조회여부

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부
            - output1 (dict): 응답상세1 - 기본정보

                - ovtm_untp_prpr: 시간외 단일가 현재가
                - ovtm_untp_prdy_vrss: 시간외 단일가 전일 대비
                - ovtm_untp_prdy_vrss_sign: 시간외 단일가 전일 대비 부호
                - ovtm_untp_prdy_ctrt: 시간외 단일가 전일 대비율
                - ovtm_untp_vol: 시간외 단일가 거래량
                - ovtm_untp_tr_pbmn: 시간외 단일가 거래 대금
                - ovtm_untp_mxpr: 시간외 단일가 상한가
                - ovtm_untp_llam: 시간외 단일가 하한가
                - ovtm_untp_oprc: 시간외 단일가 시가2
                - ovtm_untp_hgpr: 시간외 단일가 최고가
                - ovtm_untp_lwpr: 시간외 단일가 최저가
                - ovtm_untp_antc_cnpr: 시간외 단일가 예상 체결가
                - ovtm_untp_antc_cntg_vrss: 시간외 단일가 예상 체결 대비
                - ovtm_untp_antc_cntg_vrss_sign: 시간외 단일가 예상 체결 대비
                - ovtm_untp_antc_cntg_ctrt: 시간외 단일가 예상 체결 대비율
                - ovtm_untp_antc_vol: 시간외 단일가 예상 거래량
                - uplm_sign: 상한 부호
                - lslm_sign: 하한 부호

            - output2 (list): 응답상세2 - 시간대별체결 정보

                - stck_cntg_hour: 주식 체결 시간
                - stck_prpr: 주식 현재가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - askp: 매도호가
                - bidp: 매수호가
                - acml_vol: 누적 거래량
                - cntg_vol: 체결 거래량
        Raise:
            ValueError: API 에러 발생시
        """
        url_path = "/uapi/domestic-stock/v1/quotations/inquire-time-overtimeconclusion"
        tr_id = "FHPST02310000"
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": fid_input_iscd, "FID_HOUR_CLS_CODE": "1"}
        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k in ["ovtm_untp_antc_cntg_ctrt", "ovtm_untp_prdy_ctrt"]:
                output1[k] = Decimal(output1[k])
            else:
                output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "prdy_ctrt":
                    el[k] = Decimal(el[k])
                elif k == "stck_cntg_hour":
                    el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                else:
                    el[k] = int(el[k])

            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output1": output1, "output2": output2}

        return result

    def inquire_daily_overtimeprice(self, fid_input_iscd: str, tr_cont: str = ""):
        """
        (국내주식시세) 주식현재가 시간외일자별주가[v1_국내주식-026]

        주식현재가 시간외일자별주가 API입니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부

            - output1 (dict): 응답상세1 - 기본정보

                - ovtm_untp_prpr: 시간외 단일가 현 재가
                - ovtm_untp_prdy_vrss: 시간외 단일가 전일 대비
                - ovtm_untp_prdy_vrss_sign: 시간외 단일가 전일 대비 부호
                - ovtm_untp_prdy_ctrt: 시간외 단일가 전일 대비율
                - ovtm_untp_vol: 시간외 단일가 거래량
                - ovtm_untp_tr_pbmn: 시간외 단일가 거래 대금
                - ovtm_untp_mxpr: 시간외 단일가 상한가
                - ovtm_untp_llam: 시간외 단일가 하한가
                - ovtm_untp_oprc: 시간외 단일가 시가2
                - ovtm_untp_hgpr: 시간외 단일가 최고가
                - ovtm_untp_lwpr: 시간외 단일가 최저가
                - ovtm_untp_antc_cnpr: 시간외 단일가 예상 체결가
                - ovtm_untp_antc_cntg_vrss: 시간외 단일가 예상 체결 대비
                - ovtm_untp_antc_cntg_vrss_sign: 시간외 단일가 예상 체결 대비
                - ovtm_untp_antc_cntg_ctrt: 시간외 단일가 예상 체결 대비율
                - ovtm_untp_antc_vol: 시간외 단일가 예상 거래량

            - output2 (list): 응답상세2 - 일자별 정보

                - stck_bsop_date: 주식 영업 일자
                - ovtm_untp_prpr: 시간외 단일가 현재가
                - ovtm_untp_prdy_vrss: 시간외 단일가 전일 대비
                - ovtm_untp_prdy_vrss_sign: 시간외 단일가 전일 대비 부호
                - ovtm_untp_prdy_ctrt: 시간외 단일가 전일 대비율
                - ovtm_untp_vol: 시간외 단일가 거래량
                - stck_clpr: 주식 종가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - acml_vol: 누적 거래량
                - ovtm_untp_tr_pbmn: 시간외 단일가 거래대금

        Raise:
            ValueError: API 에러 발생시
        """

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-daily-overtimeprice"
        tr_id = "FHPST02320000"

        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": fid_input_iscd}

        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k in ["ovtm_untp_antc_cntg_ctrt", "ovtm_untp_prdy_ctrt"]:
                output1[k] = Decimal(output1[k])
            else:
                output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k in ["prdy_ctrt", "ovtm_untp_prdy_ctrt"]:
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])

            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output1": output1, "output2": res_body["output2"]}

        return result

    def inquire_time_itemchartprice(
        self,
        fid_input_iscd: str,
        fid_input_hour_1: dtm.time | int,
        fid_cond_mrkt_div_code: str = "J",
        fid_pw_data_incu_yn: str = "Y",
    ):
        """
        (국내주식시세) 주식당일분봉조회[v1_국내주식-022]

        주식당일분봉조회 API입니다.
        실전계좌/모의계좌의 경우, 한 번의 호출에 최대 30건까지 확인 가능합니다.

        Args:
            fid_input_iscd (str): FID 입력종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_input_hour_1 (datetime.date|int) - 조회대상(FID_COND_MRKT_DIV_CODE)에 따라 입력하는 값 상이
              | 종목(J)일 경우, 조회 시작일자(HHMMSS)
              | ex) "123000" 입력 시 12시 30분 이전부터 1분 간격으로 조회
              |
              | 업종(U)일 경우, 조회간격(초) (60 or 120 만 입력 가능)
              | ex) "60" 입력 시 현재시간부터 1분간격으로 조회
              | "120" 입력 시 현재시간부터 2분간격으로 조회
              |
              | ※ FID_INPUT_HOUR_1 에 미래일시 입력 시에 현재가로 조회됩니다.
              | ex) 오전 10시에 113000 입력 시에 오전 10시~11시30분 사이의 데이터가 오전 10시 값으로 조회됨
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN U:업종 NX:Nextrade UN:통합
            fid_pw_data_incu_yn (str): FID 과거 데이터 포함 여부 - N:당일데이터만조회 Y:과거데이터포함조회

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1

            - output1 (dict): 응답상세1 - 기본정보

                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - stck_prdy_clpr: 주식 전일 종가
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - hts_kor_isnm: HTS 한글 종목명
                - stck_prpr: 주식 현재가

            - output2 (list): 응답상세2 - 조회결과 상세

                - stck_bsop_date: 주식 영업 일자
                - stck_cntg_hour: 주식 체결 시간
                - stck_prpr: 주식 현재가
                - stck_oprc: 주식 시가
                - stck_hgpr: 주식 최고가
                - stck_lwpr: 주식 최저가
                - cntg_vol: 체결 거래량
                - acml_tr_pbmn: 누적 거래 대금

        Raise:
            ValueError: API 에러 발생시
        """

        assert fid_cond_mrkt_div_code in ["J", "U", "NX", "UN"], 'fid_cond_mrkt_div_code must be one of "J", "U", "NX", or "UN"'
        assert fid_pw_data_incu_yn in ["Y", "N"], 'fid_pw_data_incu_yn must be "Y" or "N"'
        assert fid_cond_mrkt_div_code in ["J", "NX", "UN"] and isinstance(fid_input_hour_1, dtm.time) or fid_cond_mrkt_div_code == "U" and isinstance(fid_input_hour_1, int), "fid_input_hour_1 type mismatch"
        if type(fid_input_hour_1) is int:
            assert fid_input_hour_1 in [60, 120], "fid_input_hour_1 must be 60 or 120"

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        tr_id = "FHKST03010200"
        params = {
            "FID_ETC_CLS_CODE": "",
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_INPUT_HOUR_1": fid_input_hour_1.strftime("%H%M%S") if isinstance(fid_input_hour_1, dtm.time) else str(fid_input_hour_1),
            "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
        }

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k == "hts_kor_isnm":
                pass
            elif k == "prdy_ctrt":
                output1[k] = Decimal(output1[k])
            else:
                output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "stck_bsop_date":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k == "stck_cntg_hour":
                    el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                else:
                    el[k] = int(el[k])

            output2.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "tr_cont": res_headers["tr_cont"],
            "output1": output1,
            "output2": output2,
        }

        return result

    def search_info(self, pdno: str, prdt_type_cd: str):
        """
        (국내주식시세) 상품기본조회[v1_국내주식-029]

        Args:
            pdno (str): 상품번호

              | 주식(하이닉스):000660 (코드:300)
              | 선물(101S12):KR4101SC0009 (코드:301)
              | 미국(AAPL):AAPL (코드:512)

            prdt_type_cd (str): 상품유형코드

              | '300':주식
              | '301':선물옵션
              | '302':채권
              | '512':미국 나스닥 / 513 미국 뉴욕 / 529 미국 아멕스
              | '515':일본
              | '501':홍콩 / 543 홍콩CNY / 558 홍콩USD
              | '507':베트남 하노이 / 508 베트남 호치민
              | '551':중국 상해A / 552 중국 심천A

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 응답상세

                - pdno: 상품번호
                - prdt_type_cd: 상품유형코드
                - prdt_name: 상품명
                - prdt_name120: 상품명120
                - prdt_abrv_name: 상품약어명
                - prdt_eng_name: 상품영문명
                - prdt_eng_name120: 상품영문명120
                - prdt_eng_abrv_name: 상품영문약어명
                - std_pdno: 표준상품번호
                - shtn_pdno: 단축상품번호
                - prdt_sale_stat_cd: 상품판매상태코드
                - prdt_risk_grad_cd: 상품위험등급코드
                - prdt_clsf_cd: 상품분류코드
                - prdt_clsf_name: 상품분류명
                - sale_strt_dt: 판매시작일자
                - sale_end_dt: 판매종료일자
                - wrap_asst_type_cd: 랩어카운트자산유형코드
                - ivst_prdt_type_cd: 투자상품유형코드
                - ivst_prdt_type_cd_name: 투자상품유형코드명
                - frst_erlm_dt: 최초등록일자

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert prdt_type_cd in ["300", "301", "302", "512", "513", "529", "515", "501", "543", "558", "507", "508", "551", "552"], "unknown prdt_type_cd"

        url_path = "/uapi/domestic-stock/v1/quotations/search-info"
        tr_id = "CTPF1604R"

        params = {"pdno": pdno, "prdt_type_cd": prdt_type_cd}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body["output"]

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": output}

        return result

    def chk_holiday(self, base_dt: dtm.date, ctx_area_nk: str = "", ctx_area_fk: str = ""):
        """
        (국내주식시세) 휴일여부조회[v1_국내주식-030]

        국내휴장일조회 API입니다.
        영업일, 거래일, 개장일, 결제일 여부를 조회할 수 있습니다.
        주문을 넣을 수 있는지 확인하고자 하실 경우 개장일여부(opnd_yn)을 사용하시면 됩니다.

        Args:
            base_dt (datetime.date): 기준일자.
            ctx_area_nk (str): 연속조회키
            ctx_area_fk (str): 연속조회검색조건

        Returns:
            dict:

            - rt_cd (str): 응답코드.
            - msg_cd (str): 메시지코드.
            - msg1 (str): 메시지1.
            - tr_cont (str): 연속 조회 가능 여부
            - ctx_area_nk (str): 연속조회키
            - ctx_area_fk (str): 연속조회검색조건
            - output (list): 응답상세.

                - bass_dt (datetime.date): 기준일자
                - wday_dvsn_cd (str): 요일구분코드 - 01:일요일, 02:월요일, 03:화요일, 04:수요일, 05:목요일, 06:금요일, 07:토요일
                - bzdy_yn (bool): 영업일여부 - 금융기관이 업무를 하는 날
                - tr_day_yn (bool): 거래일여부 - 증권 업무가 가능한 날(입출금, 이체 등의 업무 포함)
                - opnd_yn (bool): 개장일여부 - 주식시장이 개장되는 날. 주문을 넣고자 할 경우 개장일여부(opnd_yn)를 사용
                - sttl_day_yn (bool): 결제일여부 - 주식 거래에서 실제로 주식을 인수하고 돈을 지불하는 날

        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/quotations/chk-holiday"
        tr_id = "CTCA0903R"
        tr_cont = "" if ctx_area_fk == "" else "N"

        params = {"BASS_DT": base_dt.strftime("%Y%m%d"), "CTX_AREA_NK": ctx_area_nk, "CTX_AREA_FK": ctx_area_fk}
        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            el["bass_dt"] = dtm.datetime.strptime(el["bass_dt"], "%Y%m%d").date()
            for k in el.keys():
                if k in ["wday_dvsn_cd", "bzdy_yn", "tr_day_yn", "opnd_yn", "sttl_day_yn"]:
                    el[k] = True if el[k] == "Y" else False
            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "tr_cont": res_headers["tr_cont"],
            "ctx_area_nk": res_body["ctx_area_nk"].strip(),
            "ctx_area_fk": res_body["ctx_area_fk"].strip(),
            "output": output,
        }

        return result

    def get_foreign_institution_total(self, fid_input_iscd: str, fid_div_cls_code: str, fid_rank_sort_cls_code: str, fid_etc_cls_code: str, tr_cont: str = ""):
        """
        (국내주식시세) 국내기관_외국인 매매종목가집계[국내주식-037]

        국내기관_외국인 매매종목가집계 API입니다.

        증권사 직원이 장중에 집계/입력한 자료를 단순 누계한 수치로서,
        입력시간은 외국인 09:30, 11:20, 13:20, 14:30 / 기관종합 10:00, 11:20, 13:20, 14:30 이며 사정에 따라 변동될 수 있습니다.

        Args:
            fid_input_iscd (str): 입력 종목코드 - 0000:전체, 0001:코스피, 1001:코스닥, ... 포탈 (FAQ : 종목정보 다운로드 - 업종코드 참조)
            fid_div_cls_code (str): 분류 구분 코드 - 0: 수량정열, 1: 금액정열
            fid_rank_sort_cls_code (str): 순위 정렬 구분 코드 - 0: 순매수상위, 1: 순매도상위
            fid_etc_cls_code (str): 기타 구분 정렬 - 0:전체 1:외국인 2:기관계 3:기타
            tr_cont (str): 연속조회여부

        Returns:
            dict

            - rt_cd (str): 응답코드
            - tr_cont (str): 연속조회가능여부
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (list): 응답상세

                - hts_kor_isnm: HTS 한글 종목명
                - mksc_shrn_iscd: 유가증권 단축 종목코드
                - ntby_qty: 순매수 수량
                - stck_prpr: 주식 현재가
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_vrss: 전일 대비
                - prdy_ctrt: 전일 대비율
                - acml_vol: 누적 거래량
                - frgn_ntby_qty: 외국인 순매수 수량
                - orgn_ntby_qty: 기관계 순매수 수량
                - ivtr_ntby_qty: 투자신탁 순매수 수량
                - bank_ntby_qty: 은행 순매수 수량
                - insu_ntby_qty: 보험 순매수 수량
                - mrbn_ntby_qty: 종금 순매수 수량
                - fund_ntby_qty: 기금 순매수 수량
                - etc_orgt_ntby_vol: 기타 단체 순매수 거래량
                - etc_corp_ntby_vol: 기타 법인 순매수 거래량
                - frgn_ntby_tr_pbmn: 외국인 순매수 거래 대금 - frgn_ntby_tr_pbmn ~ etc_corp_ntby_tr_pbmn (단위 : 백만원, 수량*현재가)
                - orgn_ntby_tr_pbmn: 기관계 순매수 거래 대금
                - ivtr_ntby_tr_pbmn: 투자신탁 순매수 거래 대금
                - bank_ntby_tr_pbmn: 은행 순매수 거래 대금
                - insu_ntby_tr_pbmn: 보험 순매수 거래 대금
                - mrbn_ntby_tr_pbmn: 종금 순매수 거래 대금
                - fund_ntby_tr_pbmn: 기금 순매수 거래 대금
                - etc_orgt_ntby_tr_pbmn: 기타 단체 순매수 거래 대금
                - etc_corp_ntby_tr_pbmn: 기타 법인 순매수 거래 대금

        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert fid_div_cls_code in ["0", "1"], 'fid_div_cls_code must be "0" or "1"'
        assert fid_rank_sort_cls_code in ["0", "1"], 'fid_rank_sort_cls_code must be "0" or "1"'
        assert fid_etc_cls_code in ["0", "1", "2", "3"], 'fid_etc_cls_code must be "0", "1", "2" or "3"'

        url_path = "/uapi/domestic-stock/v1/quotations/foreign-institution-total"
        tr_id = "FHPTJ04400000"

        params = {
            "FID_COND_MRKT_DIV_CODE": "V",
            "FID_COND_SCR_DIV_CODE": "16449",
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_DIV_CLS_CODE": fid_div_cls_code,
            "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
            "FID_ETC_CLS_CODE": fid_etc_cls_code,
        }

        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            for k in el.keys():
                if k == "prdy_ctrt":
                    el[k] = Decimal(el[k])
                elif k == "hts_kor_isnm":
                    pass
                else:
                    el[k] = int(el[k])
            output.append(el)

        result = {"rt_cd": res_body["rt_cd"], "tr_cont": res_headers["tr_cont"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": output}

        return result

    def get_stock_condition_search_list(self, user_id: str, tr_cont: str = ""):
        """
        (국내주식시세) 종목조건검색 목록조회[국내주식-038]

        HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API입니다.
        종목조건검색 목록조회 API(/uapi/domestic-stock/v1/quotations/psearch-title)의 output인 'seq'을 종목조건검색조회 API(/uapi/domestic-stock/v1/quotations/psearch-result)의 input으로 사용하시면 됩니다.

        ※ 시스템 안정성을 위해 API로 제공되는 조건검색 결과의 경우 조건당 100건으로 제한을 둔 점 양해 부탁드립니다.

        ※ [0110] 화면의 '대상변경' 설정사항은 HTS [0110] 사용자 조건검색 화면에만 적용됨에 유의 부탁드립니다.

        ※ '조회가 계속 됩니다. (다음을 누르십시오.)' 오류 발생 시 해결방법
        → HTS(efriend Plus) [0110] 조건검색 화면에서 조건을 등록하신 후, 왼쪽 하단의 "사용자조건 서버저장" 클릭하셔서 등록한 조건들을 서버로 보낸 후 다시 API 호출 시도 부탁드립니다.


        Args:
            user_id (str): 사용자 HTS ID
            tr_cont (str): 연속조회여부

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - tr_cont (str): 연속조회가능여부
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (list): 응답상세

                - seq (str): 조건키값 - 해당 값을 종목조건검색조회 API의 input으로 사용 (0번부터 시작)
                - grp_nm (str): 그룹명 - HTS(eFriend Plus) [0110] "사용자조건검색"화면을 통해 등록한 사용자조건 그룹
                - condition_nm (str): 조건명 - 등록한 사용자 조건명

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/quotations/psearch-title"
        tr_id = "HHKST03900300"
        params = {"user_id": user_id}

        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output2"]:
            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "tr_cont": res_headers["tr_cont"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output": output,
        }

        return result

    def get_stock_condition_search_results(self, user_id: str, seq: str, tr_cont: str = ""):
        """
        (국내주식시세) 종목조건검색조회 [국내주식-039]

        HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API입니다.
        종목조건검색 목록조회 API(/uapi/domestic-stock/v1/quotations/psearch-title)의 output인 'seq'을 종목조건검색조회 API(/uapi/domestic-stock/v1/quotations/psearch-result)의 input으로 사용하시면 됩니다.

        ※ 시스템 안정성을 위해 API로 제공되는 조건검색 결과의 경우 조건당 100건으로 제한을 둔 점 양해 부탁드립니다.

        ※ [0110] 화면의 '대상변경' 설정사항은 HTS [0110] 사용자 조건검색 화면에만 적용됨에 유의 부탁드립니다.

        ※ '조회가 계속 됩니다. (다음을 누르십시오.)' 오류 발생 시 해결방법
        → HTS(efriend Plus) [0110] 조건검색 화면에서 조건을 등록하신 후, 왼쪽 하단의 "사용자조건 서버저장" 클릭하셔서 등록한 조건들을 서버로 보낸 후 다시 API 호출 시도 부탁드립니다.

        ※ {"rt_cd":"1","msg_cd":"MCA05918","msg1":"종목코드 오류입니다."} 메시지 발생 이유
        → 조건검색 결과 검색된 종목이 0개인 경우 위 응답값을 수신하게 됩니다.

        Args:
            user_id (str): 사용자 HTS ID
            seq (str): 사용자조건 키값 - 종목조건검색 목록조회 API의 output인 'seq'값을 사용 (0번부터 시작)
            tr_cont (str): 연속조회여부

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - tr_cont (str): 연속조회가능여부
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (list): 응답상세

                - code (str): 종목코드
                - name (str): 종목명
                - daebi (int): 전일대비부호 (1:상한 2:상승 3:보합 4:하한 5:하락)
                - price (int): 현재가
                - chgrate (Decimal): 등락율
                - acml_vol (Decimal): 거래량
                - trade_amt (Decimal): 거래대금
                - change (Decimal): 전일대비
                - cttr (Decimal): 체결강도
                - open (Decimal): 시가
                - high (Decimal): 고가
                - low (Decimal): 저가
                - high52 (Decimal): 52주최고가
                - low52 (Decimal): 52주최저가
                - expprice (Decimal): 예상체결가
                - expchange (Decimal): 예상대비
                - expchggrate (Decimal): 예상등락률
                - expcvol (Decimal): 예상체결수량
                - chgrate2 (Decimal): 전일거래량대비율
                - expdaebi (int): 예상대비부호
                - recprice (Decimal): 기준가
                - uplmtprice (Decimal): 상한가
                - dnlmtprice (Decimal): 하한가
                - stotprice (Decimal): 시가총액
        """
        url_path = "/uapi/domestic-stock/v1/quotations/psearch-result"
        tr_id = "HHKST03900400"

        params = {
            "user_id": user_id,
            "seq": seq,
        }

        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output2"]:
            for k in el.keys():
                if el[k] is None or len(el[k]) == 0:
                    pass
                elif k in ["code", "name"]:
                    pass
                elif k in ["daebi", "expdaebi"]:
                    el[k] = int(el[k])
                else:
                    el[k] = Decimal(el[k])
            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "tr_cont": res_headers["tr_cont"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output": output,
        }

        return result

    def get_program_trade_by_stock(self, fid_input_iscd: str, tr_cont: str = "", fid_cond_mrkt_div_code: str = "J"):
        """
        (국내주식시세) 종목별 프로그램매매추이(체결)[v1_국내주식-044]

        국내주식 종목별 프로그램매매추이(체결) API입니다.

        한국투자 HTS(eFriend Plus) > [0465] 종목별 프로그램 매매추이 화면(혹은 한국투자 MTS > 국내 현재가 > 기타수급 > 프로그램) 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            fid_input_iscd (str): 입력 종목코드 - 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            tr_cont (str): 연속조회여부
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - tr_cont (str): 연속조회가능여부
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (list): 응답상세

                - bsop_hour: 영업 시간
                - stck_prpr: 주식 현재가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - acml_vol: 누적 거래량
                - whol_smtn_seln_vol: 전체 합계 매도 거래량
                - whol_smtn_shnu_vol: 전체 합계 매수2 거래량
                - whol_smtn_ntby_qty: 전체 합계 순매수 수량
                - whol_smtn_seln_tr_pbmn: 전체 합계 매도 거래 대금
                - whol_smtn_shnu_tr_pbmn: 전체 합계 매수2 거래 대금
                - whol_smtn_ntby_tr_pbmn: 전체 합계 순매수 거래 대금
                - whol_ntby_vol_icdc: 전체 순매수 거래량 증감
                - whol_ntby_tr_pbmn_icdc: 전체 순매수 거래 대금 증감

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/quotations/program-trade-by-stock"
        tr_id = "FHPPG04650101"

        params = {
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
        }

        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            for k in el.keys():
                if k in ["prdy_ctrt"]:
                    el[k] = Decimal(el[k])
                elif k == "bsop_hour":
                    el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                else:
                    el[k] = int(el[k])
            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "tr_cont": res_headers["tr_cont"],
            "output": output,
        }

        return result

    def get_volume_rank(
        self,
        fid_input_iscd: str,
        fid_div_cls_code: str,
        fid_blng_cls_code: str,
        fid_trgt_cls_code: str,
        fid_trgt_excls_cls_code: str,
        fid_input_price_1: int = None,
        fid_input_price_2: int = None,
        fid_vol_cnt: int = None,
    ):
        """
        (국내주식시세) 거래량순위[v1_국내주식-047]

        국내주식 거래량순위 API입니다.

        한국투자 HTS(eFriend Plus) > [0171] 거래량 순위 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        최대 30건 확인 가능하며, 다음 조회가 불가합니다.
        +30건 이상의 목록 조회가 필요한 경우, 대안으로 종목조건검색 API를 이용해서 원하는 종목 100개까지 검색할 수 있는 기능을 제공하고 있습니다.

        종목조건검색 API는 HTS(efriend Plus) [0110] 조건검색에서 등록 및 서버저장한 나의 조건 목록을 확인할 수 있는 API로,
        HTS [0110]에서 여러가지 조건을 설정할 수 있는데, 그 중 거래량 순위(ex. 0봉전 거래량 상위순 100종목) 에 대해서도 설정해서 종목을 검색할 수 있습니다.

        자세한 사용 방법은 공지사항 - [조건검색 필독] 조건검색 API 이용안내 참고 부탁드립니다.

        Args:
            fid_input_iscd (str): 입력 종목코드 0000(전체) 기타(업종코드)
            fid_div_cls_code (str): 분류 구분 코드 0:전체 1:보통주 2:우선주
            fid_blng_cls_code (str): 소속 구분 코드 0:평균거래량 1:거래증가율 2:평균거래회전율 3:거래금액순 4:평균거래금액회전율
            fid_trgt_cls_code (str): 대상 구분 코드

              | 1 or 0 9자리 (차례대로 증거금 30% 40% 50% 60% 100% 신용보증금 30% 40% 50% 60%)
              | ex) "111111111"

            fid_trgt_exls_cls_code (str): 대상 제외 구분 코드

              | 1 or 0 6자리 (차례대로 투자위험/경고/주의 관리종목 정리매매 불성실공시 우선주 거래정지)
              | ex) "000000"

            fid_input_price_1 (int): 입력 가격1 - 가격 ~

              | ex) 0
              | 전체 가격 대상 조회 시 FID_INPUT_PRICE_1, FID_INPUT_PRICE_2 모두 None

            fid_input_price_2 (int): 입력 가격2 - ~ 가격

              | ex) 1000000
              | 전체 가격 대상 조회 시 FID_INPUT_PRICE_1, FID_INPUT_PRICE_2 모두 None

            fid_vol_cnt (int): 거래량 수 - 거래량 ~

              | ex) 100000
              | 전체 거래량 대상 조회 시 FID_VOL_CNT None

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (list): 응답상세

                - hts_kor_isnm: HTS 한글 종목명
                - mksc_shrn_iscd: 유가증권 단축 종목코드
                - data_rank: 데이터 순위
                - stck_prpr: 주식 현재가
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_vrss: 전일 대비
                - prdy_ctrt: 전일 대비율
                - acml_vol: 누적 거래량
                - prdy_vol: 전일 거래량
                - lstn_stcn: 상장 주수
                - avrg_vol: 평균 거래량
                - n_befr_clpr_vrss_prpr_rate: N일전종가대비현재가대비율
                - vol_inrt: 거래량증가율
                - vol_tnrt: 거래량 회전율
                - nday_vol_tnrt: N일 거래량 회전율
                - avrg_tr_pbmn: 평균 거래 대금
                - tr_pbmn_tnrt: 거래대금회전율
                - nday_tr_pbmn_tnrt: N일 거래대금 회전율
                - acml_tr_pbmn: 누적 거래 대금

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert fid_div_cls_code in ["0", "1"], 'fid_div_cls_code must be "0" or "1"'
        assert fid_blng_cls_code in ["0", "1", "2", "3", "4"], 'fid_blng_cls_code must be "0", "1", "2", "3" or "4"'
        assert len(fid_trgt_cls_code) == 9, "fid_trgt_cls_code length must be 9"
        assert all([x in ["0", "1"] for x in fid_trgt_cls_code]), 'fid_trgt_cls_code must be "0" or "1"'
        assert len(fid_trgt_excls_cls_code) == 6, "fid_trgt_excls_cls_code length must be 6"
        assert all([x in ["0", "1"] for x in fid_trgt_excls_cls_code]), 'fid_trgt_excls_cls_code must be "0" or "1"'
        assert fid_input_price_1 is None or isinstance(fid_input_price_1, int), "fid_input_price_1 must be None or int"
        assert fid_input_price_2 is None or isinstance(fid_input_price_2, int), "fid_input_price_2 must be None or int"
        assert fid_vol_cnt is None or isinstance(fid_vol_cnt, int), "fid_vol_cnt must be None or int"

        url_path = "/uapi/domestic-stock/v1/quotations/volume-rank"
        tr_id = "FHPST01710000"
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_DIV_CLS_CODE": fid_div_cls_code,
            "FID_BLNG_CLS_CODE": fid_blng_cls_code,
            "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
            "FID_TRGT_EXLS_CLS_CODE": fid_trgt_excls_cls_code,
            "FID_INPUT_PRICE_1": "" if fid_input_price_1 is None else int(fid_input_price_1),
            "FID_INPUT_PRICE_2": "" if fid_input_price_2 is None else int(fid_input_price_2),
            "FID_VOL_CNT": "" if fid_vol_cnt is None else int(fid_vol_cnt),
            "FID_INPUT_DATE_1": "0",
        }
        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            for k in el.keys():
                if k in ["hts_kor_isnm", "mksc_shrn_iscd"]:
                    pass
                elif k in ["prdy_ctrt", "n_befr_clpr_vrss_prpr_rate", "vol_inrt", "vol_tnrt", "nday_vol_tnrt", "tr_pbmn_tnrt", "nday_tr_pbmn_tnrt"]:
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])
            output.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": output}

        return result

    def get_investor_trend_estimate(self, mksc_shrn_iscd: str):
        """
        (국내주식시세) 종목별 외인기관 추정가집계[v1_국내주식-046]

        국내주식 종목별 외국인, 기관 추정가집계 API입니다.

        한국투자 MTS > 국내 현재가 > 투자자 > 투자자동향 탭 > 왼쪽구분을 '추정(주)'로 선택 시 확인 가능한 데이터를 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        증권사 직원이 장중에 집계/입력한 자료를 단순 누계한 수치로서,
        입력시간은 외국인 09:30, 11:20, 13:20, 14:30 / 기관종합 10:00, 11:20, 13:20, 14:30 이며, 사정에 따라 변동될 수 있습니다.

        Args:
            mksc_shrn_iscd (str): 종목코드

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (list): 응답상세

                - bsop_hour_gb: 입력구분 - 1:09시30분 입력 2:10시00분 입력 3:11시20분 입력 4:13시20분 입력 5:14시30분 입력
                - frgn_fake_ntby_qty: 외국인수량 (가집계)
                - orgn_fake_ntby_qty: 기관수량 (가집계)
                - sum_fake_ntby_qty: 합산수량 (가집계)


        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/quotations/investor-trend-estimate"
        tr_id = "HHPTJ04160200"
        params = {"MKSC_SHRN_ISCD": mksc_shrn_iscd}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "bsop_hour_gb":
                    pass
                else:
                    el[k] = int(el[k])
            output.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": res_body["output2"]}

        return result

    def inquire_time_indexchartprice(self, fid_etc_cls_code: str, fid_input_iscd: str, fid_input_hour_1: int, fid_pw_data_incu_yn: str, tr_cont: str = ""):
        """
        (국내주식시세) 업종 분봉조회[v1_국내주식-045]

        업종분봉조회 API입니다.
        실전계좌의 경우, 한 번의 호출에 최대 102건까지 확인 가능합니다.

        Args:
            fid_etc_cls_code (str): 기타 구분 코드 - 0:기본 1:장마감,시간외 제외
            fid_input_iscd (str): 입력 종목코드 - 0001:종합, 1001:코스닥종합
            fid_input_hour_1 (int): 입력 시간1 - 30,60->1분 600->10분 3600->1시간
            fid_pw_data_incu_yn (str): 과거 데이터 포함 여부 - Y:과거 N:당일
            tr_cont (str): 연속조회여부. '':초기조회, 'N':연속조회

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output1 (dict): 응답상세

                - bstp_nmix_prdy_vrss: 업종 지수 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - bstp_nmix_prdy_ctrt: 업종 지수 전일 대비율
                - prdy_nmix: 전일 지수
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - hts_kor_isnm: HTS 한글 종목명
                - bstp_nmix_prpr: 업종 지수 현재가
                - bstp_cls_code: 업종 구분 코드
                - prdy_vol: 전일 거래량
                - bstp_nmix_oprc: 업종 지수 시가2
                - bstp_nmix_hgpr: 업종 지수 최고가
                - bstp_nmix_lwpr: 업종 지수 최저가
                - futs_prdy_oprc: 선물 전일 시가
                - futs_prdy_hgpr: 선물 전일 최고가
                - futs_prdy_lwpr: 선물 전일 최저가

            - output2 (list): 응답상세

                - stck_bsop_date: 주식 영업 일자
                - stck_cntg_hour: 주식 체결 시간
                - bstp_nmix_prpr: 업종 지수 현재가
                - bstp_nmix_oprc: 업종 지수 시가2
                - bstp_nmix_hgpr: 업종 지수 최고가
                - bstp_nmix_lwpr: 업종 지수 최저가
                - cntg_vol: 체결 거래량
                - acml_tr_pbmn: 누적 거래 대금

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert fid_etc_cls_code in ["0", "1"], 'fid_etc_cls_code must be "0" or "1"'
        assert fid_input_iscd in ["0001", "1001"], 'fid_input_iscd must be "0001" or "1001"'
        assert fid_pw_data_incu_yn in ["Y", "N"], 'fid_pw_data_incu_yn must be "Y" or "N"'

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-time-indexchartprice"
        tr_id = "FHKUP03500200"
        params = {"FID_COND_MRKT_DIV_CODE": "U", "FID_ETC_CLS_CODE": fid_etc_cls_code, "FID_INPUT_ISCD": fid_input_iscd, "FID_INPUT_HOUR_1": str(fid_input_hour_1), "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn}

        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k in ["hts_kor_isnm", "bstp_cls_code"]:
                pass
            elif k in ["prdy_vrss_sign", "acml_vol", "acml_tr_pbmn", "prdy_vol"]:
                output1[k] = int(output1[k])
            else:
                output1[k] = Decimal(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "stck_bsop_date":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k == "stck_cntg_hour":
                    el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                elif k in ["cntg_vol", "acml_tr_pbmn"]:
                    el[k] = int(el[k])
                else:
                    el[k] = Decimal(el[k])
            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output1": output1, "output2": output2}
        return result

    def inquire_time_dailychartprice(self, fid_input_iscd: str, fid_input_date_1: dtm.date, fid_input_hour_1: dtm.time, fid_cond_mrkt_div_code: str = "J", fid_pw_data_incu_yn: str = "Y", fid_fake_tick_incu_yn: str = "N"):
        """
        (국내주식시세) 주식일별 분봉조회[v1_국내주식-213]

        주식일별분봉조회 API입니다.

        실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, FID_INPUT_DATE_1, FID_INPUT_HOUR_1 이용하여 과거일자 분봉조회 가능합니다.

        과거 분봉 조회 시, 당사 서버에서 보관하고 있는 만큼의 데이터만 확인이 가능합니다. (최대 1년 분봉 보관)

        Args:
            fid_input_iscd (str): 종목번호(6자리) ETN의 경우 Q로 시작(EX. Q500001)
            fid_input_date_1 (dt.date): 조회 시작일자 (ex. dtm.date(2024, 2, 8))
            fid_input_hour_1 (dt.time): 조회 시작시간 (ex. dtm.time(15, 30, 0))
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합
            fid_pw_data_incu_yn (str): 과거 데이터 포함 여부 - Y:과거 N:당일만 조회
            fid_fake_tick_incu_yn (str): 허봉 포함 여부 - 공백

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1

            - output1 (dict): 응답상세1

                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - stck_prdy_clpr: 주식 전일 종가
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - hts_kor_isnm: HTS 한글 종목명
                - stck_prpr: 주식 현재가

            - output2 (list): 응답상세2

                - stck_bsop_date: 주식 영업 일자
                - stck_cntg_hour: 주식 체결 시간
                - stck_prpr: 주식 현재가
                - stck_oprc: 주식 시가2
                - stck_hgpr: 주식 최고가
                - stck_lwpr: 주식 최저가
                - cntg_vol: 체결 거래량
                - acml_tr_pbmn: 누적 거래 대금

        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert len(fid_input_iscd) >= 6, "fid_input_iscd length must be 6"
        assert fid_cond_mrkt_div_code in ["J", "NX", "UN"], 'fid_cond_mrkt_div_code must be one of "J", "NX", or "UN"'
        assert fid_pw_data_incu_yn in ["Y", "N"], 'fid_pw_data_incu_yn must be "Y" or "N"'
        assert fid_fake_tick_incu_yn in ["Y", "N"], 'fid_fake_tick_incu_yn must be "Y" or "N"'

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-time-dailychartprice"
        tr_id = "FHKST03010230"
        params = {
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_INPUT_DATE_1": fid_input_date_1.strftime("%Y%m%d"),
            "FID_INPUT_HOUR_1": fid_input_hour_1.strftime("%H%M%S"),
            "FID_PW_DATA_INCU_YN": fid_pw_data_incu_yn,
            "FID_FAKE_TICK_INCU_YN": "",
        }

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k in ["hts_kor_isnm"]:
                pass
            elif k == ["prdy_vrss_sign", "stck_prdy_clpr", "acml_vol", "acml_tr_pbmn"]:
                output1[k] = int(output1[k])
            else:
                output1[k] = Decimal(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "stck_bsop_date":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k == "stck_cntg_hour":
                    el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                elif k in ["cntg_vol", "acml_tr_pbmn"]:
                    el[k] = int(el[k])
                else:
                    el[k] = Decimal(el[k])
            output2.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "tr_cont": res_headers["tr_cont"],
            "output1": output1,
            "output2": output2,
        }

        return result

    def inquire_price_2(self, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J"):
        """
        (국내주식시세) 주식현재가 시세2[v1_국내주식-054]

        주식현재가 시세2 API입니다.

        Args:
            fid_input_iscd (str): 입력 종목코드
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J:주식,ETF,ETN NX:Nextrade UN:통합

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 응답상세

                - rprs_mrkt_kor_name: 대표 시장 한글 명
                - new_hgpr_lwpr_cls_code: 신 고가 저가 구분 코드 - 특정 경우에만 데이터 출력
                - mxpr_llam_cls_code: 상하한가 구분 코드  - 특정 경우에만 데이터 출력
                - crdt_able_yn: 신용 가능 여부
                - stck_mxpr: 주식 상한가
                - elw_pblc_yn: ELW 발행 여부
                - prdy_clpr_vrss_oprc_rate: 전일 종가 대비 시가2 비율
                - crdt_rate: 신용 비율
                - marg_rate: 증거금 비율
                - lwpr_vrss_prpr: 최저가 대비 현재가
                - lwpr_vrss_prpr_sign: 최저가 대비 현재가 부호
                - prdy_clpr_vrss_lwpr_rate: 전일 종가 대비 최저가 비율
                - stck_lwpr: 주식 최저가
                - hgpr_vrss_prpr: 최고가 대비 현재가
                - hgpr_vrss_prpr_sign: 최고가 대비 현재가 부호
                - prdy_clpr_vrss_hgpr_rate: 전일 종가 대비 최고가 비율
                - stck_hgpr: 주식 최고가
                - oprc_vrss_prpr: 시가2 대비 현재가
                - oprc_vrss_prpr_sign: 시가2 대비 현재가 부호
                - mang_issu_yn: 관리 종목 여부
                - divi_app_cls_code: 동시호가배분처리코드 - 11:매수상한배분 12:매수하한배분 13: 매도상한배분 14:매도하한배분
                - short_over_yn: 단기과열여부
                - mrkt_warn_cls_code: 시장경고코드 - 00: 없음 01: 투자주의 02:투자경고 03:투자위험
                - invt_caful_yn: 투자유의여부
                - stange_runup_yn: 이상급등여부
                - ssts_hot_yn: 공매도과열 여부
                - low_current_yn: 저유동성 종목 여부
                - vi_cls_code: VI적용구분코드
                - short_over_cls_code: 단기과열구분코드
                - stck_llam: 주식 하한가
                - new_lstn_cls_name: 신규 상장 구분 명
                - vlnt_deal_cls_name: 임의 매매 구분 명
                - flng_cls_name: 락 구분 이름  - 특정 경우에만 데이터 출력
                - revl_issu_reas_name: 재평가 종목 사유 명 - 특정 경우에만 데이터 출력
                - mrkt_warn_cls_name: 시장 경고 구분 명 - 특정 경우에만 데이터 출력 "투자환기" / "투자경고"
                - stck_sdpr: 주식 기준가
                - bstp_cls_code: 업종 구분 코드
                - stck_prdy_clpr: 주식 전일 종가
                - insn_pbnt_yn: 불성실 공시 여부
                - fcam_mod_cls_name: 액면가 변경 구분 명 - 특정 경우에만 데이터 출력
                - stck_prpr: 주식 현재가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - acml_tr_pbmn: 누적 거래 대금
                - acml_vol: 누적 거래량
                - prdy_vrss_vol_rate: 전일 대비 거래량 비율
                - bstp_kor_isnm: 업종 한글 종목명
                - sltr_yn: 정리매매 여부
                - trht_yn: 거래정지 여부
                - oprc_rang_cont_yn: 시가 범위 연장 여부
                - vlnt_fin_cls_code: 임의 종료 구분 코드
                - stck_oprc: 주식 시가2
                - prdy_vol: 전일 거래량

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-price-2"
        tr_id = "FHPST01010000"
        params = {"FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code, "FID_INPUT_ISCD": fid_input_iscd}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body["output"]
        for k in output.keys():
            if k in ["prdy_ctrt", "prdy_vrss_vol_rate", "prdy_clpr_vrss_oprc_rate", "prdy_clpr_vrss_hgpr_rate", "prdy_clpr_vrss_lwpr_rate", "marg_rate", "crdt_rate"]:
                output[k] = Decimal(output[k])
            elif k in [
                "stck_prpr",
                "prdy_vrss",
                "prdy_vrss_sign",
                "acml_tr_pbmn",
                "acml_vol",
                "prdy_vol",
                "stck_prdy_clpr",
                "stck_oprc",
                "oprc_vrss_prpr_sign",
                "oprc_vrss_prpr",
                "stck_hgpr",
                "hgpr_vrss_prpr_sign",
                "hgpr_vrss_prpr",
                "stck_lwpr",
                "lwpr_vrss_prpr_sign",
                "lwpr_vrss_prpr",
                "stck_mxpr",
                "stck_llam",
                "bstp_cls_code",
                "stck_sdpr",
            ]:
                output[k] = int(output[k])
            else:
                output[k] = output[k].strip()

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": res_body["output"]}

        return result

    def inquire_daily_trade_volume(self, fid_input_iscd: str, fid_input_date_1: dtm.date, fid_input_date_2: dtm.date, tr_cont: str = ""):
        """
        (국내주식시세) 종목별일별매수매도체결량 [v1_국내주식-056]

        종목별일별매수매도체결량 API입니다. 실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.
        국내주식 종목의 일별 매수체결량, 매도체결량 데이터를 확인할 수 있습니다.

        Args:
            fid_input_iscd (str): 입력 종목코드
            fid_input_date_1 (dtm.date): 입력 일자1 - from
            fid_input_date_2 (dtm.date): 입력 일자2 - to
            tr_cont (str): 연속조회여부

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부

            - output1 (dict): 응답상세

                - shnu_cnqn_smtn: 매수 체결량 합계 - 당일 매수체결량 합계
                - seln_cnqn_smtn: 매도 체결량 합계 - 당일 매도체결량 합계

            - output2 (list): 응답상세

                - stck_bsop_date: 주식 영업 일자
                - total_seln_qty: 총 매도 수량
                - total_shnu_qty: 총 매수 수량

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-daily-trade-volume"
        tr_id = "FHKST03010800"
        params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": fid_input_iscd, "FID_INPUT_DATE_1": fid_input_date_1.strftime("%Y%m%d"), "FID_INPUT_DATE_2": fid_input_date_2.strftime("%Y%m%d"), "FID_PERIOD_DIV_CODE": "D"}
        res_body, res_headers = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "stck_bsop_date":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                else:
                    el[k] = int(el[k])
            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_headers["tr_cont"], "output1": output1, "output2": output2}

        return result

    def inquire_index_price(self, fid_input_iscd: str):
        """
        (국내주식시세) 국내업종 현재지수[v1_국내주식-063]

        국내업종 현재지수 API입니다.

        한국투자 HTS(eFriend Plus) > [0210] 업종 현재지수 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            fid_input_iscd (str): 입력 종목코드 - 코스피(0001), 코스닥(1001), 코스피200(2001)

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 응답상세

                - bstp_nmix_prpr: 업종 지수 현재가
                - bstp_nmix_prdy_vrss: 업종 지수 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - bstp_nmix_prdy_ctrt: 업종 지수 전일 대비율
                - acml_vol: 누적 거래량
                - prdy_vol: 전일 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - prdy_tr_pbmn: 전일 거래 대금
                - bstp_nmix_oprc: 업종 지수 시가2
                - prdy_nmix_vrss_nmix_oprc: 전일 지수 대비 지수 시가2
                - oprc_vrss_prpr_sign: 시가2 대비 현재가 부호
                - bstp_nmix_oprc_prdy_ctrt: 업종 지수 시가2 전일 대비율
                - bstp_nmix_hgpr: 업종 지수 최고가
                - prdy_nmix_vrss_nmix_hgpr: 전일 지수 대비 지수 최고가
                - hgpr_vrss_prpr_sign: 최고가 대비 현재가 부호
                - bstp_nmix_hgpr_prdy_ctrt: 업종 지수 최고가 전일 대비율
                - bstp_nmix_lwpr: 업종 지수 최저가
                - prdy_clpr_vrss_lwpr: 전일 종가 대비 최저가
                - lwpr_vrss_prpr_sign: 최저가 대비 현재가 부호
                - prdy_clpr_vrss_lwpr_rate: 전일 종가 대비 최저가 비율
                - ascn_issu_cnt: 상승 종목 수
                - uplm_issu_cnt: 상한 종목 수
                - stnr_issu_cnt: 보합 종목 수
                - down_issu_cnt: 하락 종목 수
                - lslm_issu_cnt: 하한 종목 수
                - dryy_bstp_nmix_hgpr: 연중업종지수최고가
                - dryy_hgpr_vrss_prpr_rate: 연중 최고가 대비 현재가 비율
                - dryy_bstp_nmix_hgpr_date: 연중업종지수최고가일자
                - dryy_bstp_nmix_lwpr: 연중업종지수최저가
                - dryy_lwpr_vrss_prpr_rate: 연중 최저가 대비 현재가 비율
                - dryy_bstp_nmix_lwpr_date: 연중업종지수최저가일자
                - total_askp_rsqn: 총 매도호가 잔량
                - total_bidp_rsqn: 총 매수호가 잔량
                - seln_rsqn_rate: 매도 잔량 비율
                - shnu_rsqn_rate: 매수2 잔량 비율
                - ntby_rsqn: 순매수 잔량

        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-index-price"
        tr_id = "FHPUP02100000"
        params = {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": fid_input_iscd}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body["output"]

        for k in output.keys():
            if k in ["dryy_bstp_nmix_hgpr_date", "dryy_bstp_nmix_lwpr_date"]:
                output[k] = dtm.datetime.strptime(output[k], "%Y%m%d").date()
            elif k in [
                "bstp_nmix_prdy_vrss",
                "bstp_nmix_prdy_ctrt",
                "bstp_nmix_prpr",
                "bstp_nmix_oprc",
                "prdy_nmix_vrss_nmix_oprc",
                "bstp_nmix_oprc_prdy_ctrt",
                "bstp_nmix_hgpr",
                "prdy_nmix_vrss_nmix_hgpr",
                "bstp_nmix_hgpr_prdy_ctrt",
                "bstp_nmix_lwpr",
                "prdy_clpr_vrss_lwpr",
                "prdy_clpr_vrss_lwpr_rate",
                "dryy_bstp_nmix_hgpr",
                "dryy_hgpr_vrss_prpr_rate",
                "dryy_bstp_nmix_lwpr",
                "dryy_lwpr_vrss_prpr_rate",
                "seln_rsqn_rate",
                "shnu_rsqn_rate",
            ]:
                output[k] = Decimal(output[k])
            else:
                output[k] = int(output[k])

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": output}

        return result

    def inquire_index_daily_price(
        self,
        fid_period_div_code: str,
        fid_input_iscd: str,
        fid_input_date_1: dtm.date,
    ):
        """
        (국내주식시세) 국내업종 일자별지수[v1_국내주식-065]

        국내업종 일자별지수 API입니다. 한 번의 조회에 100건까지 확인 가능합니다.

        한국투자 HTS(eFriend Plus) > [0212] 업종 일자별지수 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            fid_period_div_code (str): 기간 구분 코드 - D:일 W:주 M:월
            fid_input_iscd (str): 입력 종목코드 - 코스피(0001), 코스닥(1001), 코스피200(2001)
            fid_input_date_1 (dtm.date): 입력 일자1

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output1 (dict): 응답상세

                - bstp_nmix_prpr: 업종 지수 현재가
                - bstp_nmix_prdy_vrss: 업종 지수 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - bstp_nmix_prdy_ctrt: 업종 지수 전일 대비율
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - bstp_nmix_oprc: 업종 지수 시가2
                - bstp_nmix_hgpr: 업종 지수 최고가
                - bstp_nmix_lwpr: 업종 지수 최저가
                - prdy_vol: 전일 거래량
                - ascn_issu_cnt: 상승 종목 수
                - down_issu_cnt: 하락 종목 수
                - stnr_issu_cnt: 보합 종목 수
                - uplm_issu_cnt: 상한 종목 수
                - lslm_issu_cnt: 하한 종목 수
                - prdy_tr_pbmn: 전일 거래 대금
                - dryy_bstp_nmix_hgpr_date: 연중업종지수최고가일자
                - dryy_bstp_nmix_hgpr: 연중업종지수최고가
                - dryy_bstp_nmix_lwpr: 연중업종지수최저가
                - dryy_bstp_nmix_lwpr_date: 연중업종지수최저가일자

            - output2 (list): 응답상세

                - stck_bsop_date: 주식 영업 일자
                - bstp_nmix_prpr: 업종 지수 현재가
                - prdy_vrss_sign: 전일 대비 부호
                - bstp_nmix_prdy_vrss: 업종 지수 전일 대비
                - bstp_nmix_prdy_ctrt: 업종 지수 전일 대비율
                - bstp_nmix_oprc: 업종 지수 시가2
                - bstp_nmix_hgpr: 업종 지수 최고가
                - bstp_nmix_lwpr: 업종 지수 최저가
                - acml_vol_rlim: 누적 거래량 비중
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - invt_new_psdg: 투자 신 심리도
                - d20_dsrt: 20일 이격도

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert fid_period_div_code in ["D", "W", "M"], 'fid_period_div_code must be "D", "W" or "M"'
        assert fid_input_iscd in ["0001", "1001", "2001"], 'fid_input_iscd must be "0001", "1001" or "2001"'

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-index-daily-price"
        tr_id = "FHPUP02120000"
        params = {"FID_PERIOD_DIV_CODE": fid_period_div_code, "FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": fid_input_iscd, "FID_INPUT_DATE_1": fid_input_date_1.strftime("%Y%m%d")}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        """
        {
            'dryy_bstp_nmix_lwpr_date': '20240118'
            'dryy_bstp_nmix_hgpr_date': '20240219',
            'bstp_nmix_prpr': '2664.20',
            'bstp_nmix_prdy_vrss': '10.89',
            'bstp_nmix_prdy_ctrt': '0.41',
            'bstp_nmix_oprc': '2671.69',
            'bstp_nmix_hgpr': '2671.69',
            'bstp_nmix_lwpr': '2653.99',
            'dryy_bstp_nmix_hgpr': '2683.39',
            'dryy_bstp_nmix_lwpr': '2429.12',
            'prdy_vrss_sign': '2',
            'acml_vol': '406329',
            'acml_tr_pbmn': '8946698',
            'prdy_vol': '562144',
            'ascn_issu_cnt': '319',
            'down_issu_cnt': '545',
            'stnr_issu_cnt': '71',
            'uplm_issu_cnt': '1',
            'lslm_issu_cnt': '0',
            'prdy_tr_pbmn': '9150151',
        }
        """
        for k in output1.keys():
            if k in ["dryy_bstp_nmix_lwpr_date", "dryy_bstp_nmix_hgpr_date"]:
                try:
                    output1[k] = dtm.datetime.strptime(output1[k], "%Y%m%d").date()
                except ValueError:
                    output1[k] = None

            elif k in ["bstp_nmix_prpr", "bstp_nmix_prdy_vrss", "bstp_nmix_prdy_ctrt", "bstp_nmix_oprc", "bstp_nmix_hgpr", "bstp_nmix_lwpr", "dryy_bstp_nmix_hgpr", "dryy_bstp_nmix_lwpr"]:
                output1[k] = Decimal(output1[k])

            else:
                output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k == "stck_bsop_date":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k in ["acml_vol", "prdy_vrss_sign", "acml_tr_pbmn"]:
                    el[k] = int(el[k])
                else:
                    el[k] = Decimal(el[k])

            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output1": output1, "output2": output2}

        return result

    def inquire_index_category_price(self, fid_blng_cls_code: str, fid_input_iscd: str, fid_mrkt_cls_code: str):
        """
        (국내주식시세) 국내업종 구분별전체시세[v1_국내주식-066]

        국내업종 구분별전체시세 API입니다.
        한국투자 HTS(eFriend Plus) > [0214] 업종 전체시세 화면 의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            fid_blng_cls_code (str): FID 소속 구분 코드

              | 시장구분코드(K:거래소) 0:전업종, 1:기타구분, 2:자본금구분 3:상업별구분
              | 시장구분코드(Q:코스닥) 0:전업종, 1:기타구분, 2:벤처구분 3:일반구분
              | 시장구분코드(K2:코스닥) 0:전업종

            fid_input_iscd (str): FID 입력 종목코드 - 코스피(0001), 코스닥(1001), 코스피200(2001)
            fid_mrkt_cls_code (str): FID 시장 구분 코드 - 시장구분코드(K:거래소, Q:코스닥, K2:코스피200)

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output1 (dict): 응답상세

                - bstp_nmix_prpr: 업종 지수 현재가
                - bstp_nmix_prdy_vrss: 업종 지수 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - bstp_nmix_prdy_ctrt: 업종 지수 전일 대비율
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - bstp_nmix_oprc: 업종 지수 시가2
                - bstp_nmix_hgpr: 업종 지수 최고가
                - bstp_nmix_lwpr: 업종 지수 최저가
                - prdy_vol: 전일 거래량
                - ascn_issu_cnt: 상승 종목 수
                - down_issu_cnt: 하락 종목 수
                - stnr_issu_cnt: 보합 종목 수
                - uplm_issu_cnt: 상한 종목 수
                - lslm_issu_cnt: 하한 종목 수
                - prdy_tr_pbmn: 전일 거래 대금
                - dryy_bstp_nmix_hgpr_date: 연중업종지수최고가일자
                - dryy_bstp_nmix_hgpr: 연중업종지수최고가
                - dryy_bstp_nmix_lwpr: 연중업종지수최저가
                - dryy_bstp_nmix_lwpr_date: 연중업종지수최저가일자

            - output2 (list): 응답상세

                - bstp_cls_code: 업종 구분 코드
                - hts_kor_isnm: HTS 한글 종목명
                - bstp_nmix_prpr: 업종 지수 현재가
                - bstp_nmix_prdy_vrss: 업종 지수 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - bstp_nmix_prdy_ctrt: 업종 지수 전일 대비율
                - acml_vol: 누적 거래량
                - acml_tr_pbmn: 누적 거래 대금
                - acml_vol_rlim: 누적 거래량 비중
                - acml_tr_pbmn_rlim: 누적 거래 대금 비중
        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert fid_blng_cls_code in ["0", "1", "2", "3"], 'fid_blng_cls_code must be "0", "1", "2" or "3"'
        assert fid_input_iscd in ["0001", "1001", "2001"], 'fid_input_iscd must be "0001", "1001" or "2001"'
        assert fid_mrkt_cls_code in ["K", "Q", "K2"], 'fid_mrkt_cls_code must be "K", "Q" or "K2"'

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-index-category-price"
        tr_id = "FHPUP02140000"
        params = {"FID_COND_MRKT_DIV_CODE": "U", "FID_BLNG_CLS_CODE": fid_blng_cls_code, "FID_INPUT_ISCD": fid_input_iscd, "FID_COND_SCR_DIV_CODE": "20214", "FID_MRKT_CLS_CODE": fid_mrkt_cls_code}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k in ["dryy_bstp_nmix_lwpr_date", "dryy_bstp_nmix_hgpr_date"]:
                output1[k] = dtm.datetime.strptime(output1[k], "%Y%m%d").date()
            elif k in ["bstp_nmix_prpr", "bstp_nmix_prdy_vrss", "bstp_nmix_prdy_ctrt", "bstp_nmix_oprc", "bstp_nmix_hgpr", "bstp_nmix_lwpr", "dryy_bstp_nmix_hgpr", "dryy_bstp_nmix_lwpr"]:
                output1[k] = Decimal(output1[k])
            else:
                output1[k] = int(output1[k])

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if k in ["bstp_cls_code", "hts_kor_isnm"]:
                    pass
                elif k in ["prdy_vrss_sign", "acml_vol", "acml_tr_pbmn"]:
                    if len(el[k]) > 0:
                        el[k] = int(el[k])
                else:
                    if len(el[k]) > 0:
                        el[k] = Decimal(el[k])

            output2.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output1": output1, "output2": output2}

        return result

    def search_stock_info(self, prdt_type_cd: str, pdno: str):
        """
        (국내주식시세) 주식기본조회[v1_국내주식-067]

        주식기본조회 API입니다.
        국내주식 종목의 종목상세정보를 확인할 수 있습니다.

        Args:
            prdt_type_cd (str): 상품유형코드 - 300:주식 301:선물옵션 302:채권 306:ELS
            pdno (str): 상품번호

        Returns:
            dict:

            - tr_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 응답상세

                - pdno: 상품번호
                - prdt_type_cd: 상품유형코드
                - mket_id_cd: 시장ID코드
                - scty_grp_id_cd: 증권그룹ID코드
                - excg_dvsn_cd: 거래소구분코드
                - setl_mmdd: 결산월일
                - lstg_stqt: 상장주수
                - lstg_cptl_amt: 상장자본금액
                - cpta: 자본금
                - papr: 액면가
                - issu_pric: 발행가격
                - kospi200_item_yn: 코스피200종목여부
                - scts_mket_lstg_dt: 유가증권시장상장일자
                - scts_mket_lstg_abol_dt: 유가증권시장상장폐지일자
                - kosdaq_mket_lstg_dt: 코스닥시장상장일자
                - kosdaq_mket_lstg_abol_dt: 코스닥시장상장폐지일자
                - frbd_mket_lstg_dt: 프리보드시장상장일자
                - frbd_mket_lstg_abol_dt: 프리보드시장상장폐지일자
                - reits_kind_cd: 리츠종류코드
                - etf_dvsn_cd: ETF구분코드
                - oilf_fund_yn: 유전펀드여부
                - idx_bztp_lcls_cd: 지수업종대분류코드
                - idx_bztp_mcls_cd: 지수업종중분류코드
                - idx_bztp_scls_cd: 지수업종소분류코드
                - stck_kind_cd: 주식종류코드
                - mfnd_opng_dt: 뮤추얼펀드개시일자
                - mfnd_end_dt: 뮤추얼펀드종료일자
                - dpsi_erlm_cncl_dt: 예탁등록취소일자
                - etf_cu_qty: ETFCU수량
                - prdt_name: 상품명
                - prdt_name120: 상품명120
                - prdt_abrv_name: 상품약어명
                - std_pdno: 표준상품번호
                - prdt_eng_name: 상품영문명
                - prdt_eng_name120: 상품영문명120
                - prdt_eng_abrv_name: 상품영문약어명
                - dpsi_aptm_erlm_yn: 예탁지정등록여부
                - etf_txtn_type_cd: ETF과세유형코드
                - etf_type_cd: ETF유형코드
                - lstg_abol_dt: 상장폐지일자
                - nwst_odst_dvsn_cd: 신주구주구분코드
                - sbst_pric: 대용가격
                - thco_sbst_pric: 당사대용가격
                - thco_sbst_pric_chng_dt: 당사대용가격변경일자
                - tr_stop_yn: 거래정지여부
                - admn_item_yn: 관리종목여부
                - thdt_clpr: 당일종가
                - bfdy_clpr: 전일종가
                - clpr_chng_dt: 종가변경일자
                - std_idst_clsf_cd: 표준산업분류코드
                - std_idst_clsf_cd_name: 표준산업분류코드명
                - idx_bztp_lcls_cd_name: 지수업종대분류코드명
                - idx_bztp_mcls_cd_name: 지수업종중분류코드명
                - idx_bztp_scls_cd_name: 지수업종소분류코드명
                - ocr_no: OCR번호
                - crfd_item_yn: 크라우드펀딩종목여부
                - elec_scty_yn: 전자증권여부
                - issu_istt_cd: 발행기관코드
                - etf_chas_erng_rt_dbnb: ETF추적수익율배수
                - etf_etn_ivst_heed_item_yn: ETF/ETN투자유의종목여부
                - stln_int_rt_dvsn_cd: 대주이자율구분코드
                - frnr_psnl_lmt_rt: 외국인개인한도비율
                - lstg_rqsr_issu_istt_cd: 상장신청인발행기관코드
                - lstg_rqsr_item_cd: 상장신청인종목코드
                - trst_istt_issu_istt_cd: 신탁기관발행기관코드
                - cptt_trad_tr_psbl_yn: NXT 거래종목여부
                - nxt_tr_stop_yn: NXT 거래정지여부

        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert prdt_type_cd in ["300", "301", "302", "306"], 'prdt_type_cd must be "300", "301", "302" or "306"'

        url_path = "/uapi/domestic-stock/v1/quotations/search-stock-info"
        tr_id = "CTPF1002R"
        params = {"PRDT_TYPE_CD": prdt_type_cd, "PDNO": pdno}

        res_body, res_headers = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body["output"]
        for k in output.keys():
            if k in ["lstg_stqt", "lstg_cptl_amt", "cpta", "papr", "issu_pric", "etf_cu_qty", "sbst_pric", "thco_sbst_pric", "thdt_clpr", "bfdy_clpr"]:
                if len(output[k]) > 0:
                    output[k] = int(output[k])

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "output": output}

        return result

    def get_balance_sheet(self, fid_div_cls_code: str, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J"):
        """
        (국내주식) 대차대조표[v1_국내주식-078]

        국내주식 대차대조표 API입니다.
        한국투자 HTS(eFriend Plus) > [0635] 재무분석종합 화면의 하단 '1. 대차대조표' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            fid_div_cls_code (str): 분류 구분 코드 - 0: 년, 1: 분기
            fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 - J
            fid_input_iscd (str): 입력 종목코드 - 예: 000660 (종목코드)

        Returns:
            dict:

            - rt_cd (str): 성공 실패 여부
            - msg_cd (str): 응답코드
            - msg1 (str): 응답메세지
            - output (list of dict): 응답상세
                - stac_yymm (str): 결산 년월
                - cras (str): 유동자산
                - fxas (str): 고정자산
                - total_aset (str): 자산총계
                - flow_lblt (str): 유동부채
                - fix_lblt (str): 고정부채
                - total_lblt (str): 부채총계
                - cpfn (str): 자본금
                - cfp_surp (str): 자본 잉여금 - 출력되지 않는 데이터(99.99로 표시)
                - prfi_surp (str): 이익 잉여금 - 출력되지 않는 데이터(99.99로 표시)
                - total_cptl (str): 자본총계

        Raise:
            ValueError: API 에러 발생시
        """

        assert fid_div_cls_code in ["0", "1"]
        assert len(fid_input_iscd) >= 6

        path = "/uapi/domestic-stock/v1/finance/balance-sheet"
        tr_id = "FHKST66430100"
        params = {
            "fid_div_cls_code": fid_div_cls_code,
            "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
            "fid_input_iscd": fid_input_iscd,
        }

        res_body, _ = self._tr_request(path, tr_id, params=params)
        output = res_body["output"]

        for item in output:
            for key in item:
                if key != "stac_yymm":
                    item[key] = Decimal(item[key])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output": output,
        }

        return result

    def get_financial_ratio(self, fid_div_cls_code: str, fid_input_iscd: str, fid_cond_mrkt_div_code: str = "J"):
        """
        (국내주식) 재무비율[v1_국내주식-080]

        국내주식 재무비율 API입니다.
        한국투자 HTS(eFriend Plus) > [0635] 재무분석종합 화면의 우측의 '재무 비율' 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            fid_div_cls_code (str): 분류 구분 코드 - 0: 년, 1: 분기
            fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 - J
            fid_input_iscd (str): 입력 종목코드 - 예: 000660 (종목코드)

        Returns:
            dict:
            - rt_cd (str): 성공 실패 여부
            - msg_cd (str): 응답코드
            - msg1 (str): 응답메세지
            - output (list of dict): 응답상세
                - stac_yymm (str): 결산 년월
                - grs (str): 매출액 증가율
                - bsop_prfi_inrt (str): 영업 이익 증가율 (적자지속, 흑자전환, 적자전환인 경우 0으로 표시)
                - ntin_inrt (str): 순이익 증가율
                - roe_val (str): ROE 값
                - eps (str): EPS
                - sps (str): 주당매출액
                - bps (str): BPS
                - rsrv_rate (str): 유보 비율
                - lblt_rate (str): 부채 비율

        Raise:
            ValueError: API 에러 발생시
        """
        assert fid_div_cls_code in ["0", "1"]
        assert len(fid_input_iscd) >= 6

        path = "/uapi/domestic-stock/v1/finance/financial-ratio"
        tr_id = "FHKST66430300"
        params = {
            "fid_div_cls_code": fid_div_cls_code,
            "fid_cond_mrkt_div_code": fid_cond_mrkt_div_code,
            "fid_input_iscd": fid_input_iscd,
        }

        res_body, _ = self._tr_request(path, tr_id, params=params)
        output = res_body["output"]

        for item in output:
            for key in item:
                if key != "stac_yymm":
                    item[key] = Decimal(item[key])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output": output,
        }

        return result

    def get_income_statement(self, fid_div_cls_code: str, fid_input_iscd: str):
        """
        (국내주식시세) 국내주식 손익계산서[v1_국내주식-079]

        Args:
            fid_div_cls_code (str): 분류 구분 코드 (0:년 1:분기)
            fid_input_iscd (str): 종목코드

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지
            - output (list): 응답상세
                - stac_yymm: 결산 년월
                - sale_account: 매출액
                - sale_cost: 매출 원가
                - sale_totl_prfi: 매출 총
                - depr_cost: 감가상각비 - 출력되지 않는 데이터(99.99 로 표시)
                - sell_mang: 판매 및 관리비 - 출력되지 않는 데이터(99.99 로 표시)
                - bsop_prti: 영업 이익
                - bsop_non_ernn: 영업 외 수익 - 출력되지 않는 데이터(99.99 로 표시)
                - bsop_non_expn: 영업 외 비용 - 출력되지 않는 데이터(99.99 로 표시)
                - op_prfi: 경상 이익
                - spec_prfi: 특별 이익
                - spec_loss: 특별 손실
                - thtr_ntin: 당기순이익
        """

        assert fid_div_cls_code in ["0", "1"]
        assert len(fid_input_iscd) >= 6

        path = "/uapi/domestic-stock/v1/finance/income-statement"
        tr_id = "FHKST66430200"
        params = {
            "fid_div_cls_code": fid_div_cls_code,
            "fid_cond_mrkt_div_code": "J",
            "fid_input_iscd": fid_input_iscd,
        }

        res_body, _ = self._tr_request(path, tr_id, params=params)
        output = res_body["output"]

        for item in output:
            for key in item:
                if key != "stac_yymm":
                    item[key] = Decimal(item[key])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output": output,
        }

        return result

    def get_dividend_schedule(self, gb1: str, f_dt: str, t_dt: str, sht_cd: str = "", high_gb: str = "0", cts: str = "") -> dict:
        """
        (예탁원정보) 배당일정[v1_국내주식-145]

        예탁원정보(배당일정) API입니다.
        한국투자 HTS(eFriend Plus) > [0658] 배당 화면의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            gb1 (str): 조회구분 - 0: 배당전체, 1: 결산배당, 2: 중간배당
            f_dt (str): 조회일자From - 일자 ~
            t_dt (str): 조회일자To - ~ 일자
            sht_cd (str): 종목코드 - 공백: 전체, 특정종목 조회시 : 종목코드
            high_gb (str): 고배당여부 - 공백
            cts (str): CTS - 공백


        Returns:
            dict:

            - rt_cd (str): 성공 실패 여부
            - msg_cd (str): 응답코드
            - msg1 (str): 응답메세지
            - output1 (list of dict): 응답상세
                - record_date (str): 기준일
                - sht_cd (str): 종목코드
                - isin_name (str): 종목명
                - divi_kind (str): 배당종류
                - face_val (int): 액면가
                - per_sto_divi_amt (int): 현금배당금
                - divi_rate (Decimal): 현금배당률(%)
                - stk_divi_rate (Decimal): 주식배당률(%)
                - divi_pay_dt (str): 배당금지급일
                - stk_div_pay_dt (str): 주식배당지급일
                - odd_pay_dt (str): 단주대금지급일
                - stk_kind (str): 주식종류
                - high_divi_gb (str): 고배당종목여부

        Raise:
            ValueError: API 에러 발생시
        """
        assert gb1 in ["0", "1", "2"]
        assert f_dt.isdigit() and len(f_dt) == 8
        assert t_dt.isdigit() and len(t_dt) == 8
        assert len(sht_cd) in [0, 6]

        path = "/uapi/domestic-stock/v1/ksdinfo/dividend"
        tr_id = "HHKDB669102C0"
        params = {
            "cts": cts,
            "gb1": gb1,
            "f_dt": f_dt,
            "t_dt": t_dt,
            "sht_cd": sht_cd,
            "high_gb": high_gb,
        }

        res_body, _ = self._tr_request(path, tr_id, params=params)
        output = res_body["output1"]

        for item in output:
            for key in item:
                if key in ["divi_rate", "stk_divi_rate"]:
                    try:
                        if item[key].strip() != "":
                            item[key] = Decimal(item[key])
                    except Exception:
                        pass

                elif key in ["face_val", "per_sto_divi_amt"]:
                    try:
                        item[key] = int(item[key])
                    except Exception:
                        pass

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output": output,
        }

        return result

    def inquire_vi_status(
        self,
        fid_div_cls_code: str,
        fid_cond_scr_div_code: str,
        fid_mrkt_cls_code: str,
        fid_rank_sort_cls_code: str,
        fid_input_date_1: str,
        fid_input_iscd: str = "",
        fid_trgt_cls_code: str = "",
        fid_trgt_exls_cls_code: str = "",
    ):
        """
        (국내주식시세) 변동성완화장치(VI) 현황 [v1_국내주식-055]

        HTS(eFriend Plus) [0139] 변동성 완화장치(VI) 현황 데이터를 확인할 수 있는 API입니다.
        최근 30건까지 확인 가능합니다.

        Args:
            fid_div_cls_code (str): FID 분류 구분 코드 - 0:전체 1:상승 2:하락
            fid_cond_scr_div_code (str): FID 조건 화면 분류 코드 - 20139
            fid_mrkt_cls_code (str): FID 시장 구분 코드 - 0:전체 K:거래소 Q:코스닥
            fid_rank_sort_cls_code (str): FID 순위 정렬 구분 코드 - 0:전체 1:정적 2:동적 3:정적&동적
            fid_input_date_1 (str): FID 입력 날짜1 - 영업일
            fid_input_iscd (str): FID 입력 종목코드
            fid_trgt_cls_code (str): FID 대상 구분 코드
            fid_trgt_exls_cls_code (str): FID 대상 제외 구분 코드

        Returns:
            dict:

            - rt_cd (str): 성공 실패 여부
            - msg_cd (str): 응답코드
            - msg1 (str): 응답메세지
            - output (list): 응답상세
                - hts_kor_isnm (str): HTS 한글 종목명
                - mksc_shrn_iscd (str): 유가증권 단축 종목코드
                - vi_cls_code (str): VI발동상태 - Y: 발동 / N: 해제
                - bsop_date (datetime.date): 영업 일자
                - cntg_vi_hour (datetime.time): VI발동시간
                - vi_cncl_hour (datetime.time): VI해제시간
                - vi_kind_code (str): VI종류코드 - 1:정적 2:동적 3:정적&동적
                - vi_prc (int): VI발동가격
                - vi_stnd_prc (int): 정적VI발동기준가격
                - vi_dprt (Decimal): 정적VI발동괴리율(%)
                - vi_dmc_stnd_prc (int): 동적VI발동기준가격
                - vi_dmc_dprt (Decimal): 동적VI발동괴리율(%)
                - vi_count (int): VI발동횟수

        Raises:
            ValueError: API 에러 발생시
        """
        assert fid_div_cls_code in ["0", "1", "2"], 'fid_div_cls_code must be "0", "1" or "2"'
        assert fid_mrkt_cls_code in ["0", "K", "Q"], 'fid_mrkt_cls_code must be "0", "K" or "Q"'
        assert fid_rank_sort_cls_code in ["0", "1", "2", "3"], 'fid_rank_sort_cls_code must be "0", "1", "2" or "3"'

        url_path = "/uapi/domestic-stock/v1/quotations/inquire-vi-status"
        tr_id = "FHPST01390000"
        params = {
            "FID_DIV_CLS_CODE": fid_div_cls_code,
            "FID_COND_SCR_DIV_CODE": fid_cond_scr_div_code,
            "FID_MRKT_CLS_CODE": fid_mrkt_cls_code,
            "FID_RANK_SORT_CLS_CODE": fid_rank_sort_cls_code,
            "FID_INPUT_DATE_1": fid_input_date_1,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_TRGT_CLS_CODE": fid_trgt_cls_code,
            "FID_TRGT_EXLS_CLS_CODE": fid_trgt_exls_cls_code,
        }

        res_body, _ = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            # 날짜 형식 변환
            if "bsop_date" in el and len(el["bsop_date"]) == 8:
                el["bsop_date"] = dtm.datetime.strptime(el["bsop_date"], "%Y%m%d").date()

            # 시간 형식 변환
            for time_field in ["cntg_vi_hour", "vi_cncl_hour"]:
                if time_field in el and len(el[time_field]) == 6:
                    el[time_field] = dtm.datetime.strptime(el[time_field], "%H%M%S").time()

            # Decimal 변환
            for decimal_field in ["vi_dprt", "vi_dmc_dprt"]:
                if decimal_field in el and len(el[decimal_field]) > 0:
                    el[decimal_field] = Decimal(el[decimal_field])

            # 정수 변환
            for int_field in ["vi_prc", "vi_stnd_prc", "vi_dmc_stnd_prc", "vi_count"]:
                if int_field in el and len(el[int_field]) > 0:
                    el[int_field] = int(el[int_field])

            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "output": output,
        }

        return result

    def order_cash(
        self,
        cano: str,
        acnt_prdt_cd: str,
        side: str,
        pdno: str,
        ord_dvsn: str,
        ord_qty: int,
        ord_unpr: int = None,
        cndt_pric: int = None,
        excg_id_dvsn_cd: str = "KRX",
    ):
        """
        (국내주식주문) 주식주문(현금)[v1_국내주식-001]

        국내주식주문(현금) API 입니다.

        | ※ TTC0802U(현금매수) 사용하셔서 미수매수 가능합니다. 단, 거래하시는 계좌가 증거금40%계좌로 신청이 되어있어야 가능합니다.
        | ※ 신용매수는 별도의 API가 준비되어 있습니다.

        | ※ ORD_UNPR(주문단가)가 없는 주문은 상한가로 주문금액을 선정하고 이후 체결이되면 체결금액로 정산됩니다.

        | ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
        | https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

        Args:
            cano (str): 계좌번호
            acnt_prdt_cd (str): 계좌상품코드
            side (str): 매매구분 - 매수:buy 매도:sell
            pdno (str): 상품번호
            ord_dvsn (str): 주문구분. 각 거래소별 가능한 주문:

                [KRX]
                    - 00:지정가
                    - 01:시장가
                    - 02:조건부지정가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 05:장전 시간외 (08:20~08:40)
                    - 06:장후 시간외 (15:30~16:00)
                    - 07:시간외 단일가 (16:00~18:00)
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)
                    - 21:중간가
                    - 22:스톱지정가
                    - 23:중간가IOC
                    - 24:중간가FOK

                [NXT]
                    - 00:지정가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)
                    - 21:중간가
                    - 22:스톱지정가
                    - 23:중간가IOC
                    - 24:중간가FOK

                [SOR]
                    - 00:지정가
                    - 01:시장가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)

            ord_qty (int): 주문수량
            ord_unpr (int): 주문단가
            cndt_pric (int): 조건가격 - 스톱지정가 주문 사용 시 필수
            excg_id_dvsn_cd (str): 거래소ID구분코드 - KRX:한국거래소 NXT:넥스트레이드 SOR:자동주문전송


        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 응답상세

                - KRX_FWDG_ORD_ORGNO: 한국거래소전송주문조직번호 - 주문시 한국투자증권 시스템에서 지정된 영업점코드
                - ODNO: 주문번호 - 주문시 한국투자증권 시스템에서 채번된 주문번호
                - ORD_TMD: 주문시각 - 주문시각

        Raise:
            ValueError: API 에러 발생시
        """
        assert side in ["sell", "buy"]
        assert type(ord_dvsn) is str and len(ord_dvsn) == 2, "ord_dvsn must be a string of length 2"
        assert 0 <= int(ord_dvsn) <= 16 or 21 <= int(ord_dvsn) <= 24, "ord_dvsn must be an integer between 00~16 or 21~24"
        assert type(ord_qty) is int and ord_qty > 0, "ord_qty must be a positive integer"
        assert excg_id_dvsn_cd in ["KRX", "NXT", "SOR"], "excg_id_dvsn_cd must be 'KRX', 'NXT' or 'SOR'"

        if ord_dvsn in ["00", "02", "11", "12", "22"]:  # 지정가, 조건부지정가, IOC/FOK지정가, 스톱지정가
            assert type(ord_unpr) in (int, Decimal) and ord_unpr > 0, "ord_unpr must be a positive integer when limit order"

        if ord_dvsn in ["21", "23", "24"]:  # 중간가, 중간가IOC, 중간가FOK
            assert type(ord_unpr) in (int, Decimal) and ord_unpr == 0, "ord_unpr must be 0 when mid point order"

        if ord_dvsn in ["22"]:  # 스톱지정가
            assert type(cndt_pric) in (int, Decimal) and cndt_pric > 0, "cndt_pric must be a positive integer when stop limit order"

        url_path = "/uapi/domestic-stock/v1/trading/order-cash"

        if side == "sell":
            tr_id = "VTTC0011U" if self.auth.paper_trading else "TTTC0011U"
        else:
            tr_id = "VTTC0012U" if self.auth.paper_trading else "TTTC0012U"

        req_body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": pdno,
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(ord_qty),
            "ORD_UNPR": "0" if ord_unpr is None else str(ord_unpr),
            "EXCG_ID_DVSN_CD": excg_id_dvsn_cd,
            "CNDT_PRIC": "0" if cndt_pric is None else str(cndt_pric),
        }

        res_body, _ = self._tr_request(url_path, tr_id, body=req_body, method="POST")

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        res_body["ORD_TMD"] = dtm.datetime.strptime(res_body["output"]["ORD_TMD"], "%H%M%S").time()

        return res_body

    def order_credit(
        self,
        cano: str,
        acnt_prdt_cd: str,
        side: str,
        pdno: str,
        crdt_type: str,
        load_dt: dtm.date,
        ord_dvsn: str,
        ord_qty: int,
        rvsn_ord_yn: str,
        ord_unpr: int = None,
        cndt_pric: int = None,
        excg_id_dvsn_cd: str = "KRX",
    ):
        """
        (국내주식주문) 주식주문(신용)[v1_국내주식-002]

        국내주식주문(신용) API입니다.

        ※ 모의투자는 사용 불가합니다.

        Args:
            cano (str): 계좌번호
            acnt_prdt_cd (str): 계좌상품코드
            side (str): 매매구분 - 신용매수:buy 신용매도:sell
            pdno (str): 상품번호
            crdt_type (str): 신용유형

              | - 신용매수
              |     - 21:자기융자신규
              |     - 23:유통융자신규
              |     - 26:유통대주상환
              |     - 28:자기대주상환
              | - 신용매도
              |     - 22:유통대주신규
              |     - 24:자기대주신규
              |     - 25:자기융자상환
              |     - 27:유통융자상환

            load_dt (dtm.date): 대출일자

              | 신용매수: 신규 대출로, 오늘날짜 입력
              | 신용매도: 매도할 종목의 대출일자 입력
              | * 주식잔고조회 API(TTC8434R)의 INQR_DVSN(조회구분)을 01(대출일별)로 조회하여서 조회된 주문의 LOAN_DT(대출일자) 입력

            ord_dvsn (str): 주문구분. 각 거래소별 가능한 주문:

                [KRX]
                    - 00:지정가
                    - 01:시장가
                    - 02:조건부지정가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 05:장전 시간외 (08:20~08:40)
                    - 06:장후 시간외 (15:30~16:00)
                    - 07:시간외 단일가(16:00~18:00)
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)
                    - 21:중간가
                    - 22:스톱지정가
                    - 23:중간가IOC
                    - 24:중간가FOK

                [NXT]
                    - 00:지정가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)
                    - 21:중간가
                    - 22:스톱지정가
                    - 23:중간가IOC
                    - 24:중간가FOK

                [SOR]
                    - 00:지정가
                    - 01:시장가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)

            ord_qty (int): 주문수량
            rsvn_ord_yn (str): 예약주문여부

              | - 정규 증권시장이 열리지 않는 시간 (15:10분 ~ 익일 7:30분) 에 주문을 미리 설정 하여 다음 영업일 또는 설정한 기간 동안 아침 동시 호가에 주문하는 것.
              | - 예약주문:Y, 즉시주문:N

            ord_unpr (int): 주문단가
            cndt_pric (int): 조건가격 - 스톱지정가 주문 사용 시 필수
            excg_id_dvsn_cd (str): 거래소ID구분코드 - KRX:한국거래소 NXT:넥스트레이드 SOR:자동주문전송

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 응답상세
                - KRX_FWDG_ORD_ORGNO: 한국거래소전송주문조직번호 - 주문시 한국투자증권 시스템에서 지정된 영업점코드
                - ODNO: 주문번호 - 주문시 한국투자증권 시스템에서 채번된 주문번호
                - ORD_TMD: 주문시각 - 주문시각

        Raise:
            ValueError: API 에러 발생시
        """
        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."
        assert side in ["sell", "buy"]
        assert excg_id_dvsn_cd in ["KRX", "NXT", "SOR"], "excg_id_dvsn_cd must be 'KRX', 'NXT' or 'SOR'"

        if side == "sell":
            assert crdt_type in ["25", "27", "22", "24"], 'crdt_type must be "25", "27", "22" or "24" when sell'
        else:
            assert crdt_type in ["21", "23", "26", "28"], 'crdt_type must be "21", "23", "26" or "28" when buy'

        assert type(ord_dvsn) is str and len(ord_dvsn) == 2 and int(ord_dvsn) >= 0 and int(ord_dvsn) <= 16, "ord_dvsn must be a string of integer between 00 and 16"
        assert type(ord_qty) is int and ord_qty > 0, "ord_qty must be a positive integer"

        if ord_dvsn in ["00", "02", "11", "12"]:  # 지정가, 조건부지정가, IOC/FOK지정가
            assert type(ord_unpr) is int and ord_unpr > 0, "ord_unpr must be a positive integer when limit order"

        if ord_dvsn in ["22"]:  # 스톱지정가
            assert type(cndt_pric) in (int, Decimal) and cndt_pric > 0, "cndt_pric must be a positive integer when stop limit order"

        assert rvsn_ord_yn in ["Y", "N"], 'rvsn_ord_yn must be "Y" or "N"'

        url_path = "/uapi/domestic-stock/v1/trading/order-credit"

        if side == "sell":
            tr_id = "TTTC0051U"
        else:
            tr_id = "TTTC0052U"

        req_body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": pdno,
            "CRDT_TYPE": crdt_type,
            "LOAD_DT": load_dt.strftime("%Y%m%d"),
            "ORD_DVSN": ord_dvsn,
            "ORD_QTY": str(ord_qty),
            "ORD_UNPR": "0" if ord_unpr is None else str(ord_unpr),
            "CNDT_PRIC": "0" if cndt_pric is None else str(cndt_pric),
            "EXCG_ID_DVSN_CD": excg_id_dvsn_cd,
        }

        res_body, _ = self._tr_request(url_path, tr_id, json=req_body, method="POST")

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        res_body["output"]["ORD_TMD"] = dtm.datetime.strptime(res_body["ORD_TMD"], "%H%M%S").time()

        return res_body

    def order_reserve(
        self,
        cano: str,
        acnt_prdt_cd: str,
        side: str,
        pdno: str,
        ord_dvsn_cd: str,
        ord_qty: int,
        ord_unpr: int,
        loan_dt: dtm.date = None,
        rvsn_ord_end_dt: dtm.date = None,
        ldng_dt: dtm.date = None,
    ):
        """
        (국내주식주문) 주식예약주문[v1_국내주식-017]

        국내주식 예약주문 매수/매도 API 입니다.

        [유의사항]
         1. 예약주문 가능시간 : 15시 40분 ~ 다음 영업일 7시 30분
          (단, 서버 초기화 작업 시 예약주문 불가 : 23시 40분 ~ 00시 10분)
          - 예약주문 처리내역은 통보되지 않으므로 주문처리일 장 시작전에 반드시 주문처리 결과를 확인하시기 바랍니다.

        2. 예약주문 안내
        - 예약종료일 미입력 시 일반예약주문으로 최초 도래하는 영업일에 주문 전송됩니다.
        - 예약종료일 입력 시 기간예약주문으로 최초 예약주문수량 중 미체결 된 수량에 대해 예약종료일까지 매 영업일 주문이 실행됩니다. (예약종료일은 익영업일부터 달력일 기준으로 공휴일 포함하여 최대 30일이 되는 일자까지 입력가능)
        - 예약주문 접수 처리순서는 일반/기간예약주문 중 신청일자가 빠른 주문이 우선합니다.
        - 단, 기간예약주문 자동배치시간(약 15시35분 ~ 15시55분)사이 접수되는 주문의 경우 당일에 한해 순서와 상관없이 처리될 수 있습니다.
        - 기간예약주문 자동배치시간(약 15시35분 ~ 15시55분)에는 예약주문 조회가 제한 될 수 있습니다.
        - 기간예약주문은 계좌 당 주문건수 최대 1,000건으로 제한됩니다.

        3. 예약주문 접수내역 중 아래의 사유 등으로 인해 주문이 거부될 수 있사오니, 주문처리일 장 시작전에 반드시 주문처리 결과를 확인하시기 바랍니다.
        - 주문처리일 기준 : 매수가능금액 부족, 매도가능수량 부족, 주문수량/호가단위 오류, 대주 호가제한, 신용/대주가능종목 변경, 상/하한폭 변경, 시가형성 종목(신규상장 등)의 시장가, 거래서비스 미신청 등

        4. 익일 예상 상/하한가는 조회시점의 현재가로 계산되며 익일의 유/무상증자, 배당, 감자, 합병, 액면변경 등에 의해 변동될 수 있으며 이로 인해 상/하한가를 벗어나 주문이 거부되는 경우가 발생할 수 있사오니, 주문처리일 장 시작전에 반드시 주문처리결과를 확인하시기 바랍니다.

        5. 정리매매종목, ELW, 신주인수권증권, 신주인수권증서 등은 가격제한폭(상/하한가) 적용 제외됩니다.

        6. 영업일 장 시작 후 [기간예약주문] 내역 취소는 해당시점 이후의 예약주문이 취소되는 것으로, 일반주문으로 이미 전환된 주문에는 영향을 미치지 않습니다. 반드시 장 시작전 주문처리결과를 확인하시기 바랍니다.

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            side (str): 주문 방향 - "sell" 또는 "buy"
            pdno (str): 종목코드
            ord_dvsn_cd (str): 주문 구분 코드 - 00:지정가, 01:시장가, 02:조건부지정가, 05:장전 시간외
            ord_qty (int): 주문 수량
            ord_unpr (int): 주문 단가
            loan_dt (dtm.date): 대출일자
            rsvn_ord_end_dt(dtm.date): 예약주문 종료일자
            ldng_dt (dtm.date): 대여일자
        """

        assert side in ["sell", "buy"]
        assert ord_dvsn_cd in ["00", "01", "02", "05"]

        if rvsn_ord_end_dt:
            assert rvsn_ord_end_dt > dtm.date.today(), "rvsn_ord_end_dt must be greater than today"

        url_path = "/uapi/domestic-stock/v1/trading/order-resv"

        tr_id = "CTSC0008U"

        req_body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": pdno,
            "ORD_QTY": str(ord_qty),
            "ORD_UNPR": str(ord_unpr),
            "SLL_BUY_DVSN_CD": "01" if side == "sell" else "02",
            "ORD_DVSN_CD": ord_dvsn_cd,
            "ORD_OBJT_CBLC_DVSN_CD": "10",  # 현금
            "LOAN_DT": "" if loan_dt is None else loan_dt.strftime("%Y%m%d"),
            "RSVN_ORD_END_DT": "" if rvsn_ord_end_dt is None else rvsn_ord_end_dt.strftime("%Y%m%d"),
            "LDNG_DT": "" if ldng_dt is None else ldng_dt.strftime("%Y%m%d"),  # 대여일자
        }

        res_body, _ = self._tr_request(url_path, tr_id, body=req_body, method="POST")

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        return res_body

    def order_rvsecncl(
        self,
        cano: str,
        acnt_prdt_cd: str,
        orgn_odno: str,
        ord_dvsn: str,
        rvse_cncl_dvsn_cd: str,
        ord_qty: int,
        ord_unpr: int,
        qty_all_ord_yn: str,
        cndt_pric: int = None,
        excg_id_dvsn_cd: str = "KRX",
    ):
        """
        (국내주식주문) 주식주문(정정취소)[v1_국내주식-003]

        주문 건에 대하여 정정 및 취소하는 API입니다. 단, 이미 체결된 건은 정정 및 취소가 불가합니다.

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            orgn_odno (str): 원주문번호 - 주식일별주문체결조회 API output1의 odno(주문번호) 값 입력. 주문시 한국투자증권 시스템에서 채번된 주문번호
            ord_dvsn (str): 주문구분. 각 거래소별 가능한 주문:

                [KRX]
                    - 00:지정가
                    - 01:시장가
                    - 02:조건부지정가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 05:장전 시간외
                    - 06:장후 시간외
                    - 07:시간외 단일가
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)
                    - 21:중간가
                    - 22:스톱지정가
                    - 23:중간가IOC
                    - 24:중간가FOK

                [NXT]
                    - 00:지정가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)
                    - 21:중간가
                    - 22:스톱지정가
                    - 23:중간가IOC
                    - 24:중간가FOK

                [SOR]
                    - 00:지정가
                    - 01:시장가
                    - 03:최유리지정가
                    - 04:최우선지정가
                    - 11:IOC지정가 (즉시체결,잔량취소)
                    - 12:FOK지정가 (즉시체결,전량취소)
                    - 13:IOC시장가 (즉시체결,잔량취소)
                    - 14:FOK시장가 (즉시체결,전량취소)
                    - 15:IOC최유리 (즉시체결,잔량취소)
                    - 16:FOK최유리 (즉시체결,전량취소)

            rvse_cncl_dvsn_cd (str): 정정취소구분코드 - 정정:01 취소:02
            ord_qty (int): 주문수량 - 전부 취소/정정시 0 입력, 일부 취소/정정시 취소/정정 수량 입력
            ord_unpr (int): 주문단가 - 정정주문 1주당 가격, 취소시 0 설정
            qty_all_ord_yn (str): 잔량전부주문여부 - Y:잔량전부 N:잔량일부
            cndt_pric (int): 조건가격 - 스톱지정가호가에서 사용
            excg_id_dvsn_cd (str): 거래소ID구분코드 - KRX:한국거래소 NXT:넥스트레이드 SOR:자동주문전송

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - output (dict): 응답상세
                - KRX_FWDG_ORD_ORGNO: 한국거래소전송주문조직번호 - 주문시 한국투자증권 시스템에서 지정된 영업점코드
                - ODNO: 주문번호 - 주문시 한국투자증권 시스템에서 채번된 주문번호
                - ORD_TMD: 주문시각 - 주문시각
        """
        url_path = "/uapi/domestic-stock/v1/trading/order-rvsecncl"
        tr_id = "VTTC0013U" if self.auth.paper_trading else "TTTC0013U"
        req_body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO": orgn_odno,
            "ORD_DVSN": ord_dvsn,
            "RVSE_CNCL_DVSN_CD": rvse_cncl_dvsn_cd,
            "ORD_QTY": str(ord_qty),
            "ORD_UNPR": str(ord_unpr),
            "QTY_ALL_ORD_YN": qty_all_ord_yn,
            "CNDT_PRIC": "0" if cndt_pric is None else str(cndt_pric),
            "EXCG_ID_DVSN_CD": excg_id_dvsn_cd,
        }

        res_body, _ = self._tr_request(url_path, tr_id, body=req_body, method="POST")

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        res_body["output"]["ORD_TMD"] = dtm.datetime.strptime(res_body["output"]["ORD_TMD"], "%H%M%S").time()

        return res_body

    def inquire_psbl_rvsecncl(
        self,
        cano: str,
        acnt_prdt_cd: str,
        inqr_dvsn_1: str = "0",
        inqr_dvsn_2: str = "0",
        ctx_area_fk100: str = "",
        ctx_area_nk100: str = "",
    ):
        """
        (국내주식주문) 주식정정취소가능주문조회[v1_국내주식-004]

        주식정정취소가능주문조회 API입니다. 한 번의 호출에 최대 50건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            inqr_dvsn_1 (str): 조회구분1 - 0:주문 1:종목
            inqr_dvsn_2 (str): 조회구분2 - 0:전체 1:매도 2:매수
            ctx_area_fk100 (str): CTX_AREA_FK100
            ctx_area_nk100 (str): CTX_AREA_NK100

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속 조회 가능 여부
            - ctx_area_fk100 (str): 연속조회검색조건100
            - ctx_area_nk100 (str): 연속조회검색키100
            - output (list): 응답상세

                - ord_gno_brno: 주문채번지점번호 - 주문시 한국투자증권 시스템에서 지정된 영업점코드
                - odno: 주문번호 - 주문시 한국투자증권 시스템에서 채번된 주문번호
                - orgn_odno: 원주문번호 - 정정/취소주문 인경우 원주문번호
                - ord_dvsn_name: 주문구분명
                - pdno: 상품번호 - 종목번호(뒤 6자리만 해당)
                - prdt_name: 상품명 - 종목명
                - rvse_cncl_dvsn_name: 정정취소구분명 - 정정 또는 취소 여부 표시
                - ord_qty: 주문수량 - 주문수량
                - ord_unpr: 주문단가 - 1주당 주문가격
                - ord_tmd: 주문시각 - 주문시각(시분초HHMMSS)
                - tot_ccld_qty: 총체결수량 - 주문 수량 중 체결된 수량
                - tot_ccld_amt: 총체결금액 - 주문금액 중 체결금액
                - psbl_qty: 가능수량 - 정정/취소 주문 가능 수량
                - sll_buy_dvsn_cd: 매도매수구분코드 - 01:매도 02:매수
                - ord_dvsn_cd: 주문구분코드. 각 거래소별 주문코드:

                    [KRX]
                        - 00:지정가
                        - 01:시장가
                        - 02:조건부지정가
                        - 03:최유리지정가
                        - 04:최우선지정가
                        - 05:장전 시간외
                        - 06:장후 시간외
                        - 07:시간외 단일가
                        - 11:IOC지정가 (즉시체결,잔량취소)
                        - 12:FOK지정가 (즉시체결,전량취소)
                        - 13:IOC시장가 (즉시체결,잔량취소)
                        - 14:FOK시장가 (즉시체결,전량취소)
                        - 15:IOC최유리 (즉시체결,잔량취소)
                        - 16:FOK최유리 (즉시체결,전량취소)
                        - 21:중간가
                        - 22:스톱지정가
                        - 23:중간가IOC
                        - 24:중간가FOK

                    [NXT]
                        - 00:지정가
                        - 03:최유리지정가
                        - 04:최우선지정가
                        - 11:IOC지정가 (즉시체결,잔량취소)
                        - 12:FOK지정가 (즉시체결,전량취소)
                        - 13:IOC시장가 (즉시체결,잔량취소)
                        - 14:FOK시장가 (즉시체결,전량취소)
                        - 15:IOC최유리 (즉시체결,잔량취소)
                        - 16:FOK최유리 (즉시체결,전량취소)
                        - 21:중간가
                        - 22:스톱지정가
                        - 23:중간가IOC
                        - 24:중간가FOK

                    [SOR]
                        - 00:지정가
                        - 01:시장가
                        - 03:최유리지정가
                        - 04:최우선지정가
                        - 11:IOC지정가 (즉시체결,잔량취소)
                        - 12:FOK지정가 (즉시체결,전량취소)
                        - 13:IOC시장가 (즉시체결,잔량취소)
                        - 14:FOK시장가 (즉시체결,전량취소)
                        - 15:IOC최유리 (즉시체결,잔량취소)
                        - 16:FOK최유리 (즉시체결,전량취소)

                - mgco_aptm_odno: 운용사지정주문번호 - 주문 번호 (운용사 통한 주문)
                - excg_dvsn_cd: 거래소구분코드
                - excg_id_dvsn_cd: 거래소ID구분코드 - KRX:한국거래소 NXT:넥스트레이드 SOR:자동주문전송
                - excg_id_dvsn_name: 거래소ID구분명
                - stpm_cndt_pric: 스톱지정가 - 스톱지정가 조건가격
                - stpm_efct_occr_yn: 스톱지정가 효력발생여부 - Y: 효력발생 N: 효력미발생

        Raise:
            ValueError: API 에러 발생시
        """

        assert not self.auth.paper_trading, "실전계좌에서만 사용 가능한 API입니다."

        url_path = "/uapi/domestic-stock/v1/trading/inquire-psbl-rvsecncl"
        tr_id = "TTTC0084R"
        tr_cont = "" if ctx_area_fk100 == "" else "N"

        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "INQR_DVSN_1": inqr_dvsn_1,
            "INQR_DVSN_2": inqr_dvsn_2,
            "CTX_AREA_FK100": ctx_area_fk100,
            "CTX_AREA_NK100": ctx_area_nk100,
        }
        res_body, res_header = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            for k in el.keys():
                if k == "ord_tmd":
                    el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                elif k in ["ord_qty", "ord_unpr", "tot_ccld_qty", "tot_ccld_amt", "psbl_qty"]:
                    el[k] = int(el[k])

            output.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "tr_cont": res_header["tr_cont"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "ctx_area_fk100": res_body["ctx_area_fk100"].strip(),
            "ctx_area_nk100": res_body["ctx_area_nk100"].strip(),
            "output": output,
        }

        return result

    def inquire_daily_ccld(
        self,
        cano: str,
        acnt_prdt_cd: str,
        inqr_strt_dt: dtm.date,
        inqr_end_dt: dtm.date,
        sll_buy_dvsn_cd: str = "00",
        inqr_dvsn: str = "00",
        pdno: str = "",
        odno: str = "",
        ccld_dvsn: str = "00",
        inqr_dvsn_3: str = "00",
        inqr_dvsn_1: str = "",
        ctx_area_fk100: str = "",
        ctx_area_nk100: str = "",
        tr_cont: str = "",
        excg_id_dvsn_cd: str = "KRX",
    ):
        """
        (국내주식주문) 주식일별주문체결조회[v1_국내주식-005]

        | 주식일별주문체결조회 API입니다.
        | 실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
        | 모의계좌의 경우, 한 번의 호출에 최대 15건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        | * 다만, 3개월 이전 체결내역 조회(CTSC9115R) 의 경우,
        | 장중에는 많은 거래량으로 인해 순간적으로 DB가 밀렸거나 응답을 늦게 받거나 하는 등의 이슈가 있을 수 있어
        | ① 가급적 장 종료 이후(15:30 이후) 조회하시고
        | ② 조회기간(INQR_STRT_DT와 INQR_END_DT 사이의 간격)을 보다 짧게 해서 조회하는 것을 권유드립니다.

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            inqr_strt_dt (datetime.date): 조회시작일자
            inqr_end_dt (datetime.datestr): 조회종료일자
            sll_buy_dvsn_cd (str): 매도매수구분코드 - 00:전체 01:매도 02:매수
            inqr_dvsn (str): 조회구분 - 00:역순 01:정순
            pdno (str): 상품번호 - 종목번호(6자리) 공란:전체 조회
            odno (str): 주문번호 - 주문시 한국투자증권 시스템에서 채번된 주문번호
            ccld_dvsn (str): 체결구분 - 00:전체 01:체결 02:미체결
            inqr_dvsn_3 (str): 조회구분3 - 00:전체 01:현금 02:신용 03:담보 04:대주 05:대여 06:자기융자신규/상환 07:유통융자신규/상환
            inqr_dvsn_1 (str): 조회구분1 - 공란:전체 1:ELW 2:프리보드
            ctx_area_fk100 (str): 연속조회검색조건100 - "":최초 조회시 이전 조회 ctx_area_fk100 값:다음페이지 조회시(2번째부터)
            ctx_area_nk100 (str): 연속조회키100 - "":최초 조회시 이전 조회 ctx_area_nk100 값:다음페이지 조회시(2번째부터)
            excg_id_dvsn_cd (str): 거래소ID구분코드 - KRX:한국거래소 NXT:넥스트레이드 SOR:자동주문전송 ALL:전체

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): TR내용
            - ctx_area_fk100 (str): 연속조회검색조건100
            - ctx_area_nk100 (str): 연속조회키100
            - output1 (list): 응답상세

                - ord_dt: 주문일자 - 주문일자
                - ord_gno_brno: 주문채번지점번호 - 주문시 한국투자증권 시스템에서 지정된 영업점코드
                - odno: 주문번호 - 주문시 한국투자증권 시스템에서 채번된 주문번호, 지점별 일자별로 채번됨

                    - 주문번호 유일조건: ord_dt(주문일자) + ord_gno_brno(주문채번지점번호) + odno(주문번호)

                - orgn_odno: 원주문번호 - 이전 주문에 채번된 주문번호
                - ord_dvsn_name: 주문구분명
                - sll_buy_dvsn_cd: 매도매수구분코드 - 01:매도 02:매수
                - sll_buy_dvsn_cd_name: 매도매수구분코드명 - * 반대매매 인경우 "임의매도"로 표시됨
                - pdno: 상품번호 - 종목번호(6자리)
                - prdt_name: 상품명 - 종목명
                - ord_qty: 주문수량
                - ord_unpr: 주문단가
                - ord_tmd: 주문시각
                - tot_ccld_qty: 총체결수량
                - avg_prvs: 평균가 - 체결평균가 ( 총체결금액 / 총체결수량 )
                - cncl_yn: 취소여부
                - tot_ccld_amt: 총체결금액
                - loan_dt: 대출일자
                - ordr_empno: 주문자사번
                - ord_dvsn_cd: 주문구분코드

                    | 00:지정가
                    | 01:시장가
                    | 02:조건부지정가
                    | 03:최유리지정가
                    | 04:최우선지정가
                    | 05:장전 시간외
                    | 06:장후 시간외
                    | 07:시간외 단일가
                    | 08:자기주식
                    | 09:자기주식S-Option
                    | 10:자기주식금전신탁
                    | 11:IOC지정가 (즉시체결,잔량취소)
                    | 12:FOK지정가 (즉시체결,전량취소)
                    | 13:IOC시장가 (즉시체결,잔량취소)
                    | 14:FOK시장가 (즉시체결,전량취소)
                    | 15:IOC최유리 (즉시체결,잔량취소)
                    | 16:FOK최유리 (즉시체결,전량취소)
                - cncl_cfrm_qty: 취소확인수량
                - rmn_qty: 잔여수량
                - rjct_qty: 거부수량
                - ccld_cndt_name: 체결조건명
                - inqr_ip_addr: 조회IP주소
                - cpbc_ordp_ord_rcit_dvsn_cd: 전산주문표주문접수구분코드
                - cpbc_ordp_infm_mthd_dvsn_cd: 전산주문표통보방법구분코드
                - infm_tmd: 통보시각 - ※ 실전투자계좌로는 해당값이 제공되지 않습니다.
                - ctac_tlno: 연락전화번호
                - prdt_type_cd: 상품유형코드 - 300:주식 301:선물옵션 302:채권 306:ELS
                - excg_dvsn_cd: 거래소구분코드

                    | 01:한국증권
                    | 02:증권거래소
                    | 03:코스닥
                    | 04:K-OTC
                    | 05:선물거래소
                    | 06:CME
                    | 07:EUREX
                    | 21:금현물
                    | 51:홍콩
                    | 52:상해B
                    | 53:심천
                    | 54:홍콩거래소
                    | 55:미국
                    | 56:일본
                    | 57:상해A
                    | 58:심천A
                    | 59:베트남
                    | 61:장전시간외시장
                    | 64:경쟁대량매매
                    | 65:경매매시장
                    | 81:시간외단일가시장
                - cpbc_ordp_mtrl_dvsn_cd: 전산주문표자료구분코드
                - ord_orgno: 주문조직번호
                - rsvn_ord_end_dt: 예약주문종료일자
                - excg_id_dvsn_Cd: 거래소ID구분코드
                - stpm_cndt_pric: 스톱지정가 조건가격
                - stpm_efct_occr_dtmd: 스톱지정가 효력발생 상세시각

            - output2 (dict): 응답상세

                - tot_ord_qty: 총주문수량 - 미체결주문수량 + 체결수량 (취소주문제외)
                - tot_ccld_qty: 총체결수량
                - pchs_avg_pric: 매입평균가격 - 총체결금액 / 총체결수량
                - tot_ccld_amt: 총체결금액
                - prsm_tlex_smtl: 추정제비용합계 - 제세 + 주문수수료

                    ※ 해당 값은 당일 데이터에 대해서만 제공됩니다.

        Raise:
            ValueError: API 에러 발생시
        """

        def __is_within_3month(dt: dtm.date):
            target_date = dtm.date.today().replace(day=1)

            for _ in range(3):
                target_date = target_date - dtm.timedelta(days=1)
                target_date = target_date.replace(day=1)

            three_month_ago = target_date

            return dt >= three_month_ago

        assert __is_within_3month(inqr_strt_dt) == __is_within_3month(inqr_end_dt), "3개월 이전 채결내역은 분리하여 조회해주세요."
        assert excg_id_dvsn_cd in ["KRX", "NXT", "SOR", "ALL"], "excg_id_dvsn_cd must be 'KRX', 'NXT', 'SOR' or 'ALL'"

        within_3month = __is_within_3month(inqr_strt_dt)

        url_path = "/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
        if self.auth.paper_trading:
            tr_id = "VTTC0081R" if within_3month else "VTSC9215R"
        else:
            tr_id = "TTTC0081R" if within_3month else "CTSC9215R"

        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "INQR_STRT_DT": inqr_strt_dt.strftime("%Y%m%d"),
            "INQR_END_DT": inqr_end_dt.strftime("%Y%m%d"),
            "SLL_BUY_DVSN_CD": sll_buy_dvsn_cd,
            "INQR_DVSN": inqr_dvsn,
            "PDNO": pdno,
            "CCLD_DVSN": ccld_dvsn,
            "ORD_GNO_BRNO": "",
            "ODNO": odno,
            "INQR_DVSN_3": inqr_dvsn_3,
            "INQR_DVSN_1": inqr_dvsn_1,
            "EXCG_ID_DVSN_CD": excg_id_dvsn_cd,
            "CTX_AREA_FK100": ctx_area_fk100,
            "CTX_AREA_NK100": ctx_area_nk100,
        }

        res_body, res_header = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = []
        for el in res_body["output1"]:
            for k in el.keys():
                if k == ["ord_dt", "rsvn_ord_end_dt", "loan_dt"]:
                    if len(el[k]) == 8:
                        el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k in ["ord_tmd", "infm_tmd"]:
                    if len(el[k]) == 6:
                        el[k] = dtm.datetime.strptime(el[k], "%H%M%S").time()
                elif k in ["ord_qty", "ord_unpr", "tot_ccld_qty", "avg_prvs", "tot_ccld_amt", "cncl_cfrm_qty", "rmn_qty", "rjct_qty"]:
                    if len(el[k]) > 0:
                        el[k] = int(el[k])

            output1.append(el)

        output2 = res_body["output2"]
        for k in output2.keys():
            if k == "pchs_avg_pric":
                if len(output2[k]) > 0:
                    output2[k] = Decimal(output2[k])
            else:
                output2[k] = int(output2[k])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "tr_cont": res_header["tr_cont"],
            "ctx_area_fk100": res_body["ctx_area_fk100"].strip(),
            "ctx_area_nk100": res_body["ctx_area_nk100"].strip(),
            "output1": output1,
            "output2": output2,
        }

        return result

    def inquire_balance(self, cano: str, acnt_prdt_cd: str, inqr_dvsn: str, afhr_flpr_yn: str = "N", fund_sttl_icld_yn: str = "N", prcs_dvsn: str = "00", ctx_area_fk100: str = "", ctx_area_nk100: str = "", tr_cont: str = ""):
        """
        (국내주식주문) 주식잔고조회[v1_국내주식-006]

        주식 잔고조회 API입니다.

        실전계좌의 경우, 한 번의 호출에 최대 50건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        모의계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        * 당일 전량매도한 잔고도 보유수량 0으로 보여질 수 있으나, 해당 보유수량 0인 잔고는 최종 D-2일 이후에는 잔고에서 사라집니다.
        * NXT 선택 시: NXT 거래종목만 시세 등 정보가 NXT 기준으로 변동됩니다. KRX 종목들은 그대로 유지됩니다.

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            inqr_dvsn (str): 조회구분 - 01:대출일별 02:종목별
            afhr_flpr_yn (str): 시간외단일가여부 - N:기본값 Y:시간외단일가 X:NXT 정규장 (프리마켓, 메인, 애프터마켓)
            fund_sttl_icld_yn (str): 펀드결제분포함여부 - N:포함하지 않음 Y:포함
            prcs_dvsn (str): 처리구분 - 00:전일매매포함 01:전일매매미포함
            ctx_area_fk100 (str): 연속조회검색조건100 - 공란:최초 조회시. 이전 조회 output ctx_area_fk100 값:다음페이지 조회시(2번째부터)
            ctx_area_nk100 (str): 연속조회키100 - 공란:최초 조회시. 이전 조회 output ctx_area_nk100 값:다음페이지 조회시(2번째부터)
            tr_cont (str): 연속조회여부 - 공란:최초 조회시. N:연속조회 시

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 응답메시지
            - tr_cont (str): 연속조회가능여부
            - ctx_area_fk100 (str): 연속조회검색조건100
            - ctx_area_nk100 (str): 연속조회키100
            - output1 (list): 응답상세1

                - pdno: 상품번호 - 종목번호(뒷 6자리)
                - prdt_name: 상품명 - 종목명
                - trad_dvsn_name: 매매구분명 - 매수매도구분
                - bfdy_buy_qty: 전일매수수량
                - bfdy_sll_qty: 전일매도수량
                - thdt_buyqty: 금일매수수량
                - thdt_sll_qty: 금일매도수량
                - hldg_qty: 보유수량
                - ord_psbl_qty: 주문가능수량
                - pchs_avg_pric: 매입평균가격 = 매입금액 / 보유수량
                - pchs_amt: 매입금액
                - prpr: 현재가
                - evlu_amt: 평가금액
                - evlu_pfls_amt: 평가손익금액 = 평가금액 - 매입금액
                - evlu_pfls_rt: 평가손익율
                - evlu_erng_rt: 평가수익율 - 미사용항목(0으로 출력)
                - loan_dt: 대출일자 - INQR_DVSN(조회구분)을 01(대출일별)로 설정해야 값이 나옴
                - loan_amt: 대출금액
                - stln_slng_chgs: 대주매각대금
                - expd_dt: 만기일자
                - fltt_rt: 등락율
                - bfdy_cprs_icdc: 전일대비증감
                - item_mgna_rt_name: 종목증거금율명
                - grta_rt_name: 보증금율명
                - sbst_pric: 대용가격 - 증권매매의 위탁보증금으로서 현금 대신에 사용되는 유가증권 가격
                - stck_loan_unpr: 주식대출단가

            - output2 (list): 응답상세2

                - dnca_tot_amt: 예수금총금액 - 예수금
                - nxdy_excc_amt: 익일정산금액 - D+1 예수금
                - prvs_rcdl_excc_amt: 가수도정산금액 - D+2 예수금
                - cma_evlu_amt: CMA평가금액
                - bfdy_buy_amt: 전일매수금액
                - thdt_buy_amt: 금일매수금액
                - nxdy_auto_rdpt_amt: 익일자동상환금액
                - bfdy_sll_amt: 전일매도금액
                - thdt_sll_amt: 금일매도금액
                - d2_auto_rdpt_amt: D+2자동상환금액
                - bfdy_tlex_amt: 전일제비용금액
                - thdt_tlex_amt: 금일제비용금액
                - tot_loan_amt: 총대출금액
                - scts_evlu_amt: 유가평가금액
                - tot_evlu_amt: 총평가금액 - 유가증권 평가금액 합계금액 + D+2 예수금
                - nass_amt: 순자산금액
                - fncg_gld_auto_rdpt_yn: 융자금자동상환여부 - 보유현금에 대한 융자금만 차감여부. 신용융자 매수체결 시점에서는 융자비율을 매매대금 100%로 계산 하였다가 수도결제일에 보증금에 해당하는 금액을 고객의 현금으로 충당하여 융자금을 감소시키는 업무
                - pchs_amt_smtl_amt: 매입금액합계금액
                - evlu_amt_smtl_amt: 평가금액합계금액 - 유가증권 평가금액 합계금액
                - evlu_pfls_smtl_amt: 평가손익합계금액
                - tot_stln_slng_chgs: 총대주매각대금
                - bfdy_tot_asst_evlu_amt: 전일총자산평가금액
                - asst_icdc_amt: 자산증감액
                - asst_icdc_erng_rt: 자산증감수익율 - 데이터 미제공

        Raise:
            ValueError: API 에러 발생시
        """
        assert afhr_flpr_yn in ["Y", "N", "X"], 'afhr_flpr_yn must be "Y" or "N" or "X"'
        assert inqr_dvsn in ["01", "02"], 'inqr_dvsn must be "01" or "02"'
        assert fund_sttl_icld_yn in ["Y", "N"], 'fund_sttl_icld_yn must be "Y" or "N"'
        assert prcs_dvsn in ["00", "01"], 'prcs_dvsn must be "00" or "01"'

        url_path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        tr_id = "VTTC8434R" if self.auth.paper_trading else "TTTC8434R"
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "INQR_DVSN": inqr_dvsn,
            "AFHR_FLPR_YN": afhr_flpr_yn,
            "OFL_YN": "",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": fund_sttl_icld_yn,
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": prcs_dvsn,
            "CTX_AREA_FK100": ctx_area_fk100,
            "CTX_AREA_NK100": ctx_area_nk100,
            "TR_CONT": tr_cont,
        }

        res_body, res_header = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = []
        for el in res_body["output1"]:
            for k in el.keys():
                if len(el[k]) == 0 or k in ["pdno", "prdt_name", "trad_dvsn_name", "item_mgna_rt_name", "grta_rt_name"]:
                    pass
                elif k in ["loan_dt", "expd_dt"]:
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k in ["pchs_avg_pric", "evlu_pfls_rt", "evlu_erng_rt", "stck_loan_unpr", "fltt_rt"]:
                    el[k] = Decimal(el[k])
                else:
                    try:
                        el[k] = int(el[k])
                    except Exception:
                        pass

            output1.append(el)

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if len(el[k]) == 0 or el[k] == "fncg_gld_auto_rdpt_yn":
                    pass
                elif k == "asst_icdc_erng_rt":
                    el[k] = Decimal(el[k])
                else:
                    try:
                        el[k] = int(el[k])
                    except Exception:
                        pass

            output2.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "tr_cont": res_header["tr_cont"].strip(),
            "ctx_area_fk100": res_body["ctx_area_fk100"].strip(),
            "ctx_area_nk100": res_body["ctx_area_nk100"].strip(),
            "output1": output1,
            "output2": output2,
        }

        return result

    def inquire_psbl_order(
        self,
        cano: str,
        acnt_prdt_cd: str,
        pdno: str,
        ord_dvsn: str,
        ord_unpr: int = None,
        cma_evlu_amt: str = "N",
        ovrs_icld_yn: str = "N",
    ):
        """
        (국내주식주문) 매수가능조회[v1_국내주식-007]

        | 매수가능 조회 API입니다.
        | 실전계좌/모의계좌의 경우, 한 번의 호출에 최대 1건까지 확인 가능합니다.
        |
        | 1) 매수가능금액 확인
        | . 미수 사용 X: nrcvb_buy_amt(미수없는매수금액) 확인
        | . 미수 사용 O: max_buy_amt(최대매수금액) 확인
        |
        | 2) 매수가능수량 확인
        | . 특정 종목 전량매수 시 가능수량을 확인하실 경우 ORD_DVSN:00(지정가)는 종목증거금율이 반영되지 않습니다.
        | 따라서 "반드시" ORD_DVSN:01(시장가)로 지정하여 종목증거금율이 반영된 가능수량을 확인하시기 바랍니다.
        |
        | (다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력하여 가능수량 확인)
        |
        | . 미수 사용 X: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 nrcvb_buy_qty(미수없는매수수량) 확인
        | . 미수 사용 O: ORD_DVSN:01(시장가) or 특정 주문구분(ex.IOC)로 지정하여 max_buy_qty(최대매수수량) 확인

        Args:
            cano (str): 종합계좌번호 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 계좌번호 체계(8-2)의 뒤 2자리
            pdno (str): 상품번호 종목번호(6자리)
            ord_unpr (int): 주문단가 1주당 가격 * 시장가(ORD_DVSN:01)로 조회 시, 공란으로 입력
            ord_dvsn (str): 주문구분

              | * 특정 종목 전량매수 시 가능수량을 확인할 경우 00:지정가는 증거금율이 반영되지 않으므로 증거금율이 반영되는 01: 시장가로 조회
              | * 다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력하여 가능수량 확인
              | * 공란 시, 매수수량 없이 매수금액만 조회됨.
              |
              | 00:지정가
              | 01:시장가
              | 02:조건부지정가
              | 03:최유리지정가
              | 04:최우선지정가
              | 05:장전 시간외
              | 06:장후 시간외
              | 07:시간외 단일가
              | 08:자기주식
              | 09:자기주식S-Option
              | 10:자기주식금전신탁
              | 11:IOC지정가 (즉시체결,잔량취소)
              | 12:FOK지정가 (즉시체결,전량취소)
              | 13:IOC시장가 (즉시체결,잔량취소)
              | 14:FOK시장가 (즉시체결,전량취소)
              | 15:IOC최유리 (즉시체결,잔량취소)
              | 16:FOK최유리 (즉시체결,전량취소)
              | 51:장중대량
              | 52:장중바스켓
              | 62:장개시전 시간외대량
              | 63:장개시전 시간외바스켓
              | 67:장개시전 금전신탁자사주
              | 69:장개시전 자기주식
              | 72:시간외대량
              | 77:시간외자사주신탁
              | 79:시간외대량자기주식
              | 80:바스켓

            cma_evlu_amt_icld_yn (str): CMA평가금액포함여부 Y:포함 N:포함하지 않음
            ovrs_icld_yn (str): 해외포함여부 Y:포함 N:포함하지 않음

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 응답메시지
            - output (dict): 응답상세

                - ord_psbl_cash: 주문가능현금
                - ord_psbl_sbst: 주문가능대용
                - ruse_psbl_amt: 재사용가능금액
                - fund_rpch_chgs: 펀드환매대금
                - psbl_qty_calc_unpr: 가능수량계산단가
                - nrcvb_buy_amt: 미수없는매수금액 - 미수를 사용하지 않으실 경우 nrcvb_buy_amt(미수없는매수금액)을 확인
                - nrcvb_buy_qty: 미수없는매수수량 - 미수를 사용하지 않으실 경우 nrcvb_buy_qty(미수없는매수수량)을 확인

                    * 특정 종목 전량매수 시 가능수량을 확인하실 경우 조회 시 ORD_DVSN:01(시장가)로 지정 필수
                    * 다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력

                - max_buy_amt: 최대매수금액 - 미수를 사용하시는 경우 max_buy_amt(최대매수금액)를 확인
                - max_buy_qty: 최대매수수량 - 미수를 사용하시는 경우 max_buy_qty(최대매수수량)를 확인

                    * 특정 종목 전량매수 시 가능수량을 확인하실 경우 조회 시 ORD_DVSN:01(시장가)로 지정 필수
                    * 다만, 조건부지정가 등 특정 주문구분(ex.IOC)으로 주문 시 가능수량을 확인할 경우 주문 시와 동일한 주문구분(ex.IOC) 입력

                - cma_evlu_amt: CMA평가금액
                - ovrs_re_use_amt_wcrc: 해외재사용금액원화
                - ord_psbl_frcr_amt_wcrc: 주문가능외화금액원화
        """

        url_path = "/uapi/domestic-stock/v1/trading/inquire-psbl-order"
        tr_id = "VTTC8908R" if self.auth.paper_trading else "TTTC8908R"
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": pdno,
            "ORD_UNPR": str(ord_unpr) if ord_unpr is not None else "",
            "ORD_DVSN": ord_dvsn,
            "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt,
            "OVRS_ICLD_YN": ovrs_icld_yn,
        }

        res_body, _ = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body["output"]
        """
        {
            'ord_psbl_cash': '10000000',
            'ord_psbl_sbst': '0',
            'ruse_psbl_amt': '0',
            'fund_rpch_chgs': '0',
            'psbl_qty_calc_unpr': '21645',
            'nrcvb_buy_amt': '9950248',
            'nrcvb_buy_qty': '459',
            'max_buy_amt': '9950248',
            'max_buy_qty': '459',
            'cma_evlu_amt': '0',
            'ovrs_re_use_amt_wcrc': '0',
            'ord_psbl_frcr_amt_wcrc': '0'
        }
        """

        for k in output.keys():
            output[k] = int(output[k])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "output": output,
        }

        return result

    def inquire_balance_rlz_pl(
        self, cano: str, acnt_prdt_cd: str, afhr_flpr_yn: str = "N", fund_sttl_icld_yn: str = "N", prcs_dvsn: str = "00", cost_icld_yn: str = "N", ctx_area_fk100: str = "", ctx_area_nk100: str = "", tr_cont: str = ""
    ):
        """
        (국내주식주문) 주식잔고조회_실현손익[v1_국내주식-041]

        주식잔고조회_실현손익 API입니다.

        | 한국투자 HTS(eFriend Plus) [0800] 국내 체결기준잔고 화면을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
        | (참고: 포럼 - 공지사항 - 신규 API 추가 안내(주식잔고조회_실현손익 외 1건))

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            afhr_flpr_yn (str): 시간외단일가여부 - N:기본값 Y:시간외단일가
            fund_sttl_icld_yn (str): 펀드결제포함여부 - N:포함하지 않음 Y:포함
            prcs_dvsn (str): PRCS_DVSN - 00:전일매매포함 01:전일매매미포함
            cost_icld_yn (str): 비용포함여부
            ctx_area_fk100 (str): 연속조회검색조건100 - 공란:최초 조회시. 이전 조회 output ctx_area_fk100 값:다음페이지 조회시(2번째부터)
            ctx_area_nk100 (str): 연속조회키100 - 공란:최초 조회시. 이전 조회 output ctx_area_nk100 값:다음페이지 조회시(2번째부터)

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 응답메시지
            - output1 (list): 응답상세1

                - pdno: 상품번호 - 종목번호(뒷 6자리)
                - prdt_name: 상품명 - 종목명
                - trad_dvsn_name: 매매구분명 - 매수매도구분
                - bfdy_buy_qty: 전일매수수량
                - bfdy_sll_qty: 전일매도수량
                - thdt_buyqty: 금일매수수량
                - thdt_sll_qty: 금일매도수량
                - hldg_qty: 보유수량
                - ord_psbl_qty: 주문가능수량
                - pchs_avg_pric: 매입평균가격 - 매입금액 / 보유수량
                - pchs_amt: 매입금액
                - prpr: 현재가
                - evlu_amt: 평가금액
                - evlu_pfls_amt: 평가손익금액 - 평가금액 - 매입금액
                - evlu_pfls_rt: 평가손익율
                - evlu_erng_rt: 평가수익율
                - loan_dt: 대출일자
                - loan_amt: 대출금액
                - stln_slng_chgs: 대주매각대금 - 신용 거래에서, 고객이 증권 회사로부터 대부받은 주식의 매각 대금
                - expd_dt: 만기일자
                - stck_loan_unpr: 주식대출단가
                - bfdy_cprs_icdc: 전일대비증감
                - fltt_rt: 등락율

            - output2 (list): 응답상세2

                - dnca_tot_amt: 예수금총금액
                - nxdy_excc_amt: 익일정산금액
                - prvs_rcdl_excc_amt: 가수도정산금액
                - cma_evlu_amt: CMA평가금액
                - bfdy_buy_amt: 전일매수금액
                - thdt_buy_amt: 금일매수금액
                - nxdy_auto_rdpt_amt: 익일자동상환금액
                - bfdy_sll_amt: 전일매도금액
                - thdt_sll_amt: 금일매도금액
                - d2_auto_rdpt_amt: D+2자동상환금액
                - bfdy_tlex_amt: 전일제비용금액
                - thdt_tlex_amt: 금일제비용금액
                - tot_loan_amt: 총대출금액
                - scts_evlu_amt: 유가평가금액
                - tot_evlu_amt: 총평가금액
                - nass_amt: 순자산금액
                - fncg_gld_auto_rdpt_yn: 융자금자동상환여부
                - pchs_amt_smtl_amt: 매입금액합계금액
                - evlu_amt_smtl_amt: 평가금액합계금액
                - evlu_pfls_smtl_amt: 평가손익합계금액
                - tot_stln_slng_chgs: 총대주매각대금
                - bfdy_tot_asst_evlu_amt: 전일총자산평가금액
                - asst_icdc_amt: 자산증감액
                - asst_icdc_erng_rt: 자산증감수익율
                - rlzt_pfls: 실현손익
                - rlzt_erng_rt: 실현수익율
                - real_evlu_pfls: 실평가손익
                - real_evlu_pfls_erng_rt: 실평가손익수익율

        Raise:
            ValueError: API 에러 발생시
        """
        assert self.auth.paper_trading is False, "실전계좌에서만 조회 가능합니다."

        url_path = "/uapi/domestic-stock/v1/trading/inquire-balance-rlz-pl"
        tr_id = "TTTC8494R"
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "AFHR_FLPR_YN": afhr_flpr_yn,
            "OFL_YN": "",
            "INQR_DVSN": "00",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": fund_sttl_icld_yn,
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": prcs_dvsn,
            "COST_ICLD_YN": cost_icld_yn,
            "CTX_AREA_FK100": ctx_area_fk100,
            "CTX_AREA_NK100": ctx_area_nk100,
            "TR_CONT": tr_cont,
        }

        res_body, res_header = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = []
        for el in res_body["output1"]:
            for k in el.keys():
                if len(el[k]) == 0 or k in ["pdno", "prdt_name", "trad_dvsn_name"]:
                    pass
                elif k in ["loan_dt", "expd_dt"]:
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k in ["evlu_pfls_rt", "evlu_erng_rt", "fltt_rt", "pchs_avg_pric", "stck_loan_unpr"]:
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])
            output1.append(el)

        output2 = []
        for el in res_body["output2"]:
            for k in el.keys():
                if len(el[k]) == 0 or k in ["fncg_gld_auto_rdpt_yn"]:
                    pass
                elif k in ["asst_icdc_erng_rt", "rlzt_erng_rt", "real_evlu_pfls_erng_rt"]:
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])

            output2.append(el)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "tr_cont": res_header["tr_cont"].strip(),
            "ctx_area_fk100": res_body["ctx_area_fk100"].strip(),
            "ctx_area_nk100": res_body["ctx_area_nk100"].strip(),
            "output1": output1,
            "output2": output2,
        }

        return result

    def inquire_credit_psamount(self, cano: str, acnt_prdt_cd: str, pdno: str, ord_unpr: int, ord_dvsn: str, crdt_type: str, cma_evlu_amt_icld_yn: str = "N", ovrs_icld_yn: str = "N"):
        """
        (국내주식주문) 신용매수가능조회[v1_국내주식-042]

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            pdno (str): 상품번호 - 종목코드(6자리)
            ord_unpr (int): 주문단가 - 1주당 가격. * 장전 시간외, 장후 시간외, 시장가의 경우 1주당 가격을 공란으로 비우지 않음 0으로 입력 권고
            ord_dvsn (str): 주문구분 - 00:지정가 01:시장가 02:조건부지정가 03:최유리지정가 04:최우선지정가 05:장전 시간외 06:장후 시간외 07:시간외 단일가 등
            crdt_type (str): 신용유형 - 21:자기융자신규 23:유통융자신규 26:유통대주상환 28:자기대주상환 25:자기융자상환 27:유통융자상환 22:유통대주신규 24:자기대주신규
            cma_evlu_amt_icld_yn (str): CMA평가금액포함여부 - Y/N
            ovrs_icld_yn (str): 해외포함여부 - Y/N

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 응답메시지
            - output1 (list): 응답상세1

                - ORD_PSBL_CASH: 주문가능현금
                - ORD_PSBL_SBST: 주문가능대용
                - RUSE_PSBL_AMT: 재사용가능금액
                - FUND_RPCH_CHGS: 펀드환매대금
                - PSBL_QTY_CALC_UNPR: 가능수량계산단가
                - NRCVB_BUY_AMT: 미수없는매수금액
                - NRCVB_BUY_QTY: 미수없는매수수량
                - MAX_BUY_AMT: 최대매수금액
                - MAX_BUY_QTY: 최대매수수량
                - CMA_EVLU_AMT: CMA평가금액
                - OVRS_RE_USE_AMT_WCRC: 해외재사용금액원화
                - ORD_PSBL_FRCR_AMT_WCRC: 주문가능외화금액원화

        Raise:
            ValueError: API 에러 발생시
        """
        assert self.auth.paper_trading is False, "실전계좌에서만 조회 가능합니다."

        url_path = "/uapi/domestic-stock/v1/trading/inquire-credit-psamount"
        tr_id = "TTTC8909R"
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": pdno,
            "ORD_UNPR": ord_unpr,
            "ORD_DVSN": ord_dvsn,
            "CRDT_TYPE": crdt_type,
            "CMA_EVLU_AMT_ICLD_YN": cma_evlu_amt_icld_yn,
            "OVRS_ICLD_YN": ovrs_icld_yn,
        }

        res_body, _ = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body["output"]
        for k in output.keys():
            if len(output[k]) == 0:
                pass
            else:
                output[k] = int(output[k])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "output": output,
        }

        return result

    def inquire_account_balance(self, cano: str, acnt_prdt_cd: str):
        """
        (국내주식주문) 투자계좌자산현황조회[v1_국내주식-048]

        투자계좌자산현황조회 API입니다.

        output1은 한국투자 HTS(eFriend Plus) > [0891] 계좌 자산비중(결제기준) 화면 아래 테이블의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 응답메시지

            - output1 (list): 응답상세1

                - pchs_amt: 매입금액
                - evlu_amt: 평가금액
                - evlu_pfls_amt: 평가손익금액
                - crdt_lnd_amt: 신용대출금액
                - real_nass_amt: 실제순자산금액
                - whol_weit_rt: 전체비중율

            - output2 (dict): 응답상세2

                - pchs_amt_smtl: 매입금액합계 - 유가매입금액
                - nass_tot_amt: 순자산총금액
                - loan_amt_smtl: 대출금액합계
                - evlu_pfls_amt_smtl: 평가손익금액합계 - 평가손익금액
                - evlu_amt_smtl: 평가금액합계 - 유가평가금액
                - tot_asst_amt: 총자산금액 - 자산금액
                - tot_lnda_tot_ulst_lnda: 총대출금액총융자대출금액
                - cma_auto_loan_amt: CMA자동대출금액
                - tot_mgln_amt: 총담보대출금액
                - stln_evlu_amt: 대주평가금액
                - crdt_fncg_amt: 신용융자금액
                - ocl_apl_loan_amt: OCL_APL대출금액
                - pldg_stup_amt: 질권설정금액
                - frcr_evlu_tota: 외화평가총액
                - tot_dncl_amt: 총예수금액
                - cma_evlu_amt: CMA평가금액
                - dncl_amt: 예수금액
                - tot_sbst_amt: 총대용금액
                - thdt_rcvb_amt: 당일미수금액
                - ovrs_stck_evlu_amt1: 해외주식평가금액1
                - ovrs_bond_evlu_amt: 해외채권평가금액
                - mmf_cma_mgge_loan_amt: MMFCMA담보대출금액
                - sbsc_dncl_amt: 청약예수금액
                - pbst_sbsc_fnds_loan_use_amt: 공모주청약자금대출사용금액
                - etpr_crdt_grnt_loan_amt: 기업신용공여대출금액

        Raise:
            ValueError: API 에러 발생시
        """
        assert self.auth.paper_trading is False, "실전계좌에서만 조회 가능합니다."

        url_path = "/uapi/domestic-stock/v1/trading/inquire-account-balance"
        tr_id = "CTRP6548R"
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "INQR_DVSN_1": "",
            "BSPR_BF_DT_APLY_YN": "",
        }

        res_body, _ = self._tr_request(url_path, tr_id, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = []
        for el in res_body["output1"]:
            for k in el.keys():
                if len(el[k]) == 0:
                    pass
                elif k == "whol_weit_rt":
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])

            output1.append(el)

        output2 = res_body["output2"]
        for k in output2.keys():
            if len(output2[k]) == 0:
                pass
            elif k in ["ovrs_stck_evlu_amt1", "ovrs_bond_evlu_amt"]:
                output2[k] = Decimal(output2[k])
            else:
                output2[k] = int(output2[k])

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"].strip(), "output1": output1, "output2": output2}

        return result

    def inquire_period_trade_profit(self, cano: str, acnt_prdt_cd: str, inqr_strt_dt: dtm.date, inqr_end_dt: dtm.date, sort_dvsn: str = "00", pdno: str = "", ctx_area_nk100: str = "", ctx_area_fk100: str = "", tr_cont: str = ""):
        """
        (국내주식주문) 기간별매매손익현황조회[v1_국내주식-060]

        기간별매매손익현황조회 API입니다.

        한국투자 HTS(eFriend Plus) > [0856] 기간별 매매손익 화면 에서 "종목별" 클릭 시의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Args:
            cano (str): 종합계좌번호
            sort_dvsn (str): 정렬구분 - 00:최근순(기본값) 01:과거순 02:최근순
            acnt_prdt_cd (str): 계좌상품코드
            pdno (str): 상품번호 - "" 공란입력 시, 전체 (기본값)
            inqr_strt_dt (datetime.date): 조회시작일자
            inqr_end_dt (datetime.date): 조회종료일자
            ctx_area_nk100 (str): 연속조회키100
            ctx_area_fk100 (str): 연속조회검색조건100
            tr_cont (str): 연속조회여부 - 공란:최초 조회시. 'N':연속조회시

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 응답메시지
            - output1 (dict): 응답상세1

                - trad_dt: 매매일자
                - pdno: 상품번호 - 종목번호(뒤 6자리만 해당)
                - prdt_name: 상품명
                - trad_dvsn_name: 매매구분명
                - loan_dt: 대출일자
                - hldg_qty: 보유수량
                - pchs_unpr: 매입단가
                - buy_qty: 매수수량
                - buy_amt: 매수금액
                - sll_pric: 매도가격
                - sll_qty: 매도수량
                - sll_amt: 매도금액
                - rlzt_pfls: 실현손익
                - pfls_rt: 손익률
                - fee: 수수료
                - tl_tax: 제세금
                - loan_int: 대출이자
                - ctx_area_fk100: 연속조회검색조건100
                - ctx_area_nk100: 연속조회키100 - 100

            - output2 (list): 응답상세2

                - sll_qty_smtl: 매도수량합계
                - sll_tr_amt_smtl: 매도거래금액합계
                - sll_fee_smtl: 매도수수료합계
                - sll_tltx_smtl: 매도제세금합계
                - sll_excc_amt_smtl: 매도정산금액합계
                - buyqty_smtl: 매수수량합계
                - buy_tr_amt_smtl: 매수거래금액합계
                - buy_fee_smtl: 매수수수료합계
                - buy_tax_smtl: 매수제세금합계
                - buy_excc_amt_smtl: 매수정산금액합계
                - tot_qty: 총수량
                - tot_tr_amt: 총거래금액
                - tot_fee: 총수수료
                - tot_tltx: 총제세금
                - tot_excc_amt: 총정산금액
                - tot_rlzt_pfls: 총실현손익
                - loan_int: 대출이자
                - tot_pftrt: 총수익률

        Raise:
            ValueError: API 에러 발생시
        """

        assert self.auth.paper_trading is False, "실전계좌에서만 조회 가능합니다."
        assert sort_dvsn in ["00", "01", "02"], "sort_dvsn은 00, 01, 02 중 하나여야 합니다."

        url_path = "/uapi/domestic-stock/v1/trading/inquire-period-trade-profit"
        tr_id = "TTTC8715R"
        params = {
            "CANO": cano,
            "SORT_DVSN": sort_dvsn,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": pdno,
            "INQR_STRT_DT": inqr_strt_dt.strftime("%Y%m%d"),
            "INQR_END_DT": inqr_end_dt.strftime("%Y%m%d"),
            "CBLC_DVSN": "00",
            "CTX_AREA_NK100": ctx_area_nk100,
            "CTX_AREA_FK100": ctx_area_fk100,
        }

        res_body, res_header = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = []
        for el in res_body["output1"]:
            for k in el.keys():
                if len(el[k]) == 0 or k in ["pdno", "prdt_name", "trad_dvsn_name"]:
                    pass
                elif k in ["trad_dt", "loan_dt"]:
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k in ["pfls_rt"]:
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])

            output1.append(el)

        output2 = res_body["output2"]
        """
        {
            'sll_qty_smtl': '111',
            'sll_tr_amt_smtl': '1940820',
            'sll_fee_smtl': '81',
            'sll_tltx_smtl': '1660',
            'sll_excc_amt_smtl': '1939079',
            'buyqty_smtl': '83',
            'buy_tr_amt_smtl': '965290',
            'buy_fee_smtl': '40',
            'buy_tax_smtl': '0',
            'buy_excc_amt_smtl': '965330',
            'tot_qty': '194',
            'tot_tr_amt': '2906110',
            'tot_fee': '121',
            'tot_tltx': '1660',
            'tot_excc_amt': '2904409',
            'tot_rlzt_pfls': '8029',
            'loan_int': '0',
            'tot_pftrt': '0.41579277'
        }
        """
        for k in output2.keys():
            if len(output2[k]) == 0:
                pass
            elif k == "tot_pftrt":
                output2[k] = Decimal(output2[k])
            else:
                output2[k] = int(output2[k])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "ctx_area_fk100": res_body["ctx_area_fk100"].strip(),
            "ctx_area_nk100": res_body["ctx_area_nk100"].strip(),
            "tr_cont": res_header["tr_cont"].strip(),
            "output1": output1,
            "output2": output2,
        }

        return result

    def inquire_period_profit(self, cano: str, acnt_prdt_cd: str, inqr_strt_dt: dtm.date, inqr_end_dt: dtm.date, pdno: str = "", sort_dvsn: str = "00", ctx_area_nk100: str = "", ctx_area_fk100: str = "", tr_cont: str = ""):
        """
        (국내주식주문) 기간별손익일별합산조회[v1_국내주식-052]

        기간별손익일별합산조회 API입니다.

        한국투자 HTS(eFriend Plus) > [0856] 기간별 매매손익 화면 에서 "일별" 클릭 시의 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.

        Note:
            - 00:30 ~ 03:00 사이에는 조회 불가능합니다.

        Args:
            acnt_prdt_cd (str): 계좌상품코드
            cano (str): 종합계좌번호
            inqr_strt_dt (datetime.date): 조회시작일자
            inqr_end_dt (datetime.date): 조회종료일자
            pdno (str): 상품번호 - "" 공란입력 시, 전체
            sort_dvsn (str): 정렬구분 - 00:최근순 01:과거순 02:최근순
            ctx_area_nk100 (str): 연속조회키100
            ctx_area_fk100 (str): 연속조회검색조건100
            tr_cont (str): 연속조회여부 - 공란:최초 조회시. 'N':연속조회시

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 응답메시지

            - output1 (list): 응답상세1

                - trad_dt: 매매일자
                - buy_amt: 매수금액
                - sll_amt: 매도금액
                - rlzt_pfls: 실현손익
                - fee: 수수료
                - loan_int: 대출이자
                - tl_tax: 제세금
                - pfls_rt: 손익률
                - sll_qty1: 매도수량1
                - buy_qty1: 매수수량1

            - outpu2 (dict): 응답상세2

                - sll_qty_smtl: 매도수량합계
                - sll_tr_amt_smtl: 매도거래금액합계
                - sll_fee_smtl: 매도수수료합계
                - sll_tltx_smtl: 매도제세금합계
                - sll_excc_amt_smtl: 매도정산금액합계
                - buy_qty_smtl: 매수수량합계
                - buy_tr_amt_smtl: 매수거래금액합계
                - buy_fee_smtl: 매수수수료합계
                - buy_tax_smtl: 매수제세금합계
                - buy_excc_amt_smtl: 매수정산금액합계
                - tot_qty: 총수량
                - tot_tr_amt: 총거래금액
                - tot_fee: 총수수료
                - tot_tltx: 총제세금
                - tot_excc_amt: 총정산금액
                - tot_rlzt_pfls: 총실현손익
                - loan_int: 대출이자

        Raise:
            ValueError: API 에러 발생시
        """

        assert self.auth.paper_trading is False, "실전계좌에서만 조회 가능합니다."

        url_path = "/uapi/domestic-stock/v1/trading/inquire-period-profit"
        tr_id = "TTTC8708R"
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "PDNO": pdno,
            "INQR_STRT_DT": inqr_strt_dt.strftime("%Y%m%d"),
            "INQR_END_DT": inqr_end_dt.strftime("%Y%m%d"),
            "SORT_DVSN": sort_dvsn,
            "INQR_DVSN": "00",
            "CBLC_DVSN": "00",
            "CTX_AREA_NK100": ctx_area_nk100,
            "CTX_AREA_FK100": ctx_area_fk100,
        }

        res_body, res_header = self._tr_request(url_path, tr_id, tr_cont, params=params)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = []
        for el in res_body["output1"]:
            for k in el.keys():
                if len(el[k]) == 0:
                    pass
                elif k == "trad_dt":
                    el[k] = dtm.datetime.strptime(el[k], "%Y%m%d").date()
                elif k == "pfls_rt":
                    el[k] = Decimal(el[k])
                else:
                    el[k] = int(el[k])

            output1.append(el)

        output2 = res_body["output2"]

        for k in output2.keys():
            if len(output2[k]) == 0:
                pass

            output2[k] = int(output2[k])

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"].strip(),
            "ctx_area_fk100": res_body["ctx_area_fk100"].strip(),
            "ctx_area_nk100": res_body["ctx_area_nk100"].strip(),
            "tr_cont": res_header["tr_cont"].strip(),
            "output1": output1,
            "output2": output2,
        }

        return result

    def nav_comparison_daily_trend(self, fid_input_iscd: str, fid_input_date_1: dtm.date, fid_input_date_2: dtm.date, fid_cond_mrkt_div_code="J"):
        """
        NAV 비교추이(일) API입니다.

        한국투자 HTS(eFriend Plus) > [0244] ETF/ETN 비교추이(NAV/IIV) 좌측 화면 "일별" 비교추이 기능을 API로 개발한 사항으로, 해당 화면을 참고하시면 기능을 이해하기 쉽습니다.
        실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능합니다.

        Args:
            fid_input_iscd (str): 종목코드 (6자리)
            fid_input_date_1 (datetime.date): FID 입력일자1 - 조회 시작일자 (ex. dtm.date(2024, 1, 01))
            fid_input_date_2 (datetime.date): FID 입력일자2 - 조회 종료일자 (ex. dtm.date(2024, 1, 31))
            fid_cond_mrkt_div_code (str): FID 조건시장분류코드 - J 입력

        Returns:
            dict:

            - rt_cd (str): 응답코드
            - msg_cd (str): 메시지코드
            - msg1 (str): 메시지1
            - tr_cont (str): 연속조회가능여부
            - output (list): 응답상세

                - stck_bsop_date: 주식 영업 일자
                - stck_clpr: 주식 종가
                - prdy_vrss: 전일 대비
                - prdy_vrss_sign: 전일 대비 부호
                - prdy_ctrt: 전일 대비율
                - acml_vol: 누적 거래량
                - cntg_vol: 체결 거래량
                - dprt: 괴리율
                - nav_vrss_prpr: NAV 대비 현재가
                - nav: NAV
                - nav_prdy_vrss_sign: NAV 전일 대비 부호
                - nav_prdy_vrss: NAV 전일 대비
                - nav_prdy_ctrt: NAV 전일 대비율

        Raise:
            ValueError: API 에러 발생시
        """

        url_path = "/uapi/etfetn/v1/quotations/nav-comparison-daily-trend"
        tr_id = "FHPST02440200"
        params = {
            "FID_COND_MRKT_DIV_CODE": fid_cond_mrkt_div_code,
            "FID_INPUT_ISCD": fid_input_iscd,
            "FID_INPUT_DATE_1": fid_input_date_1.strftime("%Y%m%d"),
            "FID_INPUT_DATE_2": fid_input_date_2.strftime("%Y%m%d"),
        }

        res_body, res_header = self._tr_request(url_path, tr_id, "", params=params)

        print(res_header)

        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body["output"]:
            el["stck_bsop_date"] = dtm.datetime.strptime(el["stck_bsop_date"], "%Y%m%d").date()

            int_keys = ["stck_clpr", "prdy_vrss", "acml_vol", "cntg_vol"]
            for k in int_keys:
                if k in el and len(el[k]) > 0:
                    el[k] = int(el[k])

            decimal_keys = ["prdy_vrss_sign", "prdy_ctrt", "dprt", "nav", "nav_prdy_vrss_sign", "nav_prdy_vrss", "nav_prdy_ctrt"]
            for k in decimal_keys:
                if k in el and len(el[k]) > 0:
                    el[k] = Decimal(el[k])

            output.append(el)

        result = {"rt_cd": res_body["rt_cd"], "msg_cd": res_body["msg_cd"], "msg1": res_body["msg1"], "tr_cont": res_header["tr_cont"], "output": output}

        return result

    async def listen_order_event(self, hts_id: str, stop_event: asyncio.Event) -> AsyncGenerator:
        """
        주식 주문 이벤트를 실시간으로 수신하고 처리하는 비동기 제너레이터 함수입니다.

        이 함수는 지정된 HTS ID를 사용하여 웹소켓 연결을 통해 주문 이벤트를 실시간으로 수신합니다.
        주문 이벤트 데이터는 암호화되어 전송될 수 있으며, 이 함수는 암호화된 데이터를 해독하여 주문의 상세 정보를 추출합니다.
        추출된 정보는 비동기적으로 소비할 수 있도록 제너레이터로 반환됩니다.

        Args:
            hts_id (str): 주식 거래 시스템에서 사용되는 고유 식별자.

        Yields:
            dict: 주문에 관한 상세 정보를 포함하는 사전형 데이터. 각 키는 다음과 같습니다:
                - "cust_id": 고객 ID (HTS ID)
                - "acnt_no": 계좌번호
                - "oder_no": 주문번호
                - "ooder_no": 원주문번호
                - "seln_byov_cls": 매도매수구분 (01:매도, 02:매수)
                - "rctf_cls": 정정구분
                - "oder_kind": 주문종류
                - "oder_cond": 주문조건
                - "stck_shrn_iscd": 주식단축코드
                - "cntg_qty": 체결수량
                - "cntg_unpr": 체결 단가
                - "stck_cntg_hour": 체결 시간
                - "rfus_yn": 거부여부 (0:정상, 1:거부)
                - "cntg_yn": 체결여부 (1:주문,정정,취소,거부, 2:체결)
                - "acpt_yn": 접수여부 (1:접수, 2:확인, 3:취소)
                - "brnc_no": 지점번호
                - "oder_qty": 주문수량
                - "acnt_name": 계좌명
                - "ord_cond_prc": 주문조건가격
                - "ord_exg_cb": 주문거래소 구분 (1:KRX, 2:NXT, 3:SOR-KRX, 4:SOR-NXT)
                - "popup_yn": 실시간체결창 표시여부 (Y/N)
                - "filler": 필러
                - "crdt_cls": 신용구분
                - "crdt_loan_date": 신용대출일자
                - "cntg_isnm40": 체결종목명40
                - "oder_prc": 주문가격

        Examples:
            >>> async for order_event in listen_order_event('your_hts_id'):
            >>>    print(order_event)
            {'cust_id': 'your_hts_id', 'acnt_no': 'your_acnt_no', 'oder_no': '0027163200', 'ooder_no': '', 'seln_byov_cls': '02', 'rctf_cls': '0', 'oder_kind': '00', 'oder_cond': '0', 'stck_shrn_iscd': '005930', 'cntg_qty': 1, 'cntg_unpr': 59400, 'stck_cntg_hour': '165219', 'rfus_yn': '0', 'cntg_yn': '1', 'acpt_yn': '1', 'brnc_no': '91252', 'oder_qty': 1, 'acnt_name': '권순섭', 'ord_cond_prc': '', 'ord_exg_gb': '4', 'popup_yn': 'Y', 'filler': '', 'crdt_cls': '10', 'crdt_loan_date': '', 'cntg_isnm40': '삼성전자', 'oder_prc': ''}
            {'cust_id': 'your_hts_id', 'acnt_no': 'your_acnt_no', 'oder_no': '0027165500', 'ooder_no': '0027163200', 'seln_byov_cls': '02', 'rctf_cls': '2', 'oder_kind': '00', 'oder_cond': '0', 'stck_shrn_iscd': '005930', 'cntg_qty': 1, 'cntg_unpr': 0, 'stck_cntg_hour': '165248', 'rfus_yn': '0', 'cntg_yn': '1', 'acpt_yn': '2', 'brnc_no': '91252', 'oder_qty': 1, 'acnt_name': '권순섭', 'ord_cond_prc': '', 'ord_exg_gb': '4', 'popup_yn': 'Y', 'filler': '', 'crdt_cls': '10', 'crdt_loan_date': '', 'cntg_isnm40': '삼성전자', 'oder_prc': ''}


        Note:
            이 함수는 비동기 I/O를 사용하므로 async for 문을 사용하여 이벤트를 소비해야 합니다.
        """

        payload_pattern = re.compile(r"^(0|1)\|[^\|]+\|\d+\|([A-Za-z0-9+/=]+(\^[A-Za-z0-9+/=]+)*)?$")

        iv = None
        key = None
        tr_ids = ["H0STCNI9", "H0STCNI0"]

        async def __on_connect(ws: websockets.WebSocketClientProtocol):
            payload = {
                "header": {
                    "approval_key": self.auth.get_approval_key(),
                    "custtype": "B" if self.corp_data else "P",
                    "tr_type": "1",  # 1:등록, 2:해제
                    "content-type": "utf-8",
                },
                "body": {
                    "input": {
                        "tr_id": "H0STCNI9" if self.auth.paper_trading else "H0STCNI0",
                        "tr_key": hts_id,
                    }
                },
            }

            await ws.send(json.dumps(payload))

        def __parse_order_event_payload(data):
            keys = [
                "cust_id",  # 고객 ID (HTS ID)
                "acnt_no",  # 계좌번호
                "oder_no",  # 주문번호
                "ooder_no",  # 원주문번호
                "seln_byov_cls",  # 매도매수구분 (01:매도, 02:매수)
                "rctf_cls",  # 정정구분
                "oder_kind",  # 주문종류 주문통보: 주문낸 주문종류로 수신, 체결통보: 00으로 수신
                "oder_cond",  # 주문조건
                "stck_shrn_iscd",  # 주식단축코드
                "cntg_qty",  # 체결수량 - 체결통보(CNTG_YN=2)시 체결 수량, 정정/취소/거부 접수 통보(CNTG_YN=1)시 주문수량을 의미함
                "cntg_unpr",  # 체결 단가
                "stck_cntg_hour",  # 체결 시간
                "rfus_yn",  # 거부여부 (0:정상, 1:거부)
                "cntg_yn",  # 체결여부 (1:주문,정정,취소,거부, 2:체결)
                "acpt_yn",  # 접수여부 (1:접수, 2:확인, 3:취소)
                "brnc_no",  # 지점번호
                "oder_qty",  # 주문수량
                "acnt_name",  # 계좌명
                "ord_cond_prc",  # 스톱지정가일때만 표시
                "ord_exg_gb",  # 주문거래소 구분 (1:KRX, 2:NXT, 3:SOR-KRX, 4:SOR-NXT)
                "popup_yn",  # 실시간체결창 표시여부 (Y/N)
                "filler",  # 필러
                "crdt_cls",  # 신용구분
                "crdt_loan_date",  # 신용대출일자
                "cntg_isnm40",  # 체결종목명40
                "oder_prc",  # 주문가격 - 체결통보(CNTG_YN=2)시 주문가격, 주문,정정,취소,거부 접수 통보(CNTG_YN=1)시 체결단가(빈값으로 수신)
            ]

            tokens = data.split("|")
            tr_id = tokens[1]
            if tr_id in tr_ids:
                if iv and key:
                    decoded_str = _aes_cbc_base64_dec(key, iv, tokens[3])
                    values = decoded_str.split("^")
                    result = {}
                    for i, k in enumerate(keys):
                        if k in ["cntg_unpr", "oder_prc", "cntg_qty", "oder_qty"] and len(values[i]) > 0:
                            result[k] = int(values[i])
                        else:
                            result[k] = values[i] if i < len(values) else ""
                    return result

        def __parse_iv_and_key(data):
            nonlocal iv
            nonlocal key

            try:
                data = json.loads(data)
                body = data.get("body")
                if body:
                    output = body.get("output")
                    if output:
                        if "iv" in output and "key" in output:
                            iv = output.get("iv")
                            key = output.get("key")

            except json.JSONDecodeError:
                pass

        client = KISTRWebsocketClient(self.auth, __on_connect, stop_event)

        async for data in client.listen():
            if payload_pattern.match(data):
                event_data = __parse_order_event_payload(data)
                if event_data:
                    yield event_data
            else:
                __parse_iv_and_key(data)


def _aes_cbc_base64_dec(key, iv, cipher_text):
    """
    :param key:  str type AES256 secret key value
    :param iv: str type AES256 Initialize Vector
    :param cipher_text: Base64 encoded AES256 str
    :return: Base64-AES256 decodec str
    """
    cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
    return bytes.decode(unpad(cipher.decrypt(b64decode(cipher_text)), AES.block_size))
