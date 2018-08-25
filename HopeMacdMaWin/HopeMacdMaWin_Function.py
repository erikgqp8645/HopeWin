# -*- coding: utf-8 -*-

import pandas as pd
import os
import DATA_CONSTANTS as DC
import numpy as np
import ResultStatistics as RS
import HopeMacdMaWin_Parameter as Parameter
from datetime import datetime
import time


def stat_multi_symbol_result():
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    multi_symbol_df = pd.read_excel('HopeMacdMaWin_symbol_KMIN_set.xlsx')
    for n, row in multi_symbol_df.iterrows():
        strategy_name = row['strategyName']
        exchange_id = row['exchange_id']
        sec_id = row['sec_id']
        bar_type = row['K_MIN']
        folder_name = "%s %s %s %d\\" % (strategy_name, exchange_id, sec_id, bar_type)
        result_file_name = "%s %s.%s %d finalresults.csv" % (strategy_name, exchange_id, sec_id, bar_type)
        print result_file_name
        result_df = pd.read_csv(folder_name + result_file_name)
        multi_symbol_df.ix[n, 'OprTimes'] = result_df['OprTimes'].mean()
        multi_symbol_df.ix[n, 'Annual_max'] = result_df['Annual'].max()
        multi_symbol_df.ix[n, 'Annual_avg'] = result_df['Annual'].mean()
        multi_symbol_df.ix[n, 'EndCash_avg'] = result_df['EndCash'].mean()
        multi_symbol_df.ix[n, 'EndCash_max'] = result_df['EndCash'].max()
        multi_symbol_df.ix[n, 'own_cash_max_max'] = result_df['max_own_cash'].max()
        multi_symbol_df.ix[n, 'own_cash_max_avg'] = result_df['max_own_cash'].mean()
        multi_symbol_df.ix[n, 'Sharpe_max'] = result_df['Sharpe'].max()
        multi_symbol_df.ix[n, 'SR_avg'] = result_df['SR'].mean()
        multi_symbol_df.ix[n, 'DR_avg'] = result_df['DrawBack'].mean()
        multi_symbol_df.ix[n, 'SingleEarn_avg'] = result_df['MaxSingleEarnRate'].mean()
        multi_symbol_df.ix[n, 'SingleLoss_avg'] = result_df['MaxSingleLossRate'].mean()
        multi_symbol_df.ix[n, 'ProfitLossRate_avg'] = result_df['ProfitLossRate'].mean()
    multi_symbol_df.to_csv('HopeMacdMaWin_symbol_KMIN_set2_result.csv')


def re_concat_atrsl_result():
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    symbol_folder = "%s\\%s %s %s %d\\" % (resultpath, Parameter.strategyName, Parameter.exchange_id, Parameter.sec_id, Parameter.K_MIN)
    os.chdir(symbol_folder)
    atrsl_para_name_list = []
    atr_pendant_n_list = Parameter.atr_pendant_n_list_close
    atr_pendan_rate_list = Parameter.atr_pendant_rate_list_close
    atr_yoyo_n_list = Parameter.atr_yoyo_n_list_close
    atr_yoyo_rate_list = Parameter.atr_yoyo_rate_list_close
    for atr_pendant_n in atr_pendant_n_list:
        for atr_pendant_rate in atr_pendan_rate_list:
            for atr_yoyo_n in atr_yoyo_n_list:
                for atr_yoyo_rate in atr_yoyo_rate_list:
                    atrsl_para_name_list.append('%d_%.1f_%d_%.1f' % (atr_pendant_n, atr_pendant_rate, atr_yoyo_n, atr_yoyo_rate))
    final_result_name_0 ="%s %s.%s%d finalresult_atrsl%s.csv" % (Parameter.strategyName, Parameter.exchange_id, Parameter.sec_id, Parameter.K_MIN, atrsl_para_name_list[0])
    final_result_file = pd.read_csv("%s\\%s" % (atrsl_para_name_list[0], final_result_name_0))
    for atr_para_name in atrsl_para_name_list[1:]:
        final_result_name ="%s %s.%s%d finalresult_atrsl%s.csv" % (Parameter.strategyName, Parameter.exchange_id, Parameter.sec_id, Parameter.K_MIN, atr_para_name)
        final_result_file = pd.concat([final_result_file, pd.read_csv("%s\\%s" % (atr_para_name, final_result_name))])

    final_result_file.to_csv("%s %s.%s%d finalresult_atrsl_reconcat.csv" % (Parameter.strategyName, Parameter.exchange_id, Parameter.sec_id, Parameter.K_MIN))


