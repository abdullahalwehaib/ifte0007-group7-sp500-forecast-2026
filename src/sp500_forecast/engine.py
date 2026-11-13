"""Genuine OLS/WLS, chronological validation and saved-coefficient forecasting.

The equations and sample rules follow the archived fixed-model study. This
portable adaptation makes inputs/outputs explicit and removes archive-specific
hash pins, file-copy orchestration and cross-project dependencies. No download
or AI API is used. Synthetic inputs are not genuine historical observations.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from . import SYNTHETIC_NOTICE
from .calendar import is_session, sessions_between, target_session

LOOKBACKS=(5,10,20,40)
SCHEMES=('OLS','H24','H6')
HALF_DAYS={'H24':730.5,'H6':182.625}
WINDOWS={'A':(date(2020,1,1),date(2023,12,31),date(2024,1,1)),
         'B':(date(2020,1,1),date(2026,8,31),date(2026,9,1)),
         'C':(date(2025,1,1),date(2026,8,31),date(2026,9,1))}
VALIDATION_END=date(2026,10,30)
COMMON_ORIGIN=date(2026,9,1)
TIE_TOLERANCE=1e-12


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Price:
    session: date
    close: float


def read_prices(path, *, synthetic=False):
    """Strict explicit-file parser; closure blanks are the only exclusions.

    Private CSV: observation_date,SP500. Synthetic CSV adds data_status and
    every row must carry the exact synthetic notice. Missing actual sessions
    fail completeness checking in the requested training/validation interval.
    """
    result=[]
    previous=None
    with Path(path).open(encoding='utf-8-sig',newline='') as stream:
        reader=csv.DictReader(stream)
        expected=['observation_date','SP500']+(['data_status'] if synthetic else [])
        require(reader.fieldnames==expected,'Incorrect CSV schema: '+','.join(expected))
        for row in reader:
            require(set(row)==set(expected) and all(row[k] is not None for k in expected),
                    'Malformed CSV record.')
            day=date.fromisoformat(row['observation_date'])
            require(previous is None or day>previous,'Dates must be unique and increasing; no automatic sort.')
            previous=day
            if synthetic:
                require(row['data_status']==SYNTHETIC_NOTICE,'Synthetic row is not labelled.')
            text=row['SP500'].strip()
            if not is_session(day):
                require(text in ('','.'),'A non-session must not have a price.')
                continue
            try:
                value=float(text)
            except ValueError as exc:
                raise ValueError('Missing/invalid session close: '+str(day)) from exc
            require(math.isfinite(value) and value>0,'Closes must be finite and positive.')
            result.append(Price(day,value))
    require(bool(result),'No valid session closes.')
    return result


def complete_interval(prices, first, last):
    subset=[p for p in prices if first<=p.session<=last]
    require([p.session for p in subset]==sessions_between(first,last),
            'Missing, duplicate or unexpected sessions in '+str(first)+' through '+str(last))
    return subset


def common_training_rows(prices, first, cutoff):
    subset=complete_interval(prices,first,cutoff)
    rows=[]
    for i in range(40,len(subset)-6):
        current=subset[i]
        future=subset[i+6]
        require(future.session<=cutoff and target_session(current.session)==future.session,
                'An unmatured or misaligned target entered training.')
        row={'position':i,'origin_date':str(current.session),'origin_close':current.close,
             'target_date':str(future.session),'target_close':future.close,
             'Y_return_6':future.close/current.close-1}
        for k in LOOKBACKS:
            row[f'factor_start_{k}']=str(subset[i-k].session)
            row[f'X_{k}']=current.close/subset[i-k].close-1
        rows.append(row)
    require(len(rows)==len(subset)-46 and bool(rows),'Wrong common training sample.')
    return rows


def decay_weights(dates, scheme, reference):
    require(scheme in SCHEMES,'Unsupported weight scheme.')
    require(all(d<=reference for d in dates),'Weight date exceeds reference.')
    return [1.0 if scheme=='OLS' else 2.0**(-(reference-d).days/HALF_DAYS[scheme]) for d in dates]


def fit_weighted(xs, ys, weights):
    require(len(xs)==len(ys)==len(weights) and len(xs)>=3,'Insufficient/misaligned fit vectors.')
    require(all(math.isfinite(v) for values in (xs,ys,weights) for v in values),
            'Nonfinite fitting value.')
    require(all(w>0 for w in weights),'Weights must be positive.')
    sw=math.fsum(weights)
    xb=math.fsum(w*x for w,x in zip(weights,xs))/sw
    yb=math.fsum(w*y for w,y in zip(weights,ys))/sw
    sxx=math.fsum(w*(x-xb)**2 for w,x in zip(weights,xs))
    require(sxx>0,'Degenerate predictor.')
    beta=math.fsum(w*(x-xb)*(y-yb) for w,x,y in zip(weights,xs,ys))/sxx
    alpha=yb-beta*xb
    residuals=[y-(alpha+beta*x) for x,y in zip(xs,ys)]
    sse=math.fsum(w*e*e for w,e in zip(weights,residuals))
    sst=math.fsum(w*(y-yb)**2 for w,y in zip(weights,ys))
    ordinary_mean=math.fsum(ys)/len(ys)
    ordinary_sst=math.fsum((y-ordinary_mean)**2 for y in ys)
    require(sst>0 and ordinary_sst>0,'No target variation.')
    return {'alpha':alpha,'beta':beta,'R2_weighted':1-sse/sst,
            'R2_unweighted':1-math.fsum(e*e for e in residuals)/ordinary_sst}


def train_grid(prices):
    models=[]
    training_rows=[]
    weight_rows=[]
    for window,(first,cutoff,validation_start) in WINDOWS.items():
        rows=common_training_rows(prices,first,cutoff)
        training_rows.extend({'window':window,**r} for r in rows)
        for scheme in SCHEMES:
            weights=decay_weights([date.fromisoformat(r['origin_date']) for r in rows],scheme,cutoff)
            sw=math.fsum(weights)
            n_eff=sw*sw/math.fsum(w*w for w in weights)
            base={'window':window,'scheme':scheme,'training_start':str(first),'cutoff':str(cutoff),
                  'validation_start':str(validation_start),'n_training':len(rows),
                  'first_training_origin':rows[0]['origin_date'],'last_training_origin':rows[-1]['origin_date'],
                  'last_training_target':rows[-1]['target_date'],'N_eff':n_eff,
                  'half_life_calendar_days':HALF_DAYS.get(scheme)}
            for row,weight in zip(rows,weights):
                weight_rows.append({'window':window,'scheme':scheme,'origin_date':row['origin_date'],
                                    'age_calendar_days':(cutoff-date.fromisoformat(row['origin_date'])).days,
                                    'weight':weight,'normalised_weight':weight/sw})
            mu=math.fsum(w*r['Y_return_6'] for w,r in zip(weights,rows))/sw
            models.append({'model_id':f'{window}_{scheme}_MEAN','kind':'mean','k':0,
                           **base,'alpha':mu,'beta':0.0})
            for k in LOOKBACKS:
                fit=fit_weighted([r[f'X_{k}'] for r in rows],[r['Y_return_6'] for r in rows],weights)
                models.append({'model_id':f'{window}_{scheme}_k{k:02}','kind':'regression','k':k,**base,**fit})
    require(len(models)==45 and sum(m['kind']=='regression' for m in models)==36,'Grid count mismatch.')
    return models,training_rows,weight_rows


def forecast_model(model, history, origin, target):
    """Pure prediction from an origin-only prefix; rejects future input rows."""
    require(history and history[-1].session==origin,'History must end at origin.')
    require(all(p.session<=origin and math.isfinite(p.close) and p.close>0 for p in history),
            'Future or invalid price in forecast history.')
    require([p.session for p in history]==sessions_between(history[0].session,origin),
            'Forecast history has missing or disordered sessions.')
    require(target_session(origin)==target,'Target is not exactly six subsequent sessions.')
    require(origin>date.fromisoformat(model['cutoff']),'Coefficients unavailable at origin.')
    k=int(model['k'])
    require(len(history)>=k+1,'Insufficient lookback history.')
    close=history[-1].close
    x=close/history[-k-1].close-1 if k else None
    predicted_return=model['alpha']+model['beta']*x if k else model['alpha']
    predicted=close*(1+predicted_return)
    require(math.isfinite(predicted) and predicted>0,'Invalid prediction; no clipping.')
    return {'model_id':model['model_id'],'kind':model['kind'],'window':model['window'],
            'scheme':model['scheme'],'k':k,'origin_date':str(origin),'target_date':str(target),
            'origin_close':close,'factor_start_date':str(history[-k-1].session) if k else '',
            'X':x,'alpha':model['alpha'],'beta':model['beta'],
            'predicted_return':predicted_return,'predicted_close':predicted}


def validation_predictions(models, prices):
    history=complete_interval(prices,date(2020,1,1),VALIDATION_END)
    test_dates=[p.session for p in history if p.session>=date(2024,1,1)]
    pairs=[(test_dates[i],test_dates[i+6]) for i in range(len(test_dates)-6)]
    predictions=[]
    for origin,target in pairs:
        prefix=[p for p in history if p.session<=origin][-41:]
        for model in models:
            if origin>=date.fromisoformat(model['validation_start']):
                predictions.append(forecast_model(model,prefix,origin,target))
        close=prefix[-1].close
        predictions.append({'model_id':'UNCHANGED','kind':'unchanged','window':'ALL','scheme':'NONE','k':0,
                            'origin_date':str(origin),'target_date':str(target),'origin_close':close,
                            'factor_start_date':'','X':None,'alpha':0.,'beta':0.,
                            'predicted_return':0.,'predicted_close':close})
    # Outcomes are attached only after all per-origin predictions are complete.
    actuals={str(p.session):p.close for p in history}
    for row in predictions:
        actual=actuals[row['target_date']]
        error=row['predicted_close']-actual
        row.update(actual_close=actual,signed_error=error,AE=abs(error),squared_error=error*error,
                   APE_pct=100*abs(error)/actual,signed_pct=100*error/actual)
    lookup={(r['model_id'],r['origin_date']):r for r in predictions}
    outcome=lambda delta:'win' if delta < -TIE_TOLERANCE else 'loss' if delta>TIE_TOLERANCE else 'tie'
    for row in predictions:
        row['vs_unchanged']='benchmark' if row['kind']=='unchanged' else outcome(
            row['AE']-lookup[('UNCHANGED',row['origin_date'])]['AE'])
        row['vs_matching_mean']=outcome(row['AE']-lookup[
            (f"{row['window']}_{row['scheme']}_MEAN",row['origin_date'])]['AE']) \
            if row['kind']=='regression' else 'not_applicable'
    return predictions


def groups_for(row):
    origin=date.fromisoformat(row['origin_date'])
    target=date.fromisoformat(row['target_date'])
    windows=('A','B','C') if row['model_id']=='UNCHANGED' else (row['window'],)
    groups=['native_'+w for w in windows if origin>=WINDOWS[w][2]]
    if row['window']=='A' or row['model_id']=='UNCHANGED':
        groups.append(f'A_target_year_{target.year}')
    if origin>=COMMON_ORIGIN:
        groups+=['common','common_target_September' if target.month==9 else 'common_target_October']
    return groups


def summarise(predictions):
    grouped={}
    for row in predictions:
        for group in groups_for(row):
            grouped.setdefault((group,row['model_id']),[]).append(row)
    result=[]
    for (group,mid),rows in grouped.items():
        n=len(rows)
        entry={'group':group,'model_id':mid,'n_forecasts':n,
               'MAE':math.fsum(r['AE'] for r in rows)/n,'MAPE':math.fsum(r['APE_pct'] for r in rows)/n,
               'RMSE':math.sqrt(math.fsum(r['squared_error'] for r in rows)/n),
               'mean_signed_percentage_error':math.fsum(r['signed_pct'] for r in rows)/n,
               'wins_vs_unchanged':sum(r['vs_unchanged']=='win' for r in rows) if mid!='UNCHANGED' else '',
               'wins_vs_matching_mean':sum(r['vs_matching_mean']=='win' for r in rows)
                                        if rows[0]['kind']=='regression' else ''}
        for scheme in ('H24','H6'):
            weights=decay_weights([date.fromisoformat(r['target_date']) for r in rows],scheme,VALIDATION_END)
            entry['MAPE_'+scheme]=math.fsum(w*r['APE_pct'] for w,r in zip(weights,rows))/math.fsum(weights)
        result.append(entry)
    for group in {r['group'] for r in result}:
        rows=[r for r in result if r['group']==group]
        baseline=next(r for r in rows if r['model_id']=='UNCHANGED')['MAPE']
        for row in rows:
            row['relative_MAPE_improvement_vs_unchanged_pct']=100*(baseline-row['MAPE'])/baseline
    return sorted(result,key=lambda r:(r['group'],r['MAPE'],r['model_id']))


def run_in_memory(prices, origin=date(2026,11,12), target=date(2026,11,20)):
    models,training,weights=train_grid(prices)
    predictions=validation_predictions(models,prices)
    summary=summarise(predictions)
    prefix=[p for p in prices if p.session<=origin][-41:]
    future=[forecast_model(m,prefix,origin,target) for m in models]
    return {'models':models,'training':training,'weights':weights,'predictions':predictions,
            'summary':summary,'future':future}

