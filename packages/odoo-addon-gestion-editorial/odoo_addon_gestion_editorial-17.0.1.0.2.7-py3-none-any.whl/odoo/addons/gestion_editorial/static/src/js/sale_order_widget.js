/** @odoo-module **/

/* Modified version of original code from OCB
https://github.com/OCA/OCB/blob/17.0/addons/sale_stock/static/src/widgets/qty_at_date_widget.js
*/

import { formatDateTime } from "@web/core/l10n/dates";
import { localization } from "@web/core/l10n/localization";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { usePopover } from "@web/core/popover/popover_hook";
import { Component, onWillRender } from "@odoo/owl";

export class SaleOrderPopover extends Component {
    setup() {
        this.actionService = useService("action");
    }

    openForecast() {
        this.actionService.doAction("stock.stock_forecasted_product_product_action", {
            additionalContext: {
                active_model: 'product.product',
                active_id: this.props.record.data.product_id[0],
                warehouse: this.props.record.data.warehouse_id && this.props.record.data.warehouse_id[0],
                move_to_match_ids: this.props.record.data.move_ids.records.map(record => record.resId),
                sale_line_to_match_id: this.props.record.resId,
            },
        });
    }
}

SaleOrderPopover.template = "gestion_editorial.SaleOrderPopover";

export class SaleOrderWidget extends Component {
    setup() {
        this.popover = usePopover(this.constructor.components.Popover, { position: "top" });
        this.calcData = {};
        onWillRender(() => {
            this.initCalcData();
        })
    }

    initCalcData() {
        // calculate data not in record
        const { data } = this.props.record;
        this.calcData.not_enough_stock = data.in_stock_qty < data.qty_to_deliver;
        this.calcData.delivery_date = formatDateTime(data.scheduled_date, { format: localization.dateFormat });
    }

    showPopup(ev) {
        this.popover.open(ev.currentTarget, {
            record: this.props.record,
            calcData: this.calcData,
        });
    }
}

SaleOrderWidget.components = { Popover: SaleOrderPopover };
SaleOrderWidget.template = "gestion_editorial.SaleOrderWidget";

export const saleOrderWidget = {
    component: SaleOrderWidget,
};
registry.category("view_widgets").add("sale_order_widget", saleOrderWidget);
