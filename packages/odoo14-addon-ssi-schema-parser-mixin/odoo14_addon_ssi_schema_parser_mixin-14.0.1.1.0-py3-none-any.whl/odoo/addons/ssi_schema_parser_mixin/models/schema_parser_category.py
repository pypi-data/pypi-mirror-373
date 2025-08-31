from odoo import models


class SchemaParserCategory(models.Model):
    _name = "schema_parser_category"
    _description = "Schema Parser Category"
    _inherit = "mixin.master_data"
