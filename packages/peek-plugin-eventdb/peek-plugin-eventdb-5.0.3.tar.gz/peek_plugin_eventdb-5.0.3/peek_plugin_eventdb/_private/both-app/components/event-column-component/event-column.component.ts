
import {
    ChangeDetectionStrategy,
    ChangeDetectorRef,
    Component,
    Input,
    OnDestroy,
    OnInit,
} from "@angular/core";
import { EventDBPropertyTuple } from "@peek/peek_plugin_eventdb/tuples";
import { BehaviorSubject } from "rxjs";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { takeUntil } from "rxjs/operators";
import { EventDbController } from "../../controllers/event-db.controller";
import { NgLifeCycleEvents } from "@synerty/vortexjs";

interface ColumnState {
    allProps: EventDBPropertyTuple[];
    selectedProps: string[];
    isLoading: boolean;
}

@Component({
    selector: "plugin-eventdb-event-column",
    templateUrl: "event-column.component.html",
    styleUrls: ["./event-column.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EventDBColumnComponent
    extends NgLifeCycleEvents
    implements OnInit, OnDestroy
{
    @Input() controller: EventDbController;

    private readonly state$ = new BehaviorSubject<ColumnState>({
        allProps: [],
        selectedProps: [],
        isLoading: false,
    });

    readonly isVisible$ = new BehaviorSubject<boolean>(false);
    readonly isOkLoading$ = new BehaviorSubject<boolean>(false);
    readonly allProps$ = new BehaviorSubject<EventDBPropertyTuple[]>([]);
    readonly selectedProps$ = new BehaviorSubject<string[]>([]);

    private currentSelectedProps: string[] = [];

    constructor(
        private balloonMsg: BalloonMsgService,
        private cdr: ChangeDetectorRef,
    ) {
        super();
    }

    override ngOnInit(): void {
        this.controller
            .getState$()
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((state) => {
                this.allProps = state.allProps;
                const newSelectedProps = state.displayProps.map(prop => prop.key);
                
                // Only update if the selection has actually changed
                if (JSON.stringify(this.currentSelectedProps) !== JSON.stringify(newSelectedProps)) {
                    this.currentSelectedProps = [...newSelectedProps];
                    this.selectedProps = this.currentSelectedProps;
                }
            });
    }

    get isVisible(): boolean {
        return this.isVisible$.getValue();
    }

    set isVisible(value: boolean) {
        this.isVisible$.next(value);
    }

    get isOkLoading(): boolean {
        return this.isOkLoading$.getValue();
    }

    set isOkLoading(value: boolean) {
        this.isOkLoading$.next(value);
    }

    get allProps(): EventDBPropertyTuple[] {
        return this.allProps$.getValue();
    }

    set allProps(value: EventDBPropertyTuple[]) {
        this.allProps$.next(value);
    }

    get selectedProps(): string[] {
        return this.selectedProps$.getValue();
    }

    set selectedProps(value: string[]) {
        this.selectedProps$.next(value);
    }

    handleModalOpen(): void {
        // Store the current selection when opening the modal
        this.currentSelectedProps = [...this.selectedProps];
        this.isVisible = true;
    }

    handleModalApply(): void {
        if (this.isOkLoading) return;

        try {
            this.isOkLoading = true;
            
            // Get the currently selected property objects
            const selectedKeys = this.selectedProps;
            const allProps = this.allProps;
            const selectedProps = allProps.filter(prop => selectedKeys.includes(prop.key));

            // Update the controller with the new selection
            if (selectedProps.length > 0) {
                this.controller.updateDisplayProps(selectedProps);
                this.controller.updateRoute();
                this.isVisible = false;
            } else {
                throw new Error("At least one column must be selected");
            }
        } catch (error) {
            this.handleError("Failed to apply changes", error);
        } finally {
            this.isOkLoading = false;
            this.cdr.markForCheck();
        }
    }

    handleDefaultReset(): void {
        try {
            const defaultProps = this.allProps
                .filter(prop => prop.displayByDefaultOnDetailView)
                .map(prop => prop.key);
            
            if (defaultProps.length > 0) {
                this.selectedProps = defaultProps;
                this.currentSelectedProps = [...defaultProps];
            } else {
                throw new Error("No default columns found");
            }
        } catch (error) {
            this.handleError("Failed to reset to defaults", error);
        }
    }

    handleModalCancel(): void {
        // Restore the previous selection on cancel
        this.selectedProps = [...this.currentSelectedProps];
        this.isVisible = false;
    }

    updateState(partial: Partial<ColumnState>): void {
        if (partial.selectedProps) {
            this.selectedProps = partial.selectedProps;
        }
        
        this.state$.next({
            ...this.state$.value,
            ...partial,
        });
    }

    private handleError(message: string, error: any): void {
        console.error(message, error);
        this.balloonMsg.showError(message);
        this.isOkLoading = false;
        this.cdr.markForCheck();
    }
}