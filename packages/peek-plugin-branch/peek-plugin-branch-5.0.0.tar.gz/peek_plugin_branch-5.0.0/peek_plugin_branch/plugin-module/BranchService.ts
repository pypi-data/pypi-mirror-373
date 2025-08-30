import { NgLifeCycleEvents, Tuple, TupleSelector } from "@synerty/vortexjs";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { BranchDetailTuple } from "./BranchDetailTuple";
import { PrivateBranchTupleService } from "./_private/services/PrivateBranchTupleService";
import { CreateBranchActionTuple } from "./_private";

@Injectable()
export class BranchService extends NgLifeCycleEvents {
    constructor(private tupleService: PrivateBranchTupleService) {
        super();

        // See peek_plugin_diagram, PrivateDiagramOfflineCacherService.ts
        // for offline caching support
    }

    async createBranch(newBranch: BranchDetailTuple): Promise<Tuple[]> {
        let action = new CreateBranchActionTuple();
        action.branchDetail = newBranch;

        const tupleSelector = new TupleSelector(BranchDetailTuple.tupleName, {
            modelSetKey: newBranch.modelSetKey,
        });

        const branches = await this.branches(newBranch.modelSetKey);
        branches.push(newBranch);

        this.tupleService.offlineObserver.updateOfflineState(
            tupleSelector,
            branches
        );

        // Then tell the server.
        return await this.tupleService.offlineAction.pushAction(action);
    }

    branches(modelSetKey: string): Promise<BranchDetailTuple[]> {
        let ts = new TupleSelector(BranchDetailTuple.tupleName, {
            modelSetKey: modelSetKey,
        });
        let promise: any =
            this.tupleService.offlineObserver.promiseFromTupleSelector(ts);
        return promise;
    }

    branches$(modelSetKey: string): Observable<BranchDetailTuple[]> {
        let ts = new TupleSelector(BranchDetailTuple.tupleName, {
            modelSetKey: modelSetKey,
        });
        return <Observable<BranchDetailTuple[]>>(
            this.tupleService.offlineObserver.subscribeToTupleSelector(ts)
        );
    }

    getBranch(
        modelSetKey: string,
        key: string,
    ): Promise<BranchDetailTuple | null> {
        let ts = new TupleSelector(BranchDetailTuple.tupleName, {
            modelSetKey: modelSetKey,
        });
        let promise: any = this.tupleService.offlineObserver
            .promiseFromTupleSelector(ts)
            .then((branches: BranchDetailTuple[]) => {
                return branches.filter((b) => b.key == key)[0];
            });
        return promise;
    }
}