def re_calc_finalresult():
    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    symbol_folder = "%s\\%s %s %s %d\\" % (resultpath, Parameter.strategyName, Parameter.exchange_id, Parameter.sec_id, Parameter.K_MIN)
    os.chdir(symbol_folder)
    atrsl_folder = '10_4.0_16_2.0\\'    # 止损文件夹名
    parasetlist = pd.read_csv(resultpath + Parameter.parasetname)['Setname'].tolist()
    strategyName = Parameter.strategyName
    symbol ="%s.%s" % (Parameter.exchange_id, Parameter.sec_id)
    K_MIN = Parameter.K_MIN
    indexcols = Parameter.ResultIndexDic
    new_indexcols = []
    for i in indexcols:
        new_indexcols.append('new_' + i)
    resultdf = pd.DataFrame(columns=['setname', 'atr_sl_target', 'worknum'] + indexcols + new_indexcols)
    resultdf['No'] = range(len(parasetlist))
    i = 0
    for setname in parasetlist:
        print setname
        worknum = 0
        olddailydf = pd.read_csv(strategyName + ' ' + symbol + str(K_MIN) + ' ' + setname + ' dailyresult.csv', index_col='date')
        opr_file_name = "%s %s%d %s resultATR_by_tick.csv" % (strategyName, symbol, K_MIN, setname)
        oprdf = pd.read_csv(atrsl_folder + opr_file_name)
        oldr = RS.getStatisticsResult(oprdf, False, indexcols, olddailydf)
        opr_dialy_k_file_name = "%s %s%d %s dailyresultATR_by_tick.csv" % (strategyName, symbol, K_MIN, setname)
        dailyClose = pd.read_csv(atrsl_folder + opr_dialy_k_file_name)
        newr = RS.getStatisticsResult(oprdf, True, indexcols, dailyClose)
        resultdf.loc[i] = [setname, '10_4.0_16_2.0', worknum] + oldr + newr
        i += 1
    resultdf.to_csv("%s%s %s%d finalresult_atrsl10_4.0_16_2.0.csv" % (atrsl_folder, strategyName, symbol, K_MIN))

def calDailyReturn():
    '''基于已有的opr结果，重新补充计算dailyReturn'''
    startdate='2016-01-01'
    enddate = '2018-04-30'
    symbol = 'SHFE.RB'
    K_MIN = 3600
    symbolinfo = DC.SymbolInfo(symbol, startdate, enddate)
    strategyName = Parameter.strategyName
    #rawdata = DC.getBarData(symbol, K_MIN, startdate + ' 00:00:00', enddate + ' 23:59:59').reset_index(drop=True)
    #dailyK = DC.generatDailyClose(rawdata)
    bardic = DC.getBarBySymbolList(symbol, symbolinfo.getSymbolList(), K_MIN, startdate, enddate)

    upperpath=DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])
    #foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])+'\\DynamicStopLoss-18.0\\'
    #foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])+'\\OnceWinNoLoss8.0\\'
    #foldername = ' '.join([strategyName, Parameter.exchange_id, Parameter.sec_id, str(K_MIN)])+'\\dsl_-0.020ownl_0.008\\'
    os.chdir(foldername)
    parasetlist = pd.read_csv(resultpath + Parameter.parasetname)
    paranum = parasetlist.shape[0]

    filesuffix='result.csv'
    #filesuffix = 'resultDSL_by_tick.csv'
    #filesuffix = 'resultOWNL_by_tick.csv'
    #filesuffix = 'result_multiSLT.csv'
    indexcols=Parameter.ResultIndexDic
    resultList=[]
    for i in range(paranum):
        setname = parasetlist.ix[i, 'Setname']
        print setname
        oprdf=pd.read_csv(strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' '+filesuffix)
        symbolDomainDic = symbolinfo.amendSymbolDomainDicByOpr(oprdf)
        bars = DC.getDomainbarByDomainSymbol(symbolinfo.getSymbolList(), bardic, symbolDomainDic)
        dailyK = DC.generatDailyClose(bars)

        dR=RS.dailyReturn(symbolinfo,oprdf,dailyK,Parameter.initialCash)
        dR.calDailyResult()
        dR.dailyClose.to_csv(strategyName + ' ' + symbolinfo.domain_symbol + str(K_MIN) + ' ' + setname + ' daily'+filesuffix)

        results = RS.getStatisticsResult(oprdf, False, indexcols, dR.dailyClose)
        print results
        resultList.append([setname] + results)  # 在这里附上setname

    resultdf = pd.DataFrame(resultList,columns=['Setname'] + indexcols)
    resultdf.to_csv("%s %s %d finalresults.csv" % (strategyName,symbol, K_MIN))

