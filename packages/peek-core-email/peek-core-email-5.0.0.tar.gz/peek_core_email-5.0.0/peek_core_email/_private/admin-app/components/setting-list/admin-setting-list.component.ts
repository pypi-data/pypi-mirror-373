import { ChangeDetectionStrategy, Component } from "@angular/core";
import {
    NgLifeCycleEvents,
    Tuple,
    TupleLoader,
    VortexService,
} from "@synerty/vortexjs";
import { coreEmailFilt } from "../../PluginNames";
import { BalloonMsgService } from "@synerty/peek-plugin-base-js";
import { BehaviorSubject } from "rxjs";
import { takeUntil } from "rxjs/operators";

class SettingProperty extends Tuple {
    id: number;
    settingId: number;
    key: string;
    type: string;

    int_value: number;
    char_value: string;
    boolean_value: boolean;

    constructor() {
        super("c.s.p.setting.property");
    }
}

@Component({
    selector: "core-email-setting-list",
    templateUrl: "./admin-setting-list.component.html",
    styleUrls: ["./admin-setting-list.component.scss"],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AdminSettingListComponent extends NgLifeCycleEvents {
    protected readonly items$ = new BehaviorSubject<SettingProperty[]>([]);
    protected readonly isLoading$ = new BehaviorSubject<boolean>(false);

    private readonly loader: TupleLoader;
    private readonly filt = {
        ...coreEmailFilt,
        key: "server.setting.data",
    };

    constructor(
        private balloonMsg: BalloonMsgService,
        vortexService: VortexService,
    ) {
        super();

        this.loader = vortexService.createTupleLoader(this, this.filt);

        this.loader.observable
            .pipe(takeUntil(this.onDestroyEvent))
            .subscribe((tuples: Tuple[]) => {
                const typedTuples = <SettingProperty[]>tuples;
                this.items$.next(typedTuples);
            });
    }

    protected async handleSave(): Promise<void> {
        try {
            this.isLoading$.next(true);
            await this.loader.save();
            this.balloonMsg.showSuccess("Save Successful");
        } catch (e) {
            this.balloonMsg.showError(`${e}`);
        } finally {
            this.isLoading$.next(false);
        }
    }

    protected async handleReset(): Promise<void> {
        try {
            this.isLoading$.next(true);
            await this.loader.load();
            this.balloonMsg.showSuccess("Reset Successful");
        } catch (e) {
            this.balloonMsg.showError(`${e}`);
        } finally {
            this.isLoading$.next(false);
        }
    }

    protected handleBooleanChange(item: SettingProperty): void {
        item.boolean_value = !item.boolean_value;
    }

    protected isPasswordField(key: string): boolean {
        return key.endsWith("pass");
    }
}
