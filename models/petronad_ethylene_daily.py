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
        print(f'''
                    {report_date} 
                    {diagram.project.id}
                ''')

        productions = self.env['km_petronad.production_record'].search([('data_date', '<=', report_date),('data_date', '>=', report_date - timedelta(days=2)), ])

        print(f'''
            report_date: {report_date} 
            productions: {productions}
''')
        if len(productions) == 0:
            raise ValidationError(f'Production not found')
        # storages = self.env['km_petronad.storage_tanks'].search([])
        # if  len(storages) == 0:
        #     raise ValidationError(f'Storage not found')
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
        feeds_1 = abs(sum(list([rec.amount for rec in productions if
                                rec.data_date == report_date and rec.fluid.name == 'FEED' and rec.amount < 0])))
        feeds_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'FEED' and rec.amount < 0])))
        feeds_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'FEED' and rec.amount < 0])))

        meg_1 = abs(sum(list([rec.amount for rec in productions if
                              rec.data_date == report_date and rec.fluid.name == 'MEG' and rec.amount > 0])))
        meg_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'MEG' and rec.amount > 0])))
        meg_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'MEG' and rec.amount > 0])))

        deg_1 = abs(sum(list([rec.amount for rec in productions if
                              rec.data_date == report_date and rec.fluid.name == 'DEG' and rec.amount > 0])))
        deg_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'DEG' and rec.amount > 0])))
        deg_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'DEG' and rec.amount > 0])))

        teg_1 = abs(sum(list([rec.amount for rec in productions if
                              rec.data_date == report_date and rec.fluid.name == 'TEG' and rec.amount > 0])))
        teg_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'TEG' and rec.amount > 0])))
        teg_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'TEG' and rec.amount > 0])))

        h1_1 = abs(sum(list([rec.amount for rec in productions if
                             rec.data_date == report_date and rec.fluid.name == 'H1' and rec.amount > 0])))
        h1_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'H1' and rec.amount > 0])))
        h1_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'H1' and rec.amount > 0])))

        h2_1 = abs(sum(list([rec.amount for rec in productions if
                             rec.data_date == report_date and rec.fluid.name == 'H2' and rec.amount > 0])))
        h2_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'H2' and rec.amount > 0])))
        h2_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'H2' and rec.amount > 0])))

        feed_h1_1 = abs(sum(list([rec.amount for rec in productions if
                             rec.data_date == report_date and rec.fluid.name == 'H1' and rec.amount < 0])))
        feed_h1_2 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name == 'H1' and rec.amount < 0])))
        feed_h1_3 = abs(sum(list([rec.amount for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name == 'H1' and rec.amount < 0])))

        all_tanks = self.env['km_petronad.storage_tanks'].search([])


        duration_pro = self.env['km_petronad.production_record'].search([('data_date', '>', report_date), ])
        tank_names = list([rec.name for rec in all_tanks])
        tank_amounts = []
        tank_empty = []
        tank_capacity = []
        for rec in all_tanks:
            amount = rec.amount + sum(list([-1 * re.amount for re in duration_pro if re.fluid == rec.fluid ]))
            tank_amounts.append(amount)
            tank_empty.append(rec.capacity - amount)
            tank_capacity.append(rec.capacity )

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
            # H1
            elif rec.variable_name == 'h1_production':
                value = self.float_num(h1_1, 2)
            # H2
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
            elif rec.variable_name == 'comments':
                value = self.env['km_petronad.comments'].search([('comment_date', '=', report_date)]).description
            #     value = self.float_num(storages.meg_storage, 2)
            # # DEG
            # elif rec.variable_name == 'deg_storage':
            #     value = self.float_num(storages.deg_storage, 2)
            # # TEG
            # elif rec.variable_name == 'teg_storage':
            #     value = self.float_num(storages.teg_storage, 2)
            # # H1
            # elif rec.variable_name == 'h1_storage':
            #     value = self.float_num(storages.h1_storage, 2)
            # # H2
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
            # # H1
            # elif rec.variable_name == 'h1_tank':
            #     value = self.float_num(tanks.h1_tank - storages.h1_storage, 2)
            # # H2
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
                trace5_y = [feeds_3 , feeds_2, feeds_1 ]
                trace6_y = [feed_h1_3, feed_h1_2, feed_h1_1 ]
                trace9_y = [30, 30, 30]
                yrange = int(max(trace1_y + trace2_y + trace3_y) * 1.3)
                chart_1_trace_x = [s_start_date_3, s_start_date_2, s_start_date_1]
                trace1_y =  {
                        'x': chart_1_trace_x,
                        'y': trace1_y,
                        'type': "bar",
                        'name': "MEG",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(30,80,120)'},
                    }

                trace2_y = {
                        'x': chart_1_trace_x,
                        'y': trace2_y,
                        'type': "bar",
                        'name': "DEG",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(0,110,200)'},
                    }
                trace3_y = {
                        'x': chart_1_trace_x,
                        'y': trace3_y,
                        'type': "bar",
                        'name': "TEG",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(160,200,230)'},
                    }
                trace4_y = {
                        'x': chart_1_trace_x,
                        'y': trace4_y,
                        'type': "bar",
                        'name': "H1",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(200,90,20)'},
                    }
                trace5_y = {
                        'x': chart_1_trace_x,
                        'y': trace5_y,
                        'type': "bar",
                        'name': "Feed",
                        'xaxis': 'x2',
                        'width': 0.2,
                        'offset': -0.2,
                        'barmode': 'stack', 'marker': {'color': 'rgb(110,50,160)'},
                    }
                trace6_y = {
                        'x': chart_1_trace_x,
                        'y': trace6_y,
                        'type': "bar",
                        'name': "H1",
                        'xaxis': 'x3',
                        'width': 0.2,
                        'offset': -0.2,
                        'barmode': 'stack', 'marker': {'color': 'rgb(200,90,20)'},
                    }

                plot_value = {
                    'data': [trace1_y, trace2_y, trace3_y, trace4_y, trace5_y, trace6_y, trace9_y ],
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
                                         # 'range': [0, yrange]
                                         },
                               },
                    'config': {'responsive': True, 'displayModeBar': False}
                }

                value = json.dumps(plot_value)


            elif rec.variable_name == 'chart_11':
                # feeds_1 = [rec.amount for rec in productions if rec.data_date == report_date and rec.fluid == 'FEED' and rec.amount < 0]


                # trace1_y = [productions[2].feed, productions[1].feed, productions[0].feed]
                # trace2_y = [productions[2].meg_production, productions[1].meg_production, productions[0].meg_production]
                # trace3_y = [productions[2].h1_production, productions[1].h1_production, productions[0].h1_production]

                trace1_y = [feeds_3 , feeds_2, feeds_1 ]
                trace2_y = [meg_3, meg_2, meg_1 ]
                trace3_y = [deg_3, deg_2, deg_1 ]
                trace4_y = [teg_3, teg_2, teg_1 ]
                trace5_y = [h1_3, h1_2, h1_1 ]
                trace9_y = [30, 30, 30]
                yrange = int(max(trace1_y + trace2_y + trace3_y) * 1.3)
                chart_1_trace_x = [s_start_date_3, s_start_date_2, s_start_date_1]
                trace1 = {
                    'x': chart_1_trace_x,
                    'y': trace1_y,
                    'text': trace1_y,
                    'name': 'Feed',
                    'type': 'bar',
                    'textposition': ['outside','outside','inside',],
                    'marker': {
                        'color': 'rgb(110,50,160)'
                    }
                }
                trace2 = {
                    'x': chart_1_trace_x,
                    'y': trace2_y,
                    'text': trace2_y,
                    'name': 'MEG',
                    'type': 'bar',
                    'textposition': 'outside',
                    'marker': {
                        'color': 'rgb(30,80,120)'
                    }
                }
                trace3 = {
                    'x': chart_1_trace_x,
                    'y': trace3_y,
                    'text': trace3_y,
                    'name': 'DEG',
                    'type': 'bar',
                    'textposition': 'outside',
                    'marker': {
                        'color': 'rgb(0,110,200)'
                    }
                }
                trace4 = {
                    'x': chart_1_trace_x,
                    'y': trace4_y,
                    'text': trace4_y,
                    'name': 'TEG',
                    'type': 'bar',
                    'textposition': 'outside',
                    'marker': {
                        'color': 'rgb(160,200,230)'
                    }
                }
                trace5 = {
                    'x': chart_1_trace_x,
                    'y': trace5_y,
                    'text': trace5_y,
                    'showlegend': False,
                    'name': 'H1',
                    'type': 'bar',
                    'textposition': 'outside',
                    'marker': {
                        'color': 'rgb(200,90,20)'
                    }
                }
                trace9 = {
                    'x': chart_1_trace_x,
                    'y': trace9_y,
                    'text': trace9_y,
                    'name': 'ظرفیت',
                    'type': 'scatter',
                    'mode': 'lines',
                    'textposition': 'outside',
                    'line': {
                        'dash': 'dash',
                        'width': 2,
                        'color': 'rgb(0,110,200)',
                    }
                }

                plot_value = {
                    'data': [trace1, trace2, trace3, trace4, trace5, trace9, ],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'showlegend': True,
                               'barmode': 'stack',
                               # 'legend': {"orientation": "h"},
                               'legend': {'x': 1.2, 'y': 1, 'xanchor': 'right',},
                               'xaxis': {'fixedrange': True},
                               'yaxis': {'fixedrange': True, 'range': [0, yrange]},
                                         },
                    'config': {'responsive': True, 'displayModeBar': False}
                }
                # print(f'llllllll >>> {value}')


                value = json.dumps(plot_value)

            elif rec.variable_name == 'chart_2':

                chart_2_trace_x = tank_names
                chart_2_trace_1 = tank_amounts
                chart_2_trace_2 = tank_empty
                chart_2_trace_3 = tank_capacity
                tank_range = int(max(tank_capacity) * 1.1)

                def text_position(a):
                    if a[0] / a[1] > .5:
                        return 'top inside'
                    else:
                        return 'top outside'
                def marker_color(a):
                    if a[0] / a[1] > .9:
                        return 'rgb(160,70,120)'
                    else:
                        return 'rgb(64,64,64)'
                data_list = list(zip(tuple(chart_2_trace_1), tuple(chart_2_trace_3)))
                text_p = list(map(text_position, data_list))
                marker_c = list(map(marker_color, data_list))
                print(f'''
                text_p: {data_list}
                text_p: {text_p}

''')
                # text_p: {text_p}

                trace1 = {
                    'x': chart_2_trace_x,
                    'y': chart_2_trace_1,
                    'text': chart_2_trace_1,
                    'textposition': 'inside',
                    # 'hoverinfo': 'none',
                    'name': 'موجودی',
                    'type': 'bar',
                    # 'mode': 'bar+text',
                    'textposition': 'auto',
                    'marker': {
                        'color': marker_c
                    }
                }
                trace2 = {
                    'x': chart_2_trace_x,
                    'y': chart_2_trace_2,
                    'text': chart_2_trace_2,
                    'textposition': 'inside',
                    # 'hoverinfo': 'none',
                    'name': 'باقی مانده',
                    'type': 'bar',
                    # 'mode': 'bar+text',
                    'textposition': 'top',
                    'marker': {
                        'color': 'rgb(170,170,170)'
                    }
                }
                trace3 = {
                    'x': chart_2_trace_x,
                    'y': chart_2_trace_3,
                    'text': chart_2_trace_3,
                    'textposition': 'outside',
                    # 'hoverinfo': 'none',
                    'name': 'ظرفیت',
                    # 'type': 'bar',
                    'mode': 'text',
                    'textposition': 'top',
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
                               'showlegend': True,
                               'barmode': 'stack',
                               'legend': {'x': 1.2, 'y': 1, 'xanchor': 'right',
                                          'bgcolor': 'rgba(255, 255, 255, 0)',
                                          'bordercolor': 'rgba(255, 255, 255, 0)'
                                          },
                               'xaxis': {'fixedrange': True, 'nticks': 10,},
                               'yaxis': {'fixedrange': True,
                                         'range': [0, tank_range],
                                         'domain': [0, 1],},
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



