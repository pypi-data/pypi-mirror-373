import { NativeAudio } from "@awesome-cordova-plugins/native-audio/ngx";
import { NotifierI } from "./notifier.interface";
import { LocalNotifications } from "@capacitor/local-notifications";
import { Dialog } from "@capacitor/dialog";

export class NativeNotifier implements NotifierI {
    private nativeAudio = new NativeAudio();
    private nativeAlarmId = "peek-inbox-alarm";

    loadSound(soundFilePath: string) {
        this.nativeAudio.preloadSimple(this.nativeAlarmId, soundFilePath).then(
            (e) => {
                console.log(`NATIVE NOTIFIER load sound success: ${e}`);
            },
            (e) => {
                console.error(`NATIVE NOTIFIER load sound fail: ${e}`);
            },
        );
    }

    playSound() {
        this.nativeAudio.play(this.nativeAlarmId).then(
            (e) => {
                // on success
                console.log(`NATIVE NOTIFIER played native sound: ${e}`);
            },
            (e) => {
                // on error
                console.error(
                    `NATIVE NOTIFIER failed to play native sound: ${e}`,
                );
            },
        );
    }

    sendLocalNotification(title: string, body: string): void {
        LocalNotifications.schedule({
            notifications: [
                {
                    title,
                    body,
                    id: new Date().getTime(),
                    schedule: { at: new Date(Date.now()) },
                    sound: null,
                    attachments: null,
                    actionTypeId: "",
                    extra: null,
                },
            ],
        });
    }

    async checkNotificationSettings(): Promise<void> {
        console.log("NATIVE NOTIFIER checking iOS permissions");
        let permissionStatus = await LocalNotifications.checkPermissions();

        if (permissionStatus.display === "prompt") {
            permissionStatus = await LocalNotifications.requestPermissions();
            return;
        }

        if (permissionStatus.display === "denied") {
            const confirmed = await Dialog.confirm({
                title: "Notifications Required",
                message:
                    "Peek requires notifications to be enabled.\n" +
                    "Would you like to enable them now?",
            });

            // Open notification settings
            if (confirmed) {
                (window as any)?.cordova?.plugins?.settings?.open(
                    "notification_id",
                    () => console.log("Opened settings."),
                    () => console.log("Failed to open settings."),
                );
            }
            return;
        }
    }
}
