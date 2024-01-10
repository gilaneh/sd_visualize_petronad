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
        # print(f'--------->\n    diagarm.select_date: {diagram.select_date}')
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        value_model = self.env['sd_visualize.values']
        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])
        week_production_plan = 126
        report_date = date.fromisoformat(update_date)

        production = self.env['km_petronad.production'].search([('project', '=', diagram.project.id),
                                                                ('production_date', '<=', report_date),]
                                                               , order='production_date desc', limit=1,)
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
        
        # Production ##################################
        productions = self.env['km_petronad.production'].search([('project', '=', diagram.project.id),
                                                                 ('production_date', '>=', week_s_5),
                                                                 ('production_date', '<=', week_e_0), ]
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
        
        # Sale ##################################
        week_sales = self.env['km_petronad.sale'].search([('project', '=', diagram.project.id),
                                                     ('sale_date', '>=', week_s_0),
                                                     ('sale_date', '<=', week_e_0)],
                                                    order='sale_date desc', )
        print(f'==========> week_sales: {week_sales}')

        sales = self.env['km_petronad.sale'].search([('project', '=', diagram.project.id),
                                                     ('sale_date', '>=', week_s_5),
                                                     ('sale_date', '<=', week_e_0)],
                                                    order='sale_date desc', )
        if len(sales) > 0:
            week_sale_0 = [rec for rec in sales if
                                 rec.sale_date >= week_s_0 and rec.sale_date <= week_e_0]
            week_sale_1 = [rec for rec in sales if
                                 rec.sale_date >= week_s_1 and rec.sale_date <= week_e_1]
            week_sale_2 = [rec for rec in sales if
                                 rec.sale_date >= week_s_2 and rec.sale_date <= week_e_2]
            week_sale_3 = [rec for rec in sales if
                                 rec.sale_date >= week_s_3 and rec.sale_date <= week_e_3]
            week_sale_4 = [rec for rec in sales if
                                 rec.sale_date >= week_s_4 and rec.sale_date <= week_e_4]
            week_sale_5 = [rec for rec in sales if
                                 rec.sale_date >= week_s_5 and rec.sale_date <= week_e_5]
            week_sum_sale_0 = sum(
                list([rec.amount for rec in week_sale_0]))
            week_sum_sale_1 = sum(
                list([rec.amount for rec in week_sale_1]))
            week_sum_sale_2 = sum(
                list([rec.amount for rec in week_sale_2]))
            week_sum_sale_3 = sum(
                list([rec.amount for rec in week_sale_3]))
            week_sum_sale_4 = sum(
                list([rec.amount for rec in week_sale_4]))
            week_sum_sale_5 = sum(
                list([rec.amount for rec in week_sale_5]))
        
        # Feeds ##################################
        week_feeds = self.env['km_petronad.feeds'].search([('project', '=', diagram.project.id),
                                                     ('feed_date', '>=', week_s_0),
                                                     ('feed_date', '<=', week_e_0)],
                                                    order='feed_date desc', )
        # Storages ##################################
        storages = self.env['km_petronad.storage'].search([('project', '=', diagram.project.id),
                                                           ('storage_date', '<=', productions[0].production_date)],
                                                          order='storage_date desc', limit=1,)

        # Tanks ##################################
        tanks = self.env['km_petronad.tanks'].search([('project', '=', diagram.project.id),
                                                      ('tanks_date', '<=', productions[0].production_date)],
                                                     order='tanks_date desc', limit=1,)



        # Results ##################################
        results = []
        for rec in sorted_values:
            if not rec.calculate:
                continue
            elif rec.variable_name == 'week_days':
                value = f'{self.convert_date(calendar, week_e_0)}  -  {self.convert_date(calendar, week_s_0)}'
            elif rec.variable_name == 'week_feed_purchased':
                # Feed Purchased
                if len(week_feeds) > 0:
                    value = self.float_num(sum(list([rec.feed_amount for rec in week_feeds])), 2)
                else:
                    value = 0
            elif rec.variable_name == 'week_feed_used':
                # Feed Used
                value = self.float_num(sum(list([rec.feed for rec in  productions])), 2)
            elif rec.variable_name == 'week_production':
                # Production sum
                value = self.float_num(week_sum_production_0, 2)
            elif rec.variable_name == 'week_sale':
            # Sale sum
                if len(week_sales) > 0:
                    value = self.float_num(sum(list([rec.amount for rec in week_sales])), 2)
                else:
                    value = 0
            elif rec.variable_name == 'chart_1':
                six_weeks = ['پنجم', 'چهارم', 'سوم', 'دوم', 'هفته پیش', 'هفته جاری',]
                week_sum_production_list = [week_sum_production_5,week_sum_production_4,week_sum_production_3,week_sum_production_2,week_sum_production_1,week_sum_production_0]
                week_avr_production = self.float_num(sum(week_sum_production_list) / 6, 2)
                performance_list = list(map(lambda x: self.float_num(x * 100 / week_production_plan, 0) if week_production_plan else 0, week_sum_production_list ))
                trace1 = {
                    'x': six_weeks,
                    'y': [week_sum_production_5,week_sum_production_4,week_sum_production_3,week_sum_production_2,week_sum_production_1,week_sum_production_0],
                    'text': [week_sum_production_5,week_sum_production_4,week_sum_production_3,week_sum_production_2,week_sum_production_1,week_sum_production_0],
                    'name': 'Production',
                    'type': 'bar',
                    'marker': {
                        'color': 'rgb(169,209,142)',
                    },
                    'textposition': 'outside',

                }
                trace2 = {
                    'x': six_weeks,
                    'y': [week_production_plan, week_production_plan, week_production_plan, week_production_plan, week_production_plan, week_production_plan, ],
                    'name': 'Plan',
                    'mode': 'lines',
                    'line': {
                        'color': 'rgb(80,130,50)',
                    },
                }
                trace3 = {
                    'x': six_weeks,
                    'y': [week_avr_production,week_avr_production,week_avr_production,week_avr_production,week_avr_production,week_avr_production,week_avr_production,],
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
                               'legend': {"orientation": "h"},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {
                                   'title': _('Production(tone)'),
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
                six_weeks = ['پنجم', 'چهارم', 'سوم', 'دوم', 'هفته پیش', 'هفته جاری',]
                week_sum_sale_list = [week_sum_sale_5,week_sum_sale_4,week_sum_sale_3,week_sum_sale_2,week_sum_sale_1,week_sum_sale_0]
                week_avr_sale = self.float_num(sum(week_sum_sale_list) / 6, 2)

                trace1 = {
                    'x': six_weeks,
                    'y': [week_sum_sale_5,week_sum_sale_4,week_sum_sale_3,week_sum_sale_2,week_sum_sale_1,week_sum_sale_0],
                    'text': [week_sum_sale_5,week_sum_sale_4,week_sum_sale_3,week_sum_sale_2,week_sum_sale_1,week_sum_sale_0],
                    'name': 'sale',
                    'type': 'bar',
                    'marker': {
                        'color': 'rgb(100,160,200)',
                    },
                    'textposition': 'outside',
                    'textcolor': 'black',

                }

                trace2 = {
                    'x': six_weeks,
                    'y': [week_avr_sale,week_avr_sale,week_avr_sale,week_avr_sale,week_avr_sale,week_avr_sale,week_avr_sale,],
                    'name': 'Average',
                    'mode': 'lines',

                    'line': {
                        'dash': 'dash',
                        'width': 2,
                        'color': 'rgb(30,70,100)',
                    }
                }

                plot_value = {
                    'data': [trace1, trace2,  ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'legend': {"orientation": "h"},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {
                                   'title': _('sale(tone)'),
                                   'fixedrange': True,
                                   'range': [0, max(week_sum_sale_list) * 1.2],

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
            elif rec.variable_name == 'chart_3':
                theta = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه',]
                week_production_0_list = self.create_weekly_list(week_production_0, calendar)
                trace2_r = list([rec.feed if rec else 0 for rec in week_production_0_list ])
                tr_avr = sum(trace2_r) / 7
                trace2_avr = []
                [trace2_avr.append(tr_avr) for rec in  range(7)]
                trace1 = {
                          'type': 'scatterpolar',
                          'r': [30, 30, 30, 30, 30, 30, 30, ],
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Feed Plan',
                            'line':{
                                'color': 'rgb(50,50,50)'
                            },
                          }
                trace2 = {
                          'type': 'scatterpolar',
                          'r': trace2_r,
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Daily Feed',
                    'line': {
                        'dash': 'solid',
                        'color': 'rgb(30,100,150)',
                        'width': 3,
                        },
                          }
                trace3 = {
                          'type': 'scatterpolar',
                          'r': trace2_avr,
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Average',
                            'line': {
                            'dash': 'dash',
                            'color': 'rgb(255,128,0)'
                            },
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
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)
            elif rec.variable_name == 'chart_4':
                theta = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه',]
                week_production_0_list = self.create_weekly_list(week_production_0, calendar)
                trace2_r = list([rec.meg_production + rec.deg_production + rec.teg_production  if rec else 0 for rec in week_production_0_list ])
                tr_avr = sum(trace2_r) / 7
                trace2_avr = []
                [trace2_avr.append(tr_avr) for rec in  range(7)]
                trace1 = {
                          'type': 'scatterpolar',
                          'r': [18, 18, 18, 18, 18, 18, 18,  ],
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Feed Plan',
                            'line':{
                                'color': 'rgb(50,50,50)'
                            },
                          }
                trace2 = {
                          'type': 'scatterpolar',
                          'r': trace2_r,
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Daily Feed',
                    'line': {
                        'dash': 'solid',
                        'color': 'rgb(30,100,150)',
                        'width': 3,
                        },
                          }
                trace3 = {
                          'type': 'scatterpolar',
                          'r': trace2_avr,
                          'theta': theta,
                          # 'fill': 'toself',
                          'name': 'Average',
                            'line': {
                            'dash': 'dash',
                            'color': 'rgb(255,128,0)'
                            },
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
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)
            elif rec.variable_name == 'chart_5':
                week_production_0_list = self.create_weekly_list(week_production_0, calendar)
                meg_production = sum(list([rec.meg_production if rec else 0 for rec in week_production_0_list ]))
                deg_production = sum(list([rec.deg_production if rec else 0 for rec in week_production_0_list ]))
                teg_production = sum(list([rec.teg_production if rec else 0 for rec in week_production_0_list ]))
                tr_avr = sum(trace2_r) / 7
                trace2_avr = []
                [trace2_avr.append(tr_avr) for rec in  range(7)]
                trace1 = {
                          'type': 'pie',
                          'values': [meg_production, deg_production, teg_production, ],
                          'labels': ['MEG', 'DEG', 'TEG'],
                          'textinfo': 'label+value',
                          'textposition': 'outside',
                            'showlegend': False,


                          }

                plot_value = {
                    'data': [trace1,   ],
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
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)
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
                value = self.convert_date(calendar, productions[0].production_date)

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
            index = week_days.index(rec.production_date.weekday())
            new_record_list[index] = rec
        return new_record_list

