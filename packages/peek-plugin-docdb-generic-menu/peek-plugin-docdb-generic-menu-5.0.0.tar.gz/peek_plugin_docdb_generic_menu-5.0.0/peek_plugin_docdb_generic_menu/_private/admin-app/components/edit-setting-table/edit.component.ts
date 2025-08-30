import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
    Tuple,
} from "@synerty/vortexjs";
import {
    docDbGenericMenuFilt,
    SettingPropertyTuple,
} from "@peek/peek_plugin_docdb_generic_menu/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-docdb-generic-menu-edit-setting",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingPropertyTuple[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.SettingProperty",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(
            this,
            Object.assign({}, this.filt, docDbGenericMenuFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingPropertyTuple[]>tuples;
                this.items$.next(typedTuples);
            });
    }

    protected handleSave(): void {
        this.loading$.next(true);
        this.loader
            .save()
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e))
            .finally(() => this.loading$.next(false));
    }

    protected handleReset(): void {
        this.loading$.next(true);
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e))
            .finally(() => this.loading$.next(false));
    }
}
