# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
import jdatetime
from odoo.exceptions import AccessError, ValidationError, MissingError, UserError
import json

class SdVisualizePetronadCalculate(models.Model):
    _inherit = 'sd_visualize.calculate'

    def calculate(self, function_name, diagram_id):
        res = super(SdVisualizePetronadCalculate, self).calculate(function_name, diagram_id)
        try:
            if function_name == 'petronad_ethylene_daily':
                res['value'] = self.petronad_ethylene_daily(diagram_id)
            elif function_name == 'petronad_ethylene_weekly':
                res['value'] = self.petronad_ethylene_weekly(diagram_id)
        except Exception as err:
            logging.error(f'CALCULATION:{function_name}/ {err}')
            raise ValidationError(f'CALCULATION:{function_name}/ {err}')
        # print(f'-------> SdVcalculateDataPetronad {function_name} {diagram_id} {res}')
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
            # print(f'hhhhhhhhhh {rec.sequence}  {rec.variable_name}')
            if not rec.calculate:
                continue

            if rec.variable_name == 'report_date':
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
            # HEAVY1
            elif rec.variable_name == 'h1_production':
                value = self.float_num(productions[0].h1_production, 2)
            # HEAVY2
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
            # HEAVY1
            elif rec.variable_name == 'h1_storage':
                value = self.float_num(storages.h1_storage, 2)
            # HEAVY2
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
            # HEAVY1
            elif rec.variable_name == 'h1_tank':
                value = self.float_num(tanks.h1_tank - storages.h1_storage, 2)
            # HEAVY2
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
                    'name': 'HEAVY1',
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


            # elif rec.variable_name == 'meg_sale':
            #     meg_sale = round(sum(meg_sale_list), 2)
            #     value = self.float_num(sum(meg_sale_list), 2)
            # elif rec.variable_name == 'meg_stock':
            #     value = self.float_num(meg_production - meg_sale, 2)
            # elif rec.variable_name == 'meg_feed':
            #     value = self.float_num(meg_production * 100 / feed_out, 2) if feed_out > 0 else 0
            # # deg
            # elif rec.variable_name == 'deg_production':
            #     deg_production = round(sum(deg_production_list), 2)
            #     value = self.float_num(sum(deg_production_list), 2)
            # elif rec.variable_name == 'deg_sale':
            #     deg_sale = round(sum(deg_sale_list), 2)
            #     value = self.float_num(sum(deg_sale_list), 2)
            # elif rec.variable_name == 'deg_stock':
            #     value = self.float_num(deg_production - deg_sale, 2)
            # elif rec.variable_name == 'deg_feed':
            #     value = self.float_num(deg_production * 100 / feed_out, 2) if feed_out > 0 else 0
            #
            # # teg
            # elif rec.variable_name == 'teg_production':
            #     teg_production = round(sum(teg_production_list), 2)
            #     value = self.float_num(sum(teg_production_list), 2)
            # elif rec.variable_name == 'teg_sale':
            #     teg_sale = round(sum(teg_sale_list), 2)
            #     value = self.float_num(sum(teg_sale_list), 2)
            # elif rec.variable_name == 'teg_stock':
            #     value = self.float_num(teg_production - teg_sale, 2)
            # elif rec.variable_name == 'teg_feed':
            #     value = self.float_num(teg_production * 100 / feed_out, 2) if feed_out > 0 else 0
            #
            #
            # # h1
            # elif rec.variable_name == 'h1_production':
            #     h1_production = round(sum(h1_production_list), 2)
            #     value = self.float_num(sum(h1_production_list), 2)
            # elif rec.variable_name == 'h1_stock':
            #     value = self.float_num(h1_production, 2)
            # elif rec.variable_name == 'h1_feed':
            #     value = self.float_num(h1_production * 100 / feed_out, 2) if feed_out > 0 else 0
            #
            #
            # # h2
            # elif rec.variable_name == 'h2_production':
            #     h2_production = round(sum(h2_production_list), 2)
            #     value = self.float_num(sum(h2_production_list), 2)
            # elif rec.variable_name == 'h2_sale':
            #     h2_sale = round(sum(h2_sale_list), 2)
            #     value = self.float_num(sum(h2_sale_list), 2)
            # elif rec.variable_name == 'h2_stock':
            #     value = self.float_num(h2_production - h2_sale, 2)
            # elif rec.variable_name == 'h2_feed':
            #     value = self.float_num(h2_production * 100 / feed_out, 2) if feed_out > 0 else 0
            #
            #
            #
            # # ww
            # elif rec.variable_name == 'ww_production':
            #     production_sum = meg_production + deg_production + teg_production + h1_production + h2_production
            #     ww_production = round(feed_out - production_sum, 2)
            #     value = self.float_num(ww_production, 2)
            #
            #
            # elif rec.variable_name == 'ww_feed':
            #     value = self.float_num(ww_production * 100 / feed_out, 2) if feed_out > 0 else 0
            #
            # elif rec.variable_name == 'feed_purity':
            #     purity_sum = meg_production + deg_production + teg_production + h1_production * 0.95
            #     value = self.float_num((purity_sum / feed_out), 2) if feed_out > 0 else 0


            else:
                continue

            results.append((rec.id, value))

        for rec in results:
            value_model.browse(rec[0]).write({'value': rec[1]})

        return {'name': 'arash'}

        # return 'PETRONAD'

    def petronad_ethylene_weekly(self, diagram=0):
        diagram = self.env['sd_visualize.diagram'].browse(diagram)
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        value_model = self.env['sd_visualize.values']
        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])
        week_production_plan = 126

        production = self.env['km_petronad.production'].search([('project', '=', diagram.project.id),],order='production_date desc', limit=1,)
        if len(production) == 0:
            raise ValidationError(f'Production not found')

        # finding tha last week
        # week_e_x : friday
        # week_s_x : saturday
        this_date = production.production_date
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
        print(f'DDDDDDDDD>>> '
              f'\n this_date: {this_date}'
              f'\n week_s_0: {week_s_0}    week_e_0: {week_e_0}'
              f'\n week_s_5: {week_s_5}    week_e_5: {week_e_5}'
              f'')


        productions = self.env['km_petronad.production'].search([('project', '=', diagram.project.id),
                                                                 ('production_date', '>=', week_s_5),
                                                                 ('production_date', '<=', week_e_0),]
                                                                ,order='production_date desc', )
        if len(productions) == 0:
            raise ValidationError(f'Production not found')
        week_production_0 = [rec for rec in productions if rec.production_date >= week_s_0 and rec.production_date <= week_e_0]
        week_production_1 = [rec for rec in productions if rec.production_date >= week_s_1 and rec.production_date <= week_e_1]
        week_production_2 = [rec for rec in productions if rec.production_date >= week_s_2 and rec.production_date <= week_e_2]
        week_production_3 = [rec for rec in productions if rec.production_date >= week_s_3 and rec.production_date <= week_e_3]
        week_production_4 = [rec for rec in productions if rec.production_date >= week_s_4 and rec.production_date <= week_e_4]
        week_production_5 = [rec for rec in productions if rec.production_date >= week_s_5 and rec.production_date <= week_e_5]
        week_sum_production_0 = sum(
            list([rec.meg_production + rec.deg_production + rec.teg_production for rec in week_production_0]))
        week_sum_production_1 = sum(
            list([rec.meg_production + rec.deg_production + rec.teg_production for rec in week_production_1]))
        week_sum_production_2 = sum(
            list([rec.meg_production + rec.deg_production + rec.teg_production for rec in week_production_2]))
        week_sum_production_3 = sum(
            list([rec.meg_production + rec.deg_production + rec.teg_production for rec in week_production_3]))
        week_sum_production_4 = sum(
            list([rec.meg_production + rec.deg_production + rec.teg_production for rec in week_production_4]))
        week_sum_production_5 = sum(
            list([rec.meg_production + rec.deg_production + rec.teg_production for rec in week_production_5]))
        week_feeds = self.env['km_petronad.feeds'].search([('project', '=', diagram.project.id),
                                                                 ('feed_date', '>=', week_s_0),
                                                                 ('feed_date', '<=', week_e_0),]
                                                                ,order='feed_date desc', )
        # if len(feeds) == 0:
        #     raise ValidationError(f'Feeds not found')

        storages = self.env['km_petronad.storage'].search([('project', '=', diagram.project.id),('storage_date', '<=', productions[0].production_date)],order='id desc', limit=1,)
        if  len(storages) == 0:
            raise ValidationError(f'Storage not found')
        tanks = self.env['km_petronad.tanks'].search([('project', '=', diagram.project.id),('tanks_date', '<=', productions[0].production_date)],order='id desc', limit=1,)
        if  len(tanks) == 0:
            raise ValidationError(f'Tank not found')
        comments = self.env['km_petronad.comments'].search([('project', '=', diagram.project.id),('date', '=', productions[0].production_date)], order='sequence desc')


        results = []
        for rec in sorted_values:
            if not rec.calculate:
                continue
            elif rec.variable_name == 'week_days':
                value = f'{self.convert_date(calendar, week_s_0)}-{self.convert_date(calendar, week_e_0)}'
            # Feed Purchased
            elif rec.variable_name == 'week_feed_purchased':
                if len(week_feeds) > 0:
                    value = self.float_num(sum(list([rec.feed_amount for rec in week_feeds])), 2)
                else:
                    value = 0
            # Feed Used

            elif rec.variable_name == 'week_feed_used':
                value = self.float_num(sum(list([rec.feed for rec in  productions])), 2)
            # Production sum
            elif rec.variable_name == 'week_production':

                value = self.float_num(week_sum_production_0, 2)
            # Sale sum
            elif rec.variable_name == 'week_sale':
                value = 'None'

            elif rec.variable_name == 'chart_1':
                week_sum_production_list = [week_sum_production_5,week_sum_production_4,week_sum_production_3,week_sum_production_2,week_sum_production_1,week_sum_production_0]
                week_avr_production = self.float_num(sum(week_sum_production_list) / 6, 2)
                performance_list = list(map(lambda x: self.float_num(x * 100 / week_production_plan, 0) if week_production_plan else 0, week_sum_production_list ))
                # print(f'sssssssssssssss>>>> performance_list: {performance_list}')
                trace1 = {
                    'x': ['5th', '4th', '3rd','2nd', '1st', 'This week'],
                    'y': [week_sum_production_5,week_sum_production_4,week_sum_production_3,week_sum_production_2,week_sum_production_1,week_sum_production_0],
                    'text': [week_sum_production_5,week_sum_production_4,week_sum_production_3,week_sum_production_2,week_sum_production_1,week_sum_production_0],
                    'name': 'Production',
                    'type': 'bar',
                    'marker': {
                        'color': 'rgb(169,209,142)',
                    },
                }
                trace2 = {
                    'x': ['5th', '4th', '3rd','2nd', '1st', 'This week'],
                    'y': [week_production_plan, week_production_plan, week_production_plan, week_production_plan, week_production_plan, week_production_plan, ],
                    'name': 'Plan',
                    'mode': 'lines',
                    'line': {
                        'color': 'rgb(80,130,50)',
                    },
                }
                trace3 = {
                    'x': ['5th', '4th', '3rd','2nd', '1st', 'This week'],
                    'y': [week_avr_production,week_avr_production,week_avr_production,week_avr_production,week_avr_production,week_avr_production,week_avr_production,],
                    'name': 'Average',
                    'mode': 'lines',

                    'line': {
                        'dash': 'dot',
                        'width': 2,
                        'color': 'rgb(169,100,0)'
                    }
                }
                trace4 = {
                    'x': ['5th', '4th', '3rd','2nd', '1st', 'This week'],
                    'y': performance_list,
                    'text': [1,2,3,4,5,6],
                    'name': _('Efficiency'),
                    'mode': 'lines',
                    'yaxis': 'y2',

                    'line': {
                        'dash': 'dot',
                        'width': 2,
                        'color': 'rgb(90,150,210)'
                    }
                }
                plot_value = {
                    'data': [trace1, trace2, trace3, trace4, ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'legend': {"orientation": "h"},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {
                                   'title': _('Production(tone)'),
                                   'fixedrange': True
                               },
                               'yaxis2': {
                                   'overlaying': 'y',
                                   'side': 'right',
                                   'range': [0, 100],
                                   'fixedrange': True,
                                   'title': _('Efficiency(%)'),
                               }
                               },
                    'config': {'responsive': True, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)

            elif rec.variable_name == 'chart_2':
                trace1 = {
                    'x': ['5th', '4th', '3rd', '2nd', '1st', 'This week'],
                    'y': [200, 0, 0, 400, 0, 0],
                    'name': 'Sale',
                    'type': 'bar',
                    'marker': {
                        'color': 'rgb(70,110,200)',
                    },
                }
                plot_value = {
                    'data': [trace1,  ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'legend': {"orientation": "h"},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {
                                   'fixedrange': True
                               },

                               },
                    'config': {'responsive': True, 'displayModeBar': False}
                }


                value = json.dumps(plot_value)
            elif rec.variable_name == 'chart_3':
                theta = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه',]
                week_feeds
                trace1 = {
                          'type': 'scatterpolar',
                          'r': [30, 30, 30, 30, 30, 30, 30, ],
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Feed Plan'
                          }
                trace2 = {
                          'type': 'scatterpolar',
                          'r': [25, 27, 25, 28, 24, 0, 30],
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Average',
                          'line': {
                                'dash': 'dash',
                                },
                          }
                trace3 = {
                          'type': 'scatterpolar',
                          'r': [25, 27, 25, 28, 24, 0, 30],
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Daily Feed'
                          }
                plot_value = {
                    'data': [trace1, trace2, trace3,  ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'legend': {"orientation": "h"},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {
                                   'fixedrange': True
                               },
                               'angularaxis': {
                                   'direction': "clockwise",
                                   'period': 6
                               },
                               'polar': {
                                   'radialaxis': {
                                       'angle': 90,
                                       'textangle': 90,
                                       'showgrid': False,
                                       'showline': False,
                                       'tickangle': 90,
                                       'CanvasGradient': False,
                                   },
                                   'angularaxis': {
                                       'direction': "clockwise",
                                       'visible': True,
                                       'linecolor': 'rgb(255,255,255,0)'
                                   },
                               },
                               },
                    'config': {'responsive': True, 'displayModeBar': False}
                }


                value = json.dumps(plot_value)


            else:
                continue

            results.append((rec.id, value))

        for rec in results:
            value_model.browse(rec[0]).write({'value': rec[1]})

        return {'name': 'arash'}


    def float_num(self, num, points=2):
        fnum = round(num, int(points))
        frac = fnum - int(fnum)
        return str(int(fnum)) if frac == 0 else str(fnum)

    def convert_date(self, lang='en_US', this_date=date.today()):
        if lang == 'fa_IR':
            # first_day = jdatetime.date.fromgregorian(date=end_date).replace(day=1)
            # next_month = first_day.replace(day=28) + timedelta(days=5)
            # last_day = (next_month - timedelta(days=next_month.day)).togregorian()
            # first_day = first_day.togregorian
            s_this_date = jdatetime.date.fromgregorian(date=this_date).strftime("%Y/%m/%d")
        else:
            # first_day = end_date.replace(day=1)
            # next_month = first_day.replace(day=28) + timedelta(days=5)
            # last_day = next_month - timedelta(days=next_month.day)

            s_this_date = this_date.strftime("%Y/%m/%d")

        return s_this_date