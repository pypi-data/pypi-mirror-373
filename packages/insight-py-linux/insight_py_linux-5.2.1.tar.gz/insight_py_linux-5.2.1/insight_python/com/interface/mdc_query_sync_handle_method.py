import pandas as pd
import json
import re

from .mdc_query_sync_mapping_table import MappingTable
from .. import data_handle


# 分页合并数据
def paging_data_merge(data_merge, query_type, params):
    try:
        total_count = int(re.search('"TotalCount\\\\":(\d+)', data_merge[0]).group(1))

        page_num = len(data_merge)
        if total_count > page_num:

            paging_time = total_count // page_num
            page_max = 100000 // page_num

            if paging_time >= page_max:
                paging_time = page_max - 1

            remainder_num = total_count % page_num
            if remainder_num == 0:
                paging_time = paging_time - 1

            params['ROW_NUM'] = page_num
            start_row = 0
            for turn_num in range(paging_time):
                start_row += page_num
                params['START_ROW'] = str(start_row)
                page_data = data_handle.get_interface().queryfininfosynchronous(query_type, params)
                data_merge.extend(page_data)

            return data_merge
        else:
            return data_merge

    except Exception as e:

        return data_merge


# 新闻资讯分页合并数据
def paging_news_data_merge(data_merge, query_type, params):
    # "PAGE_SIZE": "50", "PAGE_NUM": "3"
    try:
        total_count = int(re.search('"TotalCount\\\\":(\d+)', data_merge[0]).group(1))

        page_size = len(data_merge)
        if total_count > page_size:

            page_time = total_count // page_size
            remainder_num = total_count % page_size

            if remainder_num != 0:
                page_time = page_time + 1

            page_max = 100000 // page_size
            if page_time > page_max:
                page_time = page_max

            params['PAGE_SIZE'] = page_size
            for turn_num in range(2, page_time+1):
                params['PAGE_NUM'] = str(turn_num)
                page_data = data_handle.get_interface().queryfininfosynchronous(query_type, params)
                data_merge.extend(page_data)

            return data_merge
        else:
            return data_merge

    except Exception as e:

        return data_merge


# 将返回数据转成data_frame类型
def query_to_dataframe(result, result_type=True):
    '''
    :param result:query响应结果
    :param result_type: True直接返回转置后的dateframe，False返回数据列表方便二次处理
    '''

    # 新建空列表存储所有数据
    result_list = []
    for response in iter(result):
        try:
            response_dict = json.loads(response)
        except:
            continue
        try:
            # 适用资讯
            content = json.loads(response_dict['resultData']["stringContent"])
            if content:
                result_list.append(content)
        except:
            # 适用自身接口数据
            content = response_dict['resultData']['stringContent']
            content = content.replace('"{', '{')
            content = content.replace('}"', '}')
            try:
                list_content = eval(content)
            except:
                # 适配筹码分布
                content = content.replace('false', 'False')
                content = content.replace('true', 'True')
                list_content = eval(content)
            result_list.extend(list_content)

    # 将列表字段转换成dataframe，[{}, {}, {}]->dataframe
    if result_type:
        df = pd.json_normalize(result_list)
        return df
    else:
        return result_list


# 重命名字段名(新方法)
def column_renaming(original_data, api_name):
    api_name = api_name + '_map'
    new_column_map = MappingTable.perform_operation(api_name)
    new_column_map = dict((k.lower(), v) for k, v in new_column_map.items())
    original_column_map = original_data.columns.tolist()

    new_column_dict = {}
    for original_column in original_column_map:
        if original_column.lower() in new_column_map:
            new_column_dict[original_column] = new_column_map[original_column.lower()]

    new_data = original_data.rename(columns=new_column_dict)
    return new_data


# 字符串转蛇形
def convert_to_snake_case(input_string):

    result = input_string[0].lower()

    for char in input_string[1:]:
        if char.isupper():
            result += '_' + char.lower()
        else:
            result += char

    return result


