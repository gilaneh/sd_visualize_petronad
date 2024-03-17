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
            if function_name == 'petronad_glycerin_daily':
                res['value'] = self.petronad_glycerin_daily(diagram_id, update_date)
        except Exception as err:
            logging.error(f'CALCULATION:{function_name}:\n{traceback.format_exc()}')
            raise ValidationError(f'CALCULATION:{function_name}/ {err}')
        return res


    def petronad_glycerin_daily(self, diagram=0, update_date=0):
        diagram = self.env['sd_visualize.diagram'].browse(diagram)
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        value_model = self.env['sd_visualize.values']
        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])
        report_date = date.fromisoformat(update_date)
        productions = self.env['km_petronad.production_record'].search([('data_date', '<=', report_date),
                                                                        ('data_date', '>=', report_date - timedelta(days=2)), ])
        GLY_Industial = ['GLYCERIN', 'GLYCERIN Industrial']
        GLY_Pharma = ['GLYCERIN Pharma']
        GLY_Pitch = ['GLYCERIN Pitch']
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
        glycerin_crude_1 = abs(sum(list([self.ton_amount(rec) for rec in productions
                                if rec.data_date == report_date and rec.fluid.name == 'GLYCERIN CRUDE'
                                and rec.register_type == 'feed_usage'])))
        glycerin_crude_2 = abs(sum(list([self.ton_amount(rec) for rec in productions
                                if rec.data_date == report_date - timedelta(days=1)
                                and rec.fluid.name == 'GLYCERIN CRUDE'
                                and rec.register_type == 'feed_usage'])))
        glycerin_crude_3 = abs(sum(list([self.ton_amount(rec) for rec in productions
                                if rec.data_date == report_date - timedelta(days=2)
                                and rec.fluid.name == 'GLYCERIN CRUDE'
                                and rec.register_type == 'feed_usage'])))


        glycerin_i_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                              rec.data_date == report_date and rec.fluid.name in GLY_Industial and rec.register_type == 'production'])))
        glycerin_i_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name in GLY_Industial and rec.register_type == 'production'])))
        glycerin_i_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name in GLY_Industial and rec.register_type == 'production'])))

        glycerin_p_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                              rec.data_date == report_date and rec.fluid.name in GLY_Pharma and rec.register_type == 'production'])))
        glycerin_p_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name in GLY_Pharma and rec.register_type == 'production'])))
        glycerin_p_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name in GLY_Pharma and rec.register_type == 'production'])))

        glycerin_pitch_1 = abs(sum(list([self.ton_amount(rec) for rec in productions if
                              rec.data_date == report_date and rec.fluid.name in GLY_Pitch and rec.register_type == 'production'])))
        glycerin_pitch_2 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=1) and rec.fluid.name in GLY_Pitch and rec.register_type == 'production'])))
        glycerin_pitch_3 = abs(sum(list([self.ton_amount(rec) for rec in productions if rec.data_date == report_date - timedelta(
            days=2) and rec.fluid.name in GLY_Pitch and rec.register_type == 'production'])))

        all_tanks = self.env['km_petronad.storage_tanks'].search([])
        all_tanks = list([rec for rec in all_tanks if rec.fluid.name in ['GLYCERIN', 'GLYCERIN CRUDE', 'GLYCERIN Pitch','GLYCERIN Industrial', 'GLYCERIN Pharma', ]])


        duration_pro = self.env['km_petronad.production_record'].search([('data_date', '>', report_date), ])
        tank_names = list([f'{rec.name}<br>{rec.fluid.name}' for rec in all_tanks])
        tank_amounts = []
        tank_empty = []
        tank_capacity = []
        for rec in all_tanks:
            # amount = self.ton_amount(rec) + sum(list([-1 * self.ton_amount(re) for re in duration_pro if re.fluid == rec.fluid ]))
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
            elif rec.variable_name == 'glycerin_crude':
                value = self.float_num(glycerin_crude_1, 2)
            # DEG
            elif rec.variable_name == 'glycerin_i_1':
                value = self.float_num(glycerin_i_1, 2)
            # TEG
            elif rec.variable_name == 'glycerin_p_1':
                value = self.float_num(glycerin_p_1, 2)
            # TEG
            elif rec.variable_name == 'glycerin_pitch':
                value = self.float_num(glycerin_pitch_1, 2)
            # Production sum
            elif rec.variable_name == 'sum_of_production':
                value = self.float_num((glycerin_i_1 + glycerin_p_1), 2)

            # Workers
            elif rec.variable_name == 'tank_total_capacity':
                value = self.float_num(sum(tank_capacity), 2)
            # Comments
            elif rec.variable_name == 'comments_daily':
                comments = self.env['km_petronad.comments_daily'].search([('comment_date', '=', report_date)])
                value = ''
                for comment in comments:
                    value += comment.description


            elif rec.variable_name == 'chart_1':
                trace1_y = [glycerin_i_3, glycerin_i_2, glycerin_i_1 ]
                trace2_y = [glycerin_p_3, glycerin_p_2, glycerin_p_1 ]
                trace12_y = [trace1_y[i] + trace2_y[i] for i in range(3)]

                trace5_y = [glycerin_crude_3 , glycerin_crude_2, glycerin_crude_1 ]
                # trace56_y = [trace5_y[i] + trace6_y[i] for i in range(3)]

                trace9_y = [30, 30, 30]

                max_range = max(trace12_y + trace5_y)
                yrange = int(max_range * 1.3)

                chart_1_trace_x = [s_start_date_3, s_start_date_2, s_start_date_1]
                trace1 =  {
                        'x': chart_1_trace_x,
                        'y': trace1_y,
                        'text': [rec if rec != 0 and rec > .1 * max_range else '' for rec in trace1_y],
                    'textposition': 'top',
                    'textangle': 0,
                        'type': "bar",
                        'name': "Glycerin Pure",
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
                        'name': "Glycerin Phar",
                        'xaxis': 'x1',
                        'width': 0.2,
                        'offset': 0.05,
                        'marker': {'color': 'rgb(0,110,200)'},
                    }


                trace12 = {
                        'x': chart_1_trace_x,
                        'y': trace12_y ,
                        'text': [rec if rec > 0 else '' for rec in trace12_y] ,
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
                        'name': "Glycerin Crude",
                        'xaxis': 'x2',
                        'width': 0.2,
                        'offset': -0.27,
                        'barmode': 'stack',
                    'marker': {'color': 'rgb(110,50,160)'},
                    }

                trace56 = {
                        'x': chart_1_trace_x,
                        'y': trace5_y,
                        'text': [rec if rec > 0 else '' for rec in trace5_y] ,
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
                    'data': [trace12,trace1, trace5, trace9_y ],
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
                    'textposition': 'outside right',
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
                    'textposition': 'outside right',
                    'textangle': 0,
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
                    'text': list([f'{rec}     ' for rec in chart_2_trace_3]),
                    'textposition': 'top left',
                    'textangle': 0,
                    'hoverinfo': 'none',
                    'name': 'ظرفیت',
                    # 'type': 'bar',
                    'mode': 'text',
                    'marker': {
                        'size': 26,
                        'offset': .2,
                    },
                    'textfont': {
                        'color': "#1f77b4",
                        # 'size': 20,
                    }
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

