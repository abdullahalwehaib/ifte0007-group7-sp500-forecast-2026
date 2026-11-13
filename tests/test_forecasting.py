"""Meaningful boundary and mathematical tests; never load genuine prices."""
import csv
import contextlib
import hashlib
import io
import json
import math
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sp500_forecast import SYNTHETIC_NOTICE
from sp500_forecast.calendar import is_session, sessions_between, target_session
from sp500_forecast.engine import (Price,common_training_rows,decay_weights,fit_weighted,
                                  forecast_model,read_prices,run_in_memory)
from sp500_forecast.synthetic import synthetic_prices,write_synthetic_csv
from sp500_forecast.cli import main as cli_main


class CalendarTests(unittest.TestCase):
    def test_exceptional_and_regular_closures(self):
        self.assertFalse(is_session(date(2025,1,9)))
        self.assertFalse(is_session(date(2026,6,19)))
        self.assertTrue(is_session(date(2021,12,31)))
        self.assertTrue(is_session(date(2026,11,11)))
        self.assertEqual(target_session(date(2026,11,12)),date(2026,11,20))


class MathematicalTests(unittest.TestCase):
    def test_known_linear_solution_and_weight_scale(self):
        xs=[-.05,-.02,0.,.01,.03,.07]
        ys=[.03-.7*x for x in xs]
        weights=[.1,.2,.4,.8,1.6,3.2]
        first=fit_weighted(xs,ys,weights)
        scaled=fit_weighted(xs,ys,[11*w for w in weights])
        self.assertAlmostEqual(first['alpha'],.03,places=14)
        self.assertAlmostEqual(first['beta'],-.7,places=14)
        self.assertAlmostEqual(first['beta'],scaled['beta'],places=14)
        self.assertAlmostEqual(first['alpha'],scaled['alpha'],places=14)

    def test_calendar_half_life(self):
        weights=decay_weights([date(2020,1,1),date(2022,1,1)],'H24',date(2023,12,31))
        self.assertAlmostEqual(weights[0]/weights[1],2**(-731/730.5),places=14)
        with self.assertRaises(ValueError):
            decay_weights([date(2024,1,1)],'H24',date(2023,12,31))

    def test_common_rows_and_maturity(self):
        prices=synthetic_prices()
        rows=common_training_rows(prices,date(2020,1,1),date(2023,12,31))
        train=[p for p in prices if p.session.year<=2023]
        self.assertEqual(len(rows),960)
        self.assertEqual(rows[0]['origin_date'],'2020-03-02')
        self.assertEqual(rows[-1]['target_date'],'2023-12-29')
        for i,row in enumerate(rows,40):
            self.assertEqual(row['target_date'],str(train[i+6].session))
            self.assertEqual(row['X_5'],train[i].close/train[i-5].close-1)
            self.assertEqual(row['Y_return_6'],train[i+6].close/train[i].close-1)

    def test_forecast_rejects_future_and_fitting_cutoff(self):
        prices=synthetic_prices()
        model={'model_id':'example','kind':'regression','window':'A','scheme':'H24','k':5,
               'cutoff':'2023-12-31','alpha':.001,'beta':-.03}
        origin=date(2026,11,11)
        with self.assertRaises(ValueError):
            forecast_model(model,prices[-41:],origin,target_session(origin))
        prefix=[p for p in prices if p.session<=origin][-41:]
        result=forecast_model(model,prefix,origin,target_session(origin))
        self.assertNotIn('actual_close',result)
        model['cutoff']=str(origin)
        with self.assertRaises(ValueError):
            forecast_model(model,prefix,origin,target_session(origin))