# 处理时间，修改列名，修改pandas字段名
def change_column_name(data):
    new_name_map = {
        # K线
        'htscsecurityid': 'htsc_code', 'openpx': 'open', 'closepx': 'close', 'highpx': 'high', 'lowpx': 'low',
        'totalvolumetrade': 'volume', 'totalvaluetrade': 'value', 'openinterest': 'open_interest',
        'settleprice': 'settle', 'numtrades': 'num_trades',
        # 衍生指标
        'nvalue': 'n_value', 'pvalue': 'p_value', 'nhighpx': 'n_high', 'nlowpx': 'n_low',
        # 成交分价
        'securityidsource': 'exchange', 'symbol': 'name',
        'tradeprice': 'trade_price', 'totalqty': 'total_qty', 'buyqty': 'buy_qty', 'sellqty': 'sell_qty',
        'totalnumbers': 'total_num', 'buynumbers': 'buy_num', 'sellnumbers': 'sell_num',
        'volumepernumber': 'volume_per_num',
        # 筹码分布
        'lastpx': 'last', 'preclosepx': 'prev_close', 'alistedtotalshare': 'a_listed_share',
        'tradablesharetotalnumber': 'listed_share', 'restrictedsharetotalnumber': 'restricted_share',
        'tradablemcst': 'avg_cost', 'largeshareholdersmcst': 'large_shareholders_avg_cost',
        'tradablemaxcostofpositions': 'max_cost', 'tradablemincostofpositions': 'min_cost',
        'tradableprofitpercent': 'winner_rate', 'tradablechipdispersionpercent': 'diversity',
        'tradablepreprofitpercent': 'pre_winner_rate', 'restrictedmcst': 'restricted_avg_cost',
        'restrictedmaxcostofpositions': 'restricted_max_cost', 'restrictedmincostofpositions': 'restricted_min_cost',
        'largeshareholderssharetotalnumber': 'large_shareholders_total_share',
        'largeshareholderssharepercent': 'large_shareholders_total_share_pct',
        # 资金流向
        'superlarge.outflowvalue': 'super_large_outflow_value',
        'superlarge.outflowqty': 'super_large_outflow_qty', 'superlarge.inflowvalue': 'super_large_inflow_value',
        'superlarge.inflowqty': 'super_large_inflow_qty', 'large.outflowvalue': 'large_outflow_value',
        'large.outflowqty': 'large_outflow_qty', 'large.inflowvalue': 'large_inflow_value',
        'large.inflowqty': 'large_inflow_qty', 'medium.outflowvalue': 'medium_outflow_value',
        'medium.outflowqty': 'medium_outflow_qty', 'medium.inflowvalue': 'medium_inflow_value',
        'medium.inflowqty': 'medium_inflow_qty', 'small.outflowvalue': 'small_outflow_value',
        'small.outflowqty': 'small_outflow_qty', 'small.inflowvalue': 'small_inflow_value',
        'small.inflowqty': 'small_inflow_qty', 'main.outflowvalue': 'main_outflow_value',
        'main.outflowqty': 'main_outflow_qty', 'main.inflowvalue': 'main_inflow_value',
        'main.inflowqty': 'main_inflow_qty',
        # 涨跌分析
        'upsdownscount.ups': 'ups_downs_count_ups',
        'upsdownscount.downs': 'ups_downs_count_downs', 'upsdownscount.equals': 'ups_downs_count_equals',
        'upsdownscount.preups': 'ups_downs_count_pre_ups', 'upsdownscount.predowns': 'ups_downs_count_pre_downs',
        'upsdownscount.preequals': 'ups_downs_count_pre_equals',
        'upsdownscount.upspercent': 'ups_downs_count_ups_percent',
        'upsdownscount.preupspercent': 'ups_downs_count_pre_ups_percent',
        'upsdownslimitcount.noreachedlimitpx': 'ups_downs_limit_count_no_reached_limit_px',
        'upsdownslimitcount.uplimits': 'ups_downs_limit_count_up_limits',
        'upsdownslimitcount.downlimits': 'ups_downs_limit_count_down_limits',
        'upsdownslimitcount.prenoreachedlimitpx': 'ups_downs_limit_count_pre_no_reached_limit_px',
        'upsdownslimitcount.preuplimits': 'ups_downs_limit_count_pre_up_limits',
        'upsdownslimitcount.predownlimits': 'ups_downs_limit_count_pre_down_limits',
        'upsdownslimitcount.preuplimitsaveragechangepercent': 'ups_downs_limit_count_pre_up_limits_average_change_percent',
        'upsdownslimitcount.uplimitspercent': 'ups_downs_limit_count_up_limits_percent',
        # 债券基础信息
        'secuabbr': 'name', 'secucategorycodeii': 'secu_category_code', 'idsource': 'exchange',
        'secucategory': 'category',
        'listingdate': 'listing_date', 'delistingdate': 'delisting_date', 'listingstate': 'listing_state',
        'currencycode': 'currency_code', 'bondmaturity': 'bond_maturity', 'issuestartdate': 'issue_start_date',
        'accrueddate': 'accrued_date', 'enddate': 'end_date', 'issuesize': 'issue_size',
        'bondformcode': 'bond_formcode', 'bondform': 'bond_form', 'interestmethod': 'interest_method',
        'paymentmethod': 'payment_method', 'paymentfrequency': 'payment_frequency', 'couponrate': 'coupon_rate',
        'refspread': 'ref_spread', 'refrate': 'ref_rate', 'redemptiondate': 'redemption_date',
        'interestformula': 'interest_formula', 'interestratefloor': 'interest_rate_floor', 'parval': 'par_value',
        'issueprice': 'issue_price', 'convertcode': 'convert_code', 'bondrating': 'bond_rating',
        'sramanadate': 'interest_stop_date', 'bondtypename': 'bond_type_name', 'calldate': 'call_date',
        'callprice': 'call_price', 'puttdate': 'putt_date', 'puttprice': 'putt_price', 'mtn': 'mtn',
        'delistdate': 'delist_date', 'yearpaymentdate': 'year_payment_date', 'interestratedesc': 'interest_rate_desc',
        'issuermain': 'issuer_main', 'compensationrate': 'compensation_rate',
        'figinterestmethod': 'fig_interest_method', 'expanyield': 'expan_yield', 'bondtype': 'bond_type',
        'issuemode': 'issue_mode', 'issuetype': 'issue_type', 'categorycodei': 'category_code_i',
        'categorynamei': 'category_name_i', 'categorycodeii': 'category_code_ii', 'categorynameii': 'category_name_ii',
        'interestrate': 'interest_rate', 'interestmethoddesc': 'interest_method_desc',
        'remainmaturity': 'remain_maturity', 'expectenddate': 'expect_end_date',
        # 行业分类1
        'induname': 'industry_name', 'inducode': 'industry_code', 'finducode': 'l1_code',
        'finduname': 'l1_name', 'sinducode': 'l2_code',
        'sinduname': 'l2_name', 'tinducode': 'l3_code', 'tinduname': 'l3_name',
        # 新股上市
        'raisenetfund': 'raise_net_fund', 'raisefund': 'raise_fund', 'issueshareonplan': 'issue_share_online_plan',
        'issueshare': 'issue_share', 'totalsharebissue': 'total_share_before_issue',
        'epsbissue': 'eps_before_issue', 'epsaissue': 'eps_after_issue', 'bpsbissue': 'bps_before_issue',
        'bpsaissue': 'bps_after_issue', 'pebissue': 'pe_before_issue', 'peaissue': 'pe_after_issue',
        'pbissue': 'pb_issue', 'valpe': 'val_pe', 'bookstartdateon': 'book_start_date_online',
        'bookenddateon': 'book_end_date_online', 'issueshareon': 'issue_share_online',
        'capplyshare': 'ceiling_apply_share', 'fapplyshare': 'floor_apply_share',
        'allotrateon': 'allot_rate_online',
        # 日行情接口
        'adjustclosingprice': 'backward_adjusted_closing_price', 'avgprice': 'avg_price',
        'avgvolpd': 'avg_vol_per_deal',
        'avgvapd': 'avg_value_per_deal',
        # 市值数据
        'aadjustclosingprice': 'backward_adjusted_closing_price',
        'badjustclosingprice': 'forward_adjusted_closing_price',
        # 证券市场行情
        'tradingday': 'trading_day', 'wavgnetprice': 'w_avg_net_price', 'wavgai': 'w_avg_ai',
        'netprevclosingprice': 'net_prev_closing_price', 'netprevavgclosingprice': 'net_prev_avg_closing_price',
        'netopeningprice': 'net_opening_price', 'nethighestprice': 'net_highest_price',
        'netlowestprice': 'net_lowest_price', 'netclosingprice': 'net_closing_price',
        'netavgclosingprice': 'net_avg_closing_price', 'netdaychangerate': 'net_day_change_rate',
        'netamplitude': 'net_amplitude', 'accruedinterest': 'accrued_interest',
        'fullprevclosingprice': 'full_prev_closing_price', 'fullprevavgclosingprice': 'full_prev_avg_closing_price',
        'fullopeningprice': 'full_opening_price', 'fullhighestprice': 'full_highest_price',
        'fulllowestprice': 'full_lowest_price', 'fullclosingprice': 'full_closing_price',
        'fullavgclosingprice': 'full_avg_closing_price', 'fulldaychangerate': 'full_day_change_rate',
        'fullamplitude': 'full_amplitude', 'principalval': 'principal_val', 'parvalvol': 'par_val_vol',
        'turnoverdeals': 'turnover_deals', 'turnoverrate': 'turnover_rate', 'yeartomaturity': 'year_to_maturity',
        'duration': 'duration', 'modiduration': 'modified_duration', 'convexity': 'convexity',
        'yieldtomaturity': 'yield_to_maturity', 'returnofinterest': 'return_of_interest',
        'returnofprice': 'return_of_price', 'totalreturn': 'total_return', 'openingyield': 'opening_yield',
        'highestyield': 'highest_yield', 'lowestyield': 'lowest_yield', 'avgclosingyield': 'avg_closing_yield',
        # 债券回购
        'lastcloserate': 'last_close_rate', 'openerate': 'open_rate', 'closerate': 'close_rate',
        'highestrate': 'highest_rate', 'lowestrate': 'lowest_rate', 'turnovervol': 'volume',
        'turnoverval': 'value', 'avgturnovervol': 'avg_turnover_vol', 'avgturnoverval': 'avg_turnover_val',
        'amplitude': 'amplitude', 'lavgrate': 'last_avg_rate',
        'avgrate': 'avg_rate', 'daychange': 'day_change', 'daychangerate': 'day_change_rate',
        # 可转债发行列表
        'exchangecode': 'exchange_code', 'bndtype': 'bnd_type', 'ratingcode': 'rating_code', 'capplyvol':
            'capply_online', 'allotratesh': 'allot_rate_sh', 'applyprice': 'apply_price', 'applycode': 'apply_code',
        'convertabbr': 'convert_abbr', 'conversionprice': 'conversion_price', 'issuevalplan': 'issue_val_plan',
        'preferredplacingcode': 'preferred_placing_code', 'applyabbr': 'apply_abbr',
        'preferredplacingabbr': 'preferred_placing_abbr', 'succresultnoticedate': 'succ_result_notice_date',
        'exchangcodedetail': 'exchange_code_detail', 'purchaseloweron': 'purchase_lower_online',
        # 可转债赎回信息
        'type': 'type', 'reason': 'reason', 'redemptiontype': 'redemption_type', 'begindate': 'begin_date',
        'execprice': 'exer_price', 'isincludeinterest': 'is_include_interest', 'currsqut': 'curr_qut',
        'currsamt': 'curr_amt', 'paymentdate': 'payment_date', 'fundreceivedate': 'fund_receive_date',
        'registerdate': 'register_date', 'announcementdate': 'announcement_date', 'pubdate': 'pub_date',
        # 可转债转股价变动
        'stkcode': 'convert_code', 'stksecucode': 'stk_secu_code', 'stkexchangecode': 'stk_exchange_code',
        'declaredate': 'pub_date', 'valbegdate': 'val_beg_date', 'valenddate': 'val_end_date',
        'eventstype': 'events_type', 'eventstypedetails': 'events_type_details', 'cvtratio': 'cvt_ratio',
        'cvtprice': 'cvt_price', 'initicvtprice': 'init_cvt_price', 'befcvtprice': 'bef_cvt_price',
        # 可转债转股结果
        'exertype': 'exer_type', 'exerbegdate': 'exer_begin_date', 'exerenddate': 'exer_end_date',
        'cvtaccskvol': 'cvt_acc_stock_vol', 'cvtaccamt': 'cvt_acc_amt', 'cvtactprice': 'cvt_act_price',
        'cvtaccvol': 'cvt_acc_vol', 'cvttotratio': 'cvt_tot_ratio', 'outstandingamt': 'outstanding_amt',
        'afcvtcap': 'afcvt_cap', 'skcode': 'convert_code', 'actualissueamt': 'actual_issue_amt',
        'cvtamt': 'cvt_amt', 'cvtvolcur': 'cvt_vol_cur',
        # 利润表
        'totaloperrevenue': 'total_oper_revenue', 'operrevenue': 'oper_revenue', 'interestincome': 'interest_income',
        'premiumearned': 'premium_earned', 'commissionincome': 'commission_income', 'remrevenue': 'rem_revenue',
        'otheroperrevenue': 'other_oper_revenue', 'totalopercost': 'total_oper_cost', 'opercost': 'oper_cost',
        'interestexpense': 'interest_expense', 'commissionnetincome': 'commission_net_income', 'remcost': 'rem_cost',
        'capdevelopcost': 'cap_develop_cost', 'surrenderpremium': 'surrender_premium',
        'netindemnityexpense': 'net_indemnity_expense', 'netcontactreserver': 'net_contact_reserver',
        'divepolicyexpense': 'dive_policy_expense', 'reinsuranceexpense': 'reinsurance_expense',
        'otheropercost': 'other_oper_cost', 'businesstaxsurtax': 'business_tax_sur_tax',
        'adminexpense': 'admin_expense', 'finacost': 'fin_cost', 'assetimpairmentloss': 'asset_impairment_loss',
        'fairvalgain': 'fair_val_gain', 'invincome': 'inv_income', 'ajentinvincome': 'ajent_inv_income',
        'exchangegain': 'exchange_gain', 'futureloss': 'future_loss', 'trustincome': 'trust_income',
        'bonusincome': 'bonus_income', 'otheroperprofit': 'other_oper_profit', 'operprofit': 'oper_profit',
        'nonoperrevenue': 'non_oper_revenue', 'nonoperexpense': 'non_oper_expense',
        'noncurassetdisplost': 'non_cur_asset_disp_lost', 'totalprofit': 'total_profit',
        'incometaxexpense': 'income_tax_expense', 'sgminverstloss': 'sgm_invest_loss', 'netprofit': 'net_profit',
        'netprofitcoms': 'net_profit_coms', 'networkprofit': 'net_work_profit', 'minorityprofit': 'minority_profit',
        'basiceps': 'basic_eps', 'dilutedeps': 'diluted_eps', 'otherholeprofit': 'other_hole_profit',
        'netotherprofitcoms': 'net_other_profit_coms', 'netlessprofitcoms': 'net_less_profit_coms',
        'generaltotalincome': 'general_total_income', 'netgeneraltotalincome': 'net_general_total_income',
        'netlessprofitincome': 'net_less_profit_income', 'entrytime': 'entry_time', 'updatetime': 'update_time',
        'groundtime': 'ground_time', 'updateid': 'update_id', 'recordid': 'record_id', 'opinioncode': 'opinion_code',
        'reporttype': 'period', 'interestnetincome': 'interest_net_income', 'operadminexpense': 'oper_admin_expense',
        'sellexpense': 'sell_expense',
        # 资产负债表
        'monetaryfund': 'monetary_fund', 'settlementprovision': 'settlement_provision', 'fundlending': 'fund_lending',
        'tradfinaasset': 'trad_fina_asset', 'derifinaasset': 'deri_fina_asset', 'noterec': 'note_rec',
        'accountrec': 'account_rec', 'advancetosupplier': 'advance_to_supplier', 'premiumrec': 'premium_rec',
        'reinsurancerec': 'reinsurance_rec', 'rcontactreserverec': 'rcontact_reserverec', 'interestrec': 'interest_rec',
        'devidendrec': 'devidend_rec', 'otherrec': 'other_rec', 'rexportrefund': 'rexport_refund',
        'rsubsidy': 'rsubsidy', 'rmargin': 'rmargin', 'intercontribution': 'inter_contribution',
        'purchasedresellfinaasset': 'purchased_resell_fina_asset', 'inventory': 'inventory', 'expenses': 'expenses',
        'processfluxion': 'process_fluxion', 'noncurassetoneyear': 'non_cur_asset_one_year',
        'othercurasset': 'other_curasset', 'totalcurasset': 'total_cur_asset', 'loanadvance': 'loan_advance',
        'avaisalefinaasset': 'avai_sale_fina_asset', 'heldmaturityinv': 'held_maturity_inv',
        'ltaccountrec': 'lt_account_rec', 'ltequityinv': 'lt_equity_inv', 'otherltequityinv': 'other_lt_equity_inv',
        'invproperty': 'inv_property', 'fixedassetsbefore': 'fixed_assets_before',
        'aggdepreciation': 'agg_depreciation', 'fixednav': 'fixed_nav', 'fixedwdprepare': 'fixed_wd_prepare',
        'fixedassetnet': 'fixed_asset_net', 'constructionprogress': 'construction_progress',
        'constructionmaterial': 'construction_material', 'liquidationfixedasset': 'liquidation_fixed_asset',
        'productionbiologyasset': 'production_biology_asset', 'profitbiologyasset': 'profit_biology_asset',
        'oilgasasset': 'oil_gas_asset', 'intangibleasset': 'intangible_asset', 'developexp': 'develop_exp',
        'goodwill': 'good_will', 'ltdeferredasset': 'lt_deferred_asset', 'sharedislr': 'share_dis_lr',
        'deferredincometaxasset': 'deferred_income_tax_asset', 'othernoncurasset': 'other_non_cur_asset',
        'totalnoncurasset': 'total_non_cur_asset', 'totalasset': 'total_asset', 'stborrowing': 'st_borrowing',
        'borrowingfromcbank': 'borrowing_from_cbank', 'deposit': 'deposit', 'fundborrowing': 'fund_borrowing',
        'tradfinaliab': 'trad_fina_liab', 'derifinaliab': 'deri_fina_liab', 'notespay': 'notes_pay',
        'accountpay': 'account_pay', 'advancefromcustomer': 'advance_from_customer',
        'soldrepofinaasset': 'sold_repo_fina_asset', 'commissionpay': 'commission_pay', 'payrollpay': 'payroll_pay',
        'taxpay': 'tax_pay', 'interestpay': 'interest_pay', 'dividendpay': 'dividend_pay',
        'othershouldpay': 'other_should_pay', 'shouldpaymargin': 'should_pay_margin',
        'innershouldpay': 'inner_should_pay', 'otheraccountpay': 'other_account_pay',
        'accruedexpense': 'accrued_expense', 'precastcl': 'pre_cast_cl', 'reinsurancepay': 'reinsurance_pay',
        'coireservefund': 'coi_reserve_fund', 'secuproxymoney': 'secu_proxy_money',
        'secuunderwritingmoney': 'secu_underwriting_money', 'nationpurchasebalance': 'nation_purchase_balance',
        'sofinapurchasebalance': 'so_fina_purchase_balance', 'deferredincome': 'deferred_income',
        'payshortbond': 'pay_short_bond', 'noncurliaboneyear': 'non_cur_liab_one_year',
        'othercurliab': 'other_cur_liab', 'totalcurliab': 'total_cur_liab', 'ltborrowing': 'lt_borrowing',
        'bondpay': 'bond_pay', 'ltaccountpay': 'lt_account_pay', 'specialpay': 'special_pay',
        'longdeferrtax': 'long_deferr_tax', 'precastuncurrdebt': 'pre_cast_uncurr_debt',
        'deferredincometaxliab': 'deferred_income_tax_liab', 'othernoncurliab': 'other_non_cur_liab',
        'totalnoncurliab': 'total_non_cur_liab', 'totalliab': 'total_liab', 'sharecapital': 'share_capital',
        'captitalreserve': 'capital_reserve', 'inventoryshare': 'inventory_share', 'surplusreserve': 'surplus_reserve',
        'generalriskprovision': 'general_risk_provision', 'uninvestmentloss': 'uninvestment_loss',
        'retainedearning': 'retained_earning', 'allocashdividends': 'allo_cash_dividends',
        'diffconversionfc': 'diff_conversion_fc', 'shequityparentcom': 'sh_equity_parent_com',
        'minorityinterest': 'min_shareholder_equity', 'totalshequity': 'total_sh_equity',
        'totalliabshequity': 'total_liab_sh_equity', 'goodwillratio': 'good_will_ratio',
        'totalinterestliabiratio': 'total_interest_liabi_ratio', 'monetaryfundratio': 'monetary_fund_ratio',
        'accountrecratio': 'account_rec_ratio', 'inventoryratio': 'inventory_ratio',
        'fixedassetnetratio': 'fixed_asset_net_ratio', 'othercurassetratio': 'other_cur_asset_ratio',
        'ltaccountrecratio': 'lt_account_rec_ratio', 'ltequityinvratio': 'lt_equity_inv_ratio',
        'cashdepositincbank': 'cash_deposit_inc_bank', 'depositinotherbank': 'deposit_in_other_bank',
        'depositfromotherbank': 'deposit_from_other_bank', 'otherasset': 'other_asset', 'otherliab': 'other_liab',
        # 现金流量表
        'cashrecsalegoodsservice': 'cash_recsale_goods_service', 'netincrdeposit': 'net_incr_deposit',
        'netincrborrowingcbank': 'net_incr_borrowing_cbank', 'netincrborrowingibank': 'net_incr_borrowing_ibank',
        'cashrecpremium': 'cash_rec_premium', 'netcashrecreinserance': 'net_cash_rec_reinserance',
        'netincrinsurerdepositinv': 'net_incr_insurer_deposit_inv',
        'netincrdisptradfinaasset': 'net_incr_disp_trad_fina_asset', 'cashreccommission': 'cash_rec_commission',
        'netincrborrowing': 'net_incr_borrowing', 'netincrrepo': 'net_incr_repo', 'taxrefund': 'tax_refund',
        'cashrecotheroper': 'cash_rec_other_oper', 'subtotalcashinoper': 'sub_total_cash_in_oper',
        'cashpaidsalegoodsservice': 'cash_paid_sale_goods_service', 'netincrloan': 'net_incr_loan',
        'netincrdepositcbib': 'net_incr_deposit_cbib', 'cashpaidindemnity': 'cash_paid_indemnity',
        'cashpaidintecommission': 'cash_paid_inte_commission', 'cashpaiddivi': 'cash_paid_divi',
        'cashpaidemployee': 'cash_paid_employee', 'taxpaid': 'tax_paid', 'cashpaidotheroper': 'cash_paid_other_oper',
        'subtotalcashoutoper': 'sub_total_cash_out_oper', 'netcashflowoperq': 'net_cash_flow_operq',
        'cashrecinv': 'cash_rec_inv', 'cashrecdiviinv': 'cash_rec_divi_inv',
        'netcashrecdispfiasset': 'net_cash_rec_disp_fi_asset', 'netcashrecdispsubbusi': 'net_cash_rec_disp_sub_busi',
        'cashrecotherinv': 'cash_rec_other_inv', 'reduceimpawncash': 'reduce_impawn_cash',
        'subtotalcashininv': 'sub_total_cash_in_inv', 'cashpaidfiasset': 'cash_paid_fi_asset',
        'cashpaidinv': 'cash_paid_inv', 'netincrpledgeloan': 'net_incr_pledge_loan',
        'netcashpaidacqusubbusi': 'net_cash_paid_acqu_sub_busi', 'cashpaidotherinv': 'cash_paid_other_inv',
        'addimpawncash': 'add_impawn_cash', 'subtotalcashoutinv': 'sub_total_cash_out_inv',
        'netcashflowinv': 'net_cash_flow_inv', 'cashrecinvfina': 'cash_rec_inv_fina',
        'cashrecfinafrommsheinv': 'cash_rec_fina_from_mshe_inv', 'cashrecloan': 'cash_rec_loan',
        'cashrecissuebond': 'cash_rec_issue_bond', 'cashrecotherfina': 'cash_rec_other_fina',
        'sbutotalcashinfina': 'sub_total_cash_in_fina', 'debtrepay': 'debt_repay',
        'cashpaiddiviprofinte': 'cash_paid_divi_profi_nte', 'subcompayprofit': 'sub_compay_profit',
        'cashpaidotherfina': 'cash_paid_other_fina', 'subtotalcashoutfina': 'sub_total_cash_out_fina',
        'netcashflowfina': 'net_cash_flow_fina', 'effectforeignexrate': 'effect_foreign_ex_rate',
        'cashequibeginning': 'cashequibeginning', 'cashequiending': 'cashequiending',
        'minshareholderequity': 'min_shareholder_equity', 'stuinvloss': 'stu_inv_loss',
        'assetimpairmentprov': 'asset_impairment_prov', 'fixedassetdepr': 'fixed_asset_depr',
        'amorintangibleasset': 'amor_intangible_asset', 'amorltexpense': 'amor_lt_expense',
        'reduceprepaid': 'reduce_prepaid', 'addaccrued': 'add_accrued', 'lossdispfiasset': 'loss_disp_fi_asset',
        'lossfixedasset': 'loss_fixed_asset', 'adddeferrincome': 'add_deferr_income',
        'provision': 'provision', 'invloss': 'inv_loss',
        'deferredtaxassetdecr': 'deferred_tax_asset_decr', 'deferredtaxliabdecr': 'deferred_tax_liab_decr',
        'inventorydecr': 'inventory_decr', 'operrecdecr': 'oper_rec_decr', 'operpayincr': 'oper_pay_incr',
        'reducenotcompleted': 'reduce_not_completed', 'addsettlenotcompleted': 'add_settle_not_completed',
        'otheritem': 'other_item', 'netcashflowoper': 'net_cash_flow_oper', 'debttocapital': 'debt_to_capital',
        'conbondoneyear': 'con_bond_one_year', 'finaleasedfixedasset': 'fina_leased_fixed_asset',
        'cashending': 'cash_ending', 'cashbeginning': 'cash_beginning', 'equiending': 'equi_ending',
        'equibeginning': 'equi_beginning', 'cashequinetincr': 'cash_equi_net_incr',
        # 财务指标
        'ebitdainterest': 'ebitda_interest', 'inventoryturnover': 'inventory_turnover',
        'badloansfive': 'bad_loans_five', 'badloansone': 'bad_loans_one',
        'equityratio': 'equity_ratio', 'profittocostratio': 'profit_to_cost_ratio',
        'inventoryturnoverday': 'inventory_turnover_day', 'assetcomposeratio': 'asset_compose_ratio',
        'baddebtreserverate': 'bad_debt_reserve_rate', 'norecprolossratio': 'no_recpro_loss_ratio',
        'totaldebt': 'total_debt', 'shareequity': 'share_equity', 'shetota': 'sh_e_to_ta',
        'shequityturnover': 'sh_equity_turnover', 'fixedasset': 'fixed_asset', 'fixedassetratio': 'fixed_asset_ratio',
        'fixedassetturnover': 'fixed_asset_turnover', 'currentratio': 'current_ratio',
        'netprofitparentcom': 'net_profit_parent_com', 'mainbusiproratio': 'main_busi_pro_ratio',
        'netprofitcutparentcom': 'net_profit_cut_parent_com', 'cashassetratio': 'cash_asset_ratio',
        'basicepsyoy': 'basic_eps_yoy', 'weightrisknetasset': 'weight_risk_net_asset', 'weightedroe': 'weighted_roe',
        'ncfototl': 'ncfo_to_tl', 'ncfotoor': 'ncfo_to_or', 'startdate': 'start_date',
        'netprofitnoshareholder': 'net_profit_no_shareholder', 'netprofitinshareholder': 'net_profit_in_shareholder',
        'netprofitparentcompany': 'net_profit_parent_company', 'netprofityoy': 'net_profit_yoy',
        'netprofitgr': 'net_profit_gr', 'rateoe': 'rate_oe', 'netassetyoy': 'net_asset_yoy',
        'cutbasiceps': 'cut_basic_eps', 'cutweightedroe': 'cut_weighted_roe', 'cutroe': 'cut_roe',
        'totalprofityoy': 'total_profit_yoy', 'intcovratio': 'intcov_ratio',
        'curassetturnover': 'cur_asset_turnover', 'curassetturnoverday': 'cur_asset_turnover_day',
        'netcashflowoperps': 'net_cash_flow_operps', 'netcashflowoperpsyoy': 'net_cash_flow_operps_yoy', 'bvps': 'bvps',
        'cacleps': 'cacl_eps', 'deductweighteps': 'deduct_weight_eps', 'weighteps': 'weight_eps',
        'deducteps': 'deduct_eps', 'eps': 'eps', 'epsgr': 'eps_gr', 'retainedearningps': 'retained_earningps',
        'cashflowps': 'cashflow_ps', 'sps': 'sps', 'captitalreserveps': 'captital_reserv_eps', 'remark': 'remark',
        'liquidationratio': 'liquidation_ratio', 'tatoshe': 'ta_to_she', 'roe': 'roe',
        'isaudit': 'is_audit', 'quickratio': 'quick_ratio', 'ownersequity': 'owners_equity',
        'equitynoshareholder': 'equity_no_shareholder', 'adjustbvps': 'adjust_bvps',
        'ebit': 'ebit', 'ebitpmargin': 'ebit_p_margin', 'ebitgr': 'ebit_gr', 'ebitda': 'ebit_da',
        'npmargin': 'np_margin', 'netporfitbasiceps': 'net_porfit_basic_eps',
        'operprofitmargin': 'oper_profit_margin', 'operprofityoy': 'oper_profit_yoy',
        'operprofitgr': 'oper_profit_gr', 'operrevenueyoy': 'oper_revenue_yoy',
        'openoutprice': 'open_out_price', 'accountreturnover': 'account_return_over',
        'accountrecturnoverday': 'account_recturn_over_day', 'longliability': 'long_liability', 'ltltowc': 'ltl_to_wc',
        'prioperprofitratio': 'pri_oper_profit_ratio', 'grossprofitmargin': 'gross_profit_margin',
        'prioperrevenuegr': 'pri_oper_revenue_gr', 'prioperprofit': 'pri_oper_profit',
        'prioperprofitmargin': 'pri_oper_profit_margin', 'capitalfixedratio': 'capital_fixed_ratio',
        'capitalratio': 'capital_ratio', 'netasset': 'net_asset', 'retotalassetsratio': 'retotal_assets_ratio',
        'tltota': 'tl_to_ta', 'totalassets': 'total_assets',
        'roaebit': 'roa_ebit', 'roa': 'roa', 'totalassetyoy': 'total_asset_yoy', 'totalassetgr': 'total_asset_gr',
        'totalassetturnover': 'total_asset_turnover', 'totalassetturnoverday': 'total_asset_turnover_day',
        'netprofitcut': 'net_profit_cut', 'grossprofitmargins': 'gross_profit_margins', 'profitmargin': 'profit_margin',
        'netcashflowoperpss': 'net_cash_flow_oper_ps_s', 'bvpsii': 'bvpsii',
        # 股票配售
        'inipubdate': 'ini_pub_date', 'rasiefund': 'raise_fund', 'rasienetfund': 'raise_net_fund',
        'allotmentratio': 'allotment_ratio', 'rightregdate': 'right_reg_date',
        'issueobject': 'issue_object', 'exdividate': 'ex_divi_date', 'isallothalfy': 'is_allot_half_year',
        # 股东人数
        'totalsh': 'total_sh', 'avgshare': 'avg_share', 'pctoftotalsh': 'pct_of_total_sh',
        'pctofavgshare': 'pct_of_avg_sh',
        # 股票增发
        'listingnoticedate': 'listing_notice_date', 'raisenetfundd': 'raise_net_fund_planned',
        'ispubissue': 'is_pub_issue', 'issueenddate': 'issue_end_date', 'issuecost': 'issue_cost',
        'cissueprice': 'c_issue_price', 'fissueprice': 'f_issue_price',
        # 十大股东
        'shname': 'sh_name', 'sharetype': 'sh_type', 'holdshare': 'hold_share',
        'pcttotalshare': 'pct_total_share', 'holdsharechange': 'holdshare_change',
        'pctholdsharechange': 'pct_holdshare_change', 'shcode': 'sh_code',
        # 十大流通股东
        'shnature': 'sh_nature', 'sharenature': 'share_nature', 'shkind': 'sh_kind', 'flowratio': 'flow_ratio',
        # 沪深港通持股记录
        "tradetype": "trade_type", "shhksharehold": "sh_hkshare_hold", "holdingdate": "trading_day",
        # 融资融券交易汇总
        'buyamountfina': 'buy_amount_fina', 'cashrates': 'cash_rates',
        'amountfina': 'amount_fina', 'payamountfina': 'pay_amount_fina', 'sellvolstock': 'sell_vol_stock',
        'volstock': 'vol_stock', 'payvolstock': 'pay_vol_stock', 'amountstock': 'amount_stock',
        'amountmargin': 'amount_margin',
        # 股票分红
        'implementnoticedate': 'imp_notice_date', 'splitps': 'splitps', 'divipaydate': 'divi_pay_date',
        'sharelistingdate': 'share_listing_date', 'cashbtaxf': 'cash_before_tax', 'cashataxf': 'cash_after_tax',
        'baseshare': 'base_share', 'totalshare': 'total_share', 'bonusratio': 'bonus_ratio',
        'transferratio': 'transfer_ratio', 'bonustransferratio': 'bonus_transfer_ratio', 'optratio': 'opt_ratio',
        'totalbonus': 'total_bonus', 'totaltransfer': 'total_transfer', 'equitybasedate': 'equityBaseDate',
        'distriobjtypes': 'distri_obj_types', 'lasttradingday': 'last_trading_day',
        # 复权因子
        'xdy': 'xdy', 'ltdxdy': 'b_xdy', 'theltdxdy': 'f_xdy',
        # 限售股解禁
        'listeddate': 'listing_date', 'addlisted': 'add_listed', 'sstmhdlistname': 'sstmhd_list_name',
        'persentaddlisted': 'percent_addlisted', 'persentaddlistedl': 'percent_addlisted_f',
        'sstmhdlistype': 'sstmhd_list_type', 'sstmhdlistcode': 'sstmhd_list_code',
        # 股权质押
        'frozenshare': 'frozen_share', 'freezingperiodunit': 'freezing_period_unit',
        'freezingholdratio': 'freezing_hold_ratio', 'freezingtotalratio': 'freezing_total_ratio',
        'freezingstartdate': 'freezing_start_date', 'freezingenddate': 'freezing_end_date',
        'freezingtermdesc': 'freezing_term-desc', 'freezingcause': 'freezing_cause',
        'advanceenddate': 'advance_end_date', 'freezingtype': 'freezing_type', 'freezingperiod': 'freezing_period',
        'freezingpurpose': 'freezing_purpose',
        # 港股估值
        'netprofitcutlfy': 'net_profit_cut_lfy', 'netprofitcutttm': 'net_profit_cut_ttm',
        'netprofitcutmrq': 'net_profit_cut_mrq', 'pemrq': 'pemrq', 'pslfy': 'pslfy', 'psmrq': 'psmrq', 'pcmrq': 'pcmrq',
        'dividendyieldttm': 'dividend_yield_ttm', 'corpequityvalue': 'corpe_quity_val',
        # 港股基本信息
        'boardname': 'board_name', 'nhtype': 'ny', 'setype': 'se_type', 'ahsymbol': 'ah_code', 'parvalue': 'par_value',
        # 个人主营产品
        'productcode': 'product_code', 'productname': 'product_name',
        'productengname': 'product_eng_name', 'mainproductincome': 'main_product_income',
        'mainproductincomeratio': 'main_product_income_ratio', 'mainproductprofit': 'main_product_profit',
        'mainproductprofitratio': 'main_product_profit_ratio', 'productlevel': 'product_level',
        # 个股最新估值
        'fmarketval': 'floating_market_val', 'tmarketval': 'total_market_val', 'pe': 'pe', 'pettm': 'pettm', 'pb': 'pb',
        'pc': 'pc', 'pcttm': 'pcttm', 'ps': 'ps', 'psttm': 'psttm',
        # 公司概况
        'chiname': 'com_name', 'founddate': 'found_date', 'regcapital': 'reg_capital', 'comcode': 'com_code',
        'legalrepr': 'legal_repr', 'generalmanager': 'general_manager', 'countryname': 'country',
        'provincename': 'province', 'cityname': 'city', 'regaddress': 'reg_address', 'officeaddress': 'office_address',
        'postalcode': 'postal_code', 'telcode': 'tel_code', 'email': 'email', 'website': 'website',
        'businessscope': 'business_scope', 'corebusiness': 'core_business', 'comprofile': 'com_profile',
        'icregno': 'ic_reg_no', 'taxregno': 'tax_reg_no', 'corpbusilicenseno': 'corp_busil_icense_no',
        'indunamecsrc': 'l1_name', 'indunamesw': 'l2_name', 'islisted': 'is_listed',
        'isabroadlisted': 'is_abroad_listed', 'employees': 'employees', 'president': 'president', 'localno': 'local_no',
        # 股本结构
        'atotalshare': 'a_total_share', 'alistedshare': 'a_listed_share',
        'btotalshare': 'b_total_share', 'blistedshare': 'b_listed_share', 'htotalshare': 'h_total_share',
        'hlistedshare': 'h_listed_share', 'employeeshareul': 'employee_share', 'promotershareul': 'promoter_share',
        'statepromotershare': 'state_promoter_share', 'socialpromotershare': 'social_promoter_share',
        'domesticcropshare': 'domestic_crop_share', 'statelpshareul': 'slp_share',
        'flpshareul': 'flp_share', 'otherpromotershareul': 'other_promoter_share',
        'placinglpshareul': 'placing_lp_share', 'raisestateshare': 'raise_state_share',
        'raisedomesticshare': 'raise_dlp_share', 'raisestatecropshare': 'raise_slp_share',
        'raisesocialshare': 'raise_sslp_share', 'raiseovershare': 'raise_flp_share',
        'strategycropshare': 'strategy_lp_share', 'socialcropshare': 'social_lp_share',
        'alistedshareratio': 'a_listed_share_ratio', 'blistedshareratio': 'b_listed_share_ratio',
        'hlistedshareratio': 'h_listed_share_ratio', 'aunlistedshare': 'a_unlisted_share',
        'bunlistedshare': 'b_unlisted_share', 'hunlistedshare': 'h_unlisted_share', 'statesharer': 'state_res_share',
        'dlpshareul': 'dlp_share',
        'statelpsharer': 'state_lp_res_share', 'dlpsharer': 'dlp_res_share', 'dnpsharer': 'dnp_res_share',
        'placinglpsharer': 'placing_lp_res_share', 'employeesharer': 'employee_res_share',
        'managingsharer': 'managing_res_share', 'flpsharer': 'flp_res_share', 'fnpsharer': 'fnp_res_share',
        'othersharer': 'other_res_share', 'totalsharer': 'total_res_share', 'orgaplacingshare': 'orga_placing_share',
        'limitesiplacingshare': 'limit_strategy_share', 'totalshareul': 'total_unlisted_share',
        'totalsharel': 'total_listed_share', 'othersharel': 'other_listed_share',
        'totalsharerl': 'total_listed_res_share', 'buybackshared': 'buy_back_share',
        # 基金交易状态
        'tradingstate': 'trading_state',
        'prevclosingprice': 'prev_close', 'openingprice': 'open', 'highestprice': 'high', 'lowestprice': 'low',
        'closingprice': 'close', 'discountrate': 'discount_rate',
        'unitnav': 'unit_nav', 'discount': 'discount', 'discountratio': 'discount_ratio',
        # 基金衍生数据
        'netunit': 'net_unit', 'totalnetunit': 'total_net_unit', 'postnetunit': 'post_net_unit',
        'w1navg': 'w1_navg', 'w1navgr': 'w1_navgr', 'w4navg': 'w4_navg', 'w4navgr': 'w4_navgr', 'w13navg': 'w13_navg',
        'w13navgr': 'w13_navgr', 'w26navg': 'w26_navg', 'w26navgr': 'w26_navgr', 'w52navg': 'w52_navg',
        'w52navgr': 'w52_navgr', 'ytdnavg': 'ytdn_avg', 'ytdnavgr': 'ytdn_avgr', 'y3navg': 'y3_navg',
        'y5navg': 'y5_navg', 'slnavg': 'sl_navg', 'navgvol': 'navg_vol', 'beta': 'beta', 'sharper': 'sharper',
        'jensenid': 'jensenid', 'treynorid': 'treynorid', 'r2': 'r2', 'd1navgr': 'd1_navgr',
        # ETF申赎成份券汇总表
        'subcomplist': 'sub_comp_list', 'msecuabbr': 'stock_name',
        'ctype': 'c_type', 'componentnum': 'component_num', 'unit': 'unit', 'iscashsubstitute': 'is_cash_substitute',
        'cashsubstituterate': 'cash_substitute_rate',
        'cashsubstitute': 'cash_substitute', 'subreplace': 'sub_replace', 'redreplace': 'red_replace',
        # 个股公募持仓
        'seccuabbr': 'name', 'count_fund': 'count_fund', 'sum_holdingval': 'sum_holding_val',
        'sum_holdingvol': 'sum_holding_vol', 'num_holding': 'num_holding', 'ranks': 'ranks',
        # ETF申购赎回清单
        'cashdif': 'cash_dif', 'minpraset': 'min_pr_aset', 'esticash': 'esti_cash',
        'cashsubuplimit': 'cash_sub_up_limit', 'minprunits': 'min_pr_units', 'prpermit': 'pr_permit',
        'connum': 'con_num', 'purchasecap': 'purchase_cap', 'redemptioncap': 'redemption_cap',
        'pricedate': 'price_date', 'isiopv': 'is_iopv',
        # tick
        'iopv': 'iopv', 'presettleprice': 'pre_settle', 'preopeninterest': 'pre_open_interest',
        'tradingphasecode': 'trading_phase_code',
        # 静态信息
        'securitysubtype': 'security_sub_type', 'outstandingshare': 'total_share',
        'publicfloatsharequantity': 'listed_share',
        'lotsize': 'lot_size', 'ticksize': 'tick_size', 'buyqtyunit': 'buy_qty_unit', 'sellqtyunit': 'sell_qty_unit',
        'hkspreadtablecode': 'hk_spread_table_code', 'shhkconnect': 'sh_hk_connect', 'szhkconnect': 'sz_hk_connect',
        'vcmflag': 'is_vcm', 'casflag': 'is_cas', 'posflag': 'is_pos', 'buyqtyupperlimit': 'buy_qty_upper_limit',
        'sellqtyupperlimit': 'sell_qty_upper_limit', 'buyqtylowerlimit': 'buy_qty_lower_limit',
        'sellqtylowerlimit': 'sell_qty_lower_limit',
        'currency': 'currency', 'optioncontractid': 'option_contract_id',
        'optioncontractsymbol': 'option_contract_symbol', 'optionunderlyingsecurityid': 'option_underlying_security_id',
        'optionunderlyingsymbol': 'option_underlying_symbol', 'optionunderlyingtype': 'option_underlying_type',
        'optionoptiontype': 'option_option_type', 'optioncallorput': 'option_call_or_put',
        'optioncontractmultiplierunit': 'option_contract_multiplier_unit',
        'optionexerciseprice': 'option_exercise_price', 'optionstartdate': 'option_start_date',
        'optionenddate': 'option_end_date', 'optionexercisedate': 'option_exercise_date',
        'optiondeliverydate': 'option_delivery_date', 'optionexpiredate': 'option_expire_date',
        'optionupdateversion': 'option_up_date_version', 'optiontotallongposition': 'option_total_long_position',
        'optionsecurityclosepx': 'option_security_close', 'optionsettlprice': 'option_settl_price',
        'optionunderlyingclosepx': 'option_underlying_close', 'optionpricelimittype': 'option_price_limit_type',
        'optiondailypriceuplimit': 'option_daily_price_up_limit',
        'optiondailypricedownlimit': 'option_daily_price_down_limit', 'optionmarginunit': 'option_margin_unit',
        'optionmarginratioparam1': 'option_margin_ratio_param1',
        'optionmarginratioparam2': 'option_margin_ratio_param2', 'optionroundlot': 'option_round_lot',
        'optionlmtordminfloor': 'option_lmt_ord_min_floor', 'optionlmtordmaxfloor': 'option_lmt_ord_max_floor',
        'optionmktordminfloor': 'option_mkt_ord_min_floor', 'optionmktordmaxfloor': 'option_mkt_ord_max_floor',
        'optionticksize': 'option_tick_size', 'optionsecuritystatusflag': 'option_security_status_flag',
        'expiredate': 'expire_date', 'optionlisttype': 'option_List_type', 'optiondeliverytype': 'option_delivery_type',
        'optioncontractposition': 'option_contract_position', 'optionbuyqtyupperlimit': 'option_buy_qty_upper_limit',
        'optionsellqtyupperlimit': 'option_Sell_qty_upper_limit',
        'optionmarketorderbuyqtyupperlimit': 'option_market_order_buy_qty_upper_limit',
        'optionmarketordersellqtyupperlimit': 'option_market_order_sell_qty_upper_limit',
        'optionquoteorderbuyqtyupperlimit': 'option_quote_order_buy_qty_upper_limit',
        'optionquoteordersellqtyupperlimit': 'option_quote_order_sell_qty_upper_limit',
        'optionbuyqtyunit': 'option_buy_qty_unit', 'optionsellqtyunit': 'option_sell_qty_unit',
        'optionlastsellmargin': 'option_last_sell_margin', 'optionsellmargin': 'option_sell_margin',
        'optionmarketmakerflag': 'option_market_maker_flag',
        'formersymbol': 'former_symbol', 'listdate': 'listing_date', 'deliveryyear': 'delivery_year',
        'deliverymonth': 'delivery_month', 'exchangeinstid': 'exchange_inst_id', 'productid': 'product_id',
        'volumemultiple': 'volume_multiple', 'instrumentid': 'instrument_id',
        'instrumentname': 'instrument_name', 'maxmarketordervolume': 'max_market_order_volume',
        'minmarketordervolume': 'min_market_order_volume', 'maxlimitordervolume': 'max_limit_order_volume',
        'minlimitordervolume': 'min_limit_order_volume', 'createdate': 'create_date',
        'startdelivdate': 'start_deliv_date', 'enddelivdate': 'end_deliv_date', 'positiontype': 'position_type',
        'longmarginratio': 'long_margin_ratio', 'shortmarginratio': 'short_margin_ratio',
        'maxmarginsidealgorithm': 'max_margin_side_algorithm', 'basecontractid': 'base_contract_id',
        'maxpx': 'max', 'minpx': 'min', 'securitytype': 'security_type',

    }

    name_clomuns = data.columns.tolist()
    new_name_dict = {}
    for name in name_clomuns:
        try:
            l_name = name.lower()
            new_name_dict[name] = new_name_map[l_name]
        except:
            pass

    data.rename(columns=new_name_dict, inplace=True)
    return data
