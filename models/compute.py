import random
from odoo import models, fields,api

class ComputeModel(models.Model):
    _name = 'openacademy.computed'

    name = fields.Char(compute='compute')
    value = fields.Integer()
    #@api.multi --> ya no existe desde la versión 13
    """
    def compute(self):
        for record in self:
            record.name = str(random.randint(1,1e6))
    """
    @api.depends('value')
    def _compute_name(self):
        for record in self: 
            record.name = "Records with value %s" %record.value