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
            if function_name == 'petronad_ethylene_monthly':
                res['value'] = self.petronad_ethylene_monthly(diagram_id, update_date)
        #         todo: to prevent too many update requests, we can check some value write datetiem record.
        #           It seams that 10 seconds could be a good interval between two updates
        except Exception as err:
            # logging.error(f'CALCULATION:{function_name}/ {err}')
            logging.error(f'CALCULATION:{function_name}:\n{traceback.format_exc()}')

            raise ValidationError(f'CALCULATION:{function_name}/ {err}')
        return res


    def petronad_ethylene_monthly(self, diagram=0, update_date=0):
        diagram = self.env['sd_visualize.diagram'].browse(diagram)
        # print(f'--------->\n Monthly, diagarm.select_date: {diagram.select_date} {update_date}')
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        value_model = self.env['sd_visualize.values']
        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])
        month_production_plan = 720
        month_sale_plan = 720
        month_work_hours = 720
        report_date = date.fromisoformat(update_date)
        # todo: report_date must be the latest date of the month. Mind the jalaali or gregorian calendar

        # production = self.env['km_petronad.production_record'].search([
        #                                                         ('data_date', '<=', report_date),]
        #                                                        , order='data_date desc', limit=1,)
        # if len(production) == 0:
        #     raise ValidationError(f'Production not found')

        this_date = report_date
        month_s_0, month_e_0 = self.month_start_end(this_date, 0, calendar)
        month_s_1, month_e_1 = self.month_start_end(this_date, -1, calendar)
        month_s_2, month_e_2 = self.month_start_end(this_date, -2, calendar)
        month_s_3, month_e_3 = self.month_start_end(this_date, -3, calendar)
        month_s_4, month_e_4 = self.month_start_end(this_date, -4, calendar)
        month_s_5, month_e_5 = self.month_start_end(this_date, -5, calendar)
        today = date.today()
        month_days_0 = (month_s_0 - (today if today <= month_e_0 else month_e_0 + timedelta(days=1))).days
        month_days_0 = month_days_0 if month_days_0 > 0 else 0
        month_days_1 = (month_s_1 - (today if today <= month_e_1 else month_e_1 + timedelta(days=1))).days
        month_days_1 = month_days_1 if month_days_1 > 0 else 0
        month_days_2 = (month_s_2 - (today if today <= month_e_2 else month_e_2 + timedelta(days=1))).days
        month_days_2 = month_days_2 if month_days_2 > 0 else 0

        month_no_0 = jdatetime.date.fromgregorian(date=month_s_0).month
        month_no_1 = jdatetime.date.fromgregorian(date=month_s_1).month
        month_no_2 = jdatetime.date.fromgregorian(date=month_s_2).month
        report_year = jdatetime.date.fromgregorian(date=month_s_0).strftime('%Y')
        month_name_fa = jdatetime.datetime.now().j_months_fa
        three_months = [month_name_fa[month_no_2 - 1], month_name_fa[month_no_1 - 1], month_name_fa[month_no_0 - 1], ]

        # Production ##################################
        productions = self.env['km_petronad.production_record'].search([
                                                                 ('data_date', '>=', month_s_5),
                                                                 ('data_date', '<=', month_e_0), ]
                                                                ,order='data_date desc', )

        # if len(productions) == 0:
        #     raise ValidationError(f'Production not found')
        month_production_0 = [rec for rec in productions if rec.data_date >= month_s_0 and rec.data_date <= month_e_0]
        month_production_1 = [rec for rec in productions if rec.data_date >= month_s_1 and rec.data_date <= month_e_1]
        month_production_2 = [rec for rec in productions if rec.data_date >= month_s_2 and rec.data_date <= month_e_2]
        month_production_3 = [rec for rec in productions if rec.data_date >= month_s_3 and rec.data_date <= month_e_3]
        month_production_4 = [rec for rec in productions if rec.data_date >= month_s_4 and rec.data_date <= month_e_4]
        month_production_5 = [rec for rec in productions if rec.data_date >= month_s_5 and rec.data_date <= month_e_5]


        month_sum_feed_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                   if rec.fluid.name in ['FEED']
                                   and rec.register_type == 'feed_usage']))
        month_sum_feed_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                   if rec.fluid.name in ['FEED']
                                   and rec.register_type == 'feed_usage']))
        month_sum_feed_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                   if rec.fluid.name in ['FEED']
                                   and rec.register_type == 'feed_usage']))

        month_sum_meg_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                   if rec.fluid.name in ['MEG']
                                   and rec.register_type == 'production']))
        month_sum_meg_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                   if rec.fluid.name in ['MEG']
                                   and rec.register_type == 'production']))
        month_sum_meg_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                   if rec.fluid.name in ['MEG']
                                   and rec.register_type == 'production']))

        month_sum_deg_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                   if rec.fluid.name in ['DEG']
                                   and rec.register_type == 'production']))
        month_sum_deg_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                   if rec.fluid.name in ['DEG']
                                   and rec.register_type == 'production']))
        month_sum_deg_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                   if rec.fluid.name in ['DEG']
                                   and rec.register_type == 'production']))

        month_sum_teg_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                   if rec.fluid.name in ['TEG']
                                   and rec.register_type == 'production']))
        month_sum_teg_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                   if rec.fluid.name in ['TEG']
                                   and rec.register_type == 'production']))
        month_sum_teg_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                   if rec.fluid.name in ['TEG']
                                   and rec.register_type == 'production']))



        month_sum_sale_meg_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                   if rec.fluid.name in ['MEG']
                                   and rec.register_type == 'sale']))
        month_sum_sale_meg_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                   if rec.fluid.name in ['MEG']
                                   and rec.register_type == 'sale']))
        month_sum_sale_meg_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                   if rec.fluid.name in ['MEG']
                                   and rec.register_type == 'sale']))

        month_sum_sale_deg_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                   if rec.fluid.name in ['DEG']
                                   and rec.register_type == 'sale']))
        month_sum_sale_deg_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                   if rec.fluid.name in ['DEG']
                                   and rec.register_type == 'sale']))
        month_sum_sale_deg_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                   if rec.fluid.name in ['DEG']
                                   and rec.register_type == 'sale']))

        month_sum_sale_teg_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                   if rec.fluid.name in ['TEG']
                                   and rec.register_type == 'sale']))
        month_sum_sale_teg_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                   if rec.fluid.name in ['TEG']
                                   and rec.register_type == 'sale']))
        month_sum_sale_teg_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                   if rec.fluid.name in ['TEG']
                                   and rec.register_type == 'sale']))



        month_sum_feed_h1 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                      if rec.fluid.name in ['HEAVY1']
                                      and rec.register_type == 'feed_usage']))
        month_sum_meg = sum(list([self.ton_amount(rec) for rec in month_production_0
                                  if rec.fluid.name in ['MEG']
                                  and rec.register_type == 'production']))
        month_sum_deg = sum(list([self.ton_amount(rec) for rec in month_production_0
                                  if rec.fluid.name in ['DEG']
                                  and rec.register_type == 'production']))
        month_sum_teg = sum(list([self.ton_amount(rec) for rec in month_production_0
                                  if rec.fluid.name in ['TEG']
                                  and rec.register_type == 'production']))
        month_sum_h1 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                 if rec.fluid.name in ['HEAVY1']
                                 and rec.register_type == 'production']))
        month_sum_h2 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                 if rec.fluid.name in ['HEAVY2']
                                 and rec.register_type == 'production']))

        # Shutdowns
        shutdowns = self.env['km_petronad.shutdown'].search([
                                                                 ('shutdown_date', '>=', month_s_2),
                                                                 ('shutdown_date', '<=', month_e_0),
                                                                 ('fluid', 'in', ['MEG', 'DEG']),
        ]
                                                                ,order='shutdown_date desc', )


        month_shutdown_0 = [rec for rec in shutdowns if rec.shutdown_date >= month_s_0 and rec.shutdown_date <= month_e_0]
        month_shutdown_1 = [rec for rec in shutdowns if rec.shutdown_date >= month_s_1 and rec.shutdown_date <= month_e_1]
        month_shutdown_2 = [rec for rec in shutdowns if rec.shutdown_date >= month_s_2 and rec.shutdown_date <= month_e_2]

        month_shutdown_sum_0 = sum(list([rec.shutdown_time for rec in  month_shutdown_0]))
        month_shutdown_sum_1 = sum(list([rec.shutdown_time for rec in  month_shutdown_1]))
        month_shutdown_sum_2 = sum(list([rec.shutdown_time for rec in  month_shutdown_2]))

        month_shutdown_type_0 = list([rec.shutdown_type for rec in  month_shutdown_0])
        month_shutdown_types = []
        for shutdown_type in month_shutdown_type_0:
            shutdowns = list([rec.shutdown_time for rec in month_shutdown_0 if rec.shutdown_type == shutdown_type])
            shutdown_hours = sum(shutdowns)
            month_shutdown_types.append((shutdown_type.name, shutdown_hours ))




        month_productions_list = {'meg': [], 'deg': [], 'teg': [], }
        # date_week_day = list([month_s_0 + timedelta(days=i) for i in range(7)])
        # for rec_date in date_week_day:
        #     day_meg = sum(list([self.ton_amount(rec) for rec in month_production_0 if rec.fluid.name in ['MEG'] and rec.register_type == 'production' and rec.data_date == rec_date]))
        #     day_deg = sum(list([self.ton_amount(rec) for rec in month_production_0 if rec.fluid.name in ['DEG'] and rec.register_type == 'production' and rec.data_date == rec_date]))
        #     day_teg = sum(list([self.ton_amount(rec) for rec in month_production_0 if rec.fluid.name in ['TEG'] and rec.register_type == 'production' and rec.data_date == rec_date]))
        #
        #     month_productions_list['meg'].append(day_meg)
        #     month_productions_list['deg'].append(day_deg)
        #     month_productions_list['teg'].append(day_teg)

        # month_sum_meg = sum(month_productions_list['meg'])
        # month_sum_deg = sum(month_productions_list['deg'])
        # month_sum_teg = sum(month_productions_list['teg'])

        month_sum_production_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                           if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                           and rec.register_type == 'production']))
        month_sum_production_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                           if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                           and rec.register_type == 'production']))
        month_sum_production_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                           if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                           and rec.register_type == 'production']))
        
        month_sum_sale_0 = sum(list([self.ton_amount(rec) for rec in month_production_0
                                           if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                           and rec.register_type == 'sale']))
        month_sum_sale_1 = sum(list([self.ton_amount(rec) for rec in month_production_1
                                           if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                           and rec.register_type == 'sale']))
        month_sum_sale_2 = sum(list([self.ton_amount(rec) for rec in month_production_2
                                           if rec.fluid.name in ['MEG', 'DEG', 'TEG']
                                           and rec.register_type == 'sale']))


        # month_sum_production_0 = sum(
        #     list([rec.meg_production + rec.deg_production + rec.teg_production for rec in month_production_0]))
        # month_sum_production_1 = sum(
        #     list([rec.meg_production + rec.deg_production + rec.teg_production for rec in month_production_1]))
        # month_sum_production_2 = sum(
        #     list([rec.meg_production + rec.deg_production + rec.teg_production for rec in month_production_2]))
        # month_sum_production_3 = sum(
        #     list([rec.meg_production + rec.deg_production + rec.teg_production for rec in month_production_3]))
        # month_sum_production_4 = sum(
        #     list([rec.meg_production + rec.deg_production + rec.teg_production for rec in month_production_4]))
        # month_sum_production_5 = sum(
        #     list([rec.meg_production + rec.deg_production + rec.teg_production for rec in month_production_5]))
        
        # Sale ##################################
        # month_sales = self.env['km_petronad.sale'].search([
        #                                              ('sale_date', '>=', month_s_0),
        #                                              ('sale_date', '<=', month_e_0)],
        #                                             order='sale_date desc', )
        # print(f'==========> month_sales: {month_sales}')
        #
        # sales = self.env['km_petronad.sale'].search([
        #                                              ('sale_date', '>=', month_s_5),
        #                                              ('sale_date', '<=', month_e_0)],
        #                                             order='sale_date desc', )
        # if len(sales) > 0:
        #     # self.records_list(sales, month_s_0, month_e_0)
        #     # month_sale_0 = [rec for rec in sales if
        #     #                      rec.sale_date >= month_s_0 and rec.sale_date <= month_e_0]
        #     # month_sale_1 = [rec for rec in sales if
        #     #                      rec.sale_date >= month_s_1 and rec.sale_date <= month_e_1]
        #     # month_sale_2 = [rec for rec in sales if
        #     #                      rec.sale_date >= month_s_2 and rec.sale_date <= month_e_2]
        #     # month_sale_3 = [rec for rec in sales if
        #     #                      rec.sale_date >= month_s_3 and rec.sale_date <= month_e_3]
        #     # month_sale_4 = [rec for rec in sales if
        #     #                      rec.sale_date >= month_s_4 and rec.sale_date <= month_e_4]
        #     # month_sale_5 = [rec for rec in sales if
        #     #                      rec.sale_date >= month_s_5 and rec.sale_date <= month_e_5]
        #     month_sale_0 = self.records_list(sales, 'sale_date', month_s_0, month_e_0)
        #     month_sale_1 = self.records_list(sales, 'sale_date',month_s_1, month_e_1)
        #     month_sale_2 = self.records_list(sales, 'sale_date',month_s_2, month_e_2)
        #     month_sale_3 = self.records_list(sales, 'sale_date',month_s_3, month_e_3)
        #     month_sale_4 = self.records_list(sales, 'sale_date',month_s_4, month_e_4)
        #     month_sale_5 = self.records_list(sales, 'sale_date',month_s_5, month_e_5)
        #
        #     month_sum_sale_0 = sum(list([rec.amount for rec in month_sale_0]))
        #     month_sum_sale_1 = sum(list([rec.amount for rec in month_sale_1]))
        #     month_sum_sale_2 = sum(list([rec.amount for rec in month_sale_2]))
        #     month_sum_sale_3 = sum(list([rec.amount for rec in month_sale_3]))
        #     month_sum_sale_4 = sum(list([rec.amount for rec in month_sale_4]))
        #     month_sum_sale_5 = sum(list([rec.amount for rec in month_sale_5]))
        
        # Feeds ##################################
        # month_feeds = self.env['km_petronad.feeds'].search([
        #                                              ('feed_date', '>=', month_s_0),
        #                                              ('feed_date', '<=', month_e_0)],
        #                                             order='feed_date desc', )
        # Storages ##################################
        # storages = self.env['km_petronad.storage'].search([
        #                                                    ('storage_date', '<=', month_e_0)],
        #                                                   order='storage_date desc', limit=1,)

        # Tanks ##################################
        # tanks = self.env['km_petronad.tanks'].search([
        #                                               ('tanks_date', '<=', productions[0].production_date)],
        #                                              order='tanks_date desc', limit=1,)
        # Tanks ##################################
        # shutdowns = self.env['km_petronad.shutdown'].search([
        #                                                     ('shutdown_date', '>=', month_s_5),
        #                                                     ('shutdown_date', '<=', month_e_0)],
        #                                                    order='shutdown_date desc', )
        # month_shutdown_0 = self.records_list(shutdowns, 'shutdown_date', month_s_0, month_e_0)
        # month_shutdown_1 = self.records_list(shutdowns, 'shutdown_date', month_s_1, month_e_1)
        # month_shutdown_2 = self.records_list(shutdowns, 'shutdown_date', month_s_2, month_e_2)
        # month_sum_shutdown_0 = sum(list([rec.shutdown_time for rec in month_shutdown_0]))
        # month_sum_shutdown_1 = sum(list([rec.shutdown_time for rec in month_shutdown_1]))
        # month_sum_shutdown_2 = sum(list([rec.shutdown_time for rec in month_shutdown_2]))
        #
        # shutdown_types_list = list([(str(rec.shutdown_type.name), rec.shutdown_time) for rec in month_shutdown_0])
        # shutdown_types = list([rec[0] for rec in shutdown_types_list])
        # shutdown_types_sum = {}
        # for type_rec in shutdown_types:
        #     shutdown_types_sum[type_rec] = sum(list([rec[1] for rec in shutdown_types_list if rec[0] == type_rec]))

        # Results ##################################
        results = []
        for rec in sorted_values:
            if not rec.calculate:
                continue
            elif rec.variable_name == 'report_date':
                value = f'{self.convert_date(calendar, month_e_0)}  -  {self.convert_date(calendar, month_s_0)}'

            elif rec.variable_name == 'month_name':
                value = f'{month_name_fa[month_no_0 - 1]}  {report_year}'

            elif rec.variable_name == 'production_plan':
                value = month_production_plan

            elif rec.variable_name == 'month_production':
                value = self.float_num(month_sum_production_0, 2)

            elif rec.variable_name == 'month_sum_feed':
                value = self.float_num(month_sum_feed_0, 2)

            elif rec.variable_name == 'month_sum_feed_h1':
                value = self.float_num(month_sum_feed_h1, 2)

            elif rec.variable_name == 'month_sum_meg':
                value = self.float_num(month_sum_meg, 2)

            elif rec.variable_name == 'month_sum_deg':
                value = self.float_num(month_sum_deg, 2)

            elif rec.variable_name == 'month_sum_teg':
                value = self.float_num(month_sum_teg, 2)

            elif rec.variable_name == 'month_sum_h1':
                value = self.float_num(month_sum_h1, 2)

            elif rec.variable_name == 'month_sum_h2':
                value = self.float_num(month_sum_h2, 2)

            elif rec.variable_name == 'chart_1':



                trace1_y = [ month_sum_feed_2, month_sum_feed_1, month_sum_feed_0]
                trace2_y = [ month_sum_meg_2, month_sum_meg_1, month_sum_meg_0]
                trace3_y = [ month_sum_deg_2, month_sum_deg_1, month_sum_deg_0]
                trace4_y = [ month_sum_teg_2, month_sum_teg_1, month_sum_teg_0]
                trace234_y = [trace2_y[i] + trace3_y[i] + trace4_y[i] for i in range(3)]

                max_range = max(trace1_y + trace234_y)
                yrange = int(max_range * 1.2)
                month_avr_production = self.float_num(sum(trace1_y) / len(trace1_y), 2)
                performance_list = list(
                    map(lambda x: self.float_num(x * 100 / month_production_plan, 0) if month_production_plan else 0,
                        trace1_y))
                trace1 = {
                    'x': three_months,
                    'y': trace1_y,
                    'text': [rec if rec > 0  else '' for rec in trace1_y],
                    'textangle': 0,
                    'name': 'Feed',
                    'type': 'bar',
                    'width': .3,
                    'offset': -0.2,

                    'marker': {'color': 'rgb(110,50,160)'},
                    'textposition': 'outside',

                }
                trace2 = {
                    'x': three_months,
                    'y': trace2_y,
                    'text': [rec if rec > 0 and rec > .1 * max_range else '' for rec in trace2_y],
                    'textangle': 0,
                    'width': .3,
                    'offset': 0.2,
                    'yaxis': 'y2',
                    'name': 'MEG',
                    'type': 'bar',
                    'marker': {'color': 'rgb(30,80,120)'},

                }
                trace3 = {
                    'x': three_months,
                    'y': trace3_y,
                    'text': [rec if rec > 0 and rec > .1 * max_range else '' for rec in trace3_y],
                    'textangle': 0,
                    'width': .3,
                    'offset': 0.2,
                    'yaxis': 'y2',
                    'name': 'DEG',
                    'type': 'bar',
                    'marker': {'color': 'rgb(0,110,200)'},

                }
                trace4 = {
                    'x': three_months,
                    'y': trace4_y,
                    'text': [rec if rec > 0 and rec > .1 * max_range else '' for rec in trace4_y],
                    'textangle': 0,
                    'width': .3,
                    'offset': 0.2,
                    'yaxis': 'y2',
                    'name': 'TEG',
                    'type': 'bar',
                    'marker': {'color': 'rgb(160,200,230)'},

                }
                trace234 = {
                    'x': three_months,
                    'y': trace234_y,
                    'text': [rec if rec > 0 else '' for rec in trace234_y],
                    'textangle': 0,
                    'showlegend': False,
                    'width': .3,
                    'offset': 0.2,
                    'yaxis': 'y3',
                    'name': 'TEG',
                    'type': 'bar',
                    'textposition': 'outside',
                    'marker': {'color': 'rgba(0, 0, 0, 0)'},

                }


                plot_value = {
                    'data': [trace1, trace2, trace3, trace4, trace234],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'plot_bgcolor': 'rgba(255, 255, 255, 0)',
                               'showlegend': True,
                               'barmode': 'stack',
                               'legend': {'x': 1.3, 'y': 1, 'xanchor': 'right',},
                               'xaxis': {'fixedrange': True},
                               'yaxis1': {'anchor': 'y1',
                                         'fixedrange': True,
                                         'range': [0, yrange],
                                         'barmode': 'group',

                                         'showticklabels': False,
                                         'showgrid': False,

                                         },
                               'yaxis2': {'anchor': 'y2',
                                           'range': [0, yrange],
                                           'showticklabels': False,
                                           'barmode': 'stack',
                                   'showgrid': False,

                               },
                               'yaxis3': {'anchor': 'y3',
                                           'range': [0, yrange],
                                           'showticklabels': False,
                                           'barmode': 'group',
                                   'showgrid': False,

                               },
                               },
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)


            elif rec.variable_name == 'chart_2':
                month_no_0 = jdatetime.date.fromgregorian(date=month_s_0).month
                month_no_1 = jdatetime.date.fromgregorian(date=month_s_1).month
                month_no_2 = jdatetime.date.fromgregorian(date=month_s_2).month
                month_name_fa = jdatetime.datetime.now().j_months_fa
                three_months = [ month_name_fa[month_no_2 - 1],  month_name_fa[month_no_1 - 1],  month_name_fa[month_no_0 - 1], ]

                chart_2_trace1_y = [ month_sum_sale_meg_2, month_sum_sale_meg_1, month_sum_sale_meg_0]
                chart_2_trace2_y = [ month_sum_sale_deg_2, month_sum_sale_deg_1, month_sum_sale_deg_0]
                chart_2_trace3_y = [ month_sum_sale_teg_2, month_sum_sale_teg_1, month_sum_sale_teg_0]
                chart_2_trace123_y = [chart_2_trace1_y[i] + chart_2_trace2_y[i] + chart_2_trace3_y[i] for i in range(3)]

                chart_2_max_range = max(chart_2_trace123_y)
                chart_2_yrange = int(chart_2_max_range * 1.2)


                month_sum_sale_list = [ month_sum_sale_2, month_sum_sale_1, month_sum_sale_0]
                month_avr_sale = self.float_num(sum(month_sum_sale_list) / 6, 2)
                performance_list = list(
                    map(lambda x: self.float_num(x * 100 / month_sale_plan, 0) if month_sale_plan else 0,
                        month_sum_sale_list))
                trace1 = {
                    'x': three_months,
                    'y': chart_2_trace1_y,
                    'text': [rec if rec > 0 and rec > 0.2 * chart_2_max_range else '' for rec in chart_2_trace1_y],
                    'textangle': 0,
                    'textposition': 'inside',
                    'name': 'MEG',
                    'type': 'bar',
                    'yaxis': 'y1',
                    'marker': {'color': 'rgb(30,80,120)'},

                }
                trace2 = {
                    'x': three_months,
                    'y': chart_2_trace2_y,
                    'text': [rec if rec > 0 and rec > 0.2 * chart_2_max_range else '' for rec in chart_2_trace2_y],
                    'textangle': 0,
                    'textposition': 'inside',

                    'name': 'DEG',
                    'type': 'bar',
                    'yaxis': 'y1',
                    'marker': {'color': 'rgb(0,110,200)'},
                }
                trace3 = {
                    'x': three_months,
                    'y': chart_2_trace3_y,
                    'text': [rec if rec > 0 and rec > 0.2 * chart_2_max_range else '' for rec in chart_2_trace3_y],
                    'textangle': 0,
                    'textposition': 'inside',
                    'name': 'TEG',
                    'type': 'bar',
                    'yaxis': 'y1',

                    'marker': {'color': 'rgb(160,200,230)'},
                }
                trace123 = {
                    'x': three_months,
                    'y': chart_2_trace123_y,
                    'text': [rec if rec > 0 else '' for rec in chart_2_trace123_y],
                    'textangle': 0,
                    'showlegend': False,
                    'name': 'Sum',
                    'type': 'bar',
                    'yaxis': 'y2',
                    'marker': {'color': 'rgba(0, 0, 0, 0)', },
                    'textposition': 'outside',

                }

                plot_value = {
                    'data': [trace1, trace2, trace3, trace123],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'plot_bgcolor': 'rgba(255, 255, 255, 0)',
                               'showlegend': True,
                               'barmode': 'stack',
                               'legend': {'x': 1.2, 'y': 1, 'xanchor': 'right',},
                               'xaxis': {'fixedrange': True},
                               'yaxis1': { 'anchor': 'y1',
                                   # 'title': _('sale(tone)'),
                                           'range': [0, chart_2_yrange],
                                            'fixedrange': True,
                                           'barmode': 'stack',
                                           'showticklabels': False,
                                           'showgrid': False,

                                    },
                               'yaxis2': {'anchor': 'y2',
                                   'overlaying': 'y',
                                   'side': 'right',
                                   'range': [0, chart_2_yrange],
                                   'fixedrange': True,
                                    'barmode': 'group',
                                          'showticklabels': False,
                                          'showgrid': False,
                                    }
                               },
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)

            elif rec.variable_name == 'chart_3':
                # month_shutdown_0
                # month_shutdown_sum_0
                # month_work_hours
                chart_3_trace2_y = [ month_shutdown_sum_2, month_shutdown_sum_1, month_shutdown_sum_0]

                chart_3_trace1_y = [0, 0, 0]
                chart_3_trace1_y[2] = month_days_0 * 24 - chart_3_trace2_y[2]
                chart_3_trace1_y[1] = month_days_1 * 24 - chart_3_trace2_y[1]
                chart_3_trace1_y[0] = month_days_2 * 24 - chart_3_trace2_y[0]

                chart_3_trace3_y = [0, 0, 0]
                chart_3_trace3_y[2] = month_days_0 * 24
                chart_3_trace3_y[1] = month_days_1 * 24
                chart_3_trace3_y[0] = month_days_2 * 24

                month_avr_work = self.float_num(sum(chart_3_trace1_y) / len(chart_3_trace1_y), 2)
                chart_3_yrange = month_work_hours * 1.5
                trace1 = {
                    'x': three_months,
                    'y': chart_3_trace1_y,
                    'text': [rec if rec > 0  else '' for rec in chart_3_trace1_y],
                    'textangle': 0,
                    # 'textposition': 'inside',
                    'name': 'Work',
                    'type': 'bar',
                    'width': .99,
                    # 'yaxis': 'y1',
                    'marker': {'color': 'rgb(180, 200, 230)'},

                }
                trace2 = {
                    'x': three_months,
                    'y': chart_3_trace2_y,
                    'text': [rec if rec > 0  else '' for rec in chart_3_trace2_y],
                    'textangle': 0,
                    'textposition': 'outside',

                    'name': 'Stop',
                    'type': 'bar',
                    'width': .99,
                    # 'yaxis': 'y1',
                    'marker': {'color': 'rgb(0,0,0)'},
                }
                trace3 = {
                    'x': three_months,
                    'y': chart_3_trace3_y,
                    'text': [f'{rec}     ' for rec in chart_3_trace3_y],
                    'textposition': 'top left',
                    'textangle': 'horizontal',
                    'hoverinfo': 'none',
                    'name': 'Sum',
                    'mode': 'text',
                    'width': .99,
                    'textfont': {
                        'color': "#1f77b4",
                        'size': 22,
                    }

                }


                plot_value = {
                    'data': [trace1, trace2, trace3,],
                    'layout': {'autosize': False,
                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'plot_bgcolor': 'rgba(255, 255, 255, 0)',
                               'margin': {"t": 0, "b": 50, "l": 0, "r": 0},

                               'showlegend': True,
                               'barmode': 'stack',
                               'legend': {'x': 1.3, 'y': 1, 'xanchor': 'right',},
                               'xaxis': {'fixedrange': True},
                               'yaxis1': { 'anchor': 'y1',
                                   # 'title': _('sale(tone)'),
                                           'range': [0, chart_3_yrange],
                                            'fixedrange': True,
                                           'barmode': 'stack',
                                           'showticklabels': False,
                                           'showgrid': False,

                                    },
                               'yaxis2': {'anchor': 'y2',
                                   'overlaying': 'y',
                                   'side': 'right',
                                   'range': [0, chart_3_yrange],
                                   'fixedrange': True,
                                    'barmode': 'group',
                                          'showticklabels': False,
                                          'showgrid': False,
                                    }
                               },
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)

            elif rec.variable_name == 'chart_4':
                # month_shutdown_0
                # month_shutdown_sum_0
                # month_work_hours
                chart_3_trace2_y = [ month_shutdown_sum_2, month_shutdown_sum_1, month_shutdown_sum_0]
                chart_3_trace1_y = list([month_work_hours - rec for rec in chart_3_trace2_y])

                sh_values = []
                sh_labels = []
                for sh_rec in month_shutdown_types:
                    sh_labels.append(sh_rec[0])
                    sh_values.append(sh_rec[1])

                month_avr_work = self.float_num(sum(chart_3_trace1_y) / len(chart_3_trace1_y), 2)
                chart_3_trace3_y = [ month_avr_work, month_avr_work, month_avr_work]
                chart_3_yrange = month_work_hours + 30
                trace1 = {
                    'values': sh_values,
                    'labels': sh_labels,
                    'type': 'pie',
                    'textinfo': "label+value+percent",
                    'textposition': "outside",
                    # 'marker': {'color': 'rgb(180, 200, 230)'},
                #     todo: fix colors for each type of shutdowns. It can be a record on the shutdown type record to be
                #       selected by the user.

                }


                plot_value = {
                    'data': [trace1, ],
                    'layout': {'autosize': False,
                               'margin': {"t": 60, "b": 60, "l": 60, "r": 60},

                               'paper_bgcolor': 'rgb(255,255,255,0)',
                               'plot_bgcolor': 'rgba(255, 255, 255, 0)',
                               'showlegend': False,
                               'barmode': 'stack',
                               'legend': {'x': 1.3, 'y': 1, 'xanchor': 'right',},
                               'xaxis': {'fixedrange': True},
                               'yaxis1': { 'anchor': 'y1',
                                   # 'title': _('sale(tone)'),
                                           'range': [0, chart_3_yrange],
                                            'fixedrange': True,
                                           'barmode': 'stack',
                                           'showticklabels': False,
                                           'showgrid': False,

                                    },
                               'yaxis2': {'anchor': 'y2',
                                   'overlaying': 'y',
                                   'side': 'right',
                                   'range': [0, chart_3_yrange],
                                   'fixedrange': True,
                                    'barmode': 'group',
                                          'showticklabels': False,
                                          'showgrid': False,
                                    }
                               },
                    'config': {'responsive': False, 'displayModeBar': False}
                }
                value = json.dumps(plot_value)




            # elif rec.variable_name == 'month_sale':
            # # Sale sum
            #     if len(month_sales) > 0:
            #         value = self.float_num(sum(list([rec.amount for rec in month_sales])), 2)
            #     else:
            #         value = 0
            # elif rec.variable_name == 'stock_production':
            # # Sale sum
            #     if len(storages) > 0:
            #         value = self.float_num(sum(list([rec.meg_storage + rec.deg_storage + rec.teg_storage for rec in storages])), 2)
            #     else:
            #         value = 0
            # elif rec.variable_name == 'chart_1':
            #     three_months = ['دوم', 'ماه پیش', 'ماه جاری',]
            #     month_sum_production_list = [month_sum_production_2,month_sum_production_1,month_sum_production_0]
            #     # month_avr_production = self.float_num(sum(month_sum_production_list) / 6, 2)
            #     # performance_list = list(map(lambda x: self.float_num(x * 100 / month_production_plan, 0) if month_production_plan else 0, month_sum_production_list ))
            #     trace1 = {
            #         'x': three_months,
            #         'y': [720 - month_sum_shutdown_2, 720- month_sum_shutdown_1, 720 - month_sum_shutdown_0],
            #         'text': [720 - month_sum_shutdown_2, 720- month_sum_shutdown_1, 720 - month_sum_shutdown_0],
            #         'name': 'Working',
            #         'type': 'bar',
            #         'marker': {
            #             'color': 'rgb(180,200,230)',
            #         },
            #         'textposition': 'inside',
            #
            #     }
            #     trace2 = {
            #         'x': three_months,
            #         'y': [month_sum_shutdown_2, month_sum_shutdown_1, month_sum_shutdown_0],
            #         'text': [month_sum_shutdown_2, month_sum_shutdown_1, month_sum_shutdown_0],
            #         'name': 'Shutdown',
            #         'type': 'bar',
            #         'marker': {
            #             'color': 'rgb(80,80,80)',
            #         },
            #         'textposition': 'outside',
            #
            #     }
            #
            #     plot_value = {
            #         'data': [trace1, trace2, ],
            #         'layout': {'autosize': False,
            #                    'paper_bgcolor': 'rgb(255,255,255,0)',
            #                    'showlegend': True,
            #                    'legend': {"orientation": "h"},
            #                    'barmode': 'stack',
            #                    'bargap' : 0.01, 'bargroupgap' : 0.0,
            #                    'xaxis': {'fixedrange': True},
            #                    'yaxis': {
            #                        'title': _('Production(tone)'),
            #                        'fixedrange': True,
            #                        'range': [0, month_production_plan * 1.2],
            #
            #                    },
            #                    'yaxis2': {
            #                        'overlaying': 'y',
            #                        'side': 'right',
            #                        'range': [0, 100],
            #                        'fixedrange': True,
            #                        'title': _('Efficiency(%)'),
            #                    }
            #                    },
            #         'config': {'responsive': True, 'displayModeBar': False}
            #     }
            #     value = json.dumps(plot_value)
            #
            # elif rec.variable_name == 'chart_2':
            #     six_months = ['پنجم', 'چهارم', 'سوم', 'دوم', 'هفته پیش', 'هفته جاری',]
            #     month_sum_sale_list = [month_sum_sale_5,month_sum_sale_4,month_sum_sale_3,month_sum_sale_2,month_sum_sale_1,month_sum_sale_0]
            #     month_avr_sale = self.float_num(sum(month_sum_sale_list) / 6, 2)
            #
            #     trace1 = {
            #               'type': 'pie',
            #               'values': list(shutdown_types_sum.values()),
            #               'labels': list(shutdown_types_sum.keys()),
            #               'textinfo': 'label+value',
            #               'textposition': 'outside',
            #                 'showlegend': False,
            #               }
            #
            #     plot_value = {
            #         'data': [trace1,   ],
            #         'layout': {'autosize': False,
            #                    'paper_bgcolor': 'rgb(255,255,255,0)',
            #                    'showlegend': True,
            #                    'legend': {"orientation": "h"},
            #                    'xaxis': {'fixedrange': True},
            #                    'yaxis': {
            #                        'fixedrange': True
            #                    },
            #                    'angularaxis': {
            #                        'direction': "clockwise",
            #                        'period': 6
            #                    },
            #                    'polar': {
            #                        'radialaxis': {
            #                            'angle': 90,
            #                            'textangle': 90,
            #                            'showgrid': False,
            #                            'showline': False,
            #                            'tickangle': 90,
            #                            'CanvasGradient': False,
            #                        },
            #                        'angularaxis': {
            #                            'direction': "clockwise",
            #                            'visible': True,
            #                            'linecolor': 'rgb(255,255,255,0)'
            #                        },
            #                    },
            #                    },
            #         'config': {'responsive': True, 'displayModeBar': False}
            #     }
            #     value = json.dumps(plot_value)
            #
            # elif rec.variable_name == 'chart_3':
            #     theta = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه',]
            #     month_production_0_list = self.create_monthly_list(month_production_0, calendar)
            #     trace2_r = list([rec.feed if rec else 0 for rec in month_production_0_list ])
            #     tr_avr = sum(trace2_r) / 7
            #     trace2_avr = []
            #     [trace2_avr.append(tr_avr) for rec in  range(7)]
            #     trace1 = {
            #               'type': 'scatterpolar',
            #               'r': [30, 30, 30, 30, 30, 30, 30, ],
            #               'theta': theta,
            #               # 'fill': 'toself',
            #               'name': 'Feed Plan',
            #                 'line':{
            #                     'color': 'rgb(50,50,50)'
            #                 },
            #               }
            #     trace2 = {
            #               'type': 'scatterpolar',
            #               'r': trace2_r,
            #               'theta': theta,
            #               # 'fill': 'toself',
            #               'name': 'Daily Feed',
            #         'line': {
            #             'dash': 'solid',
            #             'color': 'rgb(30,100,150)',
            #             'width': 3,
            #             },
            #               }
            #     trace3 = {
            #               'type': 'scatterpolar',
            #               'r': trace2_avr,
            #               'theta': theta,
            #               # 'fill': 'toself',
            #               'name': 'Average',
            #                 'line': {
            #                 'dash': 'dash',
            #                 'color': 'rgb(255,128,0)'
            #                 },
            #               }
            #     plot_value = {
            #         'data': [trace1, trace2, trace3,  ],
            #         'layout': {'autosize': False,
            #                    'paper_bgcolor': 'rgb(255,255,255,0)',
            #                    'showlegend': True,
            #                    'legend': {"orientation": "h"},
            #                    'xaxis': {'fixedrange': True},
            #                    'yaxis': {
            #                        'fixedrange': True
            #                    },
            #                    'angularaxis': {
            #                        'direction': "clockwise",
            #                        'period': 6
            #                    },
            #                    'polar': {
            #                        'radialaxis': {
            #                            'angle': 90,
            #                            'textangle': 90,
            #                            'showgrid': False,
            #                            'showline': False,
            #                            'tickangle': 90,
            #                            'CanvasGradient': False,
            #                        },
            #                        'angularaxis': {
            #                            'direction': "clockwise",
            #                            'visible': True,
            #                            'linecolor': 'rgb(255,255,255,0)'
            #                        },
            #                    },
            #                    },
            #         'config': {'responsive': True, 'displayModeBar': False}
            #     }
            #     value = json.dumps(plot_value)
            #
            # elif rec.variable_name == 'chart_4':
            #     theta = ['شنبه', 'یکشنبه', 'دوشنبه', 'سه شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه',]
            #     month_production_0_list = self.create_monthly_list(month_production_0, calendar)
            #     trace2_r = list([rec.meg_production + rec.deg_production + rec.teg_production  if rec else 0 for rec in month_production_0_list ])
            #     tr_avr = sum(trace2_r) / 7
            #     trace2_avr = []
            #     [trace2_avr.append(tr_avr) for rec in  range(7)]
            #     trace1 = {
            #               'type': 'scatterpolar',
            #               'r': [18, 18, 18, 18, 18, 18, 18,  ],
            #               'theta': theta,
            #               # 'fill': 'toself',
            #               'name': 'Feed Plan',
            #                 'line':{
            #                     'color': 'rgb(50,50,50)'
            #                 },
            #               }
            #     trace2 = {
            #               'type': 'scatterpolar',
            #               'r': trace2_r,
            #               'theta': theta,
            #               # 'fill': 'toself',
            #               'name': 'Daily Feed',
            #         'line': {
            #             'dash': 'solid',
            #             'color': 'rgb(30,100,150)',
            #             'width': 3,
            #             },
            #               }
            #     trace3 = {
            #               'type': 'scatterpolar',
            #               'r': trace2_avr,
            #               'theta': theta,
            #               # 'fill': 'toself',
            #               'name': 'Average',
            #                 'line': {
            #                 'dash': 'dash',
            #                 'color': 'rgb(255,128,0)'
            #                 },
            #               }
            #     plot_value = {
            #         'data': [trace1, trace2, trace3,  ],
            #         'layout': {'autosize': False,
            #                    'paper_bgcolor': 'rgb(255,255,255,0)',
            #                    'showlegend': True,
            #                    'legend': {"orientation": "h"},
            #                    'xaxis': {'fixedrange': True},
            #                    'yaxis': {
            #                        'fixedrange': True
            #                    },
            #                    'angularaxis': {
            #                        'direction': "clockwise",
            #                        'period': 6
            #                    },
            #                    'polar': {
            #                        'radialaxis': {
            #                            'angle': 90,
            #                            'textangle': 90,
            #                            'showgrid': False,
            #                            'showline': False,
            #                            'tickangle': 90,
            #                            'CanvasGradient': False,
            #                        },
            #                        'angularaxis': {
            #                            'direction': "clockwise",
            #                            'visible': True,
            #                            'linecolor': 'rgb(255,255,255,0)'
            #                        },
            #                    },
            #                    },
            #         'config': {'responsive': True, 'displayModeBar': False}
            #     }
            #     value = json.dumps(plot_value)
            # elif rec.variable_name == 'chart_5':
            #     month_production_0_list = self.create_monthly_list(month_production_0, calendar)
            #     meg_production = sum(list([rec.meg_production if rec else 0 for rec in month_production_0_list ]))
            #     deg_production = sum(list([rec.deg_production if rec else 0 for rec in month_production_0_list ]))
            #     teg_production = sum(list([rec.teg_production if rec else 0 for rec in month_production_0_list ]))
            #     tr_avr = sum(trace2_r) / 7
            #     trace2_avr = []
            #     [trace2_avr.append(tr_avr) for rec in  range(7)]
            #     trace1 = {
            #               'type': 'pie',
            #               'values': [meg_production, deg_production, teg_production, ],
            #               'labels': ['MEG', 'DEG', 'TEG'],
            #               'textinfo': 'label+value',
            #               'textposition': 'outside',
            #                 'showlegend': False,
            #
            #
            #               }
            #
            #     plot_value = {
            #         'data': [trace1,   ],
            #         'layout': {'autosize': False,
            #                    'paper_bgcolor': 'rgb(255,255,255,0)',
            #                    'showlegend': True,
            #                    'legend': {"orientation": "h"},
            #                    'xaxis': {'fixedrange': True},
            #                    'yaxis': {
            #                        'fixedrange': True
            #                    },
            #                    'angularaxis': {
            #                        'direction': "clockwise",
            #                        'period': 6
            #                    },
            #                    'polar': {
            #                        'radialaxis': {
            #                            'angle': 90,
            #                            'textangle': 90,
            #                            'showgrid': False,
            #                            'showline': False,
            #                            'tickangle': 90,
            #                            'CanvasGradient': False,
            #                        },
            #                        'angularaxis': {
            #                            'direction': "clockwise",
            #                            'visible': True,
            #                            'linecolor': 'rgb(255,255,255,0)'
            #                        },
            #                    },
            #                    },
            #         'config': {'responsive': True, 'displayModeBar': False}
            #     }
            #     value = json.dumps(plot_value)


            else:
                continue

            results.append((rec.id, value))

        # Update Values ##################################
        for rec in results:
            value_model.browse(rec[0]).write({'value': rec[1]})

        return {'name': 'arash'}



    def create_monthly_list(self, records, lang):
        new_record_list = [0, 0, 0, 0, 0, 0, 0, ]
        month_days = [5, 6, 0, 1, 2, 3, 4, ]
        for rec in records:
            index = month_days.index(rec.production_date.monthday())
            new_record_list[index] = rec
        return new_record_list


    def records_list(self, records, date_name, start_date, end_date):
        return list([rec for rec in records if rec[f'{date_name}'] >= start_date and rec[f'{date_name}'] <= end_date])

    def ton_amount(self, rec):
        return int(rec.amount * 0.001) if rec.unit == 'kg' else rec.amount