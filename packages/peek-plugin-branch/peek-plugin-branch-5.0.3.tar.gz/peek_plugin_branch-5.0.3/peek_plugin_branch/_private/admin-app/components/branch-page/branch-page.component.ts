
import { ChangeDetectionStrategy, Component } from "@angular/core";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

@Component({
    selector: "branch-admin",
    templateUrl: "branch-page.component.html",
    styleUrls: ["branch-page.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BranchPageComponent extends NgLifeCycleEvents {
    constructor() {
        super();
    }
}