import { Component } from "@angular/core";
import { NzMessageService } from "ng-zorro-antd/message";
import {
    NgLifeCycleEvents,
    TupleLoader,
    VortexService,
    Tuple
} from "@synerty/vortexjs";
import { takeUntil } from "rxjs/operators";
import { searchFilt } from "@peek/peek_core_search/_private";
import { ExcludeSearchStringTable } from "../../tuples/ExcludeSearchStringTable";

@Component({
    selector: "pl-search-edit-exclude-search-term",
    templateUrl: "./edit.component.html",
})
export class EditExcludeSearchTermComponent extends NgLifeCycleEvents {
    items: ExcludeSearchStringTable[] = [];
    itemsToDelete: ExcludeSearchStringTable[] = [];
    loader: TupleLoader;
    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.ExcludeSearchStringTableHandler",
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
                const typedTuples = <ExcludeSearchStringTable[]>tuples;
                this.items = typedTuples;
            });
    }

    save() {
        for (const item of this.items) {
            item.term = item.term.toLowerCase();
        }

        let itemsToDelete = this.itemsToDelete;

        this.loader
            .save(this.items)
            .then(() => {
                if (itemsToDelete.length != 0) {
                    return this.loader.del(itemsToDelete);
                }
            })
            .then(() => this.message.success("Save Successful"))
            .catch((e) => this.message.error(e));
    }

    load() {
        this.loader
            .load()
            .then(() => this.message.success("Reset Successful"))
            .catch((e) => this.message.error(e));
    }

    addRow() {
        this.items = [...this.items, new ExcludeSearchStringTable()];
    }

    removeRow(item: ExcludeSearchStringTable) {
        if (item.id != null) {
            this.itemsToDelete.push(item);
        }

        this.items = this.items.filter((i) => i !== item);
    }
}
