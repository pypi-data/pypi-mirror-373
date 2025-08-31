{
    "name": "Schema Parser Mixin",
    "version": "14.0.1.1.0",
    "summary": "Generic schema parser mixin with validation support",
    "author": "PT. Simetri Sinergi Indonesia",
    "website": "https://simetri-sinergi.id",
    "category": "Technical",
    "license": "AGPL-3",
    "depends": ["base", "ssi_master_data_mixin"],
    "external_dependencies": {"python": ["pyyaml"]},
    "data": [
        "security/ir_model_access.xml",
        "menus.xml",
        "views/schema_parser_category.xml",
        "views/schema_parser.xml",
    ],
    "installable": True,
    "application": False,
}
