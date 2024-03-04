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
import plotly.express as px
import plotly
import plotly.io as pio
import base64
# import kaleido
import os

import plotly.offline
import plotly.graph_objs as go


class SdVisualizePetronadCalculateDaily(models.Model):
    _inherit = 'sd_visualize.calculate'

    def calculate(self, function_name, diagram_id, update_date):
        res = super(SdVisualizePetronadCalculateDaily, self).calculate(function_name, diagram_id, update_date)
        try:
            if function_name == 'petronad_ethylene_daily':
                res['value'] = self.petronad_ethylene_daily(diagram_id, update_date)
        except Exception as err:
            logging.error(f'CALCULATION:{function_name}:\n{traceback.format_exc()}')
            raise ValidationError(f'CALCULATION:{function_name}/ {err}')
        return res


    def petronad_ethylene_daily(self, diagram=0, update_date=0):
        diagram = self.env['sd_visualize.diagram'].browse(diagram)
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        value_model = self.env['sd_visualize.values']
        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])
        report_date = date.fromisoformat(update_date)
        productions = self.env['km_petronad.production_record'].search([('data_date', '<=', report_date),('data_date', '>=', report_date - timedelta(days=2)), ])
        # if len(productions) == 0:
        #     raise ValidationError(f'Production not found')

        tanks = self.env['km_petronad.storage_tanks'].search([])
        if  len(tanks) == 0:
            raise ValidationError(f'Tank not found')
        # comments = self.env['km_petronad.comments'].search([('project', '=', diagram.project.id),
        #                                                     ('date', '=', productions[0].production_date)],
        #                                                    order='sequence')

        if calendar == 'fa_IR':
            # first_day = jdatetime.date.fromgregorian(date=end_date).replace(day=1)
            # next_month = first_day.replace(day=28) + timedelta(days=5)
            # last_day = (next_month - timedelta(days=next_month.day)).togregorian()
            # first_day = first_day.togregorian
            s_start_date_1 = jdatetime.date.fromgregorian(date=report_date).strftime("%Y/%m/%d")
            s_start_date_2 = jdatetime.date.fromgregorian(date=report_date - timedelta(days=1)).strftime("%Y/%m/%d")
            s_start_date_3 = jdatetime.date.fromgregorian(date=report_date - timedelta(days=2)).strftime("%Y/%m/%d")
            # s_storage_date = jdatetime.date.fromgregorian(date=storages.storage_date).strftime("%Y/%m/%d")
            # s_end_date = jdatetime.date.fromgregorian(date=end_date).strftime("%Y/%m/%d")

        else:
            # first_day = end_date.replace(day=1)
            # next_month = first_day.replace(day=28) + timedelta(days=5)
            # last_day = next_month - timedelta(days=next_month.day)
            s_start_date_1 = (report_date ).strftime("%Y/%m/%d")
            s_start_date_2 = (report_date - timedelta(days=1)).strftime("%Y/%m/%d")
            s_start_date_3 = (report_date - timedelta(days=2)).strftime("%Y/%m/%d")
            # s_storage_date = storages.storage_date.strftime("%Y/%m/%d")
            # s_end_date = end_date.strftime("%Y/%m/%d")
        feeds_1 = abs(sum(list([self.ton_amount(rec) for rec in productions
                                if rec.data_date == report_date and rec.fluid.name == 'FEED'
                                and rec.register_type == 'feed_usage'])))
        feeds_2 = abs(sum(list([self.ton_amount(rec) for rec in productions
                                if rec.data_date == report_date - timedelta(days=1)
                                and rec.fluid.name == 'FEED'
                                and rec.register_type == 'feed_usage'])))
        feeds_3 = abs(sum(list([self.ton_amount(rec) for rec in productions
                                if rec.data_date == report_date - timedelta(days=2)
                                and rec.fluid.name == 'FEED'
                                and rec.register_type == 'feed_usage'])))

        meg_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                              rec.data_date == report_date and rec.fluid.name == 'MEG' and rec.register_type == 'production'])))
        meg_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'MEG' and rec.register_type == 'production'])))
        meg_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'MEG' and rec.register_type == 'production'])))

        deg_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                              rec.data_date == report_date and rec.fluid.name == 'DEG' and rec.register_type == 'production'])))
        deg_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'DEG' and rec.register_type == 'production'])))
        deg_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'DEG' and rec.register_type == 'production'])))

        teg_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                              rec.data_date == report_date and rec.fluid.name == 'TEG' and rec.register_type == 'production'])))
        teg_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'TEG' and rec.register_type == 'production'])))
        teg_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'TEG' and rec.register_type == 'production'])))

        h1_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                             rec.data_date == report_date and rec.fluid.name == 'HEAVY1' and rec.register_type == 'production'])))
        h1_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'HEAVY1' and rec.register_type == 'production'])))
        h1_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'HEAVY1' and rec.register_type == 'production'])))

        h2_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                             rec.data_date == report_date and rec.fluid.name == 'HEAVY2' and rec.register_type == 'production'])))
        h2_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'HEAVY2' and rec.register_type == 'production'])))
        h2_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'HEAVY2' and rec.register_type == 'production'])))

        feed_h1_1 = abs(sum(list([rec.amount for rec in productions if
                             rec.data_date == report_date and rec.fluid.name == 'HEAVY1' and rec.register_type == 'feed_usage'])))
        feed_h1_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'HEAVY1' and rec.register_type == 'feed_usage'])))
        feed_h1_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'HEAVY1' and rec.register_type == 'feed_usage'])))

        all_tanks = self.env['km_petronad.storage_tanks'].search([])
        all_tanks = list([rec for rec in all_tanks if rec.fluid.name in ['FEED', 'MEG', 'DEG','TEG', 'HEAVY1', 'HEAVY2', ]])


        duration_pro = self.env['km_petronad.production_record'].search([('data_date', '>', report_date), ])
        tank_names = list([f'{rec.name}<br>{rec.fluid.name}' for rec in all_tanks])
        tank_amounts = []
        tank_empty = []
        tank_capacity = []
        for rec in all_tanks:
            # amount = self.ton_amount(rec) + sum(list([-1 * self.ton_amount(re) for re in duration_pro if re.fluid == rec.fluid ]))
            # tank_amounts.append(int(amount / 1000))
            # tank_empty.append(int((rec.capacity - amount) / 1000))
            # tank_capacity.append(int(rec.capacity / 1000))
            amount = self.ton_amount(rec)
            tank_amounts.append(amount)
            tank_empty.append(int((rec.capacity / 1000 - amount)))
            tank_capacity.append(int(rec.capacity / 1000))

        # tank_amounts = list([rec.amount for rec in all_tanks ])
        # tank_empty = list([rec.capacity - rec.amount for rec in all_tanks])
        # tank_capacity = list([rec.capacity for rec in all_tanks])
        results = []
        for rec in sorted_values:
            if not rec.calculate:
                continue

            elif rec.variable_name == 'report_date':
                value = s_start_date_1
            # MEG
            elif rec.variable_name == 'meg_production':
                value = self.float_num(meg_1, 2)
            # DEG
            elif rec.variable_name == 'deg_production':
                value = self.float_num(deg_1, 2)
            # TEG
            elif rec.variable_name == 'teg_production':
                value = self.float_num(teg_1, 2)
            # Production sum
            elif rec.variable_name == 'sum_of_production':
                value = self.float_num((meg_1 + deg_1 + teg_1), 2)
            # HEAVY1
            elif rec.variable_name == 'h1_production':
                value = self.float_num(h1_1, 2)
            # HEAVY2
            elif rec.variable_name == 'h2_production':
                value = self.float_num(h2_1, 2)
            # WW
            elif rec.variable_name == 'ww_production':
                value = self.float_num(productions[0].ww_production, 2)
            # Feed
            elif rec.variable_name == 'feed':
                value = self.float_num(feeds_1, 2)
            # Feed
            elif rec.variable_name == 'feed_h1':
                value = self.float_num(feed_h1_1, 2)
            # Workers
            elif rec.variable_name == 'tank_total_capacity':
                value = self.float_num(sum(tank_capacity), 2)
            # Comments
            elif rec.variable_name == 'comments_daily':
                comments = self.env['km_petronad.comments_daily'].search([('comment_date', '=', report_date)])
                value = ''
                for comment in comments:
                    value += comment.description
            #     value = self.float_num(storages.meg_storage, 2)
            # # DEG
            # elif rec.variable_name == 'deg_storage':
            #     value = self.float_num(storages.deg_storage, 2)
            # # TEG
            # elif rec.variable_name == 'teg_storage':
            #     value = self.float_num(storages.teg_storage, 2)
            # # HEAVY1
            # elif rec.variable_name == 'h1_storage':
            #     value = self.float_num(storages.h1_storage, 2)
            # # HEAVY2
            # elif rec.variable_name == 'h2_storage':
            #     value = self.float_num(storages.h2_storage, 2)
            # # WW
            # elif rec.variable_name == 'ww_storage':
            #     value = self.float_num(storages.ww_storage, 2)
            # # Feed
            # elif rec.variable_name == 'feed_storage':
            #     value = self.float_num(storages.feed_storage, 2)
            # # storage_date
            # elif rec.variable_name == 'storage_date':
            #     value = s_storage_date
            #
            # # MEG
            # elif rec.variable_name == 'meg_tank':
            #     value = self.float_num(tanks.meg_tank - storages.meg_storage, 2)
            # # DEG
            # elif rec.variable_name == 'deg_tank':
            #     value = self.float_num(tanks.deg_tank - storages.deg_storage, 2)
            # # TEG
            # elif rec.variable_name == 'teg_tank':
            #     value = self.float_num(tanks.teg_tank - storages.teg_storage, 2)
            # # HEAVY1
            # elif rec.variable_name == 'h1_tank':
            #     value = self.float_num(tanks.h1_tank - storages.h1_storage, 2)
            # # HEAVY2
            # elif rec.variable_name == 'h2_tank':
            #     value = self.float_num(tanks.h2_tank - storages.h2_storage, 2)
            # # WW
            # elif rec.variable_name == 'ww_tank':
            #     value = self.float_num(tanks.ww_tank - storages.ww_storage, 2)
            # # Feed
            # elif rec.variable_name == 'feed_tank':
            #     value = self.float_num(tanks.feed_tank_1 + tanks.feed_tank_2 - storages.feed_storage, 2)
            # # Commnets
            # elif rec.variable_name == 'comments':
            #     if len(comments) > 0:
            #         value = ''.join(list([f'<p> {rec.comment}</p>' for rec in comments]))
            #         value = f'<div style="direction: rtl;">{value}</div>'
            #     else:
            #         value = ''

            elif rec.variable_name == 'chart_1':
                trace1_y = [meg_3, meg_2, meg_1 ]
                trace2_y = [deg_3, deg_2, deg_1 ]
                trace3_y = [teg_3, teg_2, teg_1 ]
                trace4_y = [h1_3, h1_2, h1_1 ]
                trace1234_y = [trace1_y[i] + trace2_y[i] + trace3_y[i] + trace4_y[i] for i in range(3)]

                trace5_y = [feeds_3 , feeds_2, feeds_1 ]
                trace6_y = [feed_h1_3, feed_h1_2, feed_h1_1 ]
                trace56_y = [trace5_y[i] + trace6_y[i] for i in range(3)]

                trace9_y = [30, 30, 30]

                max_range = max(trace1234_y + trace56_y)
                yrange = int(max_range * 1.3)

                chart_1_trace_x = [s_start_date_3, s_start_date_2, s_start_date_1]
                trace1 =  {
                        'x': chart_1_trace_x,
                        'y': trace1_y,
                        'text': [rec if rec != 0 and rec > .1 * max_range else '' for rec in trace1_y],
                    'textposition': 'top',
                    'textangle': 0,
                        'type': "bar",
                        'name': "MEG",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(30,80,120)'},
                    }

                trace2 = {
                        'x': chart_1_trace_x,
                        'y': trace2_y,
                        'text': [rec if  rec != 0 and rec > .1 * max_range else '' for rec in trace2_y],
                    'textposition': 'top',
                    'textangle': 0,
                        'type': "bar",
                        'name': "DEG",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(0,110,200)'},
                    }
                trace3 = {
                        'x': chart_1_trace_x,
                        'y': trace3_y,
                        'text': [rec if rec != 0 and rec > .1 * max_range else '' for rec in trace3_y],
                    'textposition': 'top',
                    'textangle': 0,
                        'type': "bar",
                        'name': "TEG",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(160,200,230)'},
                    }
                trace4 = {
                        'x': chart_1_trace_x,
                        'y': trace4_y,
                        'text': [rec if rec != 0 and rec > .1 * max_range else '' for rec in trace4_y],
                    'textposition': 'top',
                    'textangle': 0,
                        'type': "bar",
                        'name': "HEAVY1",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(200,90,20)'},
                    }
                trace1234 = {
                        'x': chart_1_trace_x,
                        'y': trace1234_y ,
                        'text': [rec if rec > 0 else '' for rec in trace1234_y] ,
                        'showlegend': False,
                        # 'xaxis': 'x1',
                        'yaxis': 'y2',
                    'width': 0.2,
                    'offset': 0.05,
                    'type': 'bar',
                    'mode': 'text',
                    'textposition': 'outside',
                    'marker': {'color': 'rgba(0,0,0,0)'},

                }
                trace5 = {
                        'x': chart_1_trace_x,
                        'y': trace5_y,
                        'text': [rec if rec != 0 and rec > .1 * max_range else '' for rec in trace5_y],
                    'textposition': 'top',
                    'textangle': 0,
                        'type': "bar",
                        'name': "Feed",
                        'xaxis': 'x2',
                        'width': 0.2,
                        'offset': -0.27,
                        'barmode': 'stack',
                    'marker': {'color': 'rgb(110,50,160)'},
                    }
                trace6 = {
                        'x': chart_1_trace_x,
                        'y': trace6_y,
                        # 'text': ['nan', 'nan', 'nan'],
                        'text': [rec if rec != 0 and rec > .1 * max_range else '' for rec in trace6_y],
                    'textposition': 'top',
                    'textangle': 0,
                        'showlegend': False,
                        'type': "bar",
                        'name': "HEAVY1",
                        'xaxis': 'x3',
                        'width': 0.2,
                        'offset': -0.27,
                        'barmode': 'stack', 'marker': {'color': 'rgb(200,90,20)'},
                    }

                trace56 = {
                        'x': chart_1_trace_x,
                        'y': trace56_y,
                        'text': [rec if rec > 0 else '' for rec in trace56_y] ,
                        'showlegend': False,
                        'xaxis': 'x2',
                        'yaxis': 'y2',
                    'width': 0.2,
                    'offset': -0.27,
                    'type': 'bar',
                    'mode': 'text',
                    'textposition': 'outside',
                    'marker': {'color': 'rgba(0,0,0,0)'},
                    }
                # trace56 = {
                #         'x': chart_1_trace_x,
                #         'y': trace56_y,
                #         'text': trace56_y,
                #         'showlegend': False,
                #         'xaxis': 'x2',
                #     # 'type': 'scatter',
                #     'mode': 'text',
                #     'textposition': 'top left',
                #     'line': {
                #         'color': 'rgba(0,0,255,0)',
                #     }
                #     }

                plot_value = {
                    'data': [trace1234,trace1, trace2, trace3, trace4,  trace5, trace6, trace56, trace9_y ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'plot_bgcolor': 'rgba(255, 255, 255, 0)',

                               'showlegend': True,
                               'barmode': 'stack',
                               # 'legend': {"orientation": "h"},
                               'legend': {'x': 1.2, 'y': 1, 'xanchor': 'right', },
                               'xaxis': {'anchor': 'x1','fixedrange': True},
                               'xaxis2': {'anchor': 'x2', },

                               'yaxis': {'fixedrange': True,
                                         'range': [0, yrange],
                                         'showticklabels': False,
                                         'showgrid': False,

                                         },
                               'yaxis2': {
                                         # 'anchor': 'y2',
                                           'range': [0, yrange],
                                           'showticklabels': False,
                                           'barmode': 'group',
                                   'showgrid': False,

                               },
                               },
                    'config': {'responsive': True, 'displayModeBar': False}
                }

                value = json.dumps(plot_value)

            elif rec.variable_name == 'chart_2':
                chart_2_trace_x = tank_names
                chart_2_trace_1 = tank_amounts
                chart_2_trace_2 = tank_empty
                chart_2_trace_3 = tank_capacity
                tank_range = int(max(tank_capacity) * 1.1)

                def text_position(a, m=max(tank_capacity)):
                    if m and a[0] / m > .1:
                        return a[0]
                    else:
                        return ''
                def marker_color(a):
                    if a[1] and a[0] / a[1] > .9:
                        return 'rgb(160,70,120)'
                    else:
                        return 'rgb(64,64,64)'
                data_list = list(zip(tuple(chart_2_trace_1), tuple(chart_2_trace_3)))
                text_p = list(map(text_position, data_list))
                marker_c = list(map(marker_color, data_list))

                trace1 = {
                    'x': chart_2_trace_x,
                    'y': chart_2_trace_1,
                    'text': text_p,
                    'textposition': 'top outside',
                    'hoverinfo': 'none',
                    'textangle': 0,
                    # 'textfont': {'size': [30, 1,10,10,10,10,10]},
                    'constraintext': 'none',
                    'name': 'موجودی',
                    'type': 'bar',
                    # 'mode': 'bar+text',
                    'marker': {
                        'color': marker_c
                    }
                }
                trace2 = {
                    'x': chart_2_trace_x,
                    'y': chart_2_trace_2,
                    'text': chart_2_trace_2,
                    'textposition': 'inside',
                    'textangle': 'horizontal',
                    'hoverinfo': 'none',
                    'name': 'باقی مانده',
                    'type': 'bar',
                    # 'mode': 'bar+text',
                    'marker': {
                        'color': 'rgb(170,170,170)'
                    }
                }
                trace3 = {
                    'x': chart_2_trace_x,
                    'y': chart_2_trace_3,
                    'text': chart_2_trace_3,
                    'textposition': 'top',
                    'textangle': 'horizontal',
                    'hoverinfo': 'none',
                    'name': 'ظرفیت',
                    # 'type': 'bar',
                    'mode': 'text',
                    'marker': {
                        'size': 26,
                        'offset': .2,
                    },
                }
                plot_value = {
                    'data': [trace1, trace2, trace3, ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               # 'plot_bgcolor': 'rgb(255,255,255,0)',
                               'orientation': 'v',
                               'showticklabels': False,
                               'showgrid': False,
                               'showlegend': True,
                               'barmode': 'stack',
                               'legend': {'x': 1.2, 'y': 1, 'xanchor': 'right',
                                          'bgcolor': 'rgba(255, 255, 255, 0)',
                                          'bordercolor': 'rgba(255, 255, 255, 0)'
                                          },
                               'xaxis': {'fixedrange': True, 'nticks': 10,},
                               'yaxis': {'fixedrange': True,
                                         # 'range': [0, tank_range],
                                         'showticklabels': False,
                                         # 'domain': [0, 1],
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

    def ton_amount(self, rec):
        return int(rec.amount * 0.001) if rec.unit == 'kg' else rec.amount

