import { ChangeDetectionStrategy, Component } from "@angular/core";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import {
    livedbFilt,
    SettingPropertyTuple,
} from "@peek/peek_plugin_livedb/_private";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

@Component({
    selector: "pl-livedb-edit-setting",
    templateUrl: "./edit.component.html",
    styleUrls: ["./edit.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditSettingComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingPropertyTuple[]>([]);
    protected readonly loading$ = new BehaviorSubject<boolean>(false);
    private readonly loader: TupleLoader;

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
            Object.assign({}, this.filt, livedbFilt),
        );

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                this.items$.next(<SettingPropertyTuple[]>tuples);
            });
    }

    protected async handleSave(): Promise<void> {
        try {
            this.loading$.next(true);
            await this.loader.save();
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
