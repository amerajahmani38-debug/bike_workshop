from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager

import logging
_logger = logging.getLogger(__name__)
_logger.info(">>> LOADING bike_workshop_task portal.py NOW <<<")


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "rental_count" in counters:
            values["rental_count"] = request.env["bike.rental"].search_count([
                ("customer_id", "=", request.env.user.partner_id.id),
            ])
        return values

    @http.route(["/my/rentals", '/my/rentals/page/<int:page>'], type="http", auth="user", website=True)
    def portal_my_rentals(self, page=1, sortby=None, **kwargs):
        domain = [('customer_id', '=', request.env.user.partner_id.id)]
        rental_count = request.env["bike.rental"].search_count(domain)
        
        step = 10
        pager = portal_pager(
            url='/my/rentals',
            total=rental_count,
            page=page,
            step=step,
        )
        
        rentals = request.env["bike.rental"].search(
            domain, 
            order="start_date desc, id desc", 
            limit=step, 
            offset=pager['offset']
        )
        
        return request.render("bike_workshop_task.portal_my_rentals_list", {
            "rentals": rentals,
            "page_name": "rental",
            "pager": pager,
            "default_url": "/my/rentals",
        })

    @http.route("/my/rentals/<int:rental_id>", type="http", auth="user", website=True)
    def portal_rental_detail(self, rental_id, **kwargs):
        rental = request.env["bike.rental"].search([
            ("id", "=", rental_id),
            ("customer_id", "=", request.env.user.partner_id.id),
        ], limit=1)
        if not rental:
            return request.not_found()
        return request.render("bike_workshop_task.portal_my_rental_detail", {
            "rental": rental,
            "page_name": "rental",
        })