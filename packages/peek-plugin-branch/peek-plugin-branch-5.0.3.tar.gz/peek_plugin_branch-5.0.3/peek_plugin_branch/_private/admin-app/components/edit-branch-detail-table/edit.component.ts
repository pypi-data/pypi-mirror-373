import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import {
    BranchDetailTuple,
    branchFilt,
} from "@peek/peek_plugin_branch/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-branch-edit-branch-detail",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditBranchDetailComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<BranchDetailTuple[]>([]);
    protected readonly itemsToDelete$ = new BehaviorSubject<
        BranchDetailTuple[]
    >([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    protected readonly loader: TupleLoader;

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.BranchDetailTable",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () => {
            return Object.assign({}, this.filt, branchFilt);
        });

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                this.items$.next(<BranchDetailTuple[]>tuples);
                this.itemsToDelete$.next([]);
            });
    }

    protected handleAddRow(): void {
        const currentItems = this.items$.getValue();
        const t = new BranchDetailTuple();
        this.items$.next([...currentItems, t]);
    }

    protected handleRemoveRow(item: BranchDetailTuple): void {
        const currentItems = this.items$.getValue();
        const currentItemsToDelete = this.itemsToDelete$.getValue();

        if (item.id != null) {
            this.itemsToDelete$.next([...currentItemsToDelete, item]);
        }

        const index: number = currentItems.indexOf(item);
        if (index !== -1) {
            const newItems = [...currentItems];
            newItems.splice(index, 1);
            this.items$.next(newItems);
        }
    }

    protected async handleSave(): Promise<void> {
        try {
            this.loading$.next(true);
            const itemsToDelete = this.itemsToDelete$.getValue();
            const currentItems = this.items$.getValue();

            await this.loader.save(currentItems);

            if (itemsToDelete.length !== 0) {
                await this.loader.del(itemsToDelete);
            }

            this.balloonMsg.showSuccess("Save Successful");
        } catch (e) {
            this.balloonMsg.showError(`${e}`);
        } finally {
            this.loading$.next(false);
        }
    }

    protected async handleReset(): Promise<void> {
        try {
            this.loading$.next(true);
            await this.loader.load();
            this.balloonMsg.showSuccess("Reset Successful");
        } catch (e) {
            this.balloonMsg.showError(`${e}`);
        } finally {
            this.loading$.next(false);
        }
    }
}
