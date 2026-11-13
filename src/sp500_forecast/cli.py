"""Local CLI. Synthetic outputs are labelled; private outputs stay outside repo."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction
from pathlib import Path

from . import PRIVATE_NOTICE, SYNTHETIC_NOTICE
from .engine import read_prices, require, run_in_memory
from .synthetic import SEED, write_synthetic_csv

REPOSITORY=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_rows(path, rows, notice):
    require(bool(rows),'Cannot write an empty result table.')
    fields=['data_status']+list(rows[0])
    with Path(path).open('x',encoding='utf-8',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({'data_status':notice,**row})


def write_results(output, result, notice, input_path, seed=None):
    output.mkdir(parents=True,exist_ok=False)
    for key,name in [('models','coefficients.csv'),('training','training_rows.csv'),
                     ('weights','training_weights.csv'),('predictions','validation_forecasts.csv'),
                     ('summary','validation_summary.csv'),('future','forecast_candidates.csv')]:
        rows=result[key]
        # CSV catalog has optional diagnostic keys for mean/regression records.
        if key=='models':
            fields=list(dict.fromkeys(k for row in rows for k in row))
            rows=[{k:row.get(k,'') for k in fields} for row in rows]
        write_rows(output/name,rows,notice)
    chosen=next(r for r in result['future'] if r['model_id']=='A_H24_k05')
    record={'data_status':notice,'input_basename':Path(input_path).name,'input_sha256':sha(input_path),
            'synthetic_seed':seed,'python':platform.python_version(),
            'regression_configurations':36,'matching_mean_controls':9,
            'native_A_origins':705,'common_origins':37,
            'fitting_scope':'Fixed 2020–2023, 2020–August2026 and 2025–August2026 windows; no validation updating',
            'selected_specification_demonstration':chosen,
            'selected_specification_demo_point_2dp':str(Decimal(str(chosen['predicted_close'])).quantize(
                Decimal('.01'),rounding=ROUND_HALF_UP)),
            'outputs':{p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()}}
    (output/'run_receipt.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return record


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    generate=commands.add_parser('generate-synthetic',help='Create artificial labelled prices only.')
    generate.add_argument('--output',type=Path,default=REPOSITORY/'data/synthetic_prices.csv')
    demo=commands.add_parser('demo',help='Train and evaluate only fixed-seed synthetic data.')
    demo.add_argument('--input',type=Path,default=REPOSITORY/'data/synthetic_prices.csv')
    demo.add_argument('--output',type=Path,default=REPOSITORY/'outputs/synthetic_demo')
    private=commands.add_parser('private-reproduce',help='Use an explicitly supplied private local CSV; no downloads.')
    private.add_argument('--input',type=Path,required=True)
    private.add_argument('--output',type=Path,required=True)
    saved=commands.add_parser('forecast-saved',help='Apply the published saved coefficients to an authorised private CSV; no fitting.')
    saved.add_argument('--input',type=Path,required=True)
    saved.add_argument('--output',type=Path,required=True)
    args=parser.parse_args(argv)
    if args.command=='generate-synthetic':
        path=write_synthetic_csv(args.output)
        print(json.dumps({'data_status':SYNTHETIC_NOTICE,'file':path.name,'sha256':sha(path)},indent=2))
        return
    synthetic=args.command=='demo'
    notice=SYNTHETIC_NOTICE if synthetic else PRIVATE_NOTICE
    if not synthetic:
        require(not args.input.resolve().is_relative_to(REPOSITORY),
                'Private input must remain outside the public repository.')
        require(not args.output.resolve().is_relative_to(REPOSITORY),
                'Private outputs must remain outside the public repository.')
    require(not args.output.exists(),'Output exists; use a fresh output directory.')
    prices=read_prices(args.input,synthetic=synthetic)
    if args.command=='private-reproduce':
        require(prices[-1].session==date(2026,11,12),
                'Historical reproduction must end at the completed approved origin; future rows are not accepted.')
    if args.command=='forecast-saved':
        origin=date(2026,11,12)
        require(prices[-1].session==origin,'Saved deployment requires the completed approved origin session.')
        prefix=prices[-6:]
        from .calendar import sessions_between, target_session
        require(len(prefix)==6 and [p.session for p in prefix]==sessions_between(prefix[0].session,origin),
                'Need six consecutive completed sessions through the approved origin.')
        with args.input.open(encoding='utf-8-sig',newline='') as stream:
            raw={row['observation_date']:row['SP500'] for row in csv.DictReader(stream)}
        specification=json.loads((REPOSITORY/'evidence/official_model.json').read_text())
        alpha=Fraction(specification['coefficients']['alpha'])
        beta=Fraction(specification['coefficients']['beta'])
        level=Fraction(raw[str(origin)])
        x=level/Fraction(raw[str(prefix[0].session)])-1
        predicted_return=alpha+beta*x
        forecast=level*(1+predicted_return)
        with localcontext() as ctx:
            ctx.prec=80
            as_decimal=lambda q:Decimal(q.numerator)/Decimal(q.denominator)
            record={'data_status':PRIVATE_NOTICE,'model_id':specification['model_id'],
                    'input_sha256':sha(args.input),'origin':str(origin),'target':str(target_session(origin)),
                    'fitting_performed':False,'momentum_exact_fraction':str(x),
                    'predicted_return_exact_fraction':str(predicted_return),
                    'forecast_full_precision':str(as_decimal(forecast)),
                    'forecast_2dp':str(as_decimal(forecast).quantize(Decimal('.01'),rounding=ROUND_HALF_UP))}
        args.output.mkdir(parents=True,exist_ok=False)
        (args.output/'private_saved_forecast.json').write_text(json.dumps(record,indent=2)+'\n')
        print(json.dumps(record,indent=2))
        return
    result=run_in_memory(prices)
    record=write_results(args.output,result,notice,args.input,SEED if synthetic else None)
    print(json.dumps({'data_status':notice,'regressions':36,'native_A_origins':705,
                      'common_origins':37,'selected_specification_demo_point_2dp':
                      record['selected_specification_demo_point_2dp']},indent=2))