def calResultByPeriod():
    '''
    按时间分段统计结果:
    1.设定开始和结束时间
    2.选择时间周期
    3.设定文件夹、买卖操作文件名、日结果文件名和要生成的新文件名
    :return:
    '''
    #设定开始和结束时间
    startdate = '2011-04-01'
    enddate = '2018-07-01'

    #2.选择时间周期
    #freq='YS' #按年统计
    #freq='2QS' #按半年统计
    #freq='QS' #按季度统计
    freq='MS' #按月统计，如需多个月，可以加上数据，比如2个月：2MS

    #3.设文件和文件夹状态
    filedir='D:\\002 MakeLive\myquant\HopeWin\Results\HopeMacdMaWin DCE J 3600\dsl_-0.022ownl_0.012\ForwardOprAnalyze\\' #文件所在文件夹
    oprfilename = 'HopeMacdMaWin DCE.J3600_Rank3_win9_oprResult.csv' #买卖操作文件名
    dailyResultFileName = 'HopeMacdMaWin DCE.J3600_Rank3_win9_oprdailyResult.csv' #日结果文件名
    newFileName = 'HopeMacdMaWin DCE.J3600_Rank3_win9_result_by_Period_M.csv' #要生成的新文件名
    os.chdir(filedir)
    oprdf = pd.read_csv(oprfilename)
    dailyResultdf = pd.read_csv(dailyResultFileName)

    oprdfcols = oprdf.columns.tolist()
    if 'new_closeprice' in oprdfcols:
        newFlag = True
    else:
        newFlag = False

    monthlist = [datetime.strftime(x, '%Y-%m-%d %H:%M:%S') for x in list(pd.date_range(start=startdate, end=enddate, freq=freq, normalize=True, closed='right'))]

    if not startdate in monthlist[0]:
        monthlist.insert(0,startdate+" 00:00:00")
    if not enddate in monthlist[-1]:
        monthlist.append(enddate+" 23:59:59")
    else:
        monthlist[-1]=enddate+" 23:59:59"
    rlist=[]
    for i in range(1,len(monthlist)):
        starttime=monthlist[i-1]
        endtime = monthlist[i]
        startutc = float(time.mktime(time.strptime(starttime, "%Y-%m-%d %H:%M:%S")))
        endutc = float(time.mktime(time.strptime(endtime, "%Y-%m-%d %H:%M:%S")))

        resultdata = oprdf.loc[(oprdf['openutc'] >= startutc) & (oprdf['openutc'] < endutc)]
        dailydata = dailyResultdf.loc[(dailyResultdf['utc_time'] >= startutc) & (dailyResultdf['utc_time'] < endutc)]
        resultdata.reset_index(drop=True,inplace=True)
        if resultdata.shape[0]>0:
            rlist.append([starttime,endtime]+RS.getStatisticsResult(resultdata, newFlag, Parameter.ResultIndexDic, dailydata))
        else:
            rlist.append([0]*len(Parameter.ResultIndexDic))
    rdf = pd.DataFrame(rlist,columns=['StartTime','EndTime']+Parameter.ResultIndexDic)
    rdf.to_csv(newFileName)

def remove_polar():
    symbol = 'DCE.J'
    symbolinfo = DC.SymbolInfo(symbol)
    folder = 'D:\\002 MakeLive\myquant\HopeWin\Results\HopeMacdMaWin DCE J 3600\ForwardOprAnalyze\\'
    filename = 'HopeMacdMaWin DCE.J3600_Rank3_win9_oprResult.csv'
    opr = pd.read_csv(folder+filename)
    opr = RS.opr_result_remove_polar(opr)
    opr['commission_fee_rp'], opr['per earn_rp'], opr['own cash_rp'], opr['hands_rp'] = RS.calcResult(result=opr, symbolinfo=symbolinfo, initialCash=200000, positionRatio=1, ret_col='new_ret')
    opr.to_csv(folder+'HopeMacdMaWin DCE.J3600_Rank3_win9_oprResult_remove_polar.csv')

