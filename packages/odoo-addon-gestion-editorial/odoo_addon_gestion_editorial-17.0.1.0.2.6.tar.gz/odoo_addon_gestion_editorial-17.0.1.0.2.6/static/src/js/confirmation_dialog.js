/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { ConfirmationDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";

function showCustomConfirmDialogs(env, conditions) {
    return new Promise((resolve, reject) => {
        const showNext = (i) => {
            if (i >= conditions.length) { resolve(); return; }
            const { message } = conditions[i];
            env.services.dialog.add(ConfirmationDialog, {
                body: message,
                confirmLabel: _t("Confirmar"),
                cancelLabel: _t("Cancelar"),
                confirm: () => showNext(i + 1),
                cancel: () => reject(),
            });
        };
        showNext(0);
    });
}

patch(FormController.prototype, {
    setup() {
        super.setup(...arguments);
        this.dialogService = useService("dialog");
        this.orm = useService("orm");
    },

    // onWillSaveRecord triggers before Odoo saves the record
    async onWillSaveRecord(record, changes) {
        // Only work with product.template models, extend if needed
        if (record.resModel === "product.template") {
            const records_data = { id: record.resId, ...changes };
            let conditions = [];
            try {
                // RPC call to check_save_conditions
                conditions = await this.orm.call(
                    record.resModel,
                    "check_save_conditions",
                    [records_data]
                );
            } catch (err) {
                console.error("Error checking save conditions:", err);
                return super.onWillSaveRecord(record, changes);
            }
            if (conditions && conditions.length) {
                try {
                    await showCustomConfirmDialogs(this.env, conditions);
                } catch {
                    // User cancelled the confirmation dialog
                    return false;
                }
            }
        }
        // Execute the default save action
        return super.onWillSaveRecord(record, changes);
    },
});
