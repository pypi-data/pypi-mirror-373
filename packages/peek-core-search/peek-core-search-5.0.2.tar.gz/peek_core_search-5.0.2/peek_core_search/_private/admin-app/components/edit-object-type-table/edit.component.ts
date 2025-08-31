
import { Component } from "@angular/core";
import { NzMessageService } from 'ng-zorro-antd/message';
import {
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
    Tuple
} from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import { searchFilt } from "@peek/peek_core_search/_private";
import { SearchObjectTypeTuple } from "@peek/peek_core_search";

@Component({
    selector: "pl-search-edit-object-type",
    templateUrl: "./edit.component.html",
})
export class EditObjectTypeComponent extends NgLifeCycleEvents {
    items: SearchObjectTypeTuple[] = [];
    loader: TupleLoader;
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.SearchObjectTypeTuple",
    };

    constructor(
        private message: NzMessageService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, searchFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SearchObjectTypeTuple[]>tuples;
                this.items = typedTuples;
            });
    }

    save() {
        this.loader
            .save()
            .then(() => this.message.success("Save Successful"))
            .catch((e) => this.message.error(e));
    }

    resetClicked() {
        this.loader
            .load()
            .then(() => this.message.success("Reset Successful"))
            .catch((e) => this.message.error(e));
    }
}