/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState } from "@odoo/owl";

export class BikeDashboard extends Component {
    static template = "bike_workshop.BikeDashboardTemplate";

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.state = useState({
            activeRentals: 0,
            returnsDue: 0,
            repairsInProgress: 0,
        });

        onWillStart(async () => {
            await this.loadData();
        });
    }

    async loadData() {
        this.state.activeRentals = await this.orm.searchCount(
            "bike.rental",
            [["state", "=", "confirmed"]]
        );

        const today = new Date().toISOString().split("T")[0];
        this.state.returnsDue = await this.orm.searchCount(
            "bike.rental",
            [
                ["state", "=", "confirmed"],
                ["expected_return_date", "<=", today],
            ]
        );

        this.state.repairsInProgress = await this.orm.searchCount(
            "bike.repair",
            [["state", "=", "in_progress"]]
        );
    }

    openActiveRentals() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Active Rentals",
            res_model: "bike.rental",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", "confirmed"]],
        });
    }

    openReturnsDue() {
        const today = new Date().toISOString().split("T")[0];
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Returns Due",
            res_model: "bike.rental",
            views: [[false, "list"], [false, "form"]],
            domain: [
                ["state", "=", "confirmed"],
                ["expected_return_date", "<=", today],
            ],
        });
    }

    openRepairsInProgress() {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: "Repairs In Progress",
            res_model: "bike.repair",
            views: [[false, "list"], [false, "form"]],
            domain: [["state", "=", "in_progress"]],
        });
    }
}

registry.category("actions").add("bike_workshop_dashboard", BikeDashboard);