
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { NgLifeCycleEvents, TupleLoader, VortexService } from "@synerty/vortexjs";
import { branchFilt, SettingPropertyTuple } from "@peek/peek_plugin_branch/_private";
import { BehaviorSubject } from "rxjs";
import { Tuple } from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-branch-edit-setting",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush
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

        this.loader = vortexService.createTupleLoader(this, () => 
            Object.assign({}, this.filt, branchFilt)
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingPropertyTuple[]>tuples;
                this.items$.next(typedTuples);
            });
    }

    protected async handleSave(): Promise<void> {
        try {
            this.loading$.next(true);
            await this.loader.save();
            this.balloonMsg.showSuccess("Save Successful");
        } catch (e) {
            this.balloonMsg.showError(e);
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
            this.balloonMsg.showError(e);
        } finally {
            this.loading$.next(false);
        }
    }
}