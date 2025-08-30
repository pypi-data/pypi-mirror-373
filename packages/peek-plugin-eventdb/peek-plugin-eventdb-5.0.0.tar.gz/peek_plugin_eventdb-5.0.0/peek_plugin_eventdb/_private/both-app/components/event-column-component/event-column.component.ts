
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
                this.allProps$.next(state.allProps);
                const newSelectedProps = state.displayProps.map(prop => prop.key);
                
                // Only update if the selection has actually changed
                if (JSON.stringify(this.currentSelectedProps) !== JSON.stringify(newSelectedProps)) {
                    this.currentSelectedProps = [...newSelectedProps];
                    this.selectedProps$.next(this.currentSelectedProps);
                }
            });
    }

    handleModalOpen(): void {
        // Store the current selection when opening the modal
        this.currentSelectedProps = [...this.selectedProps$.getValue()];
        this.isVisible$.next(true);
    }

    handleModalApply(): void {
        if (this.isOkLoading$.getValue()) return;

        try {
            this.isOkLoading$.next(true);
            
            // Get the currently selected property objects
            const selectedKeys = this.selectedProps$.getValue();
            const allProps = this.allProps$.getValue();
            const selectedProps = allProps.filter(prop => selectedKeys.includes(prop.key));

            // Update the controller with the new selection
            if (selectedProps.length > 0) {
                this.controller.updateDisplayProps(selectedProps);
                this.controller.updateRoute();
                this.isVisible$.next(false);
            } else {
                throw new Error("At least one column must be selected");
            }
        } catch (error) {
            this.handleError("Failed to apply changes", error);
        } finally {
            this.isOkLoading$.next(false);
            this.cdr.markForCheck();
        }
    }

    handleDefaultReset(): void {
        try {
            const defaultProps = this.allProps$.getValue()
                .filter(prop => prop.displayByDefaultOnDetailView)
                .map(prop => prop.key);
            
            if (defaultProps.length > 0) {
                this.selectedProps$.next(defaultProps);
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
        this.selectedProps$.next([...this.currentSelectedProps]);
        this.isVisible$.next(false);
    }

    updateState(partial: Partial<ColumnState>): void {
        if (partial.selectedProps) {
            this.selectedProps$.next(partial.selectedProps);
        }
        
        this.state$.next({
            ...this.state$.value,
            ...partial,
        });
    }

    private handleError(message: string, error: any): void {
        console.error(message, error);
        this.balloonMsg.showError(message);
        this.isOkLoading$.next(false);
        this.cdr.markForCheck();
    }
}