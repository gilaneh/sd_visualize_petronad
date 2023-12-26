# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime, timedelta
import jdatetime
import json

class SdVisualizePetronadCalculate(models.Model):
    _inherit = 'sd_visualize.calculate'

    def calculate(self, function_name, diagram_id):
        res = super(SdVisualizePetronadCalculate, self).calculate(function_name, diagram_id)
        if function_name != 'petronad_ethylene_daily':
            return res
        # print(f'-------> SdVcalculateDataPetronad {function_name} {diagram_id} {res}')
        res['value'] = self.petronad_ethylene_daily(diagram_id)
        return res


    def petronad_ethylene_daily(self, diagram=0, start_date=date.today() - timedelta(days=30), end_date=date.today()):
        diagram = self.env['sd_visualize.diagram'].browse(diagram)
        print(f'calculate \n CALCULATE {diagram.values} \n {diagram}  self: {self}'
              f'\n {sorted(diagram.values, key=lambda val: val["sequence"])}')
        date_format = '%Y/%m/%d'
        calendar = self.env.context.get('lang')
        # report_date = datetime.strptime(report_date, date_format).date()

        if calendar == 'fa_IR':
            first_day = jdatetime.date.fromgregorian(date=end_date).replace(day=1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = (next_month - timedelta(days=next_month.day)).togregorian()
            first_day = first_day.togregorian
            s_start_date = jdatetime.date.fromgregorian(date=start_date).strftime("%Y/%m/%d")
            s_end_date = jdatetime.date.fromgregorian(date=end_date).strftime("%Y/%m/%d")

        else:
            first_day = end_date.replace(day=1)
            next_month = first_day.replace(day=28) + timedelta(days=5)
            last_day = next_month - timedelta(days=next_month.day)
            s_start_date = start_date.strftime("%Y/%m/%d")
            s_end_date = end_date.strftime("%Y/%m/%d")
        value_model = self.env['sd_visualize.values']
        feeds = self.env['km_data.feeds'].search([('feeds_date', '>=', start_date),
                                                  ('feeds_date', '<=', end_date), ], order='feeds_date desc')
        productions_list = self.env['km_data.production'].search([('production_date', '>=', start_date),
                                                                  ('production_date', '<=', end_date), ])
        sale_list = self.env['km_data.sale'].search([('sale_date', '>=', start_date),
                                                     ('sale_date', '<=', end_date), ])

        meg_production_list = [rec.meg_production for rec in productions_list]
        deg_production_list = [rec.deg_production for rec in productions_list]
        teg_production_list = [rec.teg_production for rec in productions_list]
        h1_production_list = [rec.h1_production for rec in productions_list]
        h2_production_list = [rec.h2_production for rec in productions_list]

        meg_sale_list = [rec.meg_sale for rec in sale_list]
        deg_sale_list = [rec.deg_sale for rec in sale_list]
        teg_sale_list = [rec.teg_sale for rec in sale_list]
        h2_sale_list = [rec.h2_sale for rec in sale_list]

        feeds_in = [rec.feed_in for rec in feeds]
        feeds_out = [rec.feed_out for rec in feeds]

        sorted_values = sorted(diagram.values, key=lambda val: val["sequence"])
        meg_production = 0
        deg_production = 0
        teg_production = 0
        h1_production = 0
        h2_production = 0
        ww_production = 0

        meg_sale = 0
        deg_sale = 0
        teg_sale = 0
        h2_sale = 0

        results = []
        for rec in sorted_values:
            # print(f'hhhhhhhhhh {rec.sequence}  {rec.variable_name}')
            if not rec.calculate:
                continue

            if rec.variable_name == 'first_date':
                value = s_start_date
            elif rec.variable_name == 'last_date':
                value = s_end_date
            elif rec.variable_name == 'feed_production':
                trace1 = {
                    'x': ['Two days before', 'The day before', 'That day'],
                    'y': [25, 28, 23],
                    'name': 'Feed',
                    'type': 'bar'
                };
                trace2 = {
                    'x': ['Two days before', 'The day before', 'That day'],
                    'y': [14, 12, 12],
                    'name': 'MEG',
                    'type': 'bar'
                };
                trace3 = {
                    'x': ['Two days before', 'The day before', 'That day'],
                    'y': [11, 10, 9],
                    'name': 'H1',
                    'type': 'bar'
                };

                value = json.dumps([trace1, trace2, trace3])
            # FEED
            # elif rec.variable_name == 'feed_in':
            #     value = self.float_num(sum(feeds_in), 2)
            # elif rec.variable_name == 'feed_out':
            #     feed_out = round(sum(feeds_out), 2)
            #     value = self.float_num(sum(feeds_out), 2)
            # elif rec.variable_name == 'feed_stock':
            #     if len(feeds) > 0:
            #         value = self.float_num(feeds[0].feed_stock, 2)
            #     else:
            #         value = '0'
            #
            # # MEG
            # elif rec.variable_name == 'meg_production':
            #     meg_production = round(sum(meg_production_list), 2)
            #     value = self.float_num(sum(meg_production_list), 2)
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

    #     @api.onchange('update')
    #     def update_compute(self):
    #         for rec in self:
    #             self._compute_values()
    #         return super(KmDataPetronad, self).update_compute()
    #
    #     def _compute_values(self):
    #         # todo: user might needed to have report based on time duration
    #         productions = self.env['km_data.production'].search([('production_date', '>=' , date.today() - timedelta(days=60))])
    #         meg_production = sum([rec.meg_production for rec in productions])
    # #        todo: diagram id

    def float_num(self, num, points):
        fnum = round(num, int(points))
        frac = fnum - int(fnum)
        return str(int(fnum)) if frac == 0 else str(fnum)
