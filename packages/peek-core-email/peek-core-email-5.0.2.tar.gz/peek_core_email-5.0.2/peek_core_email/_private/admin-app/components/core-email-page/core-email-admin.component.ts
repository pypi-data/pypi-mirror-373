
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "core-email-admin",
    templateUrl: "core-email-admin.component.html",
    styleUrls: ["core-email-admin.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CoreEmailAdminComponent extends NgLifeCycleEvents {
    constructor() {
        super();
    }
}