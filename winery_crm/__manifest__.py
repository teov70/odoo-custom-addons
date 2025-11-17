# -*- coding: utf-8 -*-
{
    "name": "Winery CRM",
    "version": "19.0.1.0.0",
    "summary": "Winery-centric CRM: estates and tastings.",
    "description": """
Winery CRM
==========

Initial skeleton: estates and tastings with basic menus and access.
""",
    "category": "Sales/CRM",
    "author": "Teo",
    "license": "LGPL-3",
    "depends": [
        "base",
        "contacts",
        "mail",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/winery_menus.xml",
        "views/winery_estate_views.xml",
        "views/winery_tasting_views.xml",
        "views/winery_variety_views.xml",
        "views/winery_sample_views.xml",
    ],
    "demo": [],
    "application": True,
}# type: ignore