def multi_slt_remove_polar():
    """
        计算多个止损策略结合回测的结果
        :param strategyName:
        :param symbolInfo:
        :param K_MIN:
        :param parasetlist:
        :param sltlist:
        :param positionRatio:
        :param initialCash:
        :return:
    """
    symbol = 'DCE.J'
    symbolInfo = DC.SymbolInfo(symbol)
    symbol = symbolInfo.domain_symbol
    new_indexcols = []
    indexcols = Parameter.ResultIndexDic
    for i in indexcols:
        new_indexcols.append('new_' + i)
    allresultdf_cols = ['setname', 'slt', 'slWorkNum'] + indexcols + new_indexcols
    allresultdf = pd.DataFrame(columns=allresultdf_cols)

    allnum = 0
    paranum = parasetlist.shape[0]

    # dailyK = DC.generatDailyClose(barxm)

    # 先生成参数列表
    allSltSetList = []  # 这是一个二维的参数列表，每一个元素是一个止损目标的参数dic列表
    for slt in sltlist:
        sltset = []
        for t in slt['paralist']:
            sltset.append({'name': slt['name'],
                           'sltValue': t,
                           'folder': ("%s%.1f\\" % (slt['folderPrefix'], (t * 1000))),
                           'fileSuffix': slt['fileSuffix']
                           })
        allSltSetList.append(sltset)
    finalSltSetList = []  # 二维数据，每个一元素是一个多个止损目标的参数dic组合
    for sltpara in allSltSetList[0]:
        finalSltSetList.append([sltpara])
    for i in range(1, len(allSltSetList)):
        tempset = allSltSetList[i]
        newset = []
        for o in finalSltSetList:
            for t in tempset:
                newset.append(o + [t])
        finalSltSetList = newset
    print finalSltSetList

    for sltset in finalSltSetList:
        newfolder = ''
        for sltp in sltset:
            newfolder += (sltp['name'] + '_%.3f' % (sltp['sltValue']))
        try:
            os.mkdir(newfolder)  # 创建文件夹
        except:
            pass
        print (newfolder)
        pool = multiprocessing.Pool(multiprocessing.cpu_count() - 1)
        l = []
        for sn in range(0, paranum):
            setname = parasetlist.ix[sn, 'Setname']
            # l.append(msl.multiStopLosslCal(strategyName, symbolInfo, K_MIN, setname, sltset, positionRatio, initialCash,
            #                           newfolder + '\\'))
            l.append(pool.apply_async(msl.multiStopLosslCal,
                                      (strategyName, symbolInfo, K_MIN, setname, sltset, barxmdic, positionRatio, initialCash, newfolder, indexcols)))
        pool.close()
        pool.join()

        resultdf = pd.DataFrame(columns=allresultdf_cols)
        i = 0
        for res in l:
            resultdf.loc[i] = res.get()
            allresultdf.loc[allnum] = resultdf.loc[i]
            i += 1
            allnum += 1
        resultfilename = ("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, newfolder))
        resultdf.to_csv(newfolder + '\\' + resultfilename, index=False)

    allresultname = ''
    for slt in sltlist:
        allresultname += slt['name']
    # allresultdf['cashDelta'] = allresultdf['new_endcash'] - allresultdf['old_endcash']
    allresultdf.to_csv("%s %s%d finalresult_multiSLT_%s.csv" % (strategyName, symbol, K_MIN, allresultname), index=False)
    pass



def plot_parameter_result_pic(multi_sybmol_file_name = "multi_symbol_1st_xu.xlsx"):
    """绘制finalresult结果中参数对应的end cash和max own cash的分布柱状图"""
    import matplotlib.pyplot as plt

    upperpath = DC.getUpperPath(Parameter.folderLevel)
    resultpath = upperpath + Parameter.resultFolderName
    os.chdir(resultpath)
    symbol_sellected = pd.read_excel(multi_sybmol_file_name)
    for n , rows in symbol_sellected.iterrows():
        fig = plt.figure(figsize=(6, 12))
        exchange = rows['exchange']
        sec = rows['sec']
        bar_type = rows['bar_type']
        folder_name = "%s %s %s %d\\" % (Parameter.strategyName, exchange, sec, bar_type)
        final_result_file = pd.read_csv(folder_name + "%s %s.%s %d finalresults.csv" % (Parameter.strategyName, exchange, sec, bar_type))
        para_file = pd.read_csv(folder_name + "%s %s %d %s.csv" % (exchange, sec, bar_type, Parameter.parasetname))
        para_name_list = ['N', 'N1', 'M1', 'M2', 'MaN']
        for i in range(len(para_name_list)):
            para_name = para_name_list[i]
            final_result_file[para_name_list] = para_file[para_name_list]
            grouped = final_result_file.groupby(para_name)
            end_cash_grouped = grouped['EndCash'].mean()
            p = plt.subplot(len(para_name_list), 1, i+1)
            p.set_title(para_name)
            p.bar(end_cash_grouped.index.tolist(), end_cash_grouped.values)
            print end_cash_grouped
        fig.savefig('%s %s %s %d_para_distribute.png' % (Parameter.strategyName, exchange, sec, bar_type), dip=500)


if __name__=='__main__':
    #re_concat_atrsl_result()  #重新汇总atrsl的结果
    #re_calc_finalresult()
    #calDailyReturn()
    #calResultByPeriod() #按时间分段统计结果
    #remove_polar()
    plot_parameter_result_pic("multi_symbol_1st_xu.xlsx")     # 绘制参数的结果分布图，用于参数优化分析，使用时要设置好文件名