class SyntheticAndSchemaTests(unittest.TestCase):
    def test_saved_forecast_cli_uses_private_synthetic_fixture_without_fitting(self):
        # Fabricated levels, not observations. Temporary private-mode outputs
        # are removed automatically and are never part of the public package.
        dates=['2026-11-05','2026-11-06','2026-11-09','2026-11-10','2026-11-11','2026-11-12']
        values=[1100,1104,1102,1107,1105,1108]
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'fabricated.csv';output=Path(folder)/'output'
            with path.open('w',newline='') as stream:
                writer=csv.writer(stream);writer.writerow(['observation_date','SP500'])
                writer.writerows(zip(dates,values))
            with patch('sp500_forecast.cli.run_in_memory',side_effect=AssertionError('No fitting allowed')):
                with contextlib.redirect_stdout(io.StringIO()):
                    cli_main(['forecast-saved','--input',str(path),'--output',str(output)])
            record=json.loads((output/'private_saved_forecast.json').read_text())
            self.assertFalse(record['fitting_performed'])
            self.assertEqual(record['target'],'2026-11-20')
            self.assertEqual(record['momentum_exact_fraction'],'2/275')
            self.assertEqual(record['model_id'],'ABD_A_H24_k05')

    def test_deterministic_generator_and_labelled_fixture(self):
        self.assertEqual(synthetic_prices(),synthetic_prices())
        self.assertNotEqual(synthetic_prices(1),synthetic_prices(2))
        with tempfile.TemporaryDirectory() as folder:
            output=write_synthetic_csv(Path(folder)/'prices.csv')
            self.assertEqual(output.read_bytes(),(ROOT/'data/synthetic_prices.csv').read_bytes())
            parsed=read_prices(output,synthetic=True)
            self.assertEqual(len(parsed),1726)
            with output.open() as stream:
                self.assertTrue(all(r['data_status']==SYNTHETIC_NOTICE for r in csv.DictReader(stream)))

    def test_invalid_schema_missing_close_and_order(self):
        samples=[
            'Date,Close\n2026-11-05,1000\n',
            'observation_date,SP500\n2026-11-05,\n',
            'observation_date,SP500\n2026-11-05,1000\n2026-11-05,1001\n',
            'observation_date,SP500\n2026-11-05,nan\n',
        ]
        with tempfile.TemporaryDirectory() as folder:
            for i,text in enumerate(samples):
                path=Path(folder)/f'bad{i}.csv';path.write_text(text)
                with self.assertRaises(ValueError):
                    read_prices(path)

    def test_missing_training_session_fails(self):
        prices=synthetic_prices()
        with self.assertRaises(ValueError):
            common_training_rows(prices[:300]+prices[301:],date(2020,1,1),date(2023,12,31))


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=run_in_memory(synthetic_prices())

    def test_native_and_common_dates_are_comparable(self):
        rows=self.result['predictions']
        groups={}
        for row in rows:
            if row['origin_date']>='2026-09-01':
                groups.setdefault(row['model_id'],set()).add((row['origin_date'],row['target_date']))
        self.assertEqual(len(groups),46)
        self.assertTrue(all(len(pairs)==37 for pairs in groups.values()))
        self.assertTrue(all(pairs==groups['UNCHANGED'] for pairs in groups.values()))
        self.assertEqual(sum(r['model_id']=='A_H24_k05' for r in rows),705)
        self.assertEqual(len(rows),12390)
        self.assertEqual({m['n_training'] for m in self.result['models'] if m['window']=='B'},{1628})
        self.assertEqual({m['n_training'] for m in self.result['models'] if m['window']=='C'},{370})

    def test_saved_coefficients_are_not_used_to_generate_synthetic_training(self):
        real_record=json.loads((ROOT/'evidence/official_model.json').read_text())
        synthetic=next(m for m in self.result['models'] if m['model_id']=='A_H24_k05')
        self.assertNotEqual(str(synthetic['alpha']),real_record['coefficients']['alpha'])
        # Public official metadata contains no observation/forecast history.
        forbidden={'prices','origin_close','lag_close','observations','training_rows','forecasts'}
        self.assertFalse(forbidden & set(real_record))

    def test_future_output_is_synthetic_and_distinct(self):
        selected=next(r for r in self.result['future'] if r['model_id']=='A_H24_k05')
        official=json.loads((ROOT/'evidence/model_selection.json').read_text())
        self.assertNotEqual(f"{selected['predicted_close']:.2f}",official['forecast'])
        self.assertEqual(selected['target_date'],'2026-11-20')
        self.assertNotIn('actual_close',selected)


if __name__=='__main__':
    unittest.main(verbosity=2)
