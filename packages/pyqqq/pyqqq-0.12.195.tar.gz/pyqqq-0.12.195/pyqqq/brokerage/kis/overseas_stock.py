from decimal import Decimal
from typing import Dict, List, Optional
from pyqqq.brokerage.kis.oauth import KISAuth
from pyqqq.brokerage.kis.tr_client import KISTRClient
import datetime as dtm


class KISOverseasStock:
    def __init__(self, auth: KISAuth, corp_data: dict = None):
        self.auth = auth
        self.corp_data = corp_data
        self.tr_client = KISTRClient(auth, corp_data)

    def _tr_request(self, *args, **kwargs):
        return self.tr_client.request(*args, **kwargs)

    def get_price(self, market: str, symbol: str) -> dict:
        ''' (해외주식현재가) 해외주식 현재 체결가 [v1_해외주식-009]

        Args:
            market (str): 거래소코드
            symbol (str): 종목코드

        Returns:
            dict: 현재 체결가 정보
                - rsym: D+시장구분(3자리)+종목코드
                - zdiv: 소수점자리수
                - base: 전일종가
                - pvol: 전일의 거래량
                - last: 현재가 - 당일 조회시점의 가격
                - sign: 대비기호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - diff: 대비 - 전일 종가와 당일 현재가의 차이 (당일 현재가 - 전일 종가)
                - rate: 등락율 = 전일 대비 / 당일 현재가 * 100
                - tvol: 당일 조회시점까지 전체 거래금액
                - tamt: 당일 조회시점까지 전체 거래금액
                - ordy: 매수주문 가능 종목 여부

        Raises:
            ValueError: API 호출 실패시 발생
        '''
        path = '/uapi/overseas-price/v1/quotations/price'
        query = {
            'AUTH': '',
            'EXCD': market,
            'SYMB': symbol
        }
        tr_id = 'HHDFS00000300'
        body, resp_header = self._tr_request(path, tr_id, params=query)

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output = body['output']
        for k in output.keys():
            if len(output[k]) == 0:
                pass
            elif k in ['rsym', 'ordy']:
                pass
            elif k in ['pvol', 'sign', 'tvol', 'tamt']:
                output[k] = int(output[k])
            else:
                output[k] = Decimal(output[k])

        return {
            'tr_id': resp_header['tr_id'],
            'tr_cont': resp_header['tr_cont'],
            'gt_uid': resp_header['gt_uid'],
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output': output,
        }

    def get_dailyprice(self, excd: str, symb: str, gubn: str, modp: str, bymd: str = '', keyb: str = '', tr_cont: str = ''):
        '''
        (해외주식현재가) 해외주식 기간별시세[v1_해외주식-010]

        Args:
            excd (str): 거래소코드 (NAS, NYS, AMS)
            symb (str): 종목코드
            gubn (str): 구분 - "0":일 "1":주 "3":월
            bymd (str): 조회일자 (YYYYMMDD)
            modp (str): 수정주가반영여부 - "0":미반영 "1":반영
            keyb (str): NEXT KEY BUFF - 응답시 다음값이 있으면 값이 셋팅되어 있으므로 다음 조회시 응답값 그대로 셋팅
            tr_cont (str): 연속조회여부 - 공백: 초기조회, "N": 연속조회

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - gt_uid: 고유번호
            - output1: 응답상세1 (dict)
                - rsym: D+시장구분(3자리)+종목코드
                - zdiv: 소수점자리수
                - nrec: 조회된 건수
            - output2: 응답상세2 (list)
                - xymd: 일자
                - clos: 종가
                - sign: 대비기호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - diff: 대비 - 전일 종가와 당일 현재가의 차이 (당일 현재가 - 전일 종가)
                - rate: 등락율 = 전일 대비 / 당일 현재가 * 100
                - open: 시가
                - high: 고가
                - low: 저가
                - tvol: 거래량
                - tamt: 거래대금
                - pbid: 매수호가
                - vbid: 매수잔량
                - pask: 매도호가
                - vask: 매도잔량

        Raises:
            ValueError: API 호출 실패시 발생
        '''

        path = '/uapi/overseas-price/v1/quotations/dailyprice'
        params = {
            'AUTH': '',
            'EXCD': excd,
            'SYMB': symb,
            'GUBN': gubn,
            'BYMD': bymd,
            'MODP': modp,
            'KEYB': keyb
        }

        tr_id = 'HHDFS76240000'
        body, header = self._tr_request(path, tr_id, tr_cont, params)

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output1 = body['output1']
        output1['nrec'] = int(output1['nrec'])
        output1['zdiv'] = int(output1['zdiv'])
        output2 = []
        for data in body['output2']:
            output2.append(
                {
                    "xymd": dtm.datetime.strptime(data["xymd"], "%Y%m%d").date(),  # 일자
                    "clos": Decimal(data["clos"]),  # 종가
                    "sign": int(data["sign"]),  # 대비기호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                    "diff": Decimal(data["diff"]),  # 대비 - 전일 종가와 당일 현재가의 차이 (당일 현재가 - 전일 종가)
                    "rate": Decimal(data["rate"]),  # 등락율 = 전일 대비 / 당일 현재가 * 100
                    "open": Decimal(data["open"]),  # 시가
                    "high": Decimal(data["high"]),  # 고가
                    "low": Decimal(data["low"]),  # 저가
                    "tvol": int(data["tvol"]),  # 거래량
                    "tamt": Decimal(data["tamt"]),  # 거래대금
                    "pbid": Decimal(data["pbid"]),  # 매수호가
                    "vbid": int(data["vbid"]),  # 매수잔량
                    "pask": Decimal(data["pask"]),  # 매도호가
                    "vask": int(data["vask"]),  # 매도잔량
                }
            )

        return {
            'tr_id': header['tr_id'],
            'tr_cont': header['tr_cont'],
            'gt_uid': header['gt_uid'],
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output1': output1,
            'output2': output2
        }

    def inquire_daily_chartprice(self, fid_cond_mrkt_div_code: str, fid_input_iscd: str, fid_input_date_1: dtm.date, fid_input_date_2: dtm.date, fid_period_div_code: str, tr_cont: str = ""):
        '''
        (해외주식현재가) 해외주식 종목/지수/환율기간별시세(일/주/월/년)[v1_해외주식-012]

        Args:
            fid_cond_mrkt_div_code (str): 시장구분코드 - "N":해외지수 "X":환율
            fid_input_iscd (str): 종목코드 (해외주식 마스터 코드 참조. 다우30, 나스닥100, S&P500 종목만 조회가능)
            fid_input_date_1 (dtm.date): 조회시작일자
            fid_input_date_2 (dtm.date): 조회종료일자
            fid_period_div_code (str): 기간구분코드 - "D":일 "W":주 "M":월 "Y":년
            tr_cont (str): 연속조회여부 - 공백: 초기조회, "N": 연속조회

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output1: 응답상세1 (dict)
                - ovrs_nmix_prdy_vrss: 전일대비
                - prdy_vrss_sign: 전일대비부호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - prdy_ctrt: 전일 대비율
                - ovrs_nmix_prdy_clpr: 전일종가
                - acml_vol: 누적거래량
                - hts_kor_isnm: HTS 한글 종목명
                - ovrs_nmix_prpr: 현재가
                - stck_shrn_iscd: 단축 종목코드
                - ovrs_prod_oprc: 시가
                - ovrs_prod_hgpr: 최고가
                - ovrs_prod_lwpr: 최저가
            - output2: 응답상세2 (list)
                - stck_bsop_date: 영업일자
                - ovrs_nmix_prpr: 현재가
                - ovrs_nmix_oprc: 시가
                - ovrs_nmix_hgpr: 최고가
                - ovrs_nmix_lwpr: 최저가
                - acml_vol: 누적 거래량
                - mod_yn: 변경 여부
        '''

        assert fid_cond_mrkt_div_code in ['N', 'X']
        assert fid_period_div_code in ['D', 'W', 'M', 'Y']

        path = '/uapi/overseas-price/v1/quotations/inquire-daily-chartprice'
        params = {
            'FID_COND_MRKT_DIV_CODE': fid_cond_mrkt_div_code,
            'FID_INPUT_ISCD': fid_input_iscd,
            'FID_INPUT_DATE_1': fid_input_date_1.strftime('%Y%m%d'),
            'FID_INPUT_DATE_2': fid_input_date_2.strftime('%Y%m%d'),
            'FID_PERIOD_DIV_CODE': fid_period_div_code
        }
        tr_id = 'FHKST03030100'

        body, header = self._tr_request(path, tr_id, tr_cont, params)

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output1 = body['output1']
        output1 = {
            'ovrs_nmix_prdy_vrss': Decimal(output1['ovrs_nmix_prdy_vrss']),
            'prdy_vrss_sign': int(output1['prdy_vrss_sign']),
            'prdy_ctrt': Decimal(output1['prdy_ctrt']),
            'ovrs_nmix_prdy_clpr': Decimal(output1['ovrs_nmix_prdy_clpr']),
            'acml_vol': int(output1['acml_vol']),
            'hts_kor_isnm': output1['hts_kor_isnm'],
            'ovrs_nmix_prpr': Decimal(output1['ovrs_nmix_prpr']),
            'stck_shrn_iscd': output1['stck_shrn_iscd'],
            'ovrs_prod_oprc': Decimal(output1['ovrs_prod_oprc']),
            'ovrs_prod_hgpr': Decimal(output1['ovrs_prod_hgpr']),
            'ovrs_prod_lwpr': Decimal(output1['ovrs_prod_lwpr']),
        }
        output2 = []
        for el in body['output2']:
            output2.append({
                'stck_bsop_date': dtm.datetime.strptime(el['stck_bsop_date'], '%Y%m%d').date(),
                'ovrs_nmix_prpr': Decimal(el['ovrs_nmix_prpr']),
                'ovrs_nmix_oprc': Decimal(el['ovrs_nmix_oprc']),
                'ovrs_nmix_hgpr': Decimal(el['ovrs_nmix_hgpr']),
                'ovrs_nmix_lwpr': Decimal(el['ovrs_nmix_lwpr']),
                'acml_vol': int(el['acml_vol']),
                'mod_yn': el['mod_yn'],
            })

        result = {
            'tr_id': header['tr_id'],
            'tr_cont': header['tr_cont'],
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output1': output1,
            'output2': output2
        }

        return result

    def inquire_search(self,
                       excd: str,
                       co_yn_pricecur: str = "",
                       co_st_pricecur: str = "",
                       co_en_pricecur: str = "",
                       co_yn_rate: str = "",
                       co_st_rate: str = "",
                       co_en_rate: str = "",
                       co_yn_volume: str = "",
                       co_st_volume: str = "",
                       co_en_volume: str = "",
                       co_yn_per: str = "",
                       co_st_per: str = "",
                       co_en_per: str = "",
                       co_yn_eps: str = "",
                       co_st_eps: str = "",
                       co_en_eps: str = "",
                       co_yn_amt: str = "",
                       co_st_amt: str = "",
                       co_en_amt: str = "",
                       co_yn_shar: str = "",
                       co_st_shar: str = "",
                       co_en_shar: str = "",
                       co_yn_valx: str = "",
                       co_st_valx: str = "",
                       co_en_valx: str = "",
                       tr_cont: str = ""):
        '''
        (해외주식현재가) 해외주식 종목검색[v1_해외주식-015]

        해외주식 조건검색 API입니다.

        현재 조건검색 결과값은 최대 100개까지 조회 가능합니다. 다음 조회(100개 이후의 값) 기능에 대해서는 개선검토 중에 있습니다.

        | ※ 그날 거래량이나 시세 형성이 안된 종목은 해외주식 기간별시세(HHDFS76240000)에서는 조회되지만
        |   해외주식 조건검색(HHDFS76410000)에서 조회되지 않습니다. (EX. NAS AATC)


        Args:
            excd (str): 거래소코드 (NAS, NYS, AMS, HKS, SHS, SZS, HSX, HNX, TSE)
            co_yn_pricecur (str): 현재가여부 - 해당 조건 사용시 "1", 미사용시 ""
            co_st_pricecur (str): 현재가시작
            co_en_pricecur (str): 현재가종료
            co_yn_rate (str): 등락률여부
            co_st_rate (str): 등락률시작
            co_en_rate (str): 등락률종료
            co_yn_volume (str): 거래량여부
            co_st_volume (str): 거래량시작
            co_en_volume (str): 거래량종료
            co_yn_per (str): PER여부
            co_st_per (str): PER시작
            co_en_per (str): PER종료
            co_yn_eps (str): EPS여부
            co_st_eps (str): EPS시작
            co_en_eps (str): EPS종료
            co_yn_amt (str): 거래대금여부
            co_st_amt (str): 거래대금시작
            co_en_amt (str): 거래대금종료
            co_yn_shar (str): 주식수여부
            co_st_shar (str): 주식수시작
            co_en_shar (str): 주식수종료
            co_yn_valx (str): 시가총액여부
            co_st_valx (str): 시가총액시작
            co_en_valx (str): 시가총액종료
            tr_cont (str): 연속조회여부 - 공백: 초기조회, "N": 연속조회

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output: 응답상세1 (dict)
                - zdiv: 소수점자리수
                - stat: 거래상태정보
                - crec: 조회된 건수
                - trec: 전체 건수
                - nrec: Record count
            - output2: 응답상세2 (list)
                - rsym: D+시장구분(3자리)+종목코드
                - excd: 거래소코드
                - name: 종목명
                - symb: 종목코드
                - last: 현재가
                - shar: 발행주식수
                - valx: 시가총액
                - plow: 최저가
                - phigh: 최고가
                - popen: 시가
                - tvol: 거래량
                - rate: 등락률
                - diff: 대비
                - sign: 대비기호
                - avol: 거래대금
                - eps: EPS
                - per: PER
                - rank: 순위
                - ename: 영문 종목명
                - e_ordyn: 매수주문 가능 여부. 가능 "O"

        Raises:
            ValueError - API 호출 에러 발생 시
        '''

        assert excd in ['NAS', 'NYS', 'AMS', 'HKS', 'SHS', 'SZS', 'HSX', 'HNX', 'TSE']

        path = '/uapi/overseas-price/v1/quotations/inquire-search'
        params = {
            'AUTH': '',
            'EXCD': excd,
            'CO_YN_PRICECUR': co_yn_pricecur,
            'CO_ST_PRICECUR': co_st_pricecur,
            'CO_EN_PRICECUR': co_en_pricecur,
            'CO_YN_RATE': co_yn_rate,
            'CO_ST_RATE': co_st_rate,
            'CO_EN_RATE': co_en_rate,
            'CO_YN_VOLUME': co_yn_volume,
            'CO_ST_VOLUME': co_st_volume,
            'CO_EN_VOLUME': co_en_volume,
            'CO_YN_PER': co_yn_per,
            'CO_ST_PER': co_st_per,
            'CO_EN_PER': co_en_per,
            'CO_YN_EPS': co_yn_eps,
            'CO_ST_EPS': co_st_eps,
            'CO_EN_EPS': co_en_eps,
            'CO_YN_AMT': co_yn_amt,
            'CO_ST_AMT': co_st_amt,
            'CO_EN_AMT': co_en_amt,
            'CO_YN_SHAR': co_yn_shar,
            'CO_ST_SHAR': co_st_shar,
            'CO_EN_SHAR': co_en_shar,
            'CO_YN_VALX': co_yn_valx,
            'CO_ST_VALX': co_st_valx,
            'CO_EN_VALX': co_en_valx,
            'KEYB': ''
        }
        tr_id = 'HHDFS76410000'
        body, header = self._tr_request(path, tr_id, tr_cont, params)

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output1 = body['output1']
        output1 = {
            'zdiv': int(output1['zdiv']),
            'stat': output1['stat'],
            'crec': int(output1['crec']),
            'trec': int(output1['trec']),
            'nrec': int(output1['nrec']),
        }

        output2 = []
        for el in body['output2']:
            output2.append({
                'rsym': el['rsym'],
                'excd': el['excd'],
                'name': el['name'],
                'symb': el['symb'],
                'last': Decimal(el['last']),
                'shar': int(el['shar']),
                'valx': Decimal(el['valx']),
                'plow': Decimal(el['plow']),
                'phigh': Decimal(el['phigh']),
                'popen': Decimal(el['popen']),
                'tvol': int(el['tvol']),
                'rate': Decimal(el['rate']),
                'diff': Decimal(el['diff']),
                'sign': int(el['sign']),
                'avol': int(el['avol']),
                'eps': Decimal(el['eps']),
                'per': Decimal(el['per']),
                'rank': int(el['rank']),
                'ename': el['ename'],
                'e_ordyn': el['e_ordyn'],
            })

        result = {
            'tr_id': header['tr_id'],
            'tr_cont': header['tr_cont'],
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output1': output1,
            'output2': output2
        }

        return result

    def get_price_detail(self,
                         excd: str,
                         symb: str):
        '''
        (해외주식현재가) 해외주식 현재가 상세정보[v1_해외주식-029]

        해외주식 현재가상세 API입니다.

        해당 API를 활용하여 해외주식 종목의 매매단위(vnit), 호가단위(e_hogau), PER, PBR, EPS, BPS 등의 데이터를 확인하실 수 있습니다.

        해외주식 시세는 무료시세(지연시세)만이 제공되며, API로는 유료시세(실시간시세)를 받아보실 수 없습니다.

        | ※ 지연시세 지연시간 : 미국 - 실시간무료(0분지연) / 홍콩, 베트남, 중국 - 15분지연 / 일본 - 20분지연
        | 미국의 경우 0분지연시세로 제공되나, 장중 당일 시가는 상이할 수 있으며, 익일 정정 표시됩니다.

        ※ 추후 HTS(efriend Plus) [7781] 시세신청(실시간) 화면에서 유료 서비스 신청 시 실시간 시세 수신할 수 있도록 변경 예정


        Args:
            excd (str): 거래소코드
            symb (str): 종목코드
            tr_cont (str): 연속조회여부 - 공백: 초기조회, "N": 연속조회

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output: 응답상세
                - rsym: D+시장구분(3자리)+종목코드
                - pvol: 전일의 거래량
                - open: 시가
                - high: 고가
                - low: 저가
                - last: 현재가
                - base: 전일종가
                - tomv: 시가총액
                - pamt: 전일거래대금
                - uplp: 상한가
                - dnlp: 하한가
                - h52p: 52주 최고가
                - h52d: 52주 최고일자
                - l52p: 52주 최저가
                - l52d: 52주 최저일자
                - perx: PER
                - pbrx: PBR
                - epsx: EPS
                - bpsx: BPS
                - shar: 발행주식수
                - mcap: 자본금
                - curr: 통화
                - zdiv: 소수점자리수
                - vnit: 매매단위
                - t_xprc: 원환산당일가격
                - t_xdif: 원환산당일대비
                - t_xrat: 원환산당일등락
                - p_xprc: 원환산전일가격
                - p_xdif: 원환산전일대비
                - p_xrat: 원환산전일등락
                - t_rate: 당일환율
                - p_rate: 전일환율
                - t_xsgn: 원환산당일기호
                - p_xsng: 원환산전일기호
                - e_ordyn: 매수주문 가능 여부. 가능 "O"
                - e_hogau: 호가단위
                - e_icod: 업종(섹터)
                - e_parp: 액면가
                - tvol: 거래량
                - tamt: 거래대금
                - etyp_nm: ETP 분류명

        Raise:
            ValueError: API 호출 실패시
        '''

        path = '/uapi/overseas-price/v1/quotations/price-detail'
        tr_id = 'HHDFS76200200'
        tr_cont = ''
        params = {
            'AUTH': '',
            'EXCD': excd,
            'SYMB': symb
        }

        body, header = self._tr_request(path, tr_id, tr_cont, params)

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output = body['output']

        for k in output.keys():
            if len(output[k]) == 0:
                pass
            elif k in ['rsym', 'curr', 'e_ordyn', 'e_icod', 'etyp_nm']:
                pass
            elif k in ['pvol', 'shar', 'vnit', 'tvol', 'tamt', 'zdiv', 't_xsgn', 'p_xsng']:
                output[k] = int(output[k])
            elif k in ['h52d', 'l52d']:
                output[k] = dtm.datetime.strptime(output[k], '%Y%m%d').date()
            else:
                output[k] = Decimal(output[k])

        result = {
            'tr_id': header['tr_id'],
            'tr_cont': header['tr_cont'],
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output': output
        }

        return result

    def inquire_time_itemchartprice(
        self,
        excd: str,
        symb: str,
        nmin: int = 1,
        pinc: int = 0,
        next: str = "",
        nrec: int = 120,
        keyb: str = "",
    ):
        """
        (해외주식현재가) 해외주식분봉조회[v1_해외주식-030]

        | 해외주식분봉조회 API입니다.
        | 실전계좌의 경우, 최근 120건까지 확인 가능합니다.

        Args:
            excd (str): 거래소코드
            symb (str): 종목코드
            nmin (int): 분봉단위 - 1:1분봉 2:2분봉, ...
            next (str): 다음 여부
            pinc (int): 전일포함여부 - 0: 당일, 1: 전일포함
            nrec (int): 요청갯수 - 레코드요청갯수 (최대 120)
            keyb (str): NEXT KEY BUFF - 응답시 다음값이 있으면 값이 셋팅되어 있으므로 다음 조회시 응답값 그대로 셋팅

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output1: 응답상세1 (dict)
                - rsym: D+시장구분(3자리)+종목코드
                - zdiv: 소수점자리수
                - stim: 시작시간
                - etim: 종료시간
                - sktm: 시작시간
                - ektm: 종료시간
                - next: 다음시작시간
                - more: 더보기여부
                - nrec: 조회된 건수
            - output2: 응답상세2 (list)
                - tymd: 일자
                - xymd: 일자
                - xhms: 시간
                - kymd: 일자
                - khms: 시간
                - open: 시가
                - high: 고가
                - low: 저가
                - last: 현재가
                - evol: 거래량
                - eamt: 거래대금

        Raises:
            ValueError: API 호출 실패시
        """

        assert nrec > 0 and nrec <= 120
        assert nmin > 0
        assert pinc == 0 or pinc == 1

        path = '/uapi/overseas-price/v1/quotations/inquire-time-itemchartprice'
        tr_id = "HHDFS76950200"
        tr_cont = ""

        params = {
            "AUTH": "",
            "EXCD": excd,
            "SYMB": symb,
            "NMIN": str(nmin),
            "PINC": str(pinc),
            "NEXT": next,
            "NREC": str(nrec),
            "FILL": "",
            "KEYB": keyb,
        }

        body, header = self._tr_request(path, tr_id, tr_cont, params)

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output1 = body['output1']

        output1 = {
            "rsym": output1["rsym"],
            "zdiv": int(output1["zdiv"]),
            "stim": dtm.datetime.strptime(output1["stim"], "%H%M%S").time(),
            "etim": dtm.datetime.strptime(output1["etim"], "%H%M%S").time(),
            "sktm": dtm.datetime.strptime(output1["sktm"], "%H%M%S").time(),
            "ektm": dtm.datetime.strptime(output1["ektm"], "%H%M%S").time(),
            "next": output1["next"],
            "more": output1["more"],
            "nrec": int(output1["nrec"]),
        }

        output2 = []

        for el in body['output2']:
            output2.append({
                'tymd': dtm.datetime.strptime(el['tymd'], '%Y%m%d').date(),
                'xymd': dtm.datetime.strptime(el['xymd'], '%Y%m%d').date(),
                'xhms': dtm.datetime.strptime(el['xhms'], '%H%M%S').time(),
                'kymd': dtm.datetime.strptime(el['kymd'], '%Y%m%d').date(),
                'khms': dtm.datetime.strptime(el['khms'], '%H%M%S').time(),
                'open': Decimal(el['open']),
                'high': Decimal(el['high']),
                'low': Decimal(el['low']),
                'last': Decimal(el['last']),
                'evol': int(el['evol']),
                'eamt': int(el['eamt']),
            })

        result = {
            'tr_id': header['tr_id'],
            'tr_cont': header['tr_cont'],
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output1': output1,
            'output2': output2
        }

        return result

    def inquire_time_indexchartprice(self,
                                     fid_cond_mrkt_div_code: str,
                                     fid_input_iscd: str,
                                     fid_hour_cls_code: str,
                                     fid_pw_data_incu_yn: str):
        '''
        (해외주식현재가) 해외지수분봉조회[v1_해외주식-031]

        | 해외지수분봉조회 API입니다.
        | 실전계좌의 경우, 최근 102건까지 확인 가능합니다.

        Args:
            fid_cond_mrkt_div_code (str): 조건 시장 분류 코드 - "N":해외지수 "X":환율 "KX":원화환율
            fid_input_iscd (str): 종목번호(ex. TSLA)
            fid_hour_cls_code (str): 시간구분코드 - "0":정규장 "1":시간외
            fid_pw_data_incu_yn (str): 과거데이터포함여부 - "Y":포함 "N":미포함

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output1: 응답상세1 (dict)
                - ovrs_nmix_prdy_vrss: 전일대비
                - prdy_vrss_sign: 전일대비부호 - 1:상한 2:상승 3:보합 4:하한 5:하락
                - hts_kor_isnm: HTS 한글 종목명
                - prdy_ctrt: 전일 대비율
                - ovrs_nmix_prdy_clpr: 전일종가
                - stck_shrn_iscd: 단축 종목코드
                - ovrs_prod_oprc: 시가
                - ovrs_prod_hgpr: 최고가
                - ovrs_prod_lwpr: 최저가
            - output2: 응답상세2 (list)
                - stck_bsop_date: 영업일자
                - stck_cntg_hour: 거래시간
                - optn_prpr: 현재가
                - optn_oprc: 시가
                - optn_hgpr: 최고가
                - optn_lwpr: 최저가
                - cntg_vol: 거래량

        '''

        assert fid_cond_mrkt_div_code in ['N', 'X', 'KX']
        assert fid_hour_cls_code in ['0', '1']
        assert fid_pw_data_incu_yn in ['Y', 'N']

        path = '/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice'
        tr_id = 'FHKST03030200'
        tr_cont = ''

        params = {
            'FID_COND_MRKT_DIV_CODE': fid_cond_mrkt_div_code,
            'FID_INPUT_ISCD': fid_input_iscd,
            'FID_HOUR_CLS_CODE': fid_hour_cls_code,
            'FID_PW_DATA_INCU_YN': fid_pw_data_incu_yn,
        }

        body, header = self._tr_request(path, tr_id, tr_cont, params)

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output1 = body['output1']
        output1 = {
            'ovrs_nmix_prdy_vrss': Decimal(output1['ovrs_nmix_prdy_vrss']),
            'prdy_vrss_sign': int(output1['prdy_vrss_sign']),
            'hts_kor_isnm': output1['hts_kor_isnm'],
            'prdy_ctrt': Decimal(output1['prdy_ctrt']),
            'ovrs_nmix_prdy_clpr': Decimal(output1['ovrs_nmix_prdy_clpr']),
            'acml_vol': int(output1['acml_vol']),
            'ovrs_nmix_prpr': Decimal(output1['ovrs_nmix_prpr']),
            'stck_shrn_iscd': output1['stck_shrn_iscd'],
            'ovrs_prod_oprc': Decimal(output1['ovrs_prod_oprc']),
            'ovrs_prod_hgpr': Decimal(output1['ovrs_prod_hgpr']),
            'ovrs_prod_lwpr': Decimal(output1['ovrs_prod_lwpr']),
        }

        output2 = []
        for el in body['output2']:
            output2.append({
                'stck_bsop_date': dtm.datetime.strptime(el['stck_bsop_date'], '%Y%m%d').date(),
                'stck_cntg_hour': dtm.datetime.strptime(el['stck_cntg_hour'], '%H%M%S').time(),
                'optn_prpr': Decimal(el['optn_prpr']),
                'optn_oprc': Decimal(el['optn_oprc']),
                'optn_hgpr': Decimal(el['optn_hgpr']),
                'optn_lwpr': Decimal(el['optn_lwpr']),
                'cntg_vol': int(el['cntg_vol']),
            })

        result = {
            'tr_id': header['tr_id'],
            'tr_cont': header['tr_cont'],
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output1': output1,
            'output2': output2
        }

        return result

    def order(self,
              cano: str,
              actn_prdt_cd: str,
              ovrs_excg_cd: str,
              pdno: str,
              ord_qty: int,
              ovrs_ord_unpr: Decimal,
              sll_type: str,
              ord_dvsn: str,
              ctac_tlno: str = None,
              mgco_aptm_odno: str = None):
        '''
        (해외주식주문) 해외주식 주문[v1_해외주식-001]

        해외주식 주문 API입니다.

        | * 모의투자의 경우, 모든 해외 종목 매매가 지원되지 않습니다. 일부 종목만 매매 가능한 점 유의 부탁드립니다.
        |
        | * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        | https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
        |
        | * 해외 거래소 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.
        | * 해외 거래소 운영시간(한국시간 기준)
        | 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        | 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        | 3) 상해 : 10:30 ~ 16:00
        | 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00
        |
        | ※ POST API의 경우 BODY값의 key값들을 대문자로 작성하셔야 합니다.
        | (EX. "CANO" : "12345678", "ACNT_PRDT_CD": "01",...)
        |
        | ※ 종목코드 마스터파일 파이썬 정제코드는 한국투자증권 Github 참고 부탁드립니다.
        | https://github.com/koreainvestment/open-trading-api/tree/main/stocks_info

        Args:
            cano (str): 계좌번호
            actn_prdt_cd (str): 계좌상품코드
            ovrs_excg_cd (str): 해외거래소코드
            pdno (str): 상품번호
            ord_qty (int): 주문수량
            ovrs_ord_unpr (Decimal): 해외주식주문가격
            ctac_tlno (str): 연락처
            mgco_aptm_odno (str): 관리자처리주문번호
            sll_type (str): 매매구분 - "00":매도 "":매수
            ord_dvsn (str): 주문구분

              | [Header tr_id TTTT1002U(미국 매수 주문)]
              | 00 : 지정가
              | 32 : LOO(장개시지정가)
              | 34 : LOC(장마감지정가)
              | * 모의투자 VTTT1002U(미국 매수 주문)로는 00:지정가만 가능
              |
              | [Header tr_id TTTT1006U(미국 매도 주문)]
              | 00 : 지정가
              | 31 : MOO(장개시시장가)
              | 32 : LOO(장개시지정가)
              | 33 : MOC(장마감시장가)
              | 34 : LOC(장마감지정가)
              | * 모의투자 VTTT1006U(미국 매도 주문)로는 00:지정가만 가능
              |
              | [Header tr_id TTTS1001U(홍콩 매도 주문)]
              | 00 : 지정가
              | 50 : 단주지정가
              | * 모의투자 VTTS1001U(홍콩 매도 주문)로는 00:지정가만 가능
              |
              | [그외 tr_id]
              | 제거

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output: 응답상세 (dict)
                - krx_fwdg_ord_orgno: 한국거래소전송주문조직번호
                - odno: 주문번호
                - ord_tmd: 주문시각
        '''

        assert ovrs_excg_cd in ['NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'HASE', 'VNSE', 'TKSE']

        def __infer_tr_id():
            pair = ('매수', '매도')
            paper_trading_pair = ('매수', '매도')

            if ovrs_excg_cd in ['NASD', 'NYSE', 'AMEX']: # 미국
                pair = ('TTTT1002U', 'TTTT1006U')
                paper_trading_pair = ('VTTT1002U', 'VTTT1001U')
            elif ovrs_excg_cd == 'TKSE': # 일본
                pair = ('TTTS0308U', 'TTTS0307U')
                paper_trading_pair = ('VTTS0308U', 'VTTS0307U')
            elif ovrs_excg_cd == 'SEHK': # 홍콩
                pair = ('TTTS1002U', 'TTTS1001U')
                paper_trading_pair = ('VTTS1002U', 'VTTS1001U')
            elif ovrs_excg_cd == 'SHAA': # 상해
                pair = ('TTTS0202U', 'TTTS1005U')
                paper_trading_pair = ('VTTS0202U', 'VTTS1005U')
            elif ovrs_excg_cd == 'SZAA': # 심천
                pair = ('TTTS0305U', 'TTTS0304U')
                paper_trading_pair = ('VTTS0305U', 'VTTS0304U')
            elif ovrs_excg_cd in ['HASE', 'VNSE']: # 베트남
                pair = ('TTTS0311U', 'TTTS0310U')
                paper_trading_pair = ('VTTS0311U', 'VTTS0310U')

            idx = 1 if sll_type == '00' else 0

            if self.auth.paper_trading:
                return paper_trading_pair[idx]
            else:
                return pair[idx]

        path = '/uapi/overseas-stock/v1/trading/order'
        tr_id = __infer_tr_id()
        tr_cont = ''

        body = {
            'CANO': cano,
            'ACNT_PRDT_CD': actn_prdt_cd,
            'OVRS_EXCG_CD': ovrs_excg_cd,
            'PDNO': pdno,
            'ORD_QTY': str(ord_qty),
            'OVRS_ORD_UNPR': str(ovrs_ord_unpr),
            'ORD_SVR_DVSN_CD': '0',
        }

        body['CTAC_TLNO'] = ctac_tlno or ''
        body['MGCO_APTM_ODNO'] = mgco_aptm_odno or ''
        if sll_type == '00':
            body['SLL_TYPE'] = sll_type
        if ord_dvsn:
            body['ORD_DVSN'] = ord_dvsn

        body, _ = self._tr_request(path, tr_id, tr_cont, body=body, method='POST')

        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        return {
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output': body['output'],
        }

    def order_rvsecncl(self,
                       cano: str,
                       acnt_prdt_cd: str,
                       ovrs_excg_cd: str,
                       pdno: str,
                       orgn_odno: str,
                       rvse_cncl_dvsn_cd: str,
                       ord_qty: int,
                       ovrs_ord_unpr: Decimal,
                       mgco_aptm_odno: str = None):

        '''
        (해외주식주문) 해외주식 정정취소주문[v1_해외주식-002]

        | 접수된 해외주식 주문을 정정하거나 취소하기 위한 API입니다.
        | (해외주식주문 시 Return 받은 ODNO를 참고하여 API를 호출하세요.)

        | * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        | https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        | * 해외 거래소 운영시간 외 API 호출 시 애러가 발생하오니 운영시간을 확인해주세요.
        | * 해외 거래소 운영시간(한국시간 기준)
        | 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        | 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        | 3) 상해 : 10:30 ~ 16:00
        | 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00

        Args:
            cano (str): 종합계좌번호 - 계좌번호 체계(8-2)의 앞 8자리
            acnt_prdt_cd (str): 계좌상품코드 - 계좌번호 체계(8-2)의 뒤 2자리
            ovrs_excg_cd (str): 해외거래소코드

              | NASD : 나스닥
              | NYSE : 뉴욕
              | AMEX : 아멕스
              | SEHK : 홍콩
              | SHAA : 중국상해
              | SZAA : 중국심천
              | TKSE : 일본
              | HASE : 베트남 하노이
              | VNSE : 베트남 호치민

            pdno (str): 상품번호
            orgn_odno (str): 원주문번호 - 정정 또는 취소할 원주문번호 (해외주식_주문 API ouput ODNO or 해외주식 미체결내역 API output ODNO 참고)
            rvse_cncl_dvsn_cd (str): 정정취소구분코드 - 01:정정 02:취소
            ord_qty (str): 주문수량
            ovrs_ord_unpr (str): 해외주문단가 - 취소주문 시, "0" 입력
            mgco_aptm_odno (str): 운용사지정주문번호

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output: 응답상세
                - KRX_FWDG_ORD_ORGNO: 한국거래소전송주문조직번호 - 주문시 한국투자증권 시스템에서 지정된 영업점코드
                - ODNO: 주문번호 - 주문시 한국투자증권 시스템에서 채번된 주문번호
                - ORD_TMD: 주문시각 - 주문시각(시분초HHMMSS)

        '''

        assert ovrs_excg_cd in ['NASD', 'NYSE', 'AMEX', 'SEHK', 'SHAA', 'SZAA', 'HASE', 'VNSE', 'TKSE']

        def __infer_tr_id():
            if ovrs_excg_cd in ['NASD', 'NYSE', 'AMEX']: # 미국
                live = 'TTTT1004U'
                paper = 'VTTT1004U'
            elif ovrs_excg_cd == 'TKSE': # 일본
                live = 'TTTS0309U'
                paper = 'VTTS0309U'
            elif ovrs_excg_cd == 'SEHK': # 홍콩
                live = 'TTTS1003U'
                paper = 'VTTS1003U'
            elif ovrs_excg_cd == 'SHAA': # 상해
                live = 'TTTS0302U'
                paper = 'VTTS0302U'
            elif ovrs_excg_cd == 'SZAA': # 심천
                live = 'TTTS0306U'
                paper = 'VTTS0306U'
            elif ovrs_excg_cd in ['HASE', 'VNSE']: # 베트남
                live = 'TTTS0312U'
                paper = 'VTTS0312U'

            if self.auth.paper_trading:
                return paper
            else:
                return live

        path = '/uapi/overseas-stock/v1/trading/order-rvsecncl'
        tr_id = __infer_tr_id()
        tr_cont = ''
        req_body = {
            'CANO': cano,
            'ACNT_PRDT_CD': acnt_prdt_cd,
            'OVRS_EXCG_CD': ovrs_excg_cd,
            'PDNO': pdno,
            'ORGN_ODNO': orgn_odno,
            'RVSE_CNCL_DVSN_CD': rvse_cncl_dvsn_cd,
            'ORD_QTY': str(ord_qty),
            'OVRS_ORD_UNPR': str(ovrs_ord_unpr),
            'ORD_SVR_DVSN_CD': '0',
        }
        if mgco_aptm_odno:
            req_body['MGCO_APTM_ODNO'] = mgco_aptm_odno

        body, _ = self._tr_request(path, tr_id, tr_cont, body=req_body, method='POST')
        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        result = {
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output': body['output'],
        }

        return result

    def inquire_nccs(self, cano: str, acnt_prdt_cd: str, ovrs_excg_cd: str, sort_sqn: str = "", ctx_area_fk200: str = "", ctx_area_nk200: str = ""):
        """
        (해외주식주문) 해외주식 미체결내역[v1_해외주식-005]

        접수된 해외주식 주문 중 체결되지 않은 미체결 내역을 조회하는 API입니다.

        | * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        | https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        | ※ 해외 거래소 운영시간(한국시간 기준)
        | 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        | 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        | 3) 상해 : 10:30 ~ 16:00
        | 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00

        Args:
            cano (str): 계좌번호
            acnt_prdt_cd (str): 계좌상품코드
            ovsrs_excg_cd (str): 해외거래소코드
            sort_sqn (str): 정렬순서 - "DS": 정순, 그외: 역순
            ctx_area_fk200 (str): 연속조회검색조건200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_FK200값
            ctx_area_nk200 (str): 연속조회키200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_NK200값

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - ctx_area_fk200: 연속조회검색조건200
            - ctx_area_nk200: 연속조회키200
            - output: 응답상세 (list)
                - ord_dt: 주문일자
                - ord_gno_brno: 주문채번지점번호
                - odno: 주문번호
                - orgn_odno: 원주문번호
                - pdno: 상품번호
                - prdt_name: 상품명
                - sll_buy_dvsn_cd: 매도매수구분코드 - 01:매도 02:매수
                - sll_buy_dvsn_cd_name: 매도매수구분코드명
                - rvse_cncl_dvsn_cd: 정정취소구분코드 - 01:정정 02:취소
                - rvse_cncl_dvsn_cd_name: 정정취소구분명
                - rjct_rson: 거부사유
                - rjct_rson_name: 거부사유명
                - ord_tmd: 주문시각
                - tr_mket_name: 거래시장명
                - tr_crcy_cd: 통화코드 - USD:미국달러 HKD:홍콩달러 JPY:일본엔 CNY:중국위안 VND:베트남동
                - natn_cd: 국가코드
                - natn_kor_name: 국가한글명
                - ft_ord_qty: FT주문수량
                - ft_ccld_qty: FT체결수량
                - nccs_qty: 미체결수량
                - ft_ord_unpr3: FT주문단가3
                - ft_ccld_unpr3 FT체결단가3
                - gt_ccld_amt3: FT체결금액3
                - ovrs_excg_cd: 해외거래소코드
                - prcs_stat_name: 처리상태명
                - loan_type_cd: 대출유형코드
                - loan_dt: 대출일자
                - usa_amk_exts_rqst_yn: 미국애프터마켓연장신청여부 Y/N

        Raises:
            ValueError: API 호출 실패시 발생
        """

        path = "/uapi/overseas-stock/v1/trading/inquire-nccs"
        tr_id = "VTTS3018R" if self.auth.paper_trading else "TTTS3018R"
        tr_cont = ""
        params = {"CANO": cano, "ACNT_PRDT_CD": acnt_prdt_cd, "OVRS_EXCG_CD": ovrs_excg_cd, "SORT_SQN": sort_sqn, "CTX_AREA_FK200": ctx_area_fk200, "CTX_AREA_NK200": ctx_area_nk200}

        body, _ = self._tr_request(path, tr_id, tr_cont, params)
        if body["rt_cd"] != "0":
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output = []
        for el in body["output"]:
            copied = el.copy()
            for k in ["ft_ord_qty", "ft_ccld_qty", "nccs_qty"]:
                if copied.get(k) is not None:
                    copied[k] = int(copied[k])

            output.append(copied)

        result = {
            "rt_cd": body["rt_cd"],
            "msg_cd": body["msg_cd"],
            "msg1": body["msg1"],
            "ctx_area_fk200": body["ctx_area_fk200"],
            "ctx_area_nk200": body["ctx_area_nk200"],
            "output": output,
        }

        return result

    def order_resv(
        self,
        cano: str,
        acnt_prdt_cd: str,
        pdno: str,
        ovrs_excg_cd: str,
        ft_ord_qty: int,
        ft_ord_unpr3: Decimal,
        sll_buy_dvsn_cd: str,
        rvse_cncl_dvsn_cd: Optional[str] = None,
        prdt_type_cd: Optional[str] = None,
        rsvn_ord_rcit_dt: Optional[str] = None,
        ord_dvsn: Optional[str] = None,
        ovrs_rsvn_odno: Optional[str] = None,
    ):
        """

        해외주식 예약주문접수[v1_해외주식-002]

        해외주식 예약 주문을 접수하는 함수입니다. 미국, 중국, 홍콩, 일본, 베트남 시장의 주식을 예약 매매할 수 있습니다.

        미국 거래소 운영 시간 외에 예약 주문을 하거나, 기타 해외 거래소에 대해 지정가 주문을 할 수 있습니다.
        미국 예약 매도 주문의 경우 MOO(장 개시 시장가) 주문도 가능합니다.

        Args:
            cano (str): 종합계좌번호 (8자리).
            acnt_prdt_cd (str): 계좌상품코드 (2자리).
            pdno (str): 상품번호
            ovrs_excg_cd (str): 해외 거래소 코드 (예: NASD: 나스닥, NYSE: 뉴욕).
            ft_ord_qty (str): 주문 수량.
            ft_ord_unpr3 (str): 주문 단가.
            sll_buy_dvsn_cd (str): 매도/매수 구분 코드. (01: 매도, 02: 매수)
            rvse_cncl_dvsn_cd (str, optional): 정정/취소 구분 코드. (00: 매도/매수 주문 시 필수, 02: 취소)
            prdt_type_cd (str, optional): 상품유형코드 (일본/홍콩/중국/베트남 인 경우만 사용)
            rsvn_ord_rcit_dt (str, optional): 예약 주문 접수 일자. (일본/홍콩/중국/베트남 인 경우만 사용)
            ord_dvsn (str, optional): 주문 구분 (미국 예약 매도 주문 시 사용, 00: 지정가, 31: MOO(시장가)).
            ovrs_rsvn_odno (str, optional): 해외 예약 주문 번호 (취소 시 사용).

        Returns:
            dict: 주문 접수에 대한 응답 정보.
                - rt_cd (str): 성공 여부 (0: 성공, 0 이외의 값: 실패).
                - msg_cd (str): 응답 코드.
                - msg1 (str): 응답 메시지.
                - output (dict): 응답 상세.
                    - ODNO (str): 한국 거래소 전송 주문 조직 번호 (미국 예약 주문 시 출력).
                    - RSVN_ORD_RCIT_DT (str): 예약 주문 접수 일자 (중국/홍콩/일본/베트남 예약 주문 시 출력).
                    - OVRS_RSVN_ODNO (str): 해외 예약 주문 번호 (중국/홍콩/일본/베트남 예약 주문 시 출력).

        Raises:
            ValueError: 필수 인자가 없거나 잘못된 경우 발생.
        """

        assert ovrs_excg_cd in ["NASD", "NYSE", "AMEX", "SEHK", "SHAA", "SZAA", "HASE", "VNSE", "TKSE"]

        def __infer_tr_id():
            pair = ("매수", "매도")
            paper_trading_pair = ("매수", "매도")

            if ovrs_excg_cd in ["NASD", "NYSE", "AMEX"]:  # 미국
                pair = ("TTTT3014U", "TTTT3016U")
                paper_trading_pair = ("VTTT3014U", "VTTT3016U")
            else:
                pair = ("TTTS3013U", "TTTS3013U")
                paper_trading_pair = ("VTTS3013U", "VTTS3013U")

            idx = 1 if sll_buy_dvsn_cd == "01" else 0

            if self.auth.paper_trading:
                return paper_trading_pair[idx]
            else:
                return pair[idx]

        path = "/uapi/overseas-stock/v1/trading/order-resv"
        tr_id = __infer_tr_id()
        tr_cont = ""

        body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "OVRS_EXCG_CD": ovrs_excg_cd,
            "PDNO": pdno,
            "FT_ORD_QTY": str(ft_ord_qty),
            "FT_ORD_UNPR3": str(ft_ord_unpr3),
            "ORD_SVR_DVSN_CD": "0",
        }

        if ovrs_excg_cd not in ["NASD", "NYSE", "AMEX"]:
            body["SLL_BUY_DVSN_CD"] = sll_buy_dvsn_cd
        if rvse_cncl_dvsn_cd:
            body["RVSE_CNCL_DVSN_CD"] = rvse_cncl_dvsn_cd
        if prdt_type_cd:
            body["PRDT_TYPE_CD"] = prdt_type_cd
        if rsvn_ord_rcit_dt:
            body["RSVN_ORD_RCIT_DT"] = rsvn_ord_rcit_dt
        if ord_dvsn:
            body["ORD_DVSN"] = ord_dvsn
        if ovrs_rsvn_odno:
            body["OVRS_RSVN_ODNO"] = ovrs_rsvn_odno

        body, _ = self._tr_request(path, tr_id, tr_cont, body=body, method="POST")

        if body["rt_cd"] != "0":
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        return {
            "rt_cd": body["rt_cd"],
            "msg_cd": body["msg_cd"],
            "msg1": body["msg1"],
            "output": body["output"],
        }

    def order_resv_ccnl(
        self,
        cano: str,
        acnt_prdt_cd: str,
        rsyn_ord_rcit_dt: dtm.date,
        ovrs_rsnv_odno: str,
    ):
        """
        해외주식 예약주문접수취소[v1_해외주식-004]

        해외주식 예약 주문을 취소하는 함수입니다. 미국 주식 예약 주문을 취소할 때 사용됩니다.
        (예약 주문 접수 시 반환된 ODNO를 사용하여 주문을 취소합니다.)

        Args:
            cano (str): 종합계좌번호 (8자리).
            acnt_prdt_cd (str): 계좌상품코드 (2자리).
            rsyn_ord_rctt_dt (str): 해외 주문 접수 일자 (YYYYMMDD 형식).
            ovrs_rsvn_odno (str): 해외 예약 주문 번호 (예약 주문 접수 시 반환된 ODNO).

        Returns:
            dict: 주문 취소에 대한 응답 정보.
                - rt_cd (str): 성공 여부 (0: 성공, 0 이외의 값: 실패).
                - msg_cd (str): 응답 코드.
                - msg1 (str): 응답 메시지.
                - output (dict): 응답 상세.
                    - OVRS_RSVN_ODNO (str): 해외 예약 주문 번호.

        Raises:
            ValueError: 필수 인자가 없거나 잘못된 경우 발생.
        """

        path = "/uapi/overseas-stock/v1/trading/order-resv-ccnl"
        tr_id = "TTTT3017U" if not self.auth.paper_trading else "VTTT3017U"
        tr_cont = ""

        body = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "RSVN_ORD_RCIT_DT": rsyn_ord_rcit_dt.strftime("%Y%m%d"),
            "OVRS_RSVN_ODNO": ovrs_rsnv_odno,
        }

        body, _ = self._tr_request(path, tr_id, tr_cont, body=body, method="POST")

        if body["rt_cd"] != "0":
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        return {
            "rt_cd": body["rt_cd"],
            "msg_cd": body["msg_cd"],
            "msg1": body["msg1"],
            "output": body["output"],
        }

    def order_resv_list(
        self,
        cano: str,
        acnt_prdt_cd: str,
        inqr_strt_dt: dtm.date,
        inqr_end_dt: dtm.date,
        inqr_dvsn_cd: str = "00",
        prdt_type_cd: str = "",
        ovrs_excg_cd: str = "",
        ctx_area_fk200: str = "",
        ctx_area_nk200: str = "",
    ) -> List:
        """
        해외주식 예약 주문을 조회하는 함수입니다. 특정 기간 동안의 예약 주문 내역을 조회할 수 있습니다.

        Args:
            cano (str): 종합계좌번호 (8자리).
            acnt_prdt_cd (str): 계좌상품코드 (2자리).
            inqr_strt_dt (str): 조회 시작 일자 (YYYYMMDD 형식).
            inqr_end_dt (str): 조회 종료 일자 (YYYYMMDD 형식).
            inqr_dvsn_cd (str): 조회 구분 코드 (00: 전체, 01: 일반 해외주식, 02: 미니스탁).
            prdt_type_cd (str): 상품 유형 코드 (조회할 거래소에 따라 다름, 공백 시 전체 조회).
            ovrs_excg_cd (str): 해외 거래소 코드 (예: NASD: 나스닥, NYSE: 뉴욕, AMEX: 아멕스).
            ctx_area_fk200 (str): 연속 조회 검색 조건 (최초 조회 시 공란).
            ctx_area_nk200 (str): 연속 조회 키 (최초 조회 시 공란).

        Returns:
            dict: 조회된 예약 주문 내역.
                - rt_cd (str): 성공 여부 (0: 성공, 0 이외의 값: 실패).
                - msg_cd (str): 응답 코드.
                - msg1 (str): 응답 메시지.
                - ctx_area_fk200 (str): 연속 조회 검색 조건.
                - ctx_area_nk200 (str): 연속 조회 키.
                - output (list): 예약 주문 상세 내역.
                    - cncl_yn (bool): 취소 여부.
                    - rsvn_ord_rcit_dt (dtm.date): 예약 주문 접수 일자.
                    - ovrs_rsvn_odno (str): 해외 예약 주문 번호.
                    - ord_dt (dtm.date): 주문 일자.
                    - sll_buy_dvsn_cd (str): 매도/매수 구분 코드.
                    - sll_buy_dvsn_name (str): 매도/매수 구분 명칭.
                    - ovrs_rsvn_ord_stat_cd (str): 해외 예약 주문 상태 코드.
                    - ovrs_rsvn_ord_stat_cd_name (str): 해외 예약 주문 상태 명칭.
                    - pdno (str): 상품 번호.
                    - prdt_name (str): 상품 명.
                    - ft_ord_qty (int): 주문 수량.
                    - ft_ord_unpr3 (Decimal): 주문 단가.
                    - ft_ccld_qty (int): 체결 수량.
                    - ft_ccld_unpr3 (Decimal): 체결 단가.
                    - nprc_rson_text (str): 미처리 사유 내용.

        Raises:
            ValueError: 필수 인자가 없거나 잘못된 경우 발생.
        """

        path = "/uapi/overseas-stock/v1/trading/order-resv-list"
        tr_id = "TTTT3039R"  # 미국
        tr_cont = ""

        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "INQR_STRT_DT": inqr_strt_dt.strftime("%Y%m%d"),
            "INQR_END_DT": inqr_end_dt.strftime("%Y%m%d"),
            "INQR_DVSN_CD": inqr_dvsn_cd,
            "PRDT_TYPE_CD": prdt_type_cd,
            "OVRS_EXCG_CD": ovrs_excg_cd,
            "CTX_AREA_FK200": ctx_area_fk200,
            "CTX_AREA_NK200": ctx_area_nk200,
        }

        body, _ = self._tr_request(path, tr_id, tr_cont, params=params, method="GET")

        if body["rt_cd"] != "0":
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output = []
        for d in body["output"]:
            copied = d.copy()
            for k in copied.keys():
                if k in ["ft_ord_qty", "ft_ccld_qty"]:
                    if copied.get(k) is not None:
                        copied[k] = int(copied[k])
                if k in ["ft_ord_unpr3", "ft_ccld_unpr3"]:
                    if copied.get(k) is not None:
                        copied[k] = Decimal(copied[k])
                if k in ["cncl_yn"]:
                    copied[k] = copied[k] == "Y"
                if k in ["rsvn_ord_rcit_dt", "ord_dt"]:
                    if copied.get(k) is not None and len(copied[k]) > 0:
                        copied[k] = dtm.datetime.strptime(copied[k], "%Y%m%d").date()

            output.append(copied)

        return {
            "rt_cd": body["rt_cd"],
            "msg_cd": body["msg_cd"],
            "msg1": body["msg1"],
            "output": output,
        }

    def inquire_balance(self,
                        cano: str,
                        acnt_prdt_cd: str,
                        ovrs_excg_cd: str,
                        tr_crcy_cd: str,
                        ctx_area_fk200: str = "",
                        ctx_area_nk200: str = ""):
        '''
        (해외주식주문) 해외주식 잔고조회[v1_해외주식-006]

        | 해외주식 잔고를 조회하는 API 입니다.
        | 실전계좌의 경우, 한 번의 호출에 최대 100건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
        |
        | * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        | https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp
        |
        | * 미니스탁 잔고는 해당 API로 확인이 불가합니다.

        Args:
            cano (str): 계좌번호
            acnt_prdt_cd (str): 계좌상품코드
            ovrs_excg_cd (str): 해외거래소코드
            tr_crcy_cd (str): 통화코드
            ctx_area_fk200 (str): 연속조회검색조건200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_FK200값
            ctx_area_nk200 (str): 연속조회키200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_NK200값

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - ctx_area_fk200: 연속조회검색조건200
            - ctx_area_nk200: 연속조회키200
            - output1: 응답상세1 (list)
                - cano: 계좌번호
                - acnt_prdt_cd: 계좌상품코드
                - prdt_type_cd: 상품유형코드
                - ovrs_pdno: 해외상품번호
                - ovrs_item_name: 해외종목명
                - frcr_evlu_pfls_amt: 외화평가손익금액
                - evlu_pfls_rt: 평가손익율
                - pchs_avg_pric: 매입평균가격
                - ovrs_cblc_qty: 해외잔고수량
                - ord_psbl_qty: 주문가능수량
                - frcr_pchs_amt1: 외화매입금액1
                - ovrs_stck_evlu_amt: 해외주식평가금액
                - now_pric2: 현재가격2
                - tr_crcy_cd: 거래통화코드 - HKD:홍콩달러 CNY:중국위안화 JPY:일본엔화 VND:베트남동
                - ovrs_excg_cd: 해외거래소코드 - NASD:나스닥 NYSE:뉴욕 AMEX:아멕스 SEHK:홍콩 SHAA:중국상해 SZAA:중국심천 TKSE:일본 HASE:하노이거래소 VNSE:호치민거래소
                - loan_type_cd: 대출유형코드 - 00:해당사항없음 01:자기융자일반형 03:자기융자투자형 05:유통융자일반형 06:유통융자투자형 07:자기대주 09:유통대주 11:주식담보대출 12:수익증권담보대출 13:ELS담보대출 14:채권담보대출 15:해외주식담보대출 16:기업신용공여 31:소액자동담보대출 41:매도담보대출 42:환매자금대출 43:매입환매자금대출 44:대여매도담보대출 81:대차거래 82:법인CMA론 91:공모주청약자금대출 92:매입자금 93:미수론서비스 94:대여
                - loan_dt: 대출일자
                - expd_dt: 만기일자
            - output2: 응답상세2
                - frcr_pchs_amt1: 외화매입금액1
                - ovrs_rlzt_pfls_amt: 해외실현손익금액
                - ovrs_tot_pfls: 해외총손익
                - rlzt_erng_rt: 실현수익율
                - tot_evlu_pfls_amt: 총평가손익금액
                - tot_pftrt: 총수익률
                - frcr_buy_amt_smtl1: 외화매수금액합계1
                - ovrs_rlzt_pfls_amt2: 해외실현손익금액2
                - frcr_buy_amt_smtl2: 외화매수금액합계2

        Raises:
            ValueError: API 호출 실패시 발생
        '''

        path = '/uapi/overseas-stock/v1/trading/inquire-balance'
        tr_id = 'VTTS3012R' if self.auth.paper_trading else 'TTTS3012R'
        tr_cont = ''

        params = {
            'CANO': cano,
            'ACNT_PRDT_CD': acnt_prdt_cd,
            'OVRS_EXCG_CD': ovrs_excg_cd,
            'TR_CRCY_CD': tr_crcy_cd,
            'CTX_AREA_FK200': ctx_area_fk200,
            'CTX_AREA_NK200': ctx_area_nk200,
        }

        body, _ = self._tr_request(path, tr_id, tr_cont, params)
        if body['rt_cd'] != '0':
            raise ValueError(f"Error: ({body['msg_cd']}) {body['msg1']}")

        output1 = []
        for el in body['output1']:
            copied = el.copy()
            for k in ['frcr_evlu_pfls_amt', 'evlu_pfls_rt', 'pchs_avg_pric', 'frcr_pchs_amt1', 'ovrs_stck_evlu_amt', 'now_pric2']:
                if copied.get(k) is not None and len(copied[k]) > 0:
                    copied[k] = Decimal(copied[k])

            for k in ['ovrs_cblc_qty', 'ord_psbl_qty']:
                if copied.get(k) is not None and len(copied[k]) > 0:
                    copied[k] = int(copied[k])

            for k in ['loan_dt', 'expd_dt']:
                if copied.get(k) is not None and len(copied[k]) > 0:
                    copied[k] = dtm.datetime.strptime(copied[k], '%Y%m%d').date()

            output1.append(copied)

        output2 = body['output2'].copy()
        for k in output2.keys():
            if output2.get(k) is not None and len(output2[k]):
                output2[k] = Decimal(output2[k])

        result = {
            'rt_cd': body['rt_cd'],
            'msg_cd': body['msg_cd'],
            'msg1': body['msg1'],
            'output1': output1,
            'output2': output2,
            'ctx_area_fk200': body['ctx_area_fk200'],
            'ctx_area_nk200': body['ctx_area_nk200'],
        }

        return result

    def inquire_ccnl(
        self,
        cano: str,
        acnt_prdt_cd: str,
        ord_strt_dt: dtm.date,
        ord_end_dt: dtm.date,
        ovrs_excg_cd: str,
        pdno: str = None,
        sll_buy_dvsn: str = "00",
        ccld_nccs_dvsn: str = "00",
        sort_sqn: str = "DS",
        ctx_area_fk200: str = "",
        ctx_area_nk200: str = "",
        tr_cont: str = "",
    ):
        '''
        (해외주식주문) 해외주식 주문체결내역[v1_해외주식-007]

        | 일정 기간의 해외주식 주문 체결 내역을 확인하는 API입니다.
        | 실전계좌의 경우, 한 번의 호출에 최대 20건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.
        | 모의계좌의 경우, 한 번의 호출에 최대 15건까지 확인 가능하며, 이후의 값은 연속조회를 통해 확인하실 수 있습니다.

        | * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        | https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        | ※ 해외 거래소 운영시간(한국시간 기준)
        | 1) 미국 : 23:30 ~ 06:00 (썸머타임 적용 시 22:30 ~ 05:00)
        | 2) 일본 : (오전) 09:00 ~ 11:30, (오후) 12:30 ~ 15:00
        | 3) 상해 : 10:30 ~ 16:00
        | 4) 홍콩 : (오전) 10:30 ~ 13:00, (오후) 14:00 ~ 17:00

        Args:
            cano (str): 계좌번호
            acnt_prdt_cd (str): 계좌상품코드
            ord_strt_dt (dtm.date): 조회시작일
            ord_end_dt (dtm.date): 조회종료일
            pdno (str): 상품번호. 전종목일경우 '%' 입력. 모의투자계좌의 경우 ""(전체조회)만 가능
            sll_buy_dvsn (str): 매매구분 - "00":전체 "01":매도 "02":매수
            ccld_nccs_dvsn (str): 체결미체결구분 - "00":전체 "01":체결 "02":미체결
            ovrs_excg_cd (str): 해외거래소코드
            sort_sqn (str): 정렬순서 - "DS": 정순, "AS": 역순
            ctx_area_fk200 (str): 연속조회검색조건200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_FK200값
            ctx_area_nk200 (str): 연속조회키200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_NK200값

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - ctx_area_fk200: 연속조회검색조건200
            - ctx_area_nk200: 연속조회키200
            - output: 응답상세 (list)

                - ord_dt: 주문일자
                - ord_gno_brno: 주문채번지점번호
                - odno: 주문번호 - ※ 정정취소주문 시, 해당 값 odno(주문번호) 넣어서 사용
                - orgn_odno: 원주문번호
                - sll_buy_dvsn_cd: 매도매수구분코드 - 01:매도 02:매수
                - sll_buy_dvsn_cd_name: 매도매수구분코드명
                - rvse_cncl_dvsn: 정정취소구분 - 01:정정 02:취소
                - rvse_cncl_dvsn_name: 정정취소구분명
                - pdno: 상품번호
                - prdt_name: 상품명
                - ft_ord_qty: FT주문수량
                - ft_ord_unpr3: FT주문단가3
                - ft_ccld_qty: FT체결수량
                - ft_ccld_unpr3: FT체결단가3
                - ft_ccld_amt3: FT체결금액3
                - nccs_qty: 미체결수량
                - prcs_stat_name: 처리상태명
                - rjct_rson: 거부사유
                - ord_tmd: 주문시각
                - tr_mket_name: 거래시장명
                - tr_natn: 거래국가
                - tr_natn_name: 거래국가명
                - ovrs_excg_cd: 해외거래소코드 - NASD:나스닥 NYSE:뉴욕 AMEX:아멕스 SEHK:홍콩 SHAA:중국상해 SZAA:중국심천 TKSE:일본 HASE:베트남 하노이 VNSE:베트남 호치민
                - tr_crcy_cd: 거래통화코드
                - dmst_ord_dt: 국내주문일자
                - thco_ord_tmd: 당사주문시각
                - loan_type_cd: 대출유형코드
                - mdia_dvsn_name: 매체구분명
                - loan_dt: 대출일자
                - rjct_rson_name: 거부사유명
                - usa_amk_exts_rqst_yn: 미국애프터마켓연장신청여부

        Raise:
            ValueError: API 호출 실패시 발생
        '''

        assert sll_buy_dvsn in ['00', '01', '02']
        assert ccld_nccs_dvsn in ['00', '01', '02']
        assert sort_sqn in ['DS', 'AS']

        if pdno is None:
            pdno = '' if self.auth.paper_trading else '%'

        path = '/uapi/overseas-stock/v1/trading/inquire-ccnl'
        tr_id = "VTTS3035R" if self.auth.paper_trading else "TTTS3035R"
        params = {
            'CANO': cano,
            'ACNT_PRDT_CD': acnt_prdt_cd,
            'PDNO': pdno,
            'ORD_STRT_DT': ord_strt_dt.strftime('%Y%m%d'),
            'ORD_END_DT': ord_end_dt.strftime('%Y%m%d'),
            'SLL_BUY_DVSN': sll_buy_dvsn,
            'CCLD_NCCS_DVSN': ccld_nccs_dvsn,
            'OVRS_EXCG_CD': ovrs_excg_cd,
            'SORT_SQN': sort_sqn,
            'ORD_DT': '',
            'ORD_GNO_BRNO': '',
            'ODNO': '',
            'CTX_AREA_FK200': ctx_area_fk200,
            'CTX_AREA_NK200': ctx_area_nk200,
        }

        res_body, res_header = self._tr_request(path, tr_id, tr_cont, params)
        if res_body['rt_cd'] != '0':
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = []
        for el in res_body['output']:
            copied = el.copy()
            for k in ["ord_dt", "loan_dt", "dmst_ord_dt"]:
                if copied.get(k) is not None and len(copied[k]) > 0:
                    copied[k] = dtm.datetime.strptime(copied[k], '%Y%m%d').date()
            for k in ['ft_ord_qty', 'ft_ccld_qty', 'nccs_qty']:
                if copied.get(k) is not None:
                    copied[k] = int(copied[k])
            for k in ['ft_ord_unpr3', 'ft_ccld_unpr3', 'ft_ccld_amt3']:
                if copied.get(k) is not None:
                    copied[k] = Decimal(copied[k])

            copied['ord_tmd'] = dtm.datetime.strptime(copied['ord_tmd'], '%H%M%S').time()

            output.append(copied)

        result = {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "tr_cont": res_header["tr_cont"],
            "ctx_area_fk200": res_body["ctx_area_fk200"],
            "ctx_area_nk200": res_body["ctx_area_nk200"],
            "output": output,
        }

        return result

    def inquire_psamount(self,
                         cano: str,
                         acnt_prdt_cd: str,
                         ovrs_excg_cd: str,
                         ovrs_ord_unpr: Decimal,
                         item_cd: str):
        '''
        (해외주식주문) 해외주식 매수가능금액조회[v1_해외주식-014]

        | 해외주식 매수가능금액조회 API입니다.
        | ※ 모의투자는 사용 불가합니다.

        | * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        | https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        Args:
            cano (str): 계좌번호
            acnt_prdt_cd (str): 계좌상품코드
            ovrs_excg_cd (str): 해외거래소코드 - NASD:나스닥 NYSE:뉴욕 AMEX:아멕스 SEHK:홍콩 SHAA:중국상해 SZAA:중국심천 TKSE:일본 HASE:하노이거래소 VNSE:호치민거래소
            ovrs_ord_unpr (Decimal): 해외주문단가
            item_cd (str): 종목코드

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - output: 응답상세 (dict)
                - tr_crcy_cd: 거래통화코드
                - ord_psbl_frcr_amt: 주문가능외화금액
                - sll_ruse_psbl_amt: 매도재사용가능금액 - 가능금액 산정 시 사용
                - ovrs_ord_psbl_amt: 해외주문가능금액 - 한국투자 앱 해외주식 주문화면내 "외화" 인경우 주문가능금액
                - max_ord_psbl_qty: 최대주문가능수량 - 한국투자 앱 해외주식 주문화면내 "외화" 인경우 주문가능수량
                - 매수 시 수량단위 절사해서 사용 - 예 : (100주단위) 545 주 -> 500 주 / (10주단위) 545 주 -> 540 주
                - echm_af_ord_psbl_amt: 환전이후주문가능금액
                - echm_af_ord_psbl_qty: 환전이후주문가능수량
                - ord_psbl_qty: 주문가능수량
                - exrt: 환율
                - frcr_ord_psbl_amt1: 외화주문가능금액1 - 한국투자 앱 해외주식 주문화면내 "통합" 인경우 주문가능금액
                - ovrs_max_ord_psbl_qty: 해외최대주문가능수량 - 한국투자 앱 해외주식 주문화면내 "통합" 인경우 주문가능수량. 매수 시 수량단위 절사해서 사용. 예: (100주단위) 545주 -> 500주 / (10주단위) 545주 -> 540주

        Raises:
            ValueError: API 호출 실패시 발생
        '''

        assert self.auth.paper_trading is False, "모의투자에서는 사용할 수 없는 API입니다."

        url_path = '/uapi/overseas-stock/v1/trading/inquire-psamount'
        tr_id = 'TTTS3007R'
        tr_cont = ''
        params = {
            'CANO': cano,
            'ACNT_PRDT_CD': acnt_prdt_cd,
            'OVRS_EXCG_CD': ovrs_excg_cd,
            'OVRS_ORD_UNPR': str(ovrs_ord_unpr),
            'ITEM_CD': item_cd,
        }

        res_body, _ = self._tr_request(url_path, tr_id, tr_cont, params)
        if res_body['rt_cd'] != '0':
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output = res_body['output'].copy()

        for k in ['ord_psbl_frcr_amt', 'sll_ruse_psbl_amt', 'ovrs_ord_psbl_amt', 'echm_af_ord_psbl_amt', 'exrt', 'frcr_ord_psbl_amt1']:
            if output.get(k) is not None and len(output.get(k)) > 0:
                output[k] = Decimal(output[k])

        for k in ['max_ord_psbl_qty', 'echm_af_ord_psbl_qty', 'ord_psbl_qty', 'ovrs_max_ord_psbl_qty']:
            if output.get(k) is not None and len(output.get(k)) > 0:
                output[k] = int(output[k])

        result = {
            'rt_cd': res_body['rt_cd'],
            'msg_cd': res_body['msg_cd'],
            'msg1': res_body['msg1'],
            'output': res_body['output'],
        }

        return result

    def inquire_period_profit(self,
                              cano: str,
                              acnt_prdt_cd: str,
                              inqr_strt_dt: dtm.date,
                              inqr_end_dt: dtm.date,
                              wcrc_frcr_dvsn_cd: str,
                              ovrs_excg_cd: str = "",
                              crcy_cd: str = "",
                              pdno: str = "",
                              ctx_area_fk200: str = "",
                              ctx_area_nk200: str = ""):
        '''
        (해외주식주문) 해외주식 기간손익[v1_해외주식-032]

        해외주식 기간손익 API입니다.

        | * 해외주식 서비스 신청 후 이용 가능합니다. (아래 링크 3번 해외증권 거래신청 참고)
        | https://securities.koreainvestment.com/main/bond/research/_static/TF03ca010001.jsp

        Args:
            cano (str): 계좌번호
            acnt_prdt_cd (str): 계좌상품코드
            inqr_strt_dt (dtm.date): 조회시작일
            inqr_end_dt (dtm.date): 조회종료일
            wcrc_frcr_dvsn_cd (str): 외화통화구분코드 - 01:원화 02:외화
            ovrs_excg_cd (str): 해외거래소코드 - 공란:전체 NASD:미국 SEHK:홍콩 SHAA:중국 TKSE:일본 HASE:베트남
            crcy_cd (str): 통화코드 - 공란:전체 USD:미국달러 HKD:홍콩달러 CNY:중국위안화 JPY:일본엔화 VND:베트남동
            pdno (str): 상품번호 - 공란:전체
            ctx_area_fk200 (str): 연속조회검색조건200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_FK200값
            ctx_area_nk200 (str): 연속조회키200 - 초기조회 시 공백, 다음페이지 조회시 이전 조회 결과의 CTX_AREA_NK200값

        Returns:
            dict:

            - rt_cd: 응답코드
            - msg_cd: 응답메시지코드
            - msg1: 응답메시지1
            - ctx_area_fk200: 연속조회검색조건200
            - ctx_area_nk200: 연속조회키200
            - tr_cont: 연속조회가능여부
            - output1: 응답상세1 (list)
                - trad_day: 매매일
                - ovrs_pdno: 해외상품번호
                - ovrs_item_name: 해외종목명
                - slcl_qty: 매도청산수량
                - pchs_avg_pric: 매입평균가격
                - frcr_pchs_amt1: 외화매입금액1
                - avg_sll_unpr: 평균매도단가
                - frcr_sll_amt_smtl1: 외화매도금액합계1
                - stck_sll_tlex: 주식매도제비용
                - ovrs_rlzt_pfls_amt: 해외실현손익금액
                - pftrt: 수익률
                - exrt: 환율
                - ovrs_excg_cd: 해외거래소코드
                - frst_bltn_exrt: 최초고시환율
            - output2: 응답상세 (dict)
                - stck_sll_amt_smtl: 주식매도금액합계 - WCRC_FRCR_DVSN_CD(원화외화구분코드)가 01(외화)이고 OVRS_EXCG_CD(해외거래소코드)가 공란(전체)인 경우 출력값 무시
                - stck_buy_amt_smtl: 주식매수금액합계 - WCRC_FRCR_DVSN_CD(원화외화구분코드)가 01(외화)이고 OVRS_EXCG_CD(해외거래소코드)가 공란(전체)인 경우 출력값 무시
                - smtl_fee1: 합계수수료1 - WCRC_FRCR_DVSN_CD(원화외화구분코드)가 01(외화)이고 OVRS_EXCG_CD(해외거래소코드)가 공란(전체)인 경우 출력값 무시
                - excc_dfrm_amt: 정산지급금액 - WCRC_FRCR_DVSN_CD(원화외화구분코드)가 01(외화)이고 OVRS_EXCG_CD(해외거래소코드)가 공란(전체)인 경우 출력값 무시
                - ovrs_rlzt_pfls_tot_amt: 해외실현손익총금액 - WCRC_FRCR_DVSN_CD(원화외화구분코드)가 01(외화)이고 OVRS_EXCG_CD(해외거래소코드)가 공란(전체)인 경우 출력값 무시
                - tot_pftrt: 총수익률
                - bass_dt: 기준일자
                - exrt: 환율

        Raises:
            ValueError - API 호출 실패시 발생
        '''

        assert self.auth.paper_trading is False, "모의투자에서는 사용할 수 없는 API입니다."
        assert wcrc_frcr_dvsn_cd in ["01", "02"], "원화외화구분코드는 01(원화) 또는 02(외화)만 가능합니다."

        url_path = "/uapi/overseas-stock/v1/trading/inquire-period-profit"
        tr_id = "TTTS3039R"
        tr_cont = ""
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "OVRS_EXCG_CD": ovrs_excg_cd,
            "CRCY_CD": crcy_cd,
            "PDNO": pdno,
            "INQR_STRT_DT": inqr_strt_dt.strftime("%Y%m%d"),
            "INQR_END_DT": inqr_end_dt.strftime("%Y%m%d"),
            "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
            "NATN_CD": "",
            "CTX_AREA_FK200": ctx_area_fk200,
            "CTX_AREA_NK200": ctx_area_nk200,
        }

        res_body, res_header = self._tr_request(url_path, tr_id, tr_cont, params)
        if res_body['rt_cd'] != '0':
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = []
        for el in res_body['output1']:
            copied = el.copy()
            copied['trad_day'] = dtm.datetime.strptime(copied['trad_day'], '%Y%m%d').date()
            copied['slcl_qty'] = int(copied['slcl_qty'])
            for k in ['pchs_avg_pric', 'frcr_pchs_amt1', 'avg_sll_unpr', 'frcr_sll_amt_smtl1', 'stck_sll_tlex', 'ovrs_rlzt_pfls_amt', 'pftrt', 'exrt', 'frst_bltn_exrt']:
                if copied.get(k) is not None and len(copied[k]) > 0:
                    copied[k] = Decimal(copied[k])

            output1.append(copied)

        output2 = res_body['output2'].copy()
        for k in ['stck_sll_amt_smtl', 'stck_buy_amt_smtl', 'smtl_fee1', 'excc_dfrm_amt', 'ovrs_rlzt_pfls_tot_amt', 'tot_pftrt', 'exrt']:
            if output2.get(k) is not None and len(output2[k]) > 0:
                output2[k] = Decimal(output2[k])

        if output2.get('base_dt') is not None and len(output2['base_dt']) > 0:
            output2['base_dt'] = dtm.datetime.strptime(output2['base_dt'], '%Y%m%d').date()

        result = {
            'rt_cd': res_body['rt_cd'],
            'msg_cd': res_body['msg_cd'],
            'msg1': res_body['msg1'],
            'tr_cont': res_header['tr_cont'],
            'output1': output1,
            'output2': output2,
            'ctx_area_fk200': res_body.get('ctx_area_fk200', ''),
            'ctx_area_nk200': res_body.get('ctx_area_nk200', ''),
        }

        return result

    def get_foreign_margin(
        self,
        cano: str,
        acnt_prdt_cd: str,
    ) -> Dict:
        """(해외증거금 통화별조회) 해외증거금 통화별 조회 [해외주식-035]

        Args:
            cano (str): 종합계좌번호 (8자리)
            acnt_prdt_cd (str): 계좌상품코드 (2자리)

        Returns:
            dict: 해외증거금 통화별 조회 정보
                - rt_cd: 성공/실패 여부
                - msg_cd: 응답 코드
                - msg1: 응답 메시지
                - output: 응답 상세 (Object Array)
                    - natn_name: 국가명
                    - crcy_cd: 통화코드
                    - frcr_dncl_amt1: 외화예수금액
                    - ustl_buy_amt: 미결제 매수금액
                    - ustl_sll_amt: 미결제 매도금액
                    - frcr_rcvb_amt: 외화미수금액
                    - frcr_mgn_amt: 외화증거금액
                    - frcr_gnrl_ord_psbl_amt: 외화 일반주문 가능금액
                    - frcr_ord_psbl_amt1: 외화 주문 가능금액
                    - itgr_ord_psbl_amt: 통합 주문 가능금액
                    - bass_exrt: 기준환율

        Raises:
            ValueError: API 호출 실패 시 발생
        """
        url_path = "/uapi/overseas-stock/v1/trading/foreign-margin"
        tr_id = "TTTC2101R"
        tr_cont = ""
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
        }

        res_body, _ = self._tr_request(url_path, tr_id, tr_cont, params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        return {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output": res_body["output"],
        }

    def inquire_paymt_stdr_balance(
        self,
        cano: str,
        acnt_prdt_cd: str,
        bass_dt: dtm.date,
        wcrc_frcr_dvsn_cd: str,
        inqr_dvsn_cd: str,
    ) -> Dict:
        """(해외주식 결제기준잔고) 해외주식 결제기준잔고 조회 [해외주식-064]

        Args:
            cano (str): 종합계좌번호 (계좌번호 체계 8-2의 앞 8자리)
            acnt_prdt_cd (str): 계좌상품코드 (계좌번호 체계 8-2의 뒤 2자리)
            bass_dt (str): 기준일자 (YYYYMMDD 형식)
            wcrc_frcr_dvsn_cd (str): 원화/외화 구분 코드 (01: 원화기준, 02: 외화기준)
            inqr_dvsn_cd (str): 조회 구분 코드 (00: 전체, 01: 일반, 02: 미니스탁)

        Returns:
            dict: 해외주식 결제기준잔고 조회 정보
                - rt_cd: 성공/실패 여부
                - msg_cd: 응답 코드
                - msg1: 응답 메시지
                - output1: 응답 상세 (Object Array)
                    - pdno: 상품번호
                    - prdt_name: 상품명
                    - cblc_qty13: 잔고수량
                    - ord_psbl_qty1: 주문가능수량
                    - avg_unpr3: 평균단가
                    - ovrs_now_pric1: 해외 현재가격
                    - frcr_pchs_amt: 외화 매입금액
                    - frcr_evlu_amt2: 외화 평가금액
                    - evlu_pfls_amt2: 평가 손익금액
                    - bass_exrt: 기준환율
                    - oprt_dtl_dtime: 조작 상세일시
                    - buy_crcy_cd: 매수 통화코드
                    - thdt_sll_ccld_qty1: 당일 매도 체결수량
                    - thdt_buy_ccld_qty1: 당일 매수 체결수량
                    - evlu_pfls_rt1: 평가손익율
                    - tr_mket_name: 거래시장명
                    - natn_kor_name: 국가 한글명
                    - std_pdno: 표준 상품번호
                    - mgge_qty: 담보수량
                    - loan_rmnd: 대출잔액
                    - prdt_type_cd: 상품유형코드
                    - ovrs_excg_cd: 해외거래소 코드
                    - scts_dvsn_name: 유가증권 구분명
                - output2: 응답 상세 (Object Array)
                    - crcy_cd: 통화코드
                    - crcy_cd_name: 통화코드명
                    - frcr_dncl_amt_2: 외화 예수금액
                    - frst_bltn_exrt: 최초 고시환율
                    - frcr_evlu_amt2: 외화 평가금액
                - output3: 응답 상세 (Object)
                    - pchs_amt_smtl_amt: 매입금액 합계
                    - tot_evlu_pfls_amt: 총 평가 손익금액
                    - evlu_erng_rt1: 평가 수익율
                    - tot_dncl_amt: 총 예수금액
                    - wcrc_evlu_amt_smtl: 원화 평가금액 합계
                    - tot_asst_amt2: 총 자산금액
                    - frcr_cblc_wcrc_evlu_amt_smtl: 외화 잔고 원화 평가금액 합계
                    - tot_loan_amt: 총 대출금액

        Raises:
            ValueError: API 호출 실패 시 발생
        """

        assert wcrc_frcr_dvsn_cd in ["01", "02"], "원화외화구분코드는 01(원화) 또는 02(외화)만 가능합니다."
        assert inqr_dvsn_cd in ["00", "01", "02"], "조회구분코드는 00(전체), 01(일반), 02(미니스탁)만 가능합니다."

        url_path = "/uapi/overseas-stock/v1/trading/inquire-paymt-stdr-balance"
        tr_id = "CTRP6010R"
        tr_cont = ""
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": acnt_prdt_cd,
            "BASS_DT": bass_dt.strftime("%Y%m%d"),
            "WCRC_FRCR_DVSN_CD": wcrc_frcr_dvsn_cd,
            "INQR_DVSN_CD": inqr_dvsn_cd,
        }

        res_body, _ = self._tr_request(url_path, tr_id, tr_cont, params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        return {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output1": res_body["output1"],
            "output2": res_body["output2"],
            "output3": res_body["output3"],
        }

    def inquire_asking_price(
        self,
        excd: str,
        symb: str,
    ):
        """
        해외주식의 현재가 10호가 정보를 조회하는 API입니다. 미국 주식의 경우 실시간으로 10호가까지 무료로 제공됩니다.
        다른 아시아 국가의 경우 지연 시세가 제공되며, 유료로 10호가까지 조회 가능합니다.

        Args:
            excd (str): 거래소 코드 (예: NYS: 뉴욕, NAS: 나스닥, AMS: 아멕스 등).
            symb (str): 종목 코드 (예: TSLA).

        Returns:
            dict: 조회된 10호가 정보.
                - output1:
                    - rsym (str): 실시간 조회 종목 코드.
                    - zdiv (str): 소수점 자리수.
                    - curr (str): 통화 코드.
                    - base (Decimal): 전일 종가.
                    - open (Decimal): 시가.
                    - high (Decimal): 고가.
                    - low (Decimal): 저가.
                    - last (Decimal): 현재가.
                    - dymd (str): 호가 일자.
                    - dhms (str): 호가 시간.
                    - bvol (int): 매수 호가 총 잔량.
                    - avol (int): 매도 호가 총 잔량.
                - output2: 각 호가의 가격 및 잔량 정보 (1호가부터 10호가까지).
                    - pbid1~10 (Decimal): 매수 호가 가격 (1~10).
                    - pask1~10 (Decimal): 매도 호가 가격 (1~10).
                    - vbid1~10 (int): 매수 호가 잔량 (1~10).
                    - vask1~10 (int): 매도 호가 잔량 (1~10).

        Raises:
            ValueError: 필수 인자가 없거나 잘못된 경우 발생.
        """

        url_path = "/uapi/overseas-price/v1/quotations/inquire-asking-price"
        tr_id = "HHDFS76200100"
        tr_cont = ""
        params = {
            "AUTH": "",
            "EXCD": excd,
            "SYMB": symb,
        }

        res_body, _ = self._tr_request(url_path, tr_id, tr_cont, params)
        if res_body["rt_cd"] != "0":
            raise ValueError(f"Error: ({res_body['msg_cd']}) {res_body['msg1']}")

        output1 = res_body["output1"]
        for k in output1.keys():
            if k in ["base", "open", "high", "low", "last"]:
                output1[k] = Decimal(output1[k])
            if k in ["bvol", "avol"]:
                output1[k] = int(output1[k])

        output2 = res_body["output2"]
        for k in output2.keys():
            if k[0] == "p":
                output2[k] = Decimal(output2[k])
            if k[0] == "v":
                output2[k] = int(output2[k])

        return {
            "rt_cd": res_body["rt_cd"],
            "msg_cd": res_body["msg_cd"],
            "msg1": res_body["msg1"],
            "output1": res_body["output1"],
            "output2": res_body["output2"],
        }
