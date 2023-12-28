# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
import jdatetime
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
import json
class SdVisualizePetronadCalculateDaily(models.Model):
    _inherit = 'sd_visualize.calculate'

    def calculate(self, function_name, diagram_id):
        res = super(SdVisualizePetronadCalculateDaily, self).calculate(function_name, diagram_id)
        try:
            if function_name == 'petronad_ethylene_daily':
                res['value'] = self.petronad_ethylene_daily(diagram_id)
        except Exception as err:
            logging.error(f'CALCULATION:{function_name}/ {err}')
            raise ValidationError(f'CALCULATION:{function_name}/ {err}')
        return res


    def petronad_ethylene_daily(self, diagram=0, start_date=date.today() - timedelta(days=30), end_date=date.today()):
        diagram = self.env['sd_visualize.diagram'].browse(diagram)
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        value_model = self.env['sd_visualize.values']
        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])

        productions = self.env['km_petronad.production'].search([('project', '=', diagram.project.id),],order='production_date desc', limit=3,)
        if len(productions) == 0:
            raise ValidationError(f'Production not found')
        storages = self.env['km_petronad.storage'].search([('project', '=', diagram.project.id),('storage_date', '<=', productions[0].production_date)],order='storage_date desc', limit=1,)
        if  len(storages) == 0:
            raise ValidationError(f'Storage not found')
        tanks = self.env['km_petronad.tanks'].search([('project', '=', diagram.project.id),('tanks_date', '<=', productions[0].production_date)],order='tanks_date desc', limit=1,)
        if  len(tanks) == 0:
            raise ValidationError(f'Tank not found')
        comments = self.env['km_petronad.comments'].search([('project', '=', diagram.project.id),('date', '=', productions[0].production_date)], order='sequence desc')

        if calendar == 'fa_IR':
            # first_day = jdatetime.date.fromgregorian(date=end_date).replace(day=1)
            # next_month = first_day.replace(day=28) + timedelta(days=5)
            # last_day = (next_month - timedelta(days=next_month.day)).togregorian()
            # first_day = first_day.togregorian
            s_start_date = jdatetime.date.fromgregorian(date=productions[0].production_date).strftime("%Y/%m/%d")
            s_storage_date = jdatetime.date.fromgregorian(date=storages.storage_date).strftime("%Y/%m/%d")
            # s_end_date = jdatetime.date.fromgregorian(date=end_date).strftime("%Y/%m/%d")

        else:
            # first_day = end_date.replace(day=1)
            # next_month = first_day.replace(day=28) + timedelta(days=5)
            # last_day = next_month - timedelta(days=next_month.day)
            s_start_date = productions[0].production_date.strftime("%Y/%m/%d")
            s_storage_date = storages.storage_date.strftime("%Y/%m/%d")
            # s_end_date = end_date.strftime("%Y/%m/%d")


        results = []
        for rec in sorted_values:
            if not rec.calculate:
                continue

            elif rec.variable_name == 'report_date':
                value = s_start_date
            # MEG
            elif rec.variable_name == 'meg_production':
                value = self.float_num(productions[0].meg_production, 2)
            # DEG
            elif rec.variable_name == 'deg_production':
                value = self.float_num(productions[0].deg_production, 2)
            # TEG
            elif rec.variable_name == 'teg_production':
                value = self.float_num(productions[0].teg_production, 2)
            # H1
            elif rec.variable_name == 'h1_production':
                value = self.float_num(productions[0].h1_production, 2)
            # H2
            elif rec.variable_name == 'h2_production':
                value = self.float_num(productions[0].h2_production, 2)
            # WW
            elif rec.variable_name == 'ww_production':
                value = self.float_num(productions[0].ww_production, 2)
            # Feed
            elif rec.variable_name == 'feed':
                value = self.float_num(productions[0].feed, 2)
            # Workers
            elif rec.variable_name == 'workers':
                value = self.float_num(productions[0].workers, 2)
            # MEG
            elif rec.variable_name == 'meg_storage':
                value = self.float_num(storages.meg_storage, 2)
            # DEG
            elif rec.variable_name == 'deg_storage':
                value = self.float_num(storages.deg_storage, 2)
            # TEG
            elif rec.variable_name == 'teg_storage':
                value = self.float_num(storages.teg_storage, 2)
            # H1
            elif rec.variable_name == 'h1_storage':
                value = self.float_num(storages.h1_storage, 2)
            # H2
            elif rec.variable_name == 'h2_storage':
                value = self.float_num(storages.h2_storage, 2)
            # WW
            elif rec.variable_name == 'ww_storage':
                value = self.float_num(storages.ww_storage, 2)
            # Feed
            elif rec.variable_name == 'feed_storage':
                value = self.float_num(storages.feed_storage, 2)
            # storage_date
            elif rec.variable_name == 'storage_date':
                value = s_storage_date

            # MEG
            elif rec.variable_name == 'meg_tank':
                value = self.float_num(tanks.meg_tank - storages.meg_storage, 2)
            # DEG
            elif rec.variable_name == 'deg_tank':
                value = self.float_num(tanks.deg_tank - storages.deg_storage, 2)
            # TEG
            elif rec.variable_name == 'teg_tank':
                value = self.float_num(tanks.teg_tank - storages.teg_storage, 2)
            # H1
            elif rec.variable_name == 'h1_tank':
                value = self.float_num(tanks.h1_tank - storages.h1_storage, 2)
            # H2
            elif rec.variable_name == 'h2_tank':
                value = self.float_num(tanks.h2_tank - storages.h2_storage, 2)
            # WW
            elif rec.variable_name == 'ww_tank':
                value = self.float_num(tanks.ww_tank - storages.ww_storage, 2)
            # Feed
            elif rec.variable_name == 'feed_tank':
                value = self.float_num(tanks.feed_tank_1 + tanks.feed_tank_2 - storages.feed_storage, 2)
            # Commnets
            elif rec.variable_name == 'comments':
                if len(comments) > 0:
                    value = '\n'.join(list([rec.comment for rec in comments]))
                else:
                    value = ''

            elif rec.variable_name == 'chart_1':
                trace1 = {
                    'x': ['Two days', 'day before', 'That day'],
                    'y': [productions[2].feed, productions[1].feed, productions[0].feed],
                    'name': 'Feed',
                    'type': 'bar'
                }
                trace2 = {
                    'x': ['Two days', 'day before', 'That day'],
                    'y': [productions[2].meg_production, productions[1].meg_production, productions[0].meg_production],
                    'name': 'MEG',
                    'type': 'bar'
                }
                trace3 = {
                    'x': ['Two days', 'day before', 'That day'],
                    'y': [productions[2].h1_production, productions[1].h1_production, productions[0].h1_production],
                    'name': 'H1',
                    'type': 'bar'
                }

                plot_value = {
                    'data': [trace1, trace2, trace3, ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'legend': {"orientation": "h"},
                               'xaxis': {'fixedrange': True}, 'yaxis': {'fixedrange': True}, },
                    'config': {'responsive': True, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)

            elif rec.variable_name == 'chart_2':
                trace1 = {
                    'x': ['Two days', 'day before', 'That day'],
                    'y': [productions[2].feed * 100 / 30, productions[1].feed * 100 / 30, productions[0].feed * 100 / 30],
                    # 'text': [productions[2].feed * 100 / 30, productions[1].feed * 100 / 30, productions[0].feed * 100 / 30],
                    # 'textposition': 'auto',
                    # 'hoverinfo': 'none',
                    'name': 'Feed',
                    'type': 'line'
                }
                plot_value = {
                    'data': [trace1, ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'legend': {"orientation": "h"},
                               'xaxis': {'fixedrange': True}, 'yaxis': {'fixedrange': True}, },
                    'config': {'responsive': True, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)



            else:
                continue
            results.append((rec.id, value))
        for rec in results:
            value_model.browse(rec[0]).write({'value': rec[1]})
        return {'name': 'arash'}



