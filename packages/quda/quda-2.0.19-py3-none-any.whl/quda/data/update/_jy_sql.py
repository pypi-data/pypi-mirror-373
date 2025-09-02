# -*- coding: utf-8 -*-
"""
---------------------------------------------
Created on 2025/5/24 19:00
@author: ZhangYundi
@email: yundi.xxii@outlook.com
---------------------------------------------
"""

DB_REMOTE = "gildata"

# 交易日历查询
sql_calendar = f"""
select date_format(TradingDate, '%Y-%m-%d') as date,
       IfTradingDay,
       IfMonthEnd,
       IfWeekEnd
from {DB_REMOTE}.qt_tradingdaynew
where SecuMarket = 83
order by date;
"""

# A股证券主表
sql_secumain = f"""
select InnerCode,
       SecuCode,
       SecuAbbr,
       SecuMarket,
       ListedSector, 
       ListedState, 
       DATE_FORMAT(ListedDate, '%Y-%m-%d') as ListedDate
from {DB_REMOTE}.secumain
where SecuMarket in (83, 90)
and SecuCategory in (1, 41)
and ListedSector in (1, 2, 3, 6, 7)
order by InnerCode;
"""

# 上市状态查询
sql_liststatus = f"""
select A.InnerCode,
       B.SecuCode,
       B.SecuAbbr,
       DATE_FORMAT(ChangeDate, '%Y-%m-%d') as ChangeDate,
       ChangeType
from {DB_REMOTE}.lc_liststatus AS A,
     {DB_REMOTE}.SecuMain AS B
where A.InnerCode = B.InnerCode
  and B.SecuMarket IN (83, 90)
  and B.SecuCategory in (1, 41)
  and B.ListedSector in (1, 2, 3, 6, 7)
union all
(select A.InnerCode,
        B.SecuCode,
        B.SecuAbbr,
        DATE_FORMAT(ChangeDate, '%Y-%m-%d') as ChangeDate,
        ChangeType
 from {DB_REMOTE}.lc_stibliststatus AS A,
      {DB_REMOTE}.SecuMain AS B
 where A.InnerCode = B.InnerCode
   and B.SecuMarket IN (83, 90)
   and B.SecuCategory in (1, 41)
   and B.ListedSector in (1, 2, 3, 6, 7))
order by InnerCode, ChangeDate;
"""

# st处理
sql_st = f"""
select lc_specialtrade.InnerCode,
       DATE_FORMAT(InfoPublDate, '%Y-%m-%d')     as InfoPublDate,
       SpecialTradeType,
       DATE_FORMAT(SpecialTradeTime, '%Y-%m-%d') as SpecialTradeDate
from {DB_REMOTE}.lc_specialtrade
         join gildata.secumain
              on lc_specialtrade.InnerCode = secumain.InnerCode
                  and secumain.SecuMarket in (83, 90)
                  and secumain.SecuCategory in (1, 41)
                  and secumain.ListedSector IN (1, 2, 3, 6, 7)
union
(select lc_stibsecuchange.InnerCode,
        DATE_FORMAT(InfoPublDate, '%Y-%m-%d') as InfoPublDate,
        ChangeType                            as SpecialTradeType,
        DATE_FORMAT(ChangeDate, '%Y-%m-%d')   as SpecialTradeDate
 from {DB_REMOTE}.lc_stibsecuchange
          join {DB_REMOTE}.secumain
               on lc_stibsecuchange.InnerCode = secumain.InnerCode
                   and secumain.SecuMarket in (83, 90)
                   and secumain.SecuCategory in (1, 41)
                   and secumain.ListedSector IN (1, 2, 3, 6, 7))
order by InnerCode, SpecialTradeDate;
"""

# 股本结构
sql_shares = f"""
select InnerCode,
       SecuCode,
       EndDate,
       InfoPublDate,
       TotalShares,
       Ashares,
       AFloats
from (select B.InnerCode,
             B.SecuCode,
             DATE_FORMAT(EndDate, '%Y-%m-%d')      as EndDate,
             DATE_FORMAT(InfoPublDate, '%Y-%m-%d') as InfoPublDate,
             TotalShares,
             AShares,
             AFloats
      from {DB_REMOTE}.lc_sharestru as A,
           {DB_REMOTE}.SecuMain as B
      where A.CompanyCode = B.CompanyCode
        and B.SecuMarket in (83, 90)
        and B.SecuCategory in (1, 41)
        and B.ListedSector IN (1, 2, 3, 6, 7)) a
union all
(select B.InnerCode,
        B.SecuCode,
        DATE_FORMAT(EndDate, '%Y-%m-%d')      as EndDate,
        DATE_FORMAT(InfoPublDate, '%Y-%m-%d') as InfoPublDate,
        TotalShares,
        AShares,
        AFloats
 from {DB_REMOTE}.lc_stibsharestru as A,
      {DB_REMOTE}.SecuMain as B
 where A.CompanyCode = B.CompanyCode
   and B.SecuMarket in (83, 90)
   and B.SecuCategory in (1, 41)
   and B.ListedSector IN (1, 2, 3, 6, 7))
 order by InnerCode, EndDate;
"""

# 行业
sql_industry = f"""
select B.InnerCode,
       B.SecuCode,
       DATE_FORMAT(InfoPublDate, '%Y-%m-%d') as InfoPublDate,
       A.FirstIndustryName                   as Lv1,
       A.SecondIndustryName                  as Lv2,
       A.ThirdIndustryName                   as Lv3
from {DB_REMOTE}.lc_exgindustry as A,
     {DB_REMOTE}.SecuMain as B
where A.CompanyCode = B.CompanyCode
  and A.Standard = 38
  and B.SecuMarket in (83, 90)
  and B.SecuCategory in (1, 41)
  and B.ListedSector IN (1, 2, 3, 6, 7)
union all
(select B.InnerCode,
        B.SecuCode,
        DATE_FORMAT(InfoPublDate, '%Y-%m-%d') as InfoPublDate,
        A.FirstIndustryName                   as Lv1,
        A.SecondIndustryName                  as Lv2,
        A.ThirdIndustryName                   as Lv3
 from {DB_REMOTE}.lc_stibexgindustry as A,
      {DB_REMOTE}.SecuMain as B
 where A.CompanyCode = B.CompanyCode
   and A.Standard = 38
   and B.SecuMarket in (83, 90)
   and B.SecuCategory in (1, 41)
   and B.ListedSector IN (1, 2, 3, 6, 7))
order by InnerCode, InfoPublDate;
"""

# 复权因子
sql_adj_factor = f"""
select InnerCode,
       AdjustingFactor,
       date_format(ExDiviDate, '%Y-%m-%d') as ExDiviDate
from {DB_REMOTE}.qt_stockadjustfactor
union all
select InnerCode,
       AdjustingFactor,
       date_format(ExDiviDate, '%Y-%m-%d') as ExDiviDate
from {DB_REMOTE}.LC_STIBAdjustingFactor;
"""

