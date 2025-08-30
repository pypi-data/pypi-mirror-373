import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
    Tuple,
} from "@synerty/vortexjs";
import {
    docDbGenericMenuFilt,
    DocDbGenericMenuTuple,
} from "@peek/peek_plugin_docdb_generic_menu/_private";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-docdb-generic-menu-edit-docdb-generic-menu",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditDocDbGenericMenuComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<DocDbGenericMenuTuple[]>(
        [],
    );
    protected readonly itemsToDelete$ = new BehaviorSubject<
        DocDbGenericMenuTuple[]
    >([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);

    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.DocDbGenericMenuTuple",
    };

    constructor(
        private vortexService: VortexService,
        private balloonMsg: BalloonMsgService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(
            this,
            Object.assign({}, this.filt, docDbGenericMenuFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <DocDbGenericMenuTuple[]>tuples;
                this.items$.next(typedTuples);
                this.itemsToDelete$.next([]);
            });
    }

    protected handleAddRow(): void {
        const t = new DocDbGenericMenuTuple();
        const currentItems = this.items$.getValue();
        this.items$.next([...currentItems, t]);
    }

    protected handleRemoveRow(item: DocDbGenericMenuTuple): void {
        if (item.id != null) {
            const currentItemsToDelete = this.itemsToDelete$.getValue();
            this.itemsToDelete$.next([...currentItemsToDelete, item]);
        }

        const currentItems = this.items$.getValue();
        const index: number = currentItems.indexOf(item);
        if (index !== -1) {
            const newItems = [...currentItems];
            newItems.splice(index, 1);
            this.items$.next(newItems);
        }
    }

    protected handleSave(): void {
        const items = this.items$.getValue();

        for (const item of items) {
            if (item.showCondition != null && item.showCondition.length != 0) {
                if (
                    item.showCondition.indexOf("==") == -1 &&
                    item.showCondition.indexOf("!=") == -1
                ) {
                    this.balloonMsg.showWarning(
                        "Failed to save, all conditions that are set must have '==' or '!=' in them",
                    );
                    return;
                }
            }

            if (item.url == null || item.url.length == 0) {
                this.balloonMsg.showWarning(
                    "Failed to save, all menus must have a url set",
                );
                return;
            }
        }

        this.loading$.next(true);
        const itemsToDelete = this.itemsToDelete$.getValue();

        this.loader
            .save(items)
            .then(() => {
                if (itemsToDelete.length != 0) {
                    return this.loader.del(itemsToDelete);
                }
                return null;
            })
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e))
            .finally(() => this.loading$.next(false));
    }

    protected handleReset(): void {
        this.loading$.next(true);
        this.loader
            .load()
            .catch((e) => this.balloonMsg.showError(e))
            .finally(() => this.loading$.next(false));
    }
}
