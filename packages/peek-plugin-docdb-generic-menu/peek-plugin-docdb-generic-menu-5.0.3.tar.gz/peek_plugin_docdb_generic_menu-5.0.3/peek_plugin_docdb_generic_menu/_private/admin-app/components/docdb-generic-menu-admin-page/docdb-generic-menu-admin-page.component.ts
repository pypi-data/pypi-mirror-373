
import { Component, ChangeDetectionStrategy } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "docDbGenericMenu-admin",
    templateUrl: "docdb-generic-menu-admin-page.component.html",
    styleUrls: ["docdb-generic-menu-admin-page.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocdbGenericMenuAdminPageComponent extends NgLifeCycleEvents {
    constructor() {
        super();
    }
}