# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
import jdatetime
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
import json
import traceback


class SdVisualizePetronadCalculate(models.Model):
    _inherit = 'sd_visualize.calculate'

    def calculate(self, function_name, diagram_id, update_date):
        res = super(SdVisualizePetronadCalculate, self).calculate(function_name, diagram_id, update_date)
        # print(f'------>\n  Calculate: {self.env.context} diagram_id: {diagram_id}\n ')

        try:
            if function_name == 'petronad_ethylene_weekly':
                res['value'] = self.petronad_ethylene_weekly(diagram_id, update_date)
        #         todo: to prevent too many update requests, we can check some value write datetiem record.
        #           It seams that 10 seconds could be a good interval between two updates
        except Exception as err:
            logging.error(f'CALCULATION:{function_name}:\n{traceback.format_exc()}')
            raise ValidationError(f'CALCULATION:{function_name}/ {err}')
        return res


    def petronad_ethylene_weekly(self, diagram=0, update_date=0):
        diagram = self.env['sd_visualize.diagram'].browse(diagram)
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        value_model = self.env['sd_visualize.values']
        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])
        week_production_plan = 126
        report_date = date.fromisoformat(update_date)

        # to fix selection of friday. This way it pretends it is selected wednesday.
        this_date = report_date - timedelta(days=2) if report_date.weekday() == 4 else report_date

        week_e_0 = this_date + relativedelta(weekday=FR(-1))
        week_s_0 = week_e_0 + relativedelta(weekday=SA(-1))
        week_e_1 = this_date + relativedelta(weekday=FR(-2))
        week_s_1 = week_e_0 + relativedelta(weekday=SA(-2))
        week_e_2 = this_date + relativedelta(weekday=FR(-3))
        week_s_2 = week_e_0 + relativedelta(weekday=SA(-3))
        week_e_3 = this_date + relativedelta(weekday=FR(-4))
        week_s_3 = week_e_0 + relativedelta(weekday=SA(-4))
        week_e_4 = this_date + relativedelta(weekday=FR(-5))
        week_s_4 = week_e_0 + relativedelta(weekday=SA(-5))
        week_e_5 = this_date + relativedelta(weekday=FR(-6))
        week_s_5 = week_e_0 + relativedelta(weekday=SA(-6))

        # Production ##################################
        productions = self.env['km_petronad.production_record'].search([
                                                                 ('data_date', '>=', week_s_5),
                                                                 ('data_date', '<=', week_e_0), ]
                                                                ,order='data_date desc', )
        # if len(productions) != 0:
            # raise ValidationError(f'Production not found')
        week_production_0 = [rec for rec in productions if rec.data_date >= week_s_0 and rec.data_date <= week_e_0]
        week_production_1 = [rec for rec in productions if rec.data_date >= week_s_1 and rec.data_date <= week_e_1]
        week_production_2 = [rec for rec in productions if rec.data_date >= week_s_2 and rec.data_date <= week_e_2]
        week_production_3 = [rec for rec in productions if rec.data_date >= week_s_3 and rec.data_date <= week_e_3]
        week_production_4 = [rec for rec in productions if rec.data_date >= week_s_4 and rec.data_date <= week_e_4]
        week_production_5 = [rec for rec in productions if rec.data_date >= week_s_5 and rec.data_date <= week_e_5]

        week_sum_feed = sum(list([self.ton_amount(rec) for rec in week_production_0
                                  if rec.fluid.name in ['FEED']
                                  and rec.register_type == 'feed_usage']))
        week_sum_feed_h1 = sum(list([self.ton_amount(rec) for rec in week_production_0
                                     if rec.fluid.name in ['HEAVY1']
                                     and rec.register_type == 'feed_usage']))
        week_productions_list = {'meg': [], 'deg': [], 'teg': [], }
        date_week_day = list([week_s_0 + timedelta(days=i) for i in range(7)])
        for rec_date in date_week_day:
            day_meg = sum(list([self.ton_amount(rec) for rec in week_production_0
                                if rec.fluid.name in ['MEG']
                                and rec.register_type == 'production'
                                and rec.data_date == rec_date]))
            day_deg = sum(list([self.ton_amount(rec) for rec in week_production_0
                                if rec.fluid.name in ['DEG']
                                and rec.register_type == 'production'
                                and rec.data_date == rec_date]))
            day_teg = sum(list([self.ton_amount(rec) for rec in week_production_0
                                if rec.fluid.name in ['TEG']
                                and rec.register_type == 'production'
                                and rec.data_date == rec_date]))
            week_productions_list['meg'].append(day_meg)
            week_productions_list['deg'].append(day_deg)
            week_productions_list['teg'].append(day_teg)

        week_sum_meg = sum(week_productions_list['meg'])
        week_sum_deg = sum(week_productions_list['deg'])
        week_sum_teg = sum(week_productions_list['teg'])

        week_sum_h1 = sum(list([self.ton_amount(rec) for rec in week_production_0
                                if rec.fluid.name in ['HEAVY1']
                                and rec.register_type == 'production']))
        week_sum_h2 = sum(list([self.ton_amount(rec) for rec in week_production_0
                                if rec.fluid.name in ['HEAVY2']
                                and rec.register_type == 'production']))
        week_sum_production_0 = sum(list([self.ton_amount(rec) for rec in week_production_0
                                          if rec.fluid.name
                                          in ['MEG', 'DEG', 'TEG']
                                          and rec.register_type == 'production']))
        week_sum_production_1 = sum(list([self.ton_amount(rec) for rec in week_production_1
                                          if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                          and rec.register_type == 'production' ]))
        week_sum_production_2 = sum(list([self.ton_amount(rec) for rec in week_production_2
                                          if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                          and rec.register_type == 'production']))


        # Results ##################################
        results = []
        for rec in sorted_values:
            if not rec.calculate:
                continue
            elif rec.variable_name == 'test':
                value = f'{week_productions_list} '
            elif rec.variable_name == 'week_days':
                # value = f'{self.convert_date(calendar, week_e_0)}  -  {self.convert_date(calendar, week_s_0)}'
                value = f'''
                    <div class="d-flex flex-column align-items-end">
                        <div>{self.convert_date(calendar, week_s_0)}</div>
                        <div>{self.convert_date(calendar, week_e_0)}</div>
                    </div>
                        '''
            elif rec.variable_name == 'week_no':
                value = jdatetime.date.fromgregorian(date=week_s_0).weeknumber()
            elif rec.variable_name == 'year':
                value = jdatetime.date.fromgregorian(date=week_s_0).year
            elif rec.variable_name == 'comments_weekly':
                value = self.env['km_petronad.comments_weekly'].search([('comment_date', '=', week_e_0)]).description

            # if len(productions) != 0:
            elif rec.variable_name == 'week_sum_feed':
                value = abs(week_sum_feed)
            elif rec.variable_name == 'week_sum_feed_h1':
                value = abs(week_sum_feed_h1)
            elif rec.variable_name == 'week_sum_meg':
                value = week_sum_meg
            elif rec.variable_name == 'week_sum_deg':
                value = week_sum_deg
            elif rec.variable_name == 'week_sum_teg':
                value = week_sum_teg
            elif rec.variable_name == 'week_sum_h1':
                value = week_sum_h1
            elif rec.variable_name == 'week_sum_h2':
                value = week_sum_h2

            elif rec.variable_name == 'week_sum_production':
                value = week_sum_production_0

            elif rec.variable_name == 'chart_1':
                week_no_0 = jdatetime.date.fromgregorian(date=week_s_0).weeknumber()
                week_no_1 = jdatetime.date.fromgregorian(date=week_s_1).weeknumber()
                week_no_2 = jdatetime.date.fromgregorian(date=week_s_2).weeknumber()
                three_weeks = [  f'{week_no_2} هفته', f'{week_no_1} هفته', f'{week_no_0} هفته', ]


                week_sum_production_list = [ week_sum_production_2, week_sum_production_1, week_sum_production_0]
                week_avr_production = self.float_num(sum(week_sum_production_list) / 6, 2)
                performance_list = list(
                    map(lambda x: self.float_num(x * 100 / week_production_plan, 0) if week_production_plan else 0,
                        week_sum_production_list))
                trace1 = {
                    'x': three_weeks,
                    'y': week_sum_production_list,
                    'text': week_sum_production_list,
                    'name': 'Production',
                    'type': 'bar',
                    'marker': {
                        'color': 'rgb(169,209,142)',
                    },
                    'textposition': 'outside',

                }
                trace2 = {
                    'x': three_weeks,
                    'y': [week_production_plan, week_production_plan, week_production_plan, week_production_plan,
                          week_production_plan, week_production_plan, ],
                    'name': 'Plan',
                    'mode': 'lines',
                    'line': {
                        'color': 'rgb(80,130,50)',
                    },
                }
                trace3 = {
                    'x': three_weeks,
                    'y': [week_avr_production, week_avr_production, week_avr_production, week_avr_production,
                          week_avr_production, week_avr_production, week_avr_production, ],
                    'name': 'Average',
                    'mode': 'lines',

                    'line': {
                        'dash': 'dash',
                        'width': 2,
                        'color': 'rgb(80,130,50)',
                    }
                }
                # trace4 = {
                #     'x': six_weeks,
                #     'y': performance_list,
                #     'text': [1,2,3,4,5,6],
                #     'name': _('Efficiency'),
                #     'mode': 'lines',
                #     'yaxis': 'y2',
                #
                #     'line': {
                #         'dash': 'dot',
                #         'width': 2,
                #         'color': 'rgb(90,150,210)'
                #     }
                # }
                plot_value = {
                    'data': [trace1, trace2, trace3, ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'legend': {'x': 1.2, 'y': 1, 'xanchor': 'right',},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {
                                   # 'title': _('Production(tone)'),
                                   'fixedrange': True,
                                   'range': [0, week_production_plan * 1.2],

                               },
                               'yaxis2': {
                                   'overlaying': 'y',
                                   'side': 'right',
                                   'range': [0, 100],
                                   'fixedrange': True,
                                   'title': _('Efficiency(%)'),
                               }
                               },
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)

            elif rec.variable_name == 'chart_2':
                def week_day(date_time, i):
                    jdate = jdatetime.date.fromgregorian(date=date_time + timedelta(days=i))
                    return f'{jdate.month}/{jdate.day}'

                week_days = [ week_day(week_s_0, i)  for i in range(7)]

                chart_2_y_1 = week_productions_list['meg']
                chart_2_y_2 = week_productions_list['deg']
                chart_2_y_3 = week_productions_list['teg']
                chart_2_y_total = list([chart_2_y_1[i] + chart_2_y_2[i] + chart_2_y_3[i] for i in range(7)])


                trace1 = {
                    'x': week_days,
                    'y': chart_2_y_1,
                    'text': chart_2_y_1,
                    'name': 'MEG',
                    'type': 'bar',
                    'textposition': 'top',
                    'marker': {
                        'color': 'rgb(30,80,120)'
                    }
                }
                trace2 = {
                    'x': week_days,
                    'y': chart_2_y_2,
                    'text': chart_2_y_2,
                    'name': 'DEG',
                    'type': 'bar',
                    'textposition': 'top',
                    'marker': {
                        'color': 'rgb(0,110,200)'
                    }
                }
                trace3 = {
                    'x': week_days,
                    'y': chart_2_y_3,
                    'text': chart_2_y_3,
                    'name': 'TEG',
                    'type': 'bar',
                    'textposition': 'top',
                    'marker': {
                        'color': 'rgb(160,200,230)'
                    }
                }
                trace4 = {
                    'x': week_days,
                    'y': chart_2_y_total,
                    'text': chart_2_y_total,
                    'name': 'Total',

                    'type': 'scatter',
                    'mode': 'lines+text',
                    'textposition': 'top',
                    'line': {
                        'color': 'rgba(0,0,0,0)',
                    }
                }
                plot_value = {
                    'data': [trace1, trace2, trace3,  trace4,  ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'barmode': 'stack',
                               'legend': {'x': 1.2, 'y': 1, 'xanchor': 'right',},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {
                                   # 'title': _('Production(tone)'),
                                   'fixedrange': True,
                                   'range': [0, max(chart_2_y_total) * 1.2],

                               },
                               'yaxis2': {
                                   'overlaying': 'y',
                                   'side': 'right',
                                   'range': [0, 100],
                                   'fixedrange': True,
                                   'title': _('Efficiency(%)'),
                               }
                               },
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)

            else:
                continue

            results.append((rec.id, value))

        # Update Values ##################################
        for rec in results:
            value_model.browse(rec[0]).write({'value': rec[1]})

        return {'name': 'arash'}



    def create_weekly_list(self, records, lang):
        new_record_list = [0, 0, 0, 0, 0, 0, 0, ]
        week_days = [5, 6, 0, 1, 2, 3, 4, ]
        for rec in records:
            index = week_days.index(rec.data_date.weekday())
            new_record_list[index] = rec
        return new_record_list

    def ton_amount(self, rec):
        return int(rec.amount * 0.001) if rec.unit == 'kg' else rec.amount
