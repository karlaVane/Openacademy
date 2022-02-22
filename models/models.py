# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class openacademy(models.Model):
#     _name = 'openacademy.openacademy'
#     _description = 'openacademy.openacademy'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100


import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

class Course(models.Model):
    _name = 'openacademy.course'
    _description = "descripción de Course"

    name = fields.Char(string="Title",required=True)
    description = fields.Text()

    ## RELACIONES
    responsible_id = fields.Many2one('res.users', ondelete = 'set null', string="Responsible", index = True) 
    session_ids = fields.One2many(
        'openacademy.session', 'course_id', string="Sessions")

    ## ACCIONES cuando crea un formulario personalizado
    def action_test(self):
        raise ValidationError("Crear la función de confirmar")

    # opción para duplicar  --> está sobre escribiendo 
    def copy (self, default= None):
        logging.info("OK")
        default = dict(default or {})

        copied_count= self.search_count( #devuelve el conteo de los registros en vez del conjunto de registros.
            [('name','=like',_(u"Copy of {}%").format(self.name))])
        
        print(copied_count)
        if not copied_count:
            new_name = _(u"Copy of {}").format(self.name)
        else:
            new_name = _(u"Copy of {} ({})").format(self.name,copied_count)

        default['name']= new_name
        return super(Course,self).copy(default)

    # Restricciones SQL   
    _sql_constraints = [
        ('name_description_check',
        'CHECK(name != description)', #sql definitionn -> table_constraint
        'The title of the course should not be the description'), #message

        ('name_unique',
        'UNIQUE(name)',
        "The course title must be unique"),
    ]

class Session(models.Model):
    _name = 'openacademy.session'
    _description = "descripción de la tabla session"

    name = fields.Char(required = True)
    color = fields.Integer()
    
    # Valores por defecto
    start_date = fields.Date(default=fields.Date.today)
    active = fields.Boolean(default=True)
    #
    duration = fields.Integer( help= "Duration in days")
    seats = fields.Integer(string="Number of seats")
    
    ## RELACIONES 
    instructor_id = fields.Many2one('res.partner', string="Instructor", 
                    domain=['&',('instructor','=',True),
                    ('category_id.name', 'ilike', "Teacher")])
    course_id = fields.Many2one('openacademy.course',ondelete = 'cascade' , string="Course", required = True,domain=[("id",">",10)])
    attendee_ids = fields.Many2many('res.partner', string="Attendees")
    
    ## valores calculados
    # el comportamiento onchange está incorporado 
    taken_seats = fields.Float(string="Taken seats", compute="_taken_seats")
    attendees_count = fields.Integer(string="Attendees count", compute="test", store = True)
    end_date = fields.Date(string="End Date", store =True, compute ="_get_end_date", inverse="_set_end_date")

    """
    --- FUNCION INVERSA ---
    hace que el campo se pueda escribir 
    y permite mover las sesiones 
    (a través de arrastrar y soltar) 
    en la vista Calendario
    """

    @api.depends("seats", "attendee_ids")
    def _taken_seats(self):
        for e in self:
            if not e.seats:
                e.taken_seats=0.00
            else: 
                e.taken_seats= 100.0 * len(e.attendee_ids)/e.seats
    
    @api.depends("attendee_ids")
    def test(self):
        for e in self:
            e.attendees_count = len(e.attendee_ids)

    
    @api.onchange("seats","attendee_ids")
    def _verify_valid_seats(self):
        if self.seats < 0:
            return {
                'warning':{
                    'title': _("incorrect 'seats' value"),
                    'message': _("The number of available seats may not be negative"),
                },
            }
        if self.seats < len(self.attendee_ids):
            return{
                'warning':{
                    'title': _("Too many attendees"),
                    'message': _("Increase seats or remove excess attendees"),
                },
            }

    @api.depends('start_date','duration')
    def _get_end_date(self):
        for r in self:
            if not (r.start_date and r.duration):
                r.end_date = r.start_date
                continue

            start = fields.Datetime.from_string(r.start_date)
            duration = timedelta(days = r.duration,seconds =-1)
            r.end_date = start + duration
        
    def _set_end_date(self):
        for r in self: 
            if not (r.start_date and r.end_date):
                continue

            start_date = fields.Datetime.from_string(r.start_date)
            end_date = fields.Datetime.from_string(r.end_date)
            r.duration = (end_date -start_date).days +1



    @api.constrains('instructor_id', 'attendee_ids')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if r.instructor_id  in r.attendee_ids:
                raise ValidationError (_("A session's instructor can't be an attendee"))

        