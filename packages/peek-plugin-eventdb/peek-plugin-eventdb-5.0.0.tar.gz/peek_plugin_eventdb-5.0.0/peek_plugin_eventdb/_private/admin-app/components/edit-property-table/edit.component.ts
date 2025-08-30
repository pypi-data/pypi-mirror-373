import { ChangeDetectionStrategy, Component } from "@angular/core";
import { takeUntil } from "rxjs/operators";
import { BehaviorSubject } from "rxjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleDataObserverService,
    TupleLoader,
    TupleSelector,
    VortexService,
} from "@synerty/vortexjs";
import { eventdbFilt } from "../../PluginNames";
import { EventDBPropertyTableTuple } from "../../tuples/EventDBPropertyTableTuple";
import { EventDBModelSetTableTuple } from "../../tuples/EventDBModelSetTableTuple";
import { EventDBPropertyValueTableTuple } from "../../tuples/EventDBPropertyValueTableTuple";

interface FilterOption {
    num: number;
    text: string;
}

@Component({
    selector: "pl-eventdb-edit-property",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditPropertyComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<
        EventDBPropertyTableTuple[]
    >([]);
    protected readonly modelSets$ = new BehaviorSubject<
        EventDBModelSetTableTuple[]
    >([]);
    protected readonly loader: TupleLoader;

    protected readonly showFilterAsOptions: FilterOption[] = [
        { num: 1, text: "Free Text" },
        { num: 2, text: "Select Many" },
        { num: 3, text: "Select One" },
    ];

    // This must match the dict defined in the admin_backend handler
    private readonly filt = {
        key: "admin.Edit.EventDBPropertyTuple",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
        private tupleObserver: TupleDataObserverService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, () =>
            Object.assign({}, this.filt, eventdbFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const items = (<EventDBPropertyTableTuple[]>tuples) //
                    .map((item) => {
                        item.uiExpandValues = false;
                        return item;
                    });
                this.items$.next(items);
            });

        const ts = new TupleSelector(EventDBModelSetTableTuple.tupleName, {});
        this.tupleObserver
            .subscribeToTupleSelector(ts)
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const sortedSets = (<EventDBModelSetTableTuple[]>tuples) //
                    .sort((a, b) =>
                        a.name < b.name ? -1 : a.name > b.name ? 1 : 0,
                    );
                this.modelSets$.next(sortedSets);
            });
    }

    protected handleAdd(): void {
        const currentItems = this.items$.getValue();
        const newItem = new EventDBPropertyTableTuple();
        newItem.modelSetId = this.modelSets$.getValue()[0]?.id;
        newItem.order = 0;
        newItem.showFilterAs = 1;
        this.items$.next([...currentItems, newItem]);
    }

    protected handleRemove(itemIndex: number): void {
        const currentItems = this.items$.getValue();
        const updatedItems = [
            ...currentItems.slice(0, itemIndex),
            ...currentItems.slice(itemIndex + 1),
        ];
        this.items$.next(updatedItems);
    }

    protected handleSave(): void {
        const items = this.items$.getValue();
        for (const item of items) {
            if (!item.isValid) {
                this.balloonMsg.showWarning(
                    "Some properties are invalid, please fix them",
                );
                return;
            }
            if (!item.enableValues) {
                item.valuesFromAdminUi = [];
            }
        }

        this.loader
            .save(items)
            .then(() => this.balloonMsg.showSuccess("Save Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    protected handleReset(): void {
        this.loader
            .load()
            .then(() => this.balloonMsg.showSuccess("Reset Successful"))
            .catch((e) => this.balloonMsg.showError(e));
    }

    protected handleAddValue(item: EventDBPropertyTableTuple): void {
        if (item.valuesFromAdminUi == null) {
            item.valuesFromAdminUi = [];
        }
        const newValue = new EventDBPropertyValueTableTuple();
        item.valuesFromAdminUi = [...item.valuesFromAdminUi, newValue];
    }

    protected handleRemoveValue(
        item: EventDBPropertyTableTuple,
        valueIndex: number,
    ): void {
        item.valuesFromAdminUi = [
            ...item.valuesFromAdminUi.slice(0, valueIndex),
            ...item.valuesFromAdminUi.slice(valueIndex + 1),
        ];
    }
}
