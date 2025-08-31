import { Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { abstracDataLoaderFilt } from "../PluginNames";
import { AppServerSettingsTuple } from "../tuples/AppServerSettingsTuple";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";

@Component({
    selector: "pl-pof-diagram-loader-edit-source-settings",
    templateUrl: "./edit.component.html",
})
export class EditAppSettingsComponent extends NgLifeCycleEvents {
    item: AppServerSettingsTuple = new AppServerSettingsTuple();
    loader: TupleLoader;
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit." + AppServerSettingsTuple.tupleName,
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, abstracDataLoaderFilt),
        );

        this.loader.observable.subscribe((tuples: AppServerSettingsTuple[]) => {
            if (tuples.length == 1) {
                this.item = tuples[0];
            } else {
                this.item = new AppServerSettingsTuple();
            }

            // Setup defaults
            if (this.item.enabled == null) this.item.enabled = false;

            if (this.item.appSshUsername == null)
                this.item.appSshUsername = "enmac";
        });
    }

    save() {
        this.loader
            .save([this.item])
            .then(() => {
                this.balloonMsg.showSuccess("Success");
            })
            .catch((e) => {
                this.balloonMsg.showError(e);
            });
    }
}